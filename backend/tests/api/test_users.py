from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.core.security import create_access_token
from app.models.domain.user import User, UserVersion


# Helper to create user and token
async def create_user_and_token(db_session: Any, email: str, role: str = "viewer") -> tuple[User, dict[str, str]]:
    user_id = uuid4()
    user = User(id=user_id, email=email, hashed_password="pw")
    db_session.add(user)

    version = UserVersion(
        head_id=user.id,
        full_name=f"User {role}",
        role=role,
        is_active=True,
        valid_from=datetime.now(UTC),
        created_by_id=user_id
    )
    db_session.add(version)
    await db_session.commit()

    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers

@pytest.mark.asyncio
async def test_get_users_admin_only(async_client: AsyncClient, db_session: Any) -> None:
    # 1. Setup Admin and Normal User
    admin, admin_headers = await create_user_and_token(db_session, "admin@test.com", "admin")
    user, user_headers = await create_user_and_token(db_session, "user@test.com", "viewer")

    # 2. Admin request -> 200 OK
    resp = await async_client.get(f"{settings.API_V1_STR}/users", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # 3. Normal user written request -> 403 Forbidden
    resp = await async_client.get(f"{settings.API_V1_STR}/users", headers=user_headers)
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_update_user_self(async_client: AsyncClient, db_session: Any) -> None:
    user, headers = await create_user_and_token(db_session, "update_self@test.com", "viewer")

    payload = {
        "full_name": "New Name Self"
    }

    resp = await async_client.put(
        f"{settings.API_V1_STR}/users/{user.id}",
        json=payload,
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "New Name Self"

@pytest.mark.asyncio
async def test_delete_user_admin_only(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(db_session, "admin_del@test.com", "admin")
    target, _ = await create_user_and_token(db_session, "target@test.com", "viewer")

    # Execute delete
    resp = await async_client.delete(
        f"{settings.API_V1_STR}/users/{target.id}",
        headers=admin_headers
    )
    assert resp.status_code == 204

    # Verify inactive
    # Re-fetch as admin
    resp = await async_client.get(f"{settings.API_V1_STR}/users/{target.id}", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_create_user_admin_only(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(db_session, "admin_cr@test.com", "admin")
    user, user_headers = await create_user_and_token(db_session, "user_cr@test.com", "viewer")

    payload = {
        "email": "created_via_api@test.com",
        "full_name": "API Created User",
        "password": "securepassword123", # UserRegister requires password
        "role": "viewer",
        "department": "Engineering"
    }

    # 1. Normal user tries to create -> 403
    resp = await async_client.post(
        f"{settings.API_V1_STR}/users",
        json=payload,
        headers=user_headers
    )
    assert resp.status_code == 403

    # 2. Admin tries to create -> 200/201
    resp = await async_client.post(
        f"{settings.API_V1_STR}/users",
        json=payload,
        headers=admin_headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "created_via_api@test.com"
    # Basic field check using available properties from UserPublic (if from_entity is working efficiently for flat dict)
    # Actually, UserPublic has: id, email, full_name, role, department, is_active.
    assert data["full_name"] == "API Created User"

@pytest.mark.asyncio
async def test_read_user_permissions(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(db_session, "admin_read@test.com", "admin")
    user1, user1_headers = await create_user_and_token(db_session, "read1@test.com", "viewer")
    user2, user2_headers = await create_user_and_token(db_session, "read2@test.com", "viewer")

    # 1. Admin reads user1 -> 200
    resp = await async_client.get(f"{settings.API_V1_STR}/users/{user1.id}", headers=admin_headers)
    assert resp.status_code == 200

    # 2. User1 reads self -> 200
    resp = await async_client.get(f"{settings.API_V1_STR}/users/{user1.id}", headers=user1_headers)
    assert resp.status_code == 200

    # 3. User1 reads user2 -> 403
    resp = await async_client.get(f"{settings.API_V1_STR}/users/{user2.id}", headers=user1_headers)
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_read_non_existent_user(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(db_session, "admin_404@test.com", "admin")
    fake_id = uuid4()

    resp = await async_client.get(f"{settings.API_V1_STR}/users/{fake_id}", headers=admin_headers)
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_create_user_validation(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(db_session, "admin_val@test.com", "admin")

    # 1. Short password -> 422
    payload_short_pw = {
        "email": "shortpw@test.com",
        "full_name": "Short Pass",
        "password": "tiny",
        "role": "viewer"
    }
    resp = await async_client.post(f"{settings.API_V1_STR}/users", json=payload_short_pw, headers=admin_headers)
    assert resp.status_code == 422

    # 2. Invalid email -> 422
    payload_bad_email = {
        "email": "not-an-email",
        "full_name": "Bad Email",
        "password": "securepassword",
        "role": "viewer"
    }
    resp = await async_client.post(f"{settings.API_V1_STR}/users", json=payload_bad_email, headers=admin_headers)
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(db_session, "admin_dup@test.com", "admin")

    payload = {
        "email": "duplicate@test.com",
        "full_name": "Dup User",
        "password": "securepassword",
        "role": "viewer"
    }

    # First create -> 201
    resp = await async_client.post(f"{settings.API_V1_STR}/users", json=payload, headers=admin_headers)
    assert resp.status_code == 201

    # Second create -> 400
    resp = await async_client.post(f"{settings.API_V1_STR}/users", json=payload, headers=admin_headers)
    assert resp.status_code == 400

@pytest.mark.asyncio
async def test_update_user_permissions(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(db_session, "admin_upd@test.com", "admin")
    user1, user1_headers = await create_user_and_token(db_session, "upd1@test.com", "viewer")
    user2, _ = await create_user_and_token(db_session, "upd2@test.com", "viewer")

    payload = {"full_name": "Updated"}

    # 1. Admin updates user1 -> 200
    resp = await async_client.put(f"{settings.API_V1_STR}/users/{user1.id}", json=payload, headers=admin_headers)
    assert resp.status_code == 200

    # 2. User1 updates user2 -> 403
    resp = await async_client.put(f"{settings.API_V1_STR}/users/{user2.id}", json=payload, headers=user1_headers)
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_delete_user_permissions(async_client: AsyncClient, db_session: Any) -> None:
    user1, user1_headers = await create_user_and_token(db_session, "del1@test.com", "viewer")
    user2, _ = await create_user_and_token(db_session, "del2@test.com", "viewer")

    # User1 tries to delete user2 -> 403
    resp = await async_client.delete(f"{settings.API_V1_STR}/users/{user2.id}", headers=user1_headers)
    assert resp.status_code == 403
