import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.user import UserVersion
from app.models.schemas.user import UserLogin, UserRegister
from app.services.auth import AuthService


@pytest.mark.asyncio
async def test_register_user_success(db_session: AsyncSession):
    auth_service = AuthService()
    user_data = UserRegister(
        email="test@example.com",
        password="secret_password",
        full_name="Test User",
        department="Engineering",
        role="admin",
    )

    user = await auth_service.register_user(db_session, user_data)

    # Verify User head
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.hashed_password != "secret_password"

    # Verify User version
    result = await db_session.execute(
        select(UserVersion).where(UserVersion.head_id == user.id)
    )
    version = result.scalar_one()
    assert version.branch == "main"
    assert version.full_name == "Test User"
    assert version.department == "Engineering"
    assert version.role == "admin"
    assert version.is_active is True
    assert version.created_by_id == user.id


@pytest.mark.asyncio
async def test_register_user_duplicate_email_fails(db_session: AsyncSession):
    auth_service = AuthService()
    user_data = UserRegister(
        email="duplicate@example.com", password="password", full_name="User 1"
    )
    await auth_service.register_user(db_session, user_data)

    # Try again
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.register_user(db_session, user_data)


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session: AsyncSession):
    auth_service = AuthService()
    user_data = UserRegister(
        email="auth_success@example.com",
        password="correct_password",
        full_name="Auth User",
    )
    await auth_service.register_user(db_session, user_data)

    login_data = UserLogin(
        email="auth_success@example.com", password="correct_password"
    )
    user = await auth_service.authenticate_user(db_session, login_data)
    assert user is not None
    assert user.email == "auth_success@example.com"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session: AsyncSession):
    auth_service = AuthService()
    user_data = UserRegister(
        email="auth_fail@example.com", password="password", full_name="Auth User"
    )
    await auth_service.register_user(db_session, user_data)

    login_data = UserLogin(email="auth_fail@example.com", password="wrong_password")
    user = await auth_service.authenticate_user(db_session, login_data)
    assert user is None
