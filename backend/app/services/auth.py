from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.domain.user import User
from app.models.schemas.user import UserLogin, UserRegister
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self) -> None:
        self.user_repo = UserRepository()

    async def register_user(
        self, session: AsyncSession, user_data: UserRegister
    ) -> User:
        """
        Register a new user.
        Raises ValueError if email already exists.
        """
        existing_user = await self.user_repo.get_by_email(session, user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        user = await self.user_repo.create_user_with_version(
            session=session,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            department=user_data.department,
            role=user_data.role,
        )
        return user

    async def authenticate_user(
        self, session: AsyncSession, login_data: UserLogin
    ) -> User | None:
        """
        Authenticate a user by email and password.
        """
        user = await self.user_repo.get_by_email(session, login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            return None
        return user

    def create_token(self, user: User) -> str:
        """
        Create an access token for a user.
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(subject=user.id, expires_delta=access_token_expires)
