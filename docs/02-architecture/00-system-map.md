# System Map: Backcast EVS

**Last Updated:** 2025-12-30
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
- **UI Library:** Ant Design 5
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

**Pattern:** Composite Primary Key `(id, valid_from)` for version tables  
**Immutability:** Append-only, updates create new versions  

**Two Versioning Types:**
1. **Non-Branching** (User, Department): Simple history tracking.
2. **Branch-Enabled** (Project, WBE, CostElement): Supports change order isolation and branching.

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
- **ADR-002:** Composite PK versioning over separate version tables.
- **ADR-004:** Strict MyPy + 80% test coverage minimum.
- **ADR-005:** React + Vite + Ant Design for enterprise-grade UI.

**Detailed Architecture:**
- [Backend Architecture](02-architecture/backend/contexts/)
- [Frontend Architecture](02-architecture/frontend/contexts/)
