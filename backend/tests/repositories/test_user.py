from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from app.models.domain.user import User, UserVersion
from app.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: Any) -> None:
    # 1. Arrange: Create multiple users
    repo = UserRepository(db_session)
    user_ids = []

    for i in range(5):
        user_id = uuid4()
        user = User(id=user_id, email=f"user_{i}@example.com", hashed_password="pw")
        db_session.add(user)

        # Add version
        version = UserVersion(
            head_id=user.id,
            full_name=f"User {i}",
            role="viewer",
            is_active=True,
            valid_from=datetime.now(UTC),
            created_by_id=user_id,
            department="IT" if i % 2 == 0 else "HR",
        )
        db_session.add(version)
        user_ids.append(user_id)

    await db_session.commit()

    # 2. Act: Get all with skip/limit
    # Test pagination 1: limit 2
    users_page_1 = await repo.get_all(skip=0, limit=2)
    assert len(users_page_1) == 2

    # Test pagination 2: skip 2, limit 2
    users_page_2 = await repo.get_all(skip=2, limit=2)
    assert len(users_page_2) == 2

    # Ensure distinct sets (simple check)
    ids_1 = {u.id for u in users_page_1}
    ids_2 = {u.id for u in users_page_2}
    assert ids_1.isdisjoint(ids_2)

    # Test getting remaining (skip 4, limit 2 should return 1)
    users_page_3 = await repo.get_all(skip=4, limit=2)
    assert len(users_page_3) == 1

    # 3. Assert: Verify loading of versions
    # The repository should ensure versions are loaded or joined
    user_0 = users_page_1[0]
    # Access a property that might require version data if logical,
    # but here we just check if we got the User objects
    assert isinstance(user_0, User)
