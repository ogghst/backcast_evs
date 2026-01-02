# System Map: Backcast EVS

**Last Updated:** 2026-01-01
**Technology:** Python 3.12, FastAPI, React 18, PostgreSQL, AsyncIO

## High-Level Architecture

Backcast EVS is a full-stack application for project financial management.

- **Frontend**: React SPA (Single Page Application) for user interaction.
- **Backend**: FastAPI implementation of Entity Versioning Control System (EVCS).

**Frontend (SPA)** → **API Layer** → **Service Layer** → **Repository Layer** → **Database**

## Core Technology Choices

### Backend

- **Web Framework:** FastAPI (async ASGI)
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** PostgreSQL 15+
- **Migration:** Alembic
- **Testing:** pytest (asyncio)

### Frontend

- **Framework:** React 18 + Vite
- **Language:** TypeScript
- **UI Library:** Ant Design 6
- **Data Fetching:** TanStack Query (React Query)
- **State:** Zustand

## Key Bounded Contexts

The system is partitioned into the following bounded contexts. See [01-bounded-contexts.md](01-bounded-contexts.md).

1.  Authentication & Authorization
2.  User Management
3.  Department Management
4.  Project & WBE Management
5.  Cost Element & Financial Tracking
6.  Change Order & Branching
7.  EVM Calculations & Reporting

## Versioning Architecture (EVCS Core)

**Pattern:** Bitemporal Single-Table with PostgreSQL `TSTZRANGE`  
**Immutability:** Append-only, updates create new versions  
**ADR:** [ADR-005: Bitemporal Versioning](decisions/ADR-005-bitemporal-versioning.md)

**Key Features:**

- **Bitemporal:** Track valid time (business) and transaction time (system)
- **Branching:** All entities support branch isolation for change orders
- **Soft Delete:** Reversible deletion with `deleted_at` timestamp
- **Version Chain:** DAG structure via `parent_id` for history traversal
- **Generic Framework:** `TemporalBase`, `TemporalService[T]`, generic commands
- **Non-Versioned:** `SimpleBase` for config/preferences (standard CRUD)

**Documentation:** [EVCS Core Architecture](backend/contexts/evcs-core/architecture.md)

## Directory Structure

```
.
├── backend/
│   ├── app/           # FastAPI application
│   ├── tests/         # Pytest suite
│   └── alembic/       # Database migrations
│
└── frontend/
    ├── src/
    │   ├── api/       # API clients
    │   ├── features/  # Domain features
    │   └── layouts/   # UI Layouts
    └── vite.config.ts
```

## Cross-Cutting Concerns

- **Database Strategy:** AsyncPG connection pooling.
- **API Conventions:** REST, `/api/v1` prefix.
- **Security:** JWT access tokens, Argon2 hashing.
- **Performance:** <200ms API response target.

## Key Design Decisions

- **ADR-001:** FastAPI + SQLAlchemy 2.0 for async performance.
- **ADR-005:** Bitemporal versioning with PostgreSQL TSTZRANGE (supersedes ADR-002).
- **ADR-004:** Strict MyPy + 80% test coverage minimum.

**Detailed Architecture:**

- [Backend Contexts](backend/contexts/)
- [Frontend Contexts](frontend/contexts/)
- [ADR Index](decisions/adr-index.md)
