# System Map: Backcast EVS Backend

**Last Updated:** 2025-12-29  
**Technology:** Python 3.12, FastAPI, SQLAlchemy 2.0, PostgreSQL, AsyncIO

## High-Level Architecture

Backcast EVS is a FastAPI-based backend implementing Entity Versioning Control System (EVCS) for project financial management. The system follows clean architecture principles with strict separation of concerns across four layers:

**API Layer** → **Service Layer** → **Repository Layer** → **Database**

## Core Technology Choices

- **Web Framework:** FastAPI (async ASGI, automatic OpenAPI docs)
- **ORM:** SQLAlchemy 2.0 (async, relationship loading, type-safe queries)
- **Database:** PostgreSQL 15+ (composite primary keys, JSONB, timestamp support)
- **Migration:** Alembic (async templates)
- **Testing:** pytest (pytest-asyncio, >80% coverage target)
- **Type Safety:** MyPy strict mode (100% type hint coverage)
- **Linting:** Ruff (import sorting, code quality)
- **Package Manager:** uv (fast, deterministic)

## Key Bounded Contexts

The system is partitioned into the following bounded contexts. See [01-bounded-contexts.md](01-bounded-contexts.md) for detailed definitions, responsibilities, and interactions.

1.  Authentication & Authorization
2.  User Management
3.  Department Management
4.  Project & WBE Management
5.  Cost Element & Financial Tracking
6.  Change Order & Branching
7.  EVM Calculations & Reporting

## Versioning Architecture (EVCS Core)

**Pattern:** Composite Primary Key `(id, valid_from)` for version tables  
**Immutability:** Append-only, updates create new versions  
**Query Filtering:** Automatic filtering to active + latest versions

**Two Versioning Types:**

1. **Non-Branching** (User, Department)
   - Simple history tracking
   - `UserVersion` with `(head_id, valid_from)` PK

2. **Branch-Enabled** (Project, WBE, CostElement)
   - Supports change order isolation
   - Composite PK includes `branch` field
   - Deep copy on branch creation
   - Merge operations with conflict detection

## Directory Structure

```
backend/
├── app/
│   ├── api/           # FastAPI routes & dependencies
│   ├── commands/      # Command pattern (Create/Update/Delete)
│   ├── core/          # Config, security, versioning helpers
│   ├── db/            # Session management  
│   ├── models/        # SQLAlchemy entities + Pydantic schemas
│   ├── repositories/  # Data access layer
│   └── services/      # Business logic orchestration
│
├── tests/
│   ├── unit/          # Commands, services, repositories
│   └── api/           # Integration tests
│
└── alembic/           # Database migrations
```

## Cross-Cutting Concerns

- **Database Strategy:** AsyncPG connection pooling, Alembic migrations
- **API Conventions:** REST, `/api/v1` prefix, pagination support
- **Error Handling:** HTTPException with structured detail, global exception handler
- **Security:** Argon2 password hashing, JWT access tokens, role-based middleware
- **Performance:** <200ms API response target, query optimization via indexes

## Roadmap

- Department Management
- EVCS Core (versioning helpers, time-travel queries)
- Project/WBE entities with branch support

## Key Design Decisions

- **ADR-001:** FastAPI + SQLAlchemy 2.0 for async performance
- **ADR-002:** Composite PK versioning over separate version tables
- **ADR-003:** Command pattern for write operations (undo support)
- **ADR-004:** Strict MyPy + 80% test coverage minimum

**For detailed architecture per context, see:** `02-architecture/contexts/{context-name}/architecture.md`
