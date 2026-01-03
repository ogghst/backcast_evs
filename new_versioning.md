Implement a structured recap of the **key requirements** derived from user queries, along with the **architectural choices** made to address them. I've included **minimal code examples** (snippets) for clarity, focusing on core patterns without full implementations. This system evolved from a simple time-versioned entity to a generalized, extensible framework for temporal entities with branching, soft deletes, and relationships—optimized for SQLAlchemy + PostgreSQL in a FastAPI context.

### 1. **Core Requirement: Support for Time-Versioned Entities Using Native Range Types**
   - **Requirements**: Use SQLAlchemy's support for PostgreSQL range types (e.g., `TSTZRANGE`) for validity periods in temporal tables. Enable CRUD operations on versioned entities, ensuring new versions on changes, with queries for current/history.
   - **Architectural Choices**:
     - Adopted `TSTZRANGE` for `valid_period` with operators like `@>` for current checks.
     - Uni-temporal (valid time only; no transaction time yet).
     - Command pattern for operations to decouple logic (e.g., `CreateCommand`, `UpdateCommand`).
     - GIST indexes for range query perf.
   - **Minimal Code Example**:
     ```python
     from sqlalchemy.dialects.postgresql import TSTZRANGE
     from sqlalchemy.orm import Mapped, mapped_column

     class TemporalMixin:
         valid_period: Mapped[TSTZRANGE] = mapped_column(TSTZRANGE, nullable=False)

     class ProductVersion(TemporalBase):  # Inherits TemporalMixin
         __tablename__ = "product_versions"
     ```

### 2. **Generalization with Mixins and Protocols**
   - **Requirements**: Make entities reusable/extensible with minimal boilerplate. Support derived classes (e.g., add branch column). Use protocols for interfaces.
   - **Architectural Choices**:
     - Mixins for composability: `TemporalMixin` (core versioning + `clone()`), `SoftDeleteMixin`, `GitBranchMixin`.
     - `TemporalEntity` protocol for minimal contract.
     - Abstract `TemporalBase` combines mixins + indexes.
     - Generic types (`TypeVar[T]`) for type-safety in helpers/commands/services.
   - **Minimal Code Example**:
     ```python
     from typing import Protocol, TypeVar
     T = TypeVar("T", bound="TemporalEntity")

     class TemporalEntity(Protocol):
         valid_period: Mapped[TSTZRANGE]

     class TemporalMixin:
         def clone(self, **overrides) -> Self:
             # Copy attrs, exclude system fields
             pass

     class ProductVersion(TemporalBase, GitBranchMixin):
         branch: Mapped[str | None]
     ```

### 3. **Soft Delete and Git-Like Branching**
   - **Requirements**: Add soft delete (timestamp-based). Support branching (create from existing, merge with overwrite), forming a DAG via `parent_id`.
   - **Architectural Choices**:
     - `deleted_at` column + methods (`soft_delete()/undelete()`).
     - Git-inspired: `branch` label, self-ref `parent_id` FK, `merge_from_branch` for tracking.
     - Unique partial indexes to prevent multiple current versions per branch/root.
     - Hooks (`before_mutate/after_mutate`) for extensibility (e.g., undo/logging).
     - No multi-parent merges (simple overwrite for now).
   - **Minimal Code Example**:
     ```python
     class SoftDeleteMixin:
         deleted_at: Mapped[datetime | None]
         def soft_delete(self): self.deleted_at = func.now()

     class GitBranchMixin:
         parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("self.id"))

     class CreateBranchCommand(Generic[T]):
         def execute(self, session: Session) -> T:
             current = ...  # from from_branch
             new = current.clone(branch=new_branch, parent_id=current.id)
             session.add(new)
     ```

### 4. **Service Layer Abstraction for FastAPI**
   - **Requirements**: Abstract operations in a service class for FastAPI routes (dependency injection). Minimize per-entity boilerplate.
   - **Architectural Choices**:
     - Generic `TemporalService[T]` wraps commands, takes `Session` + entity class.
     - Entity-specific subclass (e.g., `ProductService`) adds wrappers if needed.
     - Mutators don't commit (caller does).
     - No fallback in merge (as per latest user OK)—merge uses simple overwrite, strict same-branch for relations.
   - **Minimal Code Example**:
     ```python
     class TemporalService(Generic[T]):
         def __init__(self, session: Session, entity_class: Type[T]):
             self.session = session
             self.entity_class = entity_class

         def merge_branch(self, root_id: UUID, source_branch: str, target_branch: str = "main") -> T:
             cmd = MergeBranchCommand(self.entity_class, root_id, source_branch, target_branch)
             return cmd.execute(self.session)

     class ProductService(TemporalService[ProductVersion]):
         pass  # Minimal – inherits all
     ```

### 5. **One-to-Many Relationships (Project ↔ WBE)**
   - **Requirements**: Model 1:N (Project 1 → many WBEs). Support strict (same-branch) or merge-style (fallback to main if missing in branch).
   - **Architectural Choices**:
     - FK on stable root ID (`project_id`), not version `id` (avoids cascades).
     - Relationships use `primaryjoin` with filters for current/same-branch (strict by default).
     - Service handles optional merge/fallback via query param (e.g., `resolution="strict"` or `"merge-fallback"` with UNION/EXISTS).
     - Branching optionally copies children (configurable strategy: copy-all, fallback-only).
     - No fallback in merge service (per user)—merge doesn't auto-resolve; explicit.
   - **Minimal Code Example**:
     ```python
     class ProjectVersion(...):
         wbes: Mapped[List["WBEVersion"]] = relationship(
             primaryjoin="and_(WBEVersion.project_id == ProjectVersion.project_id, WBEVersion.branch == ProjectVersion.branch, ...)"
         )

     class WBEVersion(...):
         project_id: Mapped[UUID] = mapped_column(ForeignKey("project_versions.project_id"))

     # In ProjectService
     def get_current_wbes(self, project_id: UUID, branch: str, resolution: str = "strict") -> List[WBEVersion]:
         if resolution == "strict":
             return self.session.scalars(select(WBEVersion).where(... same branch ...)).all()
         # Else: UNION with main fallback + ~exists(same_branch)
     ```

Critical Review
===============

**Strengths**:
- **Extensibility & Reusability (A+)**: Mixins + generics minimize boilerplate—new entities need ~10-20 lines (inherit, add fields, override FKs). Hooks enable future features like undo without refactoring.
- **Performance-Oriented (A)**: GIST/partial indexes optimize temporal/branch queries. UUID PKs are stable; root IDs group logically without composite PK bloat.
- **Domain Fit (A-)**: Handles time-versioning, branching, soft-delete well for audit-heavy domains (e.g., products, projects). Command pattern decouples ops for testing/events.
- **FastAPI Integration (B+)**: Service layer is DI-friendly; no commits in mutators promotes UoW pattern.
- **Type-Safety & Modern Python (A)**: Protocols, generics, annotations ensure robustness.

**Weaknesses**:
- **Complexity Creep (B-)**: Many mixins/commands can overwhelm juniors—risk of over-engineering for simple use cases. Fallback/merge logic in service adds query overhead (subqueries/UNIONs could slow large datasets without optimization).
- **Limited Bitemporal (C)**: Only uni-temporal; no transaction_time for full audit (e.g., who/when changed).
- **Merge Simplicity (B)**: Overwrite strategy ignores conflicts—real git-like needs diff/resolution.
- **Relationship Rigidity (B)**: Strict mode requires explicit child copies on branch; fallback risks inconsistency if main changes post-branch.
- **Testing/Validation Gaps (C+)**: No built-in validation (e.g., pydantic integration) or unit tests shown; hooks are underused.
- **Scalability (B)**: Fine for moderate data; but history tables grow linearly—needs partitioning/archiving for huge volumes.

Overall Grade: **B+**. Solid for mid-scale apps, but could be more battle-tested (e.g., via real perf benchmarks).

Suggested Improvements and Features
===================================

1. **Add Bitemporal Support**: Introduce `transaction_time: TSTZRANGE` in `TemporalMixin` (system-managed, immutable). Update commands to set it on insert/update. Queries filter both ranges.
   - **Why**: Full audit trail (valid + asserted time).
   - **Snippet**: `transaction_time: Mapped[TSTZRANGE] = mapped_column(server_default=func.tstzrange(func.now(), func.now(), "[]"))`

2. **Conflict Resolution in Merge**: Enhance `MergeBranchCommand` with strategies (e.g., manual diff via hooks, or auto-merge fields).
   - **Why**: Prevents silent overwrites in collaborative branches.
   - **Feature**: Add `merge_strategy: str = "overwrite"` param.

3. **Undo/Revert Enhancements**: Leverage hooks to build an undo stack (e.g., log mutations in a separate audit table). Expand `RevertCommand` to multi-level undo.
   - **Why**: User-friendly error recovery.
   - **Snippet**: In `before_mutate`: `session.add(AuditLog(entity_id=self.id, changes=...))`

4. **Partitioning & Archiving**: For large history, add table partitioning by `valid_period` or `branch`. Add service method to archive old versions.
   - **Why**: Scalability for long-lived entities.

5. **Pydantic Integration**: Auto-generate schemas from entities (e.g., via `sqlalchemy_to_pydantic`). Use in FastAPI for validation/serialization.
   - **Why**: Reduces boilerplate in routes; ensures type-safe APIs.
   - **Snippet**: `class ProductCreate(BaseModel): name: str; price_cents: int`

6. **Event Sourcing Hooks**: Fire domain events in `after_mutate` (e.g., via `blinker` or custom dispatcher) for integrations (e.g., notifications, caches).
   - **Why**: Decouples side-effects.

7. **Query Optimization**: Materialized views for "current state" across branches. Cache frequent queries (e.g., via Redis).
   - **Why**: Perf for read-heavy apps.

8. **Testing Framework**: Add pytest fixtures for session/entity setup. Test commands/services in isolation.
   - **Why**: Ensures reliability as system grows.

9. **Multi-Tenancy**: Add `tenant_id` mixin for shared DBs.
   - **Why**: Enterprise scalability.

10. **Documentation & Onboarding**: Generate ERDs via `sqlalchemy_schemadisplay`; add docstrings/examples for mixins.

This would elevate the system to A-grade for production use. If needed, we can prototype any of these!

# Full Codebase Reference:

```python
# app/core/db/base.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Self, TypeVar, Generic, Type
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import (
    Column, String, func, Index, ForeignKey, text,
    event as sa_event
)
from sqlalchemy.dialects.postgresql import TSTZRANGE, UUID as PG_UUID
from sqlalchemy.ext.declarative import declared_attr, declarative_base
from sqlalchemy.orm import (
    Mapped, mapped_column, Session, DeclarativeBase,
    relationship as sa_relationship
)

Base: DeclarativeBase = declarative_base()


T = TypeVar("T", bound="TemporalBase")


class TemporalBase(Base):
    """Abstract base for bitemporal entities with branching, soft-delete, and clone/revert support"""

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True
    )

    valid_time: Mapped[TSTZRANGE] = mapped_column(
        TSTZRANGE,
        nullable=False,
        server_default=func.tstzrange(func.now(), None, "[]"),
        index=True,
    )

    transaction_time: Mapped[TSTZRANGE] = mapped_column(
        TSTZRANGE,
        nullable=False,
        server_default=func.tstzrange(func.now(), func.now(), "[]"),
        index=True,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
        default=None,
        index=True
    )

    branch: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True,
        index=True,
        default="main"
    )

    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        # Self-ref; override in subclasses
        nullable=True,
        index=True
    )

    merge_from_branch: Mapped[Optional[str]] = mapped_column(
        String(80),
        nullable=True
    )

    @property
    def is_current(self) -> bool:
        now = func.now()
        return (
            self.valid_time.op("@>")(now)
            & self.transaction_time.op("@>")(now)
            & (self.deleted_at.is_(None))
        )

    def clone(self, **overrides: Any) -> Self:
        """Clone for new versions/branches/merges"""
        excluded = {
            "id", "valid_time", "transaction_time", "deleted_at",
            "parent_id", "merge_from_branch", "_sa_instance_state"
        }
        data = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_") and k not in excluded
        }
        data.update(overrides)

        data["valid_time"] = func.tstzrange(func.now(), None, "[]")
        data["transaction_time"] = func.tstzrange(func.now(), func.now(), "[]")

        return type(self)(**data)

    def soft_delete(self) -> None:
        self.deleted_at = func.now()

    def undelete(self) -> None:
        self.deleted_at = None

    @classmethod
    def current_for(
        cls: Type[T],
        session: Session,
        *,
        where: Any = True,
        order_by_desc: bool = True,
    ) -> Optional[T]:
        now = func.now().cast(TSTZRANGE)
        q = session.query(cls).filter(
            cls.valid_time.op("@>")(now),
            cls.transaction_time.op("@>")(now),
            cls.deleted_at.is_(None),
            where
        )
        if order_by_desc:
            q = q.order_by(cls.valid_time.desc())
        return q.first()

    @classmethod
    def close_current(
        cls: Type[T],
        session: Session,
        *,
        where: Any = True,
        end_time: Optional[datetime] = None,
    ) -> Optional[T]:
        current = cls.current_for(session, where=where)
        if current:
            end = end_time or func.now()
            current.valid_time = func.tstzrange(current.valid_time.lower, end, "[)")
            # Update tx time on close
            current.transaction_time = func.tstzrange(func.now(), func.now(), "[]")
        return current

    @declared_attr
    def __table_args__(cls) -> tuple:
        return (
            Index(
                f"ix_{cls.__tablename__}_valid_gist",
                "valid_time",
                postgresql_using="gist"
            ),
            Index(
                f"ix_{cls.__tablename__}_tx_gist",
                "transaction_time",
                postgresql_using="gist"
            ),
            Index(
                f"uq_{cls.__tablename__}_current_branch",
                "branch",
                postgresql_where=(
                    text("upper(valid_time) IS NULL")
                    & text("upper(transaction_time) IS NULL")
                    & text("deleted_at IS NULL")
                ),
                unique=True,
            ),
        )


# ────────────────────────────────────────────────
#   COMMANDS (Generic for all temporal entities)
# ────────────────────────────────────────────────

class CreateCommand(Generic[T]):
    def __init__(
        self,
        entity_class: Type[T],
        root_id: UUID,
        branch: str = "main",
        **fields: Any
    ):
        self.entity_class = entity_class
        self.root_id = root_id
        self.branch = branch
        self.fields = fields

    def execute(self, session: Session) -> T:
        root_field = f"{self.entity_class.__name__.lower().removesuffix('version')}_id"
        version = self.entity_class(
            branch=self.branch,
            **{root_field: self.root_id},
            **self.fields
        )
        session.add(version)
        return version


class UpdateCommand(Generic[T]):
    def __init__(
        self,
        entity_class: Type[T],
        root_id: UUID,
        updates: Dict[str, Any],
        branch: str = "main"
    ):
        self.entity_class = entity_class
        self.root_id = root_id
        self.updates = updates
        self.branch = branch

    def execute(self, session: Session) -> T:
        root_field = f"{self.entity_class.__name__.lower().removesuffix('version')}_id"
        where = (
            getattr(self.entity_class, "branch") == self.branch,
            getattr(self.entity_class, root_field) == self.root_id,
        )
        current = self.entity_class.current_for(session, where=where)
        if not current:
            raise ValueError(f"No current version in branch {self.branch} for root {self.root_id}")
        self.entity_class.close_current(session, where=where)
        new_version = current.clone(parent_id=current.id, **self.updates)
        session.add(new_version)
        return new_version


class SoftDeleteCommand(Generic[T]):
    def __init__(
        self,
        entity_class: Type[T],
        root_id: UUID,
        branch: str = "main"
    ):
        self.entity_class = entity_class
        self.root_id = root_id
        self.branch = branch

    def execute(self, session: Session) -> Optional[T]:
        root_field = f"{self.entity_class.__name__.lower().removesuffix('version')}_id"
        where = (
            getattr(self.entity_class, "branch") == self.branch,
            getattr(self.entity_class, root_field) == self.root_id,
        )
        current = self.entity_class.current_for(session, where=where)
        if current:
            current.soft_delete()
        return current


class UndeleteCommand(Generic[T]):
    def __init__(
        self,
        entity_class: Type[T],
        root_id: UUID,
        branch: str = "main"
    ):
        self.entity_class = entity_class
        self.root_id = root_id
        self.branch = branch

    def execute(self, session: Session) -> Optional[T]:
        root_field = f"{self.entity_class.__name__.lower().removesuffix('version')}_id"
        where = (
            getattr(self.entity_class, "branch") == self.branch,
            getattr(self.entity_class, root_field) == self.root_id,
            getattr(self.entity_class, "deleted_at").isnot(None),
        )
        deleted = session.query(self.entity_class).filter(*where).order_by(
            self.entity_class.valid_time.desc()
        ).first()
        if deleted:
            deleted.undelete()
        return deleted


class CreateBranchCommand(Generic[T]):
    def __init__(
        self,
        entity_class: Type[T],
        root_id: UUID,
        new_branch: str,
        from_branch: str = "main"
    ):
        self.entity_class = entity_class
        self.root_id = root_id
        self.new_branch = new_branch
        self.from_branch = from_branch

    def execute(self, session: Session) -> T:
        root_field = f"{self.entity_class.__name__.lower().removesuffix('version')}_id"
        where = (
            getattr(self.entity_class, "branch") == self.from_branch,
            getattr(self.entity_class, root_field) == self.root_id,
        )
        current = self.entity_class.current_for(session, where=where)
        if not current:
            raise ValueError(f"No current version in branch {self.from_branch} for root {self.root_id}")
        new_version = current.clone(branch=self.new_branch, parent_id=current.id)
        session.add(new_version)
        return new_version


class MergeBranchCommand(Generic[T]):
    def __init__(
        self,
        entity_class: Type[T],
        root_id: UUID,
        source_branch: str,
        target_branch: str = "main"
    ):
        self.entity_class = entity_class
        self.root_id = root_id
        self.source_branch = source_branch
        self.target_branch = target_branch

    def execute(self, session: Session) -> T:
        root_field = f"{self.entity_class.__name__.lower().removesuffix('version')}_id"
        source_where = (
            getattr(self.entity_class, "branch") == self.source_branch,
            getattr(self.entity_class, root_field) == self.root_id,
        )
        source_current = self.entity_class.current_for(session, where=source_where)
        if not source_current:
            raise ValueError(f"No current version in source branch {self.source_branch}")

        target_where = (
            getattr(self.entity_class, "branch") == self.target_branch,
            getattr(self.entity_class, root_field) == self.root_id,
        )
        target_current = self.entity_class.current_for(session, where=target_where)

        if target_current:
            self.entity_class.close_current(session, where=target_where)

        new_version = source_current.clone(
            branch=self.target_branch,
            parent_id=target_current.id if target_current else None,
            merge_from_branch=self.source_branch
        )
        session.add(new_version)
        return new_version


class RevertCommand(Generic[T]):
    """Revert to parent version state (undo last change via history)"""
    def __init__(
        self,
        entity_class: Type[T],
        root_id: UUID,
        branch: str = "main",
        to_version_id: Optional[UUID] = None  # Optional: revert to specific ancestor
    ):
        self.entity_class = entity_class
        self.root_id = root_id
        self.branch = branch
        self.to_version_id = to_version_id

    def execute(self, session: Session) -> Optional[T]:
        root_field = f"{self.entity_class.__name__.lower().removesuffix('version')}_id"
        where = (
            getattr(self.entity_class, "branch") == self.branch,
            getattr(self.entity_class, root_field) == self.root_id,
        )
        current = self.entity_class.current_for(session, where=where)
        if not current:
            raise ValueError(f"No current version in branch {self.branch}")

        target_id = self.to_version_id or current.parent_id
        if not target_id:
            raise ValueError("No parent to revert to")

        target = session.get(self.entity_class, target_id)
        if not target:
            raise ValueError("Target version not found")

        self.entity_class.close_current(session, where=where)
        new_version = target.clone(parent_id=current.id, branch=self.branch)
        session.add(new_version)
        return new_version


# ────────────────────────────────────────────────
#   PROJECT ENTITY (example)
# ────────────────────────────────────────────────

class ProjectVersion(TemporalBase):
    __tablename__ = "project_versions"

    parent_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project_versions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    # Add more domain fields as needed

    # Relationships (example for 1:N with WBE – strict same-branch current)
    # wbes: Mapped[List["WBEVersion"]] = sa_relationship(... )  # As in previous

    class Create(BaseModel):
        name: str
        description: Optional[str] = None
        branch: str = "main"

        model_config = ConfigDict(from_attributes=True)

    class Update(BaseModel):
        name: Optional[str] = None
        description: Optional[str] = None

        model_config = ConfigDict(from_attributes=True)

    class Read(BaseModel):
        id: UUID
        project_id: UUID
        name: str
        description: Optional[str]
        branch: Optional[str]
        valid_time: str  # Serialize range as string
        transaction_time: str
        deleted_at: Optional[datetime]

        model_config = ConfigDict(from_attributes=True)


# Trigger tx_time update on UPDATE
@sa_event.listens_for(TemporalBase, "before_update", propagate=True)
def update_tx_time(mapper, connection, target):
    target.transaction_time = func.tstzrange(func.now(), func.now(), "[]")


# ────────────────────────────────────────────────
#   BASE SERVICE (Generic)
# ────────────────────────────────────────────────

class TemporalService(Generic[T]):
    def __init__(self, session: Session, entity_class: Type[T]):
        self.session = session
        self.entity_class = entity_class
        self.root_field = f"{entity_class.__name__.lower().removesuffix('version')}_id"

    def create(self, root_id: UUID, branch: str = "main", **fields: Any) -> T:
        cmd = CreateCommand(self.entity_class, root_id, branch, **fields)
        return cmd.execute(self.session)

    def get_current(
        self, root_id: UUID, branch: str = "main", include_deleted: bool = False
    ) -> Optional[T]:
        where = (getattr(self.entity_class, self.root_field) == root_id, getattr(self.entity_class, "branch") == branch)
        if not include_deleted:
            where += (getattr(self.entity_class, "deleted_at").is_(None),)
        return self.entity_class.current_for(self.session, where=where)

    def update(self, root_id: UUID, updates: Dict[str, Any], branch: str = "main") -> T:
        cmd = UpdateCommand(self.entity_class, root_id, updates, branch)
        return cmd.execute(self.session)

    def soft_delete(self, root_id: UUID, branch: str = "main") -> Optional[T]:
        cmd = SoftDeleteCommand(self.entity_class, root_id, branch)
        return cmd.execute(self.session)

    def undelete(self, root_id: UUID, branch: str = "main") -> Optional[T]:
        cmd = UndeleteCommand(self.entity_class, root_id, branch)
        return cmd.execute(self.session)

    def create_branch(self, root_id: UUID, new_branch: str, from_branch: str = "main") -> T:
        cmd = CreateBranchCommand(self.entity_class, root_id, new_branch, from_branch)
        return cmd.execute(self.session)

    def merge_branch(self, root_id: UUID, source_branch: str, target_branch: str = "main") -> T:
        cmd = MergeBranchCommand(self.entity_class, root_id, source_branch, target_branch)
        return cmd.execute(self.session)

    def revert(self, root_id: UUID, branch: str = "main", to_version_id: Optional[UUID] = None) -> Optional[T]:
        cmd = RevertCommand(self.entity_class, root_id, branch, to_version_id)
        return cmd.execute(self.session)

    # Add history, list_branches, etc. as needed


# ────────────────────────────────────────────────
#   PROJECT SERVICE (inherits generic + specifics)
# ────────────────────────────────────────────────

class ProjectService(TemporalService[ProjectVersion]):
    def __init__(self, session: Session):
        super().__init__(session, ProjectVersion)

    # Example entity-specific wrapper
    def create_project(self, data: ProjectVersion.Create) -> ProjectVersion:
        root_id = uuid4()
        return self.create(
            root_id=root_id,
            branch=data.branch,
            name=data.name,
            description=data.description
        )

    def update_project(self, project_id: UUID, data: ProjectVersion.Update, branch: str = "main") -> ProjectVersion:
        updates = data.model_dump(exclude_unset=True)
        return self.update(project_id, updates, branch)

    # Add get_wbes, etc. if 1:N needed


# ────────────────────────────────────────────────
#   FASTAPI ROUTES EXAMPLE (projects.py)
# ────────────────────────────────────────────────

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.db.session import get_db
from app.models.project import ProjectVersion
from app.services.project import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", status_code=201)
def create_project(
    data: ProjectVersion.Create,
    db: Session = Depends(get_db)
) -> Dict[str, UUID]:
    service = ProjectService(db)
    version = service.create_project(data)
    db.commit()
    return {"project_id": version.project_id, "version_id": version.id}


@router.get("/{project_id}/current")
def get_current_project(
    project_id: UUID,
    branch: str = "main",
    db: Session = Depends(get_db)
) -> ProjectVersion.Read:
    service = ProjectService(db)
    version = service.get_current(project_id, branch)
    if not version:
        raise HTTPException(404, "No current version found")
    return ProjectVersion.Read.from_orm(version)


@router.patch("/{project_id}")
def update_project(
    project_id: UUID,
    data: ProjectVersion.Update,
    branch: str = "main",
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    service = ProjectService(db)
    try:
        new_version = service.update_project(project_id, data, branch)
        db.commit()
        return {"message": "Updated", "new_version_id": str(new_version.id)}
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/{project_id}/revert")
def revert_project(
    project_id: UUID,
    branch: str = "main",
    to_version_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    service = ProjectService(db)
    try:
        new_version = service.revert(project_id, branch, to_version_id)
        if not new_version:
            raise ValueError("Revert failed")
        db.commit()
        return {"message": "Reverted", "new_version_id": str(new_version.id)}
    except ValueError as e:
        raise HTTPException(400, str(e))


# Add soft_delete, create_branch, merge_branch routes similarly
```