from typing import Any

import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.api.test_users import create_user_and_token


@pytest.mark.asyncio
async def test_create_department_admin_only(
    async_client: AsyncClient, db_session: Any
) -> None:
    admin, admin_headers = await create_user_and_token(
        db_session, "admin_dept@test.com", "admin"
    )
    user, user_headers = await create_user_and_token(
        db_session, "user_dept@test.com", "viewer"
    )

    payload = {
        "code": "ENG",
        "name": "Engineering",
        "is_active": True,
    }

    # 1. Normal user tries to create -> 403
    resp = await async_client.post(
        f"{settings.API_V1_STR}/departments", json=payload, headers=user_headers
    )
    assert resp.status_code == 403

    # 2. Admin tries to create -> 201
    resp = await async_client.post(
        f"{settings.API_V1_STR}/departments", json=payload, headers=admin_headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "ENG"
    assert data["name"] == "Engineering"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_read_departments(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(
        db_session, "admin_read@test.com", "admin"
    )

    # Create dept
    payload = {"code": "HR", "name": "Human Resources"}
    await async_client.post(
        f"{settings.API_V1_STR}/departments", json=payload, headers=admin_headers
    )

    # Read all
    resp = await async_client.get(
        f"{settings.API_V1_STR}/departments", headers=admin_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(d["code"] == "HR" for d in data)


@pytest.mark.asyncio
async def test_update_department(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(
        db_session, "admin_upd@test.com", "admin"
    )

    # Create
    resp = await async_client.post(
        f"{settings.API_V1_STR}/departments",
        json={"code": "IT", "name": "IT Dept"},
        headers=admin_headers,
    )
    dept_id = resp.json()["id"]

    # Update
    payload = {"name": "Information Technology"}
    resp = await async_client.put(
        f"{settings.API_V1_STR}/departments/{dept_id}",
        json=payload,
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Information Technology"
    assert data["code"] == "IT"  # Code should remain unchanged


@pytest.mark.asyncio
async def test_delete_department(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(
        db_session, "admin_del@test.com", "admin"
    )

    # Create
    resp = await async_client.post(
        f"{settings.API_V1_STR}/departments",
        json={"code": "SALES", "name": "Sales"},
        headers=admin_headers,
    )
    dept_id = resp.json()["id"]

    # Delete
    resp = await async_client.delete(
        f"{settings.API_V1_STR}/departments/{dept_id}", headers=admin_headers
    )
    assert resp.status_code == 204

    # Verify inactive
    resp = await async_client.get(
        f"{settings.API_V1_STR}/departments/{dept_id}", headers=admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_create_duplicate_code(async_client: AsyncClient, db_session: Any) -> None:
    admin, admin_headers = await create_user_and_token(
        db_session, "admin_dup@test.com", "admin"
    )

    payload = {"code": "FIN", "name": "Finance"}
    await async_client.post(
        f"{settings.API_V1_STR}/departments", json=payload, headers=admin_headers
    )

    # Duplicate create
    resp = await async_client.post(
        f"{settings.API_V1_STR}/departments", json=payload, headers=admin_headers
    )
    assert resp.status_code == 400
