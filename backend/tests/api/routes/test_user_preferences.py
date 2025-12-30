import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import UTC, datetime
from typing import Any

from app.core.security import create_access_token
from app.models.domain.user import User, UserVersion


# Helper to create user and token (copied/adapted from test_users.py)
async def create_user_and_token(
    db_session: Any, email: str, role: str = "viewer"
) -> tuple[User, dict[str, str]]:
    user_id = uuid4()
    user = User(id=user_id, email=email, hashed_password="pw")
    db_session.add(user)

    version = UserVersion(
        head_id=user.id,
        full_name=f"User {role}",
        role=role,
        is_active=True,
        valid_from=datetime.now(UTC),
        created_by_id=user_id,
    )
    db_session.add(version)
    await db_session.commit()

    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


@pytest.mark.asyncio
async def test_get_and_update_preferences(
    async_client: AsyncClient,
    db_session: Any
) -> None:
    # 1. Setup User
    user, headers = await create_user_and_token(db_session, "pref_user@test.com")

    # 2. Get default preferences (should be created automatically)
    response = await async_client.get(
        "/api/v1/users/me/preferences", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "light"

    # 3. Update to dark mode
    update_data = {"theme": "dark"}
    response = await async_client.put(
        "/api/v1/users/me/preferences",
        headers=headers,
        json=update_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "dark"

    # 4. Verify persistence
    response = await async_client.get(
        "/api/v1/users/me/preferences", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "dark"

    # 5. Verify no change update
    response = await async_client.put(
        "/api/v1/users/me/preferences",
        headers=headers,
        json=update_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["theme"] == "dark"
