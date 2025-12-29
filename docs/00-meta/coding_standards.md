# Coding Standards

## 1. Python Standards

### 1.1 Type Safety (MyPy)
- **Strict Mode:** All code must pass `mypy --strict`.
- **Explicit Returns:** All functions must have return type hints.
- **Generics:** Use `TypeVar` for reusable components.
- **No Implicit Optional:** Explicitly use `None` as default for `Optional` arguments.

### 1.2 Linting (Ruff)
- **Configuration:** `pyproject.toml`
- **Line Length:** 88 characters (Black compatible)
- **Import Sorting:** `isort` compatible (enforced by Ruff I001)
- **FastAPI Exception:** `B008` (function calls in default arguments) is ignored to allow `Depends()`.

### 1.3 Testing
- **Structure:**
  - `tests/unit/`: Isolated tests for services, repositories, commands.
  - `tests/api/`: Integration tests for API endpoints.
- **Fixtures:** Use `conftest.py` for shared resources (`db_session`, `client`).
- **Async:** Use `pytest-asyncio` strict mode.
- **Coverage:** Minimum 80% coverage required.

## 2. Architecture Patterns

### 2.1 Layered Architecture
- **API**: Validation, Parsing, Dependency Injection.
- **Service**: Business Logic, Orchestration.
- **Repository**: Data Access, Query Building.
- **Model**: Database Schema (SQLAlchemy).

### 2.2 Versioning (EVCS)
- **Immutability:** Head + Version Table pattern.
- **Versioning Mixins:** Use `VersionableHeadMixin` and `VersionSnapshotMixin`.
- **Commands:** Use Command pattern for state-changing operations (Create/Update/Delete).

## 3. Documentation
- **Docstrings:** All public functions/classes must have Google-style docstrings.
- **ADRs:** Significant decisions recorded in `docs/dev/adr/`.
