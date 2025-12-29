---
trigger: manual
---

# Testing Guidelines

This document defines our strategy and patterns for maintaining high test quality and coverage.

## 1. Test Philosophy

*   **Test-Driven Development (TDD)**: We prefer writing tests before implementation (Red-Green-Refactor).
*   **Feedback Loop**: Tests should be fast and reliable to provide immediate feedback.
*   **Coverage Target**: We aim for **80% code coverage** for feature code and **90%+** for critical domain logic.

## 2. Test Pattern: AAA (Arrange-Act-Assert)

Every test should follow the AAA pattern for clarity and consistency.

```python
def test_feature_scenario_expected_outcome():
    # Arrange: Set up preconditions (fixtures, variables)
    value = 5
    
    # Act: Execute the behavior under test
    result = double(value)
    
    # Assert: Verify the expected outcome
    assert result == 10
```

## 3. Test Hierarchy

1.  **Unit Tests (`tests/unit/`)**: Test individual functions or classes in isolation. Use mocks for dependencies.
2.  **Integration Tests (`tests/integration/`)**: Test interactions between components (e.g., Service + Repository). These often use a test database.
3.  **API Tests (`tests/api/`)**: Test the full request-response cycle using `FastAPI.testclient`.

## 4. Fixtures and Configuration

*   **`tests/conftest.py`**: Place shared fixtures and configuration here.
*   **Database**: Use the `db_session` fixture for isolated database tests. It automatically rolls back changes after each test.
*   **Client**: Use the `client` fixture for API tests.

## 5. Async Testing

*   Use `pytest-asyncio` for testing async functions.
*   Decorate async tests with `@pytest.mark.asyncio`.
*   Ensure `asyncio_mode = "auto"` is set in `pyproject.toml`.

## 6. Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=app --cov-report=term-missing
```
