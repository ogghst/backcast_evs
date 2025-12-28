"""Database integration tests."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_database_session_creates_successfully(db_session: AsyncSession) -> None:
    """Ver ify async database session can be created."""
    # Arrange: Database session available via fixture
    # Act: Check session type
    # Assert: Session is AsyncSession instance
    assert isinstance(db_session, AsyncSession)


@pytest.mark.asyncio
async def test_database_session_can_execute_query(db_session: AsyncSession) -> None:
    """Verify database session can execute simple query."""
    # Arrange: Database session available
    # Act: Execute simple SELECT query
    result = await db_session.execute(text("SELECT 1 as test"))
    row = result.fetchone()

    # Assert: Query executes successfully
    assert row is not None
    assert row[0] == 1
