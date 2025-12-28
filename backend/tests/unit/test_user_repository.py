import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_create_user_with_version_creates_head_and_version(
    db_session: AsyncSession,
):
    repo = UserRepository()
    user = await repo.create_user_with_version(
        db_session,
        email="repo_test@example.com",
        password="password",
        full_name="Repo User",
        department="Dev",
        role="viewer",
    )

    assert user.id is not None
    assert user.email == "repo_test@example.com"
    # Check if version exists (by relationship or query)
    # Since we didn't eager load versions in create method return (unless we changed it),
    # we might need to refresh or query. But creating the user object should have flushed.

    # Verify we can retrieve it
    retrieved = await repo.get_by_email(db_session, "repo_test@example.com")
    assert retrieved is not None
    assert retrieved.id == user.id
    assert len(retrieved.versions) == 1
    assert retrieved.versions[0].full_name == "Repo User"


@pytest.mark.asyncio
async def test_get_by_email_returns_user(db_session: AsyncSession):
    repo = UserRepository()
    await repo.create_user_with_version(
        db_session, "email_lookup@example.com", "pass", "Lookup User"
    )

    user = await repo.get_by_email(db_session, "email_lookup@example.com")
    assert user is not None
    assert user.email == "email_lookup@example.com"

    non_existent = await repo.get_by_email(db_session, "nothing@example.com")
    assert non_existent is None


@pytest.mark.asyncio
async def test_get_by_id_returns_user(db_session: AsyncSession):
    repo = UserRepository()
    created = await repo.create_user_with_version(
        db_session, "id_lookup@example.com", "pass", "ID User"
    )

    user = await repo.get_by_id(db_session, created.id)
    assert user is not None
    assert user.email == "id_lookup@example.com"
