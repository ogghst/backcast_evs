from typing import Any

import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_register_endpoint_success(async_client: AsyncClient, db_session: Any) -> None:
    # db_session fixture used to ensure DB is clean/ready
    payload = {
        "email": "api_reg@example.com",
        "password": "strong_password",
        "full_name": "API User",
        "department": "IT",
    }
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/register", json=payload
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_endpoint_duplicate_email(
    async_client: AsyncClient, db_session: Any
) -> None:
    # First registration
    payload = {
        "email": "duplicate_api@example.com",
        "password": "password",
        "full_name": "API User",
    }
    await async_client.post(f"{settings.API_V1_STR}/auth/register", json=payload)

    # Second registration
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/register", json=payload
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_endpoint_success(async_client: AsyncClient, db_session: Any) -> None:
    # Register first
    payload = {
        "email": "login_api@example.com",
        "password": "password123",
        "full_name": "Login User",
    }
    await async_client.post(f"{settings.API_V1_STR}/auth/register", json=payload)

    # Login
    login_data = {"username": payload["email"], "password": payload["password"]}
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_endpoint_invalid_credentials(async_client: AsyncClient) -> None:
    login_data = {"username": "wrong@example.com", "password": "wrongpassword"}
    response = await async_client.post(
        f"{settings.API_V1_STR}/auth/login",
        data=login_data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_endpoint_success(async_client: AsyncClient, db_session: Any) -> None:
    # Register and login
    payload = {
        "email": "me_api@example.com",
        "password": "password123",
        "full_name": "Me User",
    }
    await async_client.post(f"{settings.API_V1_STR}/auth/register", json=payload)

    login_data = {"username": payload["email"], "password": payload["password"]}
    login_res = await async_client.post(
        f"{settings.API_V1_STR}/auth/login", data=login_data
    )
    token = login_res.json()["access_token"]

    # Access protected route
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]


@pytest.mark.asyncio
async def test_me_endpoint_no_token(async_client: AsyncClient) -> None:
    response = await async_client.get(f"{settings.API_V1_STR}/auth/me")
    assert response.status_code == 401
