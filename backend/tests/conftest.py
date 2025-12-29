"""
Pytest configuration and shared fixtures.

This module provides:
- Database fixtures for testing
- Test client fixtures
- Common test utilities
"""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.main import app

# Test database URL (use separate test database)
TEST_DATABASE_URL = str(settings.DATABASE_URL).replace(
    "/backcast_evs", "/backcast_evs_test"
)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Configure anyio backend for async tests."""
    return "asyncio"


@pytest.fixture(scope="function")
def event_loop() -> Any:
    """Create a new event loop for each test with proper cleanup."""
    import asyncio

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop

    # Cleanup all pending tasks
    try:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()

        # Wait for all tasks to complete cancellation
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    finally:
        loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator[Any, None]:
    """Create async engine for tests."""
    import asyncio

    engine = create_async_engine(
        TEST_DATABASE_URL, echo=False, poolclass=NullPool, pool_pre_ping=True
    )
    yield engine
    await engine.dispose()
    # Wait for all connections to close
    await asyncio.sleep(0.1)


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine: Any) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for tests."""
    from app.db.session import get_db

    async_session_maker = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        # Override the get_db dependency with the test session
        async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
            yield session

        app.dependency_overrides[get_db] = override_get_db

        yield session

        # Cleanup
        app.dependency_overrides.pop(get_db, None)
        await session.rollback()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db(db_engine: Any) -> AsyncGenerator[None, None]:
    """Create and drop tables for each test."""
    # Import all models so they are found
    from app.models.domain import department, user  # noqa: F401
    from app.models.domain.base import Base

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Create test client for API testing (Synchronous)."""
    return TestClient(app)


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[Any, None]:
    """Create async client for API testing."""
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac
