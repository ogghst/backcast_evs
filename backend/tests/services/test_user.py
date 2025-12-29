from typing import Any
from uuid import uuid4

import pytest

from app.models.domain.user import UserVersion
from app.models.schemas.user import UserRegister, UserUpdate
from app.services.user import UserService

# Mocking the repository and session to test service logic in isolation
# However, integration tests are often better for services.
# But for now, let's use unit tests with mocks or real DB session if accessible.
# Since we have db_session fixture, let's use real DB for simplicity and confidence.

@pytest.mark.asyncio
async def test_user_service_crud(db_session: Any) -> None:
    service = UserService(db_session)

    # 1. Test Create User
    admin_id = uuid4()

    user_data = UserRegister(
        email=f"service_test_{admin_id}@example.com",
        password="securepassword123", # Fixed: Meets min length requirement
        full_name="Original Name",
        role="viewer",
        department="HR"
    )

    user = await service.create_user(user_data, actor_id=admin_id)
    user_id = user.id

    # Verify Creation
    assert user.id is not None
    assert len(user.versions) == 1
    v1 = user.versions[0]
    assert v1.full_name == "Original Name"
    assert v1.role == "viewer"
    assert v1.created_by_id == admin_id

    # 2. Test get_user
    fetched_user = await service.get_user(user_id)
    assert fetched_user is not None
    assert fetched_user.id == user_id
    assert fetched_user.versions[0].full_name == "Original Name"

    # 3. Test get_users
    users = await service.get_users(skip=0, limit=10)
    assert len(users) >= 1
    found = any(u.id == user_id for u in users)
    assert found

    # 4. Test update_user
    update_data = UserUpdate(full_name="Updated Name", department="IT")
    updated_version = await service.update_user(user_id, update_data, actor_id=admin_id)

    assert updated_version.full_name == "Updated Name"
    assert updated_version.department == "IT"
    assert updated_version.valid_to is None

    # 5. Test delete_user
    await service.delete_user(user_id, actor_id=admin_id)

    # Verify soft delete
    # Explicit check
    from sqlalchemy import select
    stmt = select(UserVersion).where(
        UserVersion.head_id == user_id,
        UserVersion.valid_to.is_(None)
    )
    current_version = (await db_session.execute(stmt)).scalar_one()
    assert current_version.is_active is False
