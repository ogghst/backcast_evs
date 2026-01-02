# Coding Standards

## 1. Python Standards (Backend)

### 1.1 Code Reuse

- **ABCs:** Use Abstract Base Classes (ABCs) for shared interfaces.
- **Mixins:** Use mixins for reusable functionality.
- **Protocols:** Use protocols for type hints.
- **TypeVar:** Use `TypeVar` for reusable components.
- **Type Checking:** Use type checking for reusable components.

### 1.2 Type Safety (MyPy)

- **Strict Mode:** All code must pass `mypy --strict`.
- **Explicit Returns:** All functions must have return type hints.
- **No Implicit Optional:** Explicitly use `None` as default for `Optional` arguments.

### 1.3 Linting (Ruff)

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

## 2. TypeScript Standards (Frontend)

### 2.1 Type Safety

- **Strict Mode:** TypeScript `strict: true` must be enabled.
- **No Any:** Avoid `any`; use `unknown` or specific interfaces.
- **Props:** Define component props as named interfaces (e.g., `UserListProps`).

### 2.2 Linting & Formatting

- **ESLint:** Use the provided flat config (extends `tseslint`, `react-hooks`).
- **Prettier:** Run before verify.
- **Naming:**
  - Components: PascalCase (`UserProfile.tsx`)
  - Hooks: camelCase (`useAuth.ts`)
  - constants: UPPER_SNAKE_CASE

### 2.3 State Management

- **Server State:** Use `TanStack Query` (React Query). Do not store API data in global stores unless absolutely necessary.
- **Client State:** Use `Zustand` for global UI state (modals, auth capability).
- **Local State:** Use `useState`/`useReducer` for component-local logic.

### 2.4 Styling

- **Ant Design:** Use `ConfigProvider` themes.
- **Tokens:** Use design tokens (`theme.useToken()`) instead of hardcoded hex values.

## 3. Architecture Patterns (Backend)

### 3.1 Layered Architecture

- **API**: Validation, Parsing, Dependency Injection.
- **Service**: Business Logic, Orchestration.
- **Repository**: Data Access, Query Building.
- **Model**: Database Schema (SQLAlchemy).

### 3.2 Versioning (EVCS)

- **Immutability:** Head + Version Table pattern.
- **Versioning Mixins:** Use `VersionableHeadMixin` and `VersionSnapshotMixin`.
- **Commands:** Use Command pattern for state-changing operations (Create/Update/Delete).

## 4. Architecture Patterns (Frontend)

### 4.1 Frontend Architecture

- **Feature-Based**: Organize by domain feature (`src/features/projects`) where possible.
- **API Client**: Use the centralized Axios instance (`src/api/client.ts`).
- **Routes**: Centralized definition in `src/routes/`.

## 5. Documentation

- **Docstrings:** All public functions/classes must have Google-style docstrings.
- **ADRs:** Significant decisions recorded in `docs/decisions/`.
