---
trigger: always_on
---

# Backend Coding Standards

This document outlines the coding standards and best practices for the Backcast EVS backend. Adherence to these standards ensures code quality, maintainability, and consistency across the codebase.

Backend project resides in backend/ folder. All commands are relatives to that folder.

## 1. Type Safety

We enforce strict type safety using MyPy.

*   **Requirement**: All new code must pass `mypy --strict`.
*   **Type Hints**: Every function signature must have comprehensive type hints for all arguments and return values.
*   **Avoid `Any`**: Use specific types whenever possible. If `Any` is absolutely necessary, document why.
*   **No Silence**: Only use `# type: ignore` as a last resort and always include a specific error code (e.g., `# type: ignore[misc]`) and a comment explaining why it's needed.

## 2. Formatting and Linting

We use **Ruff** for both formatting and linting. It is significantly faster than previous tools and provides a unified experience.

*   **Line Length**: Standardized at 88 characters (Black default).
*   **Sorting**: Imports must be sorted using Ruff's isort-compatible rules.
*   **Auto-fix**: Run `uv run ruff check --fix .` regularly to maintain standards.
*   **Pre-commit**: Ruff runs automatically on every commit via pre-commit hooks.

## 3. Naming Conventions

*   **Modules/Packages**: `snake_case`
*   **Classes**: `PascalCase`
*   **Functions/Variables**: `snake_case`
*   **Constants**: `UPPER_SNAKE_CASE`

## 4. Documentation

*   **Docstrings**: All public functions and classes should have Google-style docstrings.
*   **Comments**: Use comments to explain the "why", not the "how" (the code should be self-explanatory).

## 5. Error Handling

*   Use custom exception classes for domain-specific errors.
*   Ensure all exceptions are handled at the appropriate layer (e.g., API routes for HTTP exceptions).
*   Avoid broad `except Exception:` blocks.

## 6. Logging
*   **Requirement**: All backend code must use the configured logger to track code flow.
*   **Levels**:
    *   `DEBUG`: Detailed information for diagnosing problems (e.g., variable values, loop iterations).
    *   `INFO`: Confirmation that things are working as expected (e.g., startup messages, key state changes).
    *   **Note**: Avoid using `print()` statements. Use `logger.info()` or `logger.debug()` instead.
    *   `WARNING`: Indication that something unexpected happened, but the software is still working as expected.
    *   `ERROR`: Due to a more serious problem, the software has not been able to perform some function.
*   **Output**: Logs must be written to both console (stdout) and the `logs/` directory.
*   **Format**: Use the standard format defined in [app/core/logging.py]

## 7. Project Structure

Adhere to the Clean Architecture layers:
1.  **API**: `app/api/` (Routes, Dependencies)
2.  **Domain/Models**: `app/models/` (SQLAlchemy models, Pydantic schemas)
3.  **Services**: `app/services/` (Business logic)
4.  **Repositories**: `app/repositories/` (Data access)
5.  **Core**: `app/core/` (Configuration, Security)