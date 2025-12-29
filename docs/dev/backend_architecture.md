# Backend Architecture Documentation

## 1. Executive Summary

This document defines the technical architecture for the **Backcast EVS (Entity Versioning System)** backend, a Project Budget Management and Earned Value Management (EVM) application with Git-style versioning capabilities.

The system implements:
- **Immutable Version History:** All entity changes create new version records; history is never overwritten
- **Branch Isolation:** Full support for parallel development via change order branches
- **Time Travel:** Query any entity's state at any historical point in time
- **Type Safety:** Comprehensive type hints with strict MyPy validation
- **Clean Architecture:** Strict separation of concerns across API, Service, and Repository layers

---

## 2. Technology Stack

### 2.1 Core Runtime

| Component | Version | Rationale |
|-----------|---------|-----------|
| **Python** | 3.12+ | Advanced type hints (`TypeAlias`, improved generics), performance improvements, pattern matching |
| **FastAPI** | 0.115+ | ASGI performance, native Pydantic V2 integration, automatic OpenAPI docs, dependency injection |
| **Uvicorn** | Latest | Production-grade ASGI server with worker management |

### 2.2 Data Layer

| Component | Version | Rationale |
|-----------|---------|-----------|
| **PostgreSQL** | 15+ | `DISTINCT ON`, Recursive CTEs, JSONB, composite primary keys, advanced indexing |
| **SQLAlchemy** | 2.0+ | Async support, `Mapped[]` type hints, 2.0-style queries, declarative models |
| **Alembic** | 1.12+ | Database schema version control, auto-generation from models |
| **asyncpg** | Latest | High-performance async PostgreSQL driver |

### 2.3 Validation & Serialization

| Component | Version | Rationale |
|-----------|---------|-----------|
| **Pydantic** | 2.0+ | Rust-powered validation, settings management, JSON schema generation |
| **pydantic-settings** | 2.0+ | Environment-based configuration with validation |

### 2.4 Development Tools

| Tool | Purpose |
|------|---------|
| **uv** | Fast Python package installer and resolver |
| **ruff** | Fast linter and formatter (replaces black, isort, flake8) |
| **mypy** | Static type checker (strict mode) |
| **pytest** | Testing framework with async support |
| **pytest-cov** | Code coverage reporting |
| **httpx** | Async HTTP client for API testing |
| **pre-commit** | Git hooks for automated quality checks |

---

## 3. Architecture Patterns

### 3.1 Layered Architecture

The application follows **Clean Architecture** principles with strict dependency rules:

```mermaid
graph TB
    subgraph "Presentation Layer"
        API[FastAPI Routes]
    end
    
    subgraph "Application Layer"
        Services[Service Layer]
    end
    
    subgraph "Domain Layer"
        Models[Domain Models]
        Schemas[Pydantic Schemas]
    end
    
    subgraph "Infrastructure Layer"
        Repos[Repositories]
        DB[(PostgreSQL)]
    end
    
    subgraph "Cross-Cutting"
        Auth[Authentication]
        Config[Configuration]
        Events[Event Bus]
    end
    
    API --> Services
    Services --> Repos
    Services --> Models
    API --> Schemas
    Repos --> DB
    Repos --> Models
    Services -.-> Events
    API -.-> Auth
```

**Dependency Rules:**
- **API Layer** depends on Services and Schemas (never on Repositories or ORM models)
- **Service Layer** depends on Repositories and Domain Models
- **Repository Layer** depends only on Domain Models and Database
- **Domain Layer** has no dependencies (pure business logic)

### 3.2 Authentication Pattern

Authentication follows a **stateless JWT** pattern integrated with the EVCS architecture:

- **Identity Separation**: User identity (Head) is separated from User profile state (Version).
  - `User` (Head): Stores immutable identity (`id`, `email`) and security credentials (`hashed_password`).
  - `UserVersion`: Stores mutable profile data (`full_name`, `role`, `department`) with full version history.
- **Stateless Tokens**: `ACCESS_TOKEN` (JWT) is issued upon login and contains `sub` (user_id).
- **Security**: 
  - Passwords are hashed using **Argon2** (via `pwdlib`).
  - `hashed_password` is **never** versioned in history tables to prevent security leaks in audit logs.
- **Authorization**:
  - `get_current_user` dependency validates the token signature.
  - `get_current_active_user` checks the `is_active` flag on the *latest* `UserVersion`.

### 3.3 Schema Mapping Pattern

To maintain separation of concerns and reduce duplication:
- **Factory Methods**: Complex transformations from Domain Models -> Pydantic Schemas reside in the Schema layer.
- **Pattern**: Use `SchemaClass.from_entity(domain_entity)` factory methods (e.g., `UserPublic.from_entity(user)`) to encapsulate logic for combining Head and Version data.
- **Prohibition**: Do not perform manual field-by-field mapping in API route handlers.

### 3.4 Dependency Injection Pattern

FastAPI's dependency injection system manages all cross-cutting concerns:

```python
# app/api/dependencies/database.py
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session_maker

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide database session with automatic cleanup."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# app/api/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from app.models.domain.user import User
from app.services.auth import AuthService

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate current user from JWT token."""
    auth_service = AuthService(db)
    user = await auth_service.get_user_from_token(token.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user

# Usage in routes
@router.get("/projects/")
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectPublic]:
    service = ProjectService(db)
    projects = await service.list_user_projects(current_user.id)
    return [ProjectPublic.model_validate(p) for p in projects]
```

### 3.3 Repository Pattern

Repositories abstract all database operations and implement the versioning logic:

```python
# app/repositories/base.py
from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

HeadT = TypeVar("HeadT")
VersionT = TypeVar("VersionT")

class VersionedRepository(Generic[HeadT, VersionT]):
    """Base repository for versioned entities."""
    
    def __init__(
        self,
        session: AsyncSession,
        head_model: type[HeadT],
        version_model: type[VersionT],
    ):
        self.session = session
        self.head_model = head_model
        self.version_model = version_model
    
    async def get(self, id: UUID, branch: str = "main") -> HeadT | None:
        """Get current head for entity."""
        stmt = select(self.head_model).where(
            self.head_model.id == id,
            self.head_model.branch == branch,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_at_date(
        self,
        id: UUID,
        branch: str,
        control_date: datetime,
    ) -> VersionT | None:
        """Time-travel: get entity version at specific date."""
        stmt = (
            select(self.version_model)
            .where(
                self.version_model.head_id == id,
                self.version_model.branch == branch,
                self.version_model.valid_from <= control_date,
                (self.version_model.valid_to.is_(None) | 
                 (self.version_model.valid_to > control_date)),
            )
            .order_by(self.version_model.valid_from.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

# app/repositories/project.py
class ProjectRepository(VersionedRepository[Project, ProjectVersion]):
    """Project-specific repository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project, ProjectVersion)
    
    async def list_by_user(self, user_id: UUID, branch: str = "main") -> list[Project]:
        """Get all projects for a user."""
        stmt = select(self.head_model).where(
            self.head_model.owner_id == user_id,
            self.head_model.branch == branch,
            self.head_model.status == "active",
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
```

### 3.4 Service Layer Pattern

Services orchestrate business logic and coordinate between repositories:

```python
# app/services/project.py
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.project import ProjectRepository
from app.models.domain.project import Project
from app.core.versioning import create_entity_with_version

class ProjectService:
    """Business logic for project management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProjectRepository(session)
    
    async def create_project(
        self,
        name: str,
        owner_id: UUID,
        branch: str = "main",
    ) -> Project:
        """Create new project with initial version."""
        project = await create_entity_with_version(
            session=self.session,
            head_model=Project,
            version_model=ProjectVersion,
            data={"name": name, "owner_id": owner_id},
            branch=branch,
        )
        return project
    
    async def list_user_projects(self, user_id: UUID) -> list[Project]:
        """Get all active projects for user."""
        return await self.repo.list_by_user(user_id)
```

---

## 4. Database Architecture

### 4.1 Composite Primary Key Pattern

All versioned entities use a **composite primary key** of `(id, branch)`:

```python
from sqlalchemy import String, UUID
from sqlalchemy.orm import Mapped, mapped_column

class Project(Base):
    """Project head table - stable identity."""
    __tablename__ = "projects"
    
    # Composite Primary Key
    id: Mapped[UUID] = mapped_column(primary_key=True)
    branch: Mapped[str] = mapped_column(String(100), primary_key=True, default="main")
    
    # Mutable fields
    current_version_id: Mapped[UUID] = mapped_column(UUID, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
```

### 4.2 Version Table Pattern

Version tables store immutable historical snapshots:

```python
class ProjectVersion(Base):
    """Project version table - immutable history."""
    __tablename__ = "project_versions"
    
    # Unique version ID
    id: Mapped[UUID] = mapped_column(primary_key=True)
    
    # Reference to head
    head_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    branch: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Version chain
    parent_version_id: Mapped[UUID | None] = mapped_column(UUID, nullable=True)
    version: Mapped[int] = mapped_column(nullable=False)
    
    # Temporal validity
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Business data (immutable)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[UUID] = mapped_column(UUID, nullable=False)
```

### 4.3 Async Session Management

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
```

---

## 5. Entity Versioning & Branching System Architecture

This section provides an in-depth exploration of the Entity Version Control System (EVCS), which implements Git-like versioning and branching for database entities.

### 5.1 System Overview

The EVCS is built on several foundational design patterns that work together to provide:

- **Type Safety:** Compile-time type verification using Python generics and MyPy
- **Git-like Branching:** Multiple parallel branches, each pointing to specific commits
- **Temporal Queries:** Retrieve entity state at any commit, timestamp, or branch
- **Immutability:** Commits and snapshots are immutable, ensuring historical integrity
- **Flexibility:** Custom serialization through `to_dict()`/`from_dict()` methods
- **Performance:** Optimized indexes on `entity_type`, `entity_id`, and `commit_id`
- **Diff Capabilities:** Compare versions across commits and branches

- **Diff Capabilities:** Compare versions across commits and branches

### 5.2 Core Architectural Patterns

#### 5.2.1 The "Git" Data Model (DAG)

We separate the concept of **Identity** from **State**.

*   **Entity (Container):** Represents the stable identity (ID).
*   **Version (Commit):** An immutable snapshot of data at a point in time. Contains a `parent_id` pointer, forming a Directed Acyclic Graph (DAG).
*   **Branch (Pointer):** A mutable reference to a specific `Version` (HEAD).

#### 5.2.2 Generic Type Pattern with TypeVar

The implementation leverages Python's type system to ensure compile-time type safety through generics. The `VersionedRepository` class is parameterized on the entity type it manages, allowing MyPy to verify type correctness.

**Benefits:**
- Compile-time type checking prevents runtime errors
- IDE autocomplete and type hints improve developer experience
- Generic repository eliminates code duplication across entity types

**Implementation:**

```python
# app/core/versioning/types.py
from typing import TypeVar, Protocol, Generic
from uuid import UUID
from datetime import datetime

class VersionableEntity(Protocol):
    """Protocol defining the interface for versionable entities."""
    id: UUID
    branch: str
    current_version_id: UUID | None
    status: str
    
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "VersionableEntity": ...

class VersionSnapshot(Protocol):
    """Protocol defining the interface for version snapshots."""
    id: UUID
    head_id: UUID
    branch: str
    parent_version_id: UUID | None
    version: int
    valid_from: datetime
    valid_to: datetime | None
    created_at: datetime
    created_by: UUID
    
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "VersionSnapshot": ...

# Type variables for generic repository
HeadT = TypeVar("HeadT", bound=VersionableEntity)
VersionT = TypeVar("VersionT", bound=VersionSnapshot)

# Generic repository with type safety
class VersionedRepository(Generic[HeadT, VersionT]):
    """
    Generic repository for versioned entities.
    
    Type parameters ensure compile-time verification:
    - HeadT: The head table model (e.g., Project)
    - VersionT: The version table model (e.g., ProjectVersion)
    """
    
    def __init__(
        self,
        session: AsyncSession,
        head_model: type[HeadT],
        version_model: type[VersionT],
    ):
        self.session = session
        self.head_model = head_model
        self.version_model = version_model
    
    async def get(self, id: UUID, branch: str = "main") -> HeadT | None:
        """Type-safe retrieval of head entity."""
        # MyPy knows the return type is HeadT
        ...
    
    async def create_version(
        self,
        head: HeadT,
        data: dict,
        user_id: UUID,
    ) -> VersionT:
        """Type-safe version creation."""
        # MyPy knows the return type is VersionT
        ...
```

**Usage Example:**

```python
# app/repositories/project.py
from app.models.domain.project import Project, ProjectVersion
from app.core.versioning.repository import VersionedRepository

class ProjectRepository(VersionedRepository[Project, ProjectVersion]):
    """
    Project-specific repository.
    MyPy knows:
    - self.head_model is type[Project]
    - self.version_model is type[ProjectVersion]
    - get() returns Project | None
    - create_version() returns ProjectVersion
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project, ProjectVersion)
    
    async def get_by_name(self, name: str, branch: str = "main") -> Project | None:
        """Custom query with full type safety."""
        stmt = select(self.head_model).where(
            self.head_model.name == name,
            self.head_model.branch == branch,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()  # MyPy knows this is Project | None
```

#### 5.2.3 Mixin Pattern with declared_attr

The Mixin Pattern allows adding common functionality to different classes through multiple inheritance. We implement a **Mixin Hierarchy** to separate basic versioning (temporal validity) from advanced branching capabilities.

**Hierarchy:**
1.  **Base Mixins (`BaseHeadMixin`, `BaseVersionMixin`)**: Provide core versioning (Identity, Temporal Validity, Auditing). Used for non-branching entities like `User`.
2.  **Branch-Aware Mixins (`VersionableHeadMixin`, `VersionSnapshotMixin`)**: Extend the base mixins to add `branch`, `parent_version_id`, and composite primary keys including branch. Used for `Project`, `WBE`, etc.

**Features:**
- **Generic Serialization**: All mixins implement `to_dict()` using SQLAlchemy inspection to automatically serializes all columns.
- **Timezone Awareness**: All timestamps use `DateTime(timezone=True)` (TIMESTAMPTZ) and `datetime.now(timezone.utc)`.

**Implementation:**

```python
# app/models/mixins/versionable.py
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, inspect
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

# ============================================================================
# Base Mixins (Non-Branching)
# ============================================================================

class BaseHeadMixin:
    """Base mixin for head tables (stable identity)."""
    
    @declared_attr
    def id(cls) -> Mapped[UUID]:
        """Logical entity ID (stable identity)."""
        return mapped_column(SQLUUID, primary_key=True, default=uuid4)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize entity to dictionary using SQLAlchemy inspection."""
        from sqlalchemy.orm import Mapper
        data = {}
        mapper = inspect(self.__class__)
        if isinstance(mapper, Mapper):
            for column in mapper.column_attrs:
                value = getattr(self, column.key)
                if isinstance(value, UUID):
                    data[column.key] = str(value)
                elif isinstance(value, datetime):
                    data[column.key] = value.isoformat()
                else:
                    data[column.key] = value
        return data

class BaseVersionMixin:
    """Base mixin for version tables (immutable snapshots)."""
    
    @declared_attr
    def head_id(cls) -> Mapped[UUID]:
        return mapped_column(SQLUUID, primary_key=True, index=True)
    
    @declared_attr
    def valid_from(cls) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), primary_key=True, index=True, default=lambda: datetime.now(timezone.utc))
    
    @declared_attr
    def valid_to(cls) -> Mapped[datetime | None]:
        return mapped_column(DateTime(timezone=True), nullable=True, index=True)
    
    @declared_attr
    def created_by_id(cls) -> Mapped[UUID | None]:
        return mapped_column(SQLUUID, nullable=True)
    
    # Uses generic to_dict() logic similar to BaseHeadMixin

# ============================================================================
# Branch-Aware Mixins (Extends Base Mixins)
# ============================================================================

class VersionableHeadMixin(BaseHeadMixin):
    """Mixin for branch-aware head tables."""
    
    @declared_attr
    def branch(cls) -> Mapped[str]:
        return mapped_column(String(100), primary_key=True, default="main")
    
    @declared_attr
    def current_version_id(cls) -> Mapped[UUID | None]:
        return mapped_column(SQLUUID, nullable=True)
    
    @declared_attr
    def status(cls) -> Mapped[str]:
        return mapped_column(String(20), default="active", index=True)

class VersionSnapshotMixin(BaseVersionMixin):
    """Mixin for branch-aware version tables."""
    
    @declared_attr
    def branch(cls) -> Mapped[str]:
        return mapped_column(String(100), primary_key=True, index=True)
    
    @declared_attr
    def parent_version_id(cls) -> Mapped[UUID | None]:
        return mapped_column(SQLUUID, nullable=True, index=True)
    
    @declared_attr
    def version(cls) -> Mapped[int]:
        return mapped_column(nullable=False)
```

**Usage in domain models:**

```python
# app/models/domain/project.py
class Project(VersionableHeadMixin, Base):
    """Project head table with versioning capabilities."""
    __tablename__ = "projects"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(SQLUUID, nullable=False)

class ProjectVersion(VersionSnapshotMixin, Base):
    """Project version table with immutable snapshots."""
    __tablename__ = "project_versions"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=True)
    owner_id: Mapped[UUID] = mapped_column(SQLUUID, nullable=False)
```

#### 5.2.4 Snapshot Pattern for Temporal Data (Time Propagation)

The Snapshot Pattern stores the complete state of an entity at each significant point in time. Unlike a changelog that records only changes, a snapshot contains the entire state, simplifying temporal queries.

To resolve the "Parent-Child" consistency problem (e.g., "What did the Project AND its Tasks look like last Tuesday?"), we use **Time Propagation**.

**Mechanism:**
We use PostgreSQL `DISTINCT ON (entity_id) ORDER BY created_at DESC` filtered by the requested timestamp. This efficiently retrieves the valid version of every child entity at that exact moment.

**Benefits:**
- Simple temporal queries (no need to replay changes)
- Fast point-in-time reconstruction
- Complete audit trail
- Supports complex entity graphs

**Implementation:**

```python
# app/core/versioning/snapshot.py
from typing import TypeVar, Generic
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=VersionSnapshot)

class SnapshotManager(Generic[T]):
    """
    Manages creation and retrieval of entity snapshots.
    Each snapshot captures the complete entity state.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        version_model: type[T],
    ):
        self.session = session
        self.version_model = version_model
    
    async def create_snapshot(
        self,
        head_id: UUID,
        branch: str,
        data: dict,
        user_id: UUID,
        parent_version_id: UUID | None = None,
    ) -> T:
        """
        Create immutable snapshot of entity state.
        
        The snapshot contains:
        - Complete entity data (not just changes)
        - Link to parent version (DAG structure)
        - Temporal validity range
        - Audit information
        """
        # Get next version number
        stmt = select(func.coalesce(func.max(self.version_model.version), 0)).where(
            self.version_model.head_id == head_id,
            self.version_model.branch == branch,
        )
        result = await self.session.execute(stmt)
        next_version = result.scalar() + 1
        
        # Close previous version's validity
        if parent_version_id:
            stmt = (
                update(self.version_model)
                .where(self.version_model.id == parent_version_id)
                .values(valid_to=datetime.now(timezone.utc))
            )
            await self.session.execute(stmt)
        
        # Create new snapshot with complete state
        snapshot = self.version_model(
            head_id=head_id,
            branch=branch,
            parent_version_id=parent_version_id,
            version=next_version,
            valid_from=datetime.now(timezone.utc),
            valid_to=None,  # Open-ended validity
            created_by=user_id,
            **data,  # Complete entity state
        )
        
        self.session.add(snapshot)
        await self.session.flush()
        return snapshot
    
    async def get_snapshot_at_time(
        self,
        head_id: UUID,
        branch: str,
        control_date: datetime,
    ) -> T | None:
        """
        Retrieve entity snapshot valid at specific time.
        
        Uses temporal validity range for efficient lookup:
        valid_from <= control_date < valid_to (or valid_to IS NULL)
        """
        stmt = (
            select(self.version_model)
            .where(
                self.version_model.head_id == head_id,
                self.version_model.branch == branch,
                self.version_model.valid_from <= control_date,
                (self.version_model.valid_to.is_(None) | 
                 (self.version_model.valid_to > control_date)),
            )
            .order_by(self.version_model.valid_from.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_snapshot_by_version(
        self,
        head_id: UUID,
        branch: str,
        version: int,
    ) -> T | None:
        """Retrieve specific version snapshot."""
        stmt = select(self.version_model).where(
            self.version_model.head_id == head_id,
            self.version_model.branch == branch,
            self.version_model.version == version,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_version_history(
        self,
        head_id: UUID,
        branch: str,
    ) -> list[T]:
        """Get complete version history for entity in branch."""
        stmt = (
            select(self.version_model)
            .where(
                self.version_model.head_id == head_id,
                self.version_model.branch == branch,
            )
            .order_by(self.version_model.version.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
```

#### 5.2.5 Command Pattern for Operations

Every modification operation to the repository represents a command that is recorded as a commit. The commit itself contains operation metadata, effectively implementing the Command Pattern with undo capabilities.

**Benefits:**
- Every operation is traceable
- Supports undo/redo functionality
- Audit trail of all changes
- Can replay operations

**Implementation:**

```python
# app/core/versioning/commands.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

T = TypeVar("T")

@dataclass
class CommandMetadata:
    """Metadata for version control commands."""
    command_type: str
    user_id: UUID
    timestamp: datetime
    description: str
    branch: str

class VersionCommand(ABC, Generic[T]):
    """
    Abstract base class for version control commands.
    Each command represents an atomic operation on an entity.
    """
    
    def __init__(self, metadata: CommandMetadata):
        self.metadata = metadata
    
    @abstractmethod
    async def execute(self, session: AsyncSession) -> T:
        """Execute the command and return the result."""
        pass
    
    @abstractmethod
    async def undo(self, session: AsyncSession) -> None:
        """Undo the command (if possible)."""
        pass
    
    def to_commit_message(self) -> str:
        """Generate commit message for this command."""
        return f"[{self.metadata.command_type}] {self.metadata.description}"

class CreateEntityCommand(VersionCommand[HeadT]):
    """Command to create a new versioned entity."""
    
    def __init__(
        self,
        metadata: CommandMetadata,
        head_model: type[HeadT],
        version_model: type[VersionT],
        data: dict,
    ):
        super().__init__(metadata)
        self.head_model = head_model
        self.version_model = version_model
        self.data = data
        self.created_head_id: UUID | None = None
    
    async def execute(self, session: AsyncSession) -> HeadT:
        """Create head and initial version snapshot."""
        # Create head entity
        head = self.head_model(
            branch=self.metadata.branch,
            status="active",
        )
        session.add(head)
        await session.flush()
        self.created_head_id = head.id
        
        # Create initial version snapshot
        snapshot = self.version_model(
            head_id=head.id,
            branch=self.metadata.branch,
            parent_version_id=None,
            version=1,
            valid_from=self.metadata.timestamp,
            valid_to=None,
            created_by=self.metadata.user_id,
            **self.data,
        )
        session.add(snapshot)
        await session.flush()
        
        # Update head to point to version
        head.current_version_id = snapshot.id
        return head
    
    async def undo(self, session: AsyncSession) -> None:
        """Soft delete the created entity."""
        if self.created_head_id:
            # Create deletion version
            stmt = select(self.head_model).where(
                self.head_model.id == self.created_head_id,
                self.head_model.branch == self.metadata.branch,
            )
            result = await session.execute(stmt)
            head = result.scalar_one()
            head.status = "deleted"

class UpdateEntityCommand(VersionCommand[VersionT]):
    """Command to update an existing entity."""
    
    def __init__(
        self,
        metadata: CommandMetadata,
        head_id: UUID,
        version_model: type[VersionT],
        changes: dict,
    ):
        super().__init__(metadata)
        self.head_id = head_id
        self.version_model = version_model
        self.changes = changes
        self.new_version_id: UUID | None = None
        self.previous_version_id: UUID | None = None
    
    async def execute(self, session: AsyncSession) -> VersionT:
        """Create new version snapshot with changes."""
        # Get current version
        stmt = (
            select(self.version_model)
            .where(
                self.version_model.head_id == self.head_id,
                self.version_model.branch == self.metadata.branch,
                self.version_model.valid_to.is_(None),
            )
        )
        result = await session.execute(stmt)
        current_version = result.scalar_one()
        self.previous_version_id = current_version.id
        
        # Close current version
        current_version.valid_to = self.metadata.timestamp
        
        # Create new version with changes
        version_data = current_version.to_dict()
        version_data.update(self.changes)
        
        new_version = self.version_model(
            head_id=self.head_id,
            branch=self.metadata.branch,
            parent_version_id=current_version.id,
            version=current_version.version + 1,
            valid_from=self.metadata.timestamp,
            valid_to=None,
            created_by=self.metadata.user_id,
            **{k: v for k, v in version_data.items() 
               if k not in ['id', 'head_id', 'branch', 'parent_version_id', 
                           'version', 'valid_from', 'valid_to', 'created_at', 'created_by']},
        )
        session.add(new_version)
        await session.flush()
        self.new_version_id = new_version.id
        
        return new_version
    
    async def undo(self, session: AsyncSession) -> None:
        """Revert to previous version."""
        if self.new_version_id and self.previous_version_id:
            # Delete new version
            stmt = delete(self.version_model).where(
                self.version_model.id == self.new_version_id
            )
            await session.execute(stmt)
            
            # Reopen previous version
            stmt = (
                update(self.version_model)
                .where(self.version_model.id == self.previous_version_id)
                .values(valid_to=None)
            )
            await session.execute(stmt)

class CommandExecutor:
    """Executes and tracks version control commands."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.command_history: list[VersionCommand] = []
    
    async def execute(self, command: VersionCommand[T]) -> T:
        """Execute command and add to history."""
        result = await command.execute(self.session)
        self.command_history.append(command)
        return result
    
    async def undo_last(self) -> None:
        """Undo the last executed command."""
        if self.command_history:
            command = self.command_history.pop()
            await command.undo(self.session)
```

#### 5.2.6 Immutable Object Pattern

Commits and snapshots are immutable by design. Once created, their state cannot be modified, ensuring the integrity of history. This pattern is fundamental for reliable version control systems.

**Benefits:**
- Historical integrity guaranteed
- Thread-safe (no concurrent modification issues)
- Simplified reasoning about state
- Enables caching and optimization

**Implementation:**

```python
# app/models/domain/immutable.py
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.exc import InvalidRequestError

class ImmutableVersionMixin:
    """
    Mixin that enforces immutability on version records.
    Once created, version records cannot be modified.
    """
    
    __immutable__ = True
    
    @classmethod
    def __declare_last__(cls):
        """Register event listeners to enforce immutability."""
        
        @event.listens_for(cls, "before_update", propagate=True)
        def prevent_update(mapper, connection, target):
            """Prevent any updates to immutable records."""
            if getattr(cls, "__immutable__", False):
                raise InvalidRequestError(
                    f"Cannot update immutable {cls.__name__} record. "
                    f"Version records are immutable once created."
                )
        
        @event.listens_for(cls, "before_delete", propagate=True)
        def prevent_delete(mapper, connection, target):
            """Prevent deletion of immutable records."""
            if getattr(cls, "__immutable__", False):
                raise InvalidRequestError(
                    f"Cannot delete immutable {cls.__name__} record. "
                    f"Version records are permanent."
                )

# Usage in version models
class ProjectVersion(ImmutableVersionMixin, VersionSnapshotMixin, Base):
    """
    Project version table with immutability enforced.
    Any attempt to update or delete will raise an exception.
    """
    __tablename__ = "project_versions"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=True)

# Example: Attempting to modify raises an exception
async def example_immutability():
    version = await session.get(ProjectVersion, version_id)
    
    # This will raise InvalidRequestError
    try:
        version.name = "Modified Name"
        await session.commit()
    except InvalidRequestError as e:
        print(f"Immutability enforced: {e}")
    
    # Correct approach: Create new version
    new_version = await create_new_version(
        head_id=version.head_id,
        changes={"name": "Modified Name"},
    )
```

#### 5.2.7 Chain of Responsibility Pattern

When searching for an entity's state at a specific commit, the system traverses the chain of parent commits until it finds the relevant snapshot. This implements the Chain of Responsibility pattern.

**Benefits:**
- Flexible version traversal
- Supports complex version graphs (branches, merges)
- Enables diff calculation between any two versions

**Implementation:**

```python
# app/core/versioning/chain.py
from typing import TypeVar, Generic, Callable
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound=VersionSnapshot)

class VersionChain(Generic[T]):
    """
    Traverses the version chain (DAG) to find snapshots.
    Implements Chain of Responsibility for version lookup.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        version_model: type[T],
    ):
        self.session = session
        self.version_model = version_model
    
    async def traverse_to_root(
        self,
        version_id: UUID,
    ) -> list[T]:
        """
        Traverse from given version to root (version 1).
        Returns list of versions in reverse chronological order.
        """
        chain: list[T] = []
        current_id = version_id
        
        while current_id:
            stmt = select(self.version_model).where(
                self.version_model.id == current_id
            )
            result = await self.session.execute(stmt)
            version = result.scalar_one_or_none()
            
            if not version:
                break
            
            chain.append(version)
            current_id = version.parent_version_id
        
        return chain
    
    async def find_common_ancestor(
        self,
        version_a_id: UUID,
        version_b_id: UUID,
    ) -> T | None:
        """
        Find the most recent common ancestor of two versions.
        Used for three-way merges and diff calculations.
        """
        # Get chains for both versions
        chain_a = await self.traverse_to_root(version_a_id)
        chain_b = await self.traverse_to_root(version_b_id)
        
        # Convert to sets of IDs
        ids_a = {v.id for v in chain_a}
        ids_b = {v.id for v in chain_b}
        
        # Find common ancestors
        common_ids = ids_a & ids_b
        
        if not common_ids:
            return None
        
        # Return the most recent common ancestor
        for version in chain_a:
            if version.id in common_ids:
                return version
        
        return None
    
    async def apply_handler_chain(
        self,
        version_id: UUID,
        handlers: list[Callable[[T], bool]],
    ) -> T | None:
        """
        Apply chain of handlers to find matching version.
        Each handler returns True if it handles the version.
        """
        chain = await self.traverse_to_root(version_id)
        
        for version in chain:
            for handler in handlers:
                if handler(version):
                    return version
        
        return None

# Example: Find version where budget exceeded threshold
async def find_budget_threshold_version(
    session: AsyncSession,
    current_version_id: UUID,
    threshold: Decimal,
) -> ProjectVersion | None:
    """
    Traverse version chain to find when budget first exceeded threshold.
    """
    chain = VersionChain(session, ProjectVersion)
    
    def budget_exceeds_threshold(version: ProjectVersion) -> bool:
        return version.budget > threshold
    
    return await chain.apply_handler_chain(
        current_version_id,
        [budget_exceeds_threshold],
    )
```

#### 5.2.8 Observer Pattern for Domain Events

The Observer Pattern decouples version control operations from side effects (notifications, cache invalidation, webhooks) using an event bus.

**Benefits:**
- Loose coupling between core logic and side effects
- Easy to add new event handlers
- Supports async event processing
- Testable in isolation

**Implementation:**

```python
# app/core/events/bus.py
from typing import Callable, Any
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from collections import defaultdict
import asyncio

@dataclass
class DomainEvent:
    """Base class for domain events."""
    event_type: str
    timestamp: datetime
    user_id: UUID
    metadata: dict[str, Any]

@dataclass
class EntityCreatedEvent(DomainEvent):
    """Event fired when entity is created."""
    entity_id: UUID
    entity_type: str
    branch: str
    version_id: UUID

@dataclass
class EntityUpdatedEvent(DomainEvent):
    """Event fired when entity is updated."""
    entity_id: UUID
    entity_type: str
    branch: str
    version_id: UUID
    changes: dict[str, Any]

@dataclass
class BranchCreatedEvent(DomainEvent):
    """Event fired when branch is created."""
    source_branch: str
    target_branch: str
    entity_count: int

@dataclass
class BranchMergedEvent(DomainEvent):
    """Event fired when branch is merged."""
    source_branch: str
    target_branch: str
    merged_entities: list[UUID]

EventHandler = Callable[[DomainEvent], Any]

class EventBus:
    """
    In-memory event bus for domain events.
    Implements Observer pattern for loose coupling.
    """
    
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._async_handlers: dict[str, list[EventHandler]] = defaultdict(list)
    
    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        async_handler: bool = False,
    ) -> None:
        """Register event handler for specific event type."""
        if async_handler:
            self._async_handlers[event_type].append(handler)
        else:
            self._handlers[event_type].append(handler)
    
    def unsubscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """Remove event handler."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
        if handler in self._async_handlers[event_type]:
            self._async_handlers[event_type].remove(handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish event to all registered handlers."""
        # Execute sync handlers
        for handler in self._handlers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                # Log error but don't stop other handlers
                print(f"Error in event handler: {e}")
        
        # Execute async handlers concurrently
        async_tasks = [
            handler(event)
            for handler in self._async_handlers[event.event_type]
        ]
        
        if async_tasks:
            results = await asyncio.gather(*async_tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    print(f"Error in async event handler: {result}")

# Global event bus instance
event_bus = EventBus()

# Example event handlers
async def send_notification_on_entity_created(event: EntityCreatedEvent):
    """Send notification when entity is created."""
    # Send email, push notification, etc.
    print(f"Notification: Entity {event.entity_id} created in branch {event.branch}")

async def invalidate_cache_on_entity_updated(event: EntityUpdatedEvent):
    """Invalidate cache when entity is updated."""
    # Clear cached data
    print(f"Cache invalidated for entity {event.entity_id}")

def log_domain_event(event: DomainEvent):
    """Log all domain events."""
    print(f"[{event.timestamp}] {event.event_type}: {event.metadata}")

# Register handlers
event_bus.subscribe("entity_created", send_notification_on_entity_created, async_handler=True)
event_bus.subscribe("entity_updated", invalidate_cache_on_entity_updated, async_handler=True)
event_bus.subscribe("entity_created", log_domain_event)
event_bus.subscribe("entity_updated", log_domain_event)

# Usage in repository
class VersionedRepository(Generic[HeadT, VersionT]):
    async def create(self, data: dict, user_id: UUID, branch: str = "main") -> HeadT:
        """Create entity and publish event."""
        # Create entity
        head = await self._create_head_and_version(data, user_id, branch)
        
        # Publish event
        event = EntityCreatedEvent(
            event_type="entity_created",
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            entity_id=head.id,
            entity_type=self.head_model.__tablename__,
            branch=branch,
            version_id=head.current_version_id,
            metadata={},
        )
        await event_bus.publish(event)
        
        return head
```

### 5.3 Diff and Comparison System

The diff system compares entity states across versions, branches, and time periods.

**Implementation:**

```python
# app/core/versioning/diff.py
from typing import TypeVar, Generic, Any
from dataclasses import dataclass
from enum import Enum

T = TypeVar("T", bound=VersionSnapshot)

class ChangeType(Enum):
    """Types of changes in diff."""
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"
    UNCHANGED = "unchanged"

@dataclass
class FieldDiff:
    """Difference in a single field."""
    field_name: str
    change_type: ChangeType
    old_value: Any
    new_value: Any

@dataclass
class EntityDiff:
    """Complete diff between two entity versions."""
    entity_id: UUID
    entity_type: str
    old_version: int | None
    new_version: int | None
    field_diffs: list[FieldDiff]
    
    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return any(
            diff.change_type != ChangeType.UNCHANGED
            for diff in self.field_diffs
        )

class DiffCalculator(Generic[T]):
    """Calculate differences between entity versions."""
    
    def __init__(self, version_model: type[T]):
        self.version_model = version_model
        self._excluded_fields = {
            'id', 'head_id', 'branch', 'parent_version_id',
            'version', 'valid_from', 'valid_to', 'created_at', 'created_by'
        }
    
    def calculate_diff(
        self,
        old_version: T | None,
        new_version: T | None,
    ) -> EntityDiff:
        """
        Calculate diff between two versions.
        Handles cases where one version is None (creation/deletion).
        """
        if old_version is None and new_version is None:
            raise ValueError("Both versions cannot be None")
        
        entity_id = (new_version or old_version).head_id
        entity_type = self.version_model.__tablename__
        
        old_data = old_version.to_dict() if old_version else {}
        new_data = new_version.to_dict() if new_version else {}
        
        # Get all business fields
        all_fields = set(old_data.keys()) | set(new_data.keys())
        business_fields = all_fields - self._excluded_fields
        
        field_diffs: list[FieldDiff] = []
        
        for field in sorted(business_fields):
            old_value = old_data.get(field)
            new_value = new_data.get(field)
            
            if field not in old_data:
                change_type = ChangeType.ADDED
            elif field not in new_data:
                change_type = ChangeType.REMOVED
            elif old_value != new_value:
                change_type = ChangeType.MODIFIED
            else:
                change_type = ChangeType.UNCHANGED
            
            field_diffs.append(FieldDiff(
                field_name=field,
                change_type=change_type,
                old_value=old_value,
                new_value=new_value,
            ))
        
        return EntityDiff(
            entity_id=entity_id,
            entity_type=entity_type,
            old_version=old_version.version if old_version else None,
            new_version=new_version.version if new_version else None,
            field_diffs=field_diffs,
        )
    
    async def calculate_branch_diff(
        self,
        session: AsyncSession,
        entity_id: UUID,
        source_branch: str,
        target_branch: str,
    ) -> EntityDiff:
        """Calculate diff between same entity in different branches."""
        # Get current version in source branch
        stmt = (
            select(self.version_model)
            .where(
                self.version_model.head_id == entity_id,
                self.version_model.branch == source_branch,
                self.version_model.valid_to.is_(None),
            )
        )
        result = await session.execute(stmt)
        source_version = result.scalar_one_or_none()
        
        # Get current version in target branch
        stmt = (
            select(self.version_model)
            .where(
                self.version_model.head_id == entity_id,
                self.version_model.branch == target_branch,
                self.version_model.valid_to.is_(None),
            )
        )
        result = await session.execute(stmt)
        target_version = result.scalar_one_or_none()
        
        return self.calculate_diff(source_version, target_version)

# Usage example
async def compare_branches(session: AsyncSession, project_id: UUID):
    """Compare project between main and change order branch."""
    calculator = DiffCalculator(ProjectVersion)
    
    diff = await calculator.calculate_branch_diff(
        session,
        project_id,
        source_branch="co-123",
        target_branch="main",
    )
    
    if diff.has_changes:
        print(f"Changes found in project {project_id}:")
        for field_diff in diff.field_diffs:
            if field_diff.change_type != ChangeType.UNCHANGED:
                print(f"  {field_diff.field_name}: "
                      f"{field_diff.old_value} -> {field_diff.new_value}")
```

### 5.4 Performance Optimization

**Database Indexes:**

```sql
-- Composite indexes for efficient temporal queries
CREATE INDEX idx_version_temporal ON project_versions(head_id, branch, valid_from, valid_to);
CREATE INDEX idx_version_lookup ON project_versions(head_id, branch, version);
CREATE INDEX idx_version_chain ON project_versions(parent_version_id);

-- Partial index for current versions
CREATE INDEX idx_current_versions ON project_versions(head_id, branch) 
WHERE valid_to IS NULL;

-- Index for branch operations
CREATE INDEX idx_head_branch_status ON projects(branch, status);
```

**Query Optimization:**

```python
# Use DISTINCT ON for efficient "latest version" queries
stmt = (
    select(ProjectVersion)
    .where(ProjectVersion.branch == "main")
    .distinct(ProjectVersion.head_id)
    .order_by(ProjectVersion.head_id, ProjectVersion.version.desc())
)

# Eager load relationships to avoid N+1 queries
stmt = (
    select(Project)
    .options(selectinload(Project.versions))
    .where(Project.branch == "main")
)
```

---

## 6. Security Architecture

### 5.1 Authentication

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password."""
    return pwd_context.hash(password)
```

### 5.2 Authorization

```python
# app/api/dependencies/permissions.py
from fastapi import Depends, HTTPException, status
from app.models.domain.user import User
from app.api.dependencies.auth import get_current_user

async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin role."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
```

---

## 6. Configuration Management

```python
# app/core/config.py
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings from environment."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    APP_NAME: str = "Backcast EVS"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: PostgresDsn = Field(..., validation_alias="DATABASE_URL")
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        """Validate and transform database URL."""
        if isinstance(v, str):
            return v.replace("postgresql://", "postgresql+asyncpg://")
        return v

settings = Settings()
```

---

## 7. Testing Strategy

### 7.1 Test Structure

```
tests/
├── unit/                   # Fast, isolated tests
│   ├── test_services/
│   ├── test_repositories/
│   └── test_utils/
├── integration/            # Database integration tests
│   ├── test_api/
│   └── test_versioning/
├── conftest.py            # Shared fixtures
└── factories.py           # Test data factories
```

### 7.2 Test Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.base import Base

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost/test_db",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncSession:
    """Provide clean database session for each test."""
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()
```

### 7.3 API Testing

```python
# tests/integration/test_api/test_projects.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, auth_headers: dict):
    """Test project creation endpoint."""
    response = await client.post(
        "/api/v1/projects/",
        json={"name": "Test Project", "budget": 100000},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data
```

---

## 8. CI/CD Pipeline

### 8.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Install dependencies
        run: uv sync
      - name: Run ruff
        run: uv run ruff check .
      - name: Check formatting
        run: uv run ruff format --check .
  
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Install dependencies
        run: uv sync
      - name: Run mypy
        run: uv run mypy .
  
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Install dependencies
        run: uv sync
      - name: Run tests
        run: uv run pytest --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://test:test@localhost/test_db
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 8.2 Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.2
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

---

## 9. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies/          # Dependency injection providers
│   │   │   ├── auth.py
│   │   │   ├── database.py
│   │   │   └── permissions.py
│   │   └── routes/                # API endpoints
│   │       ├── __init__.py
│   │       ├── projects.py
│   │       ├── wbes.py
│   │       └── cost_elements.py
│   ├── core/                      # Core utilities
│   │   ├── config.py              # Settings management
│   │   ├── security.py            # Auth utilities
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── versioning.py          # Version helpers
│   ├── db/
│   │   ├── base.py                # SQLAlchemy base
│   │   └── session.py             # Session management
│   ├── models/
│   │   ├── domain/                # SQLAlchemy ORM models
│   │   │   ├── project.py
│   │   │   ├── wbe.py
│   │   │   └── user.py
│   │   └── schemas/               # Pydantic DTOs
│   │       ├── project.py
│   │       ├── wbe.py
│   │       └── user.py
│   ├── repositories/              # Data access layer
│   │   ├── base.py
│   │   ├── project.py
│   │   └── wbe.py
│   └── services/                  # Business logic layer
│       ├── project.py
│       ├── wbe.py
│       └── auth.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── conftest.py
│   └── factories.py
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
├── .env.example
├── .pre-commit-config.yaml
├── pyproject.toml
├── docker-compose.yml
└── README.md
```

---

## 10. Development Guidelines

### 10.1 Code Style

1. **Type Everything:** All functions must have type hints for parameters and return values
2. **Async by Default:** Use `async def` for all I/O operations
3. **Dependency Injection:** Never instantiate dependencies directly; use FastAPI's `Depends()`
4. **No ORM in Routes:** API routes return Pydantic schemas, never SQLAlchemy models
5. **Immutable Versions:** Never `UPDATE` version tables; always `INSERT` new rows

### 10.2 Naming Conventions

- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions/Variables:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private:** Prefix with `_`

### 10.3 Error Handling

```python
from fastapi import HTTPException, status

# Use appropriate HTTP status codes
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Project not found",
)

# Custom exceptions for business logic
class VersionConflictError(Exception):
    """Raised when version conflict detected."""
    pass
```

### 10.4 Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use structured logging
logger.info(
    "Project created",
    extra={"project_id": str(project.id), "user_id": str(user.id)},
)
```

---

## 11. Performance Optimization

### 11.1 Database Query Optimization

- Use `selectinload()` for eager loading relationships
- Add indexes on frequently queried columns
- Use `EXPLAIN ANALYZE` to optimize slow queries
- Implement pagination for large result sets

### 11.2 Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_settings() -> Settings:
    """Cache settings instance."""
    return Settings()
```

### 11.3 Connection Pooling

- Configure appropriate pool sizes based on load
- Use `pool_pre_ping=True` for connection health checks
- Monitor connection pool metrics

---

## 12. Deployment Considerations

### 12.1 Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (min 32 chars)
- `BACKEND_CORS_ORIGINS`: Comma-separated allowed origins

### 12.2 Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install dependencies
COPY pyproject.toml .
RUN uv sync --frozen

# Copy application
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

---

## 13. Monitoring & Observability

### 13.1 Health Checks

```python
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
```

### 13.2 Metrics

- Request latency
- Database query performance
- Error rates
- Active connections

---

## 14. References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
