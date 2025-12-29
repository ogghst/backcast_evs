from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.user import CreateUserCommand, UpdateUserCommand
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.versioning.commands import CommandMetadata
from app.models.domain.user import User, UserVersion
from app.models.schemas.user import UserLogin, UserRegister
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, user_data: UserRegister) -> User:
        """
        Register a new user using Command Pattern.
        Raises ValueError if email already exists.
        """
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Generate ID for the new user so we can set it as created_by_id
        new_user_id = uuid4()

        # Create Command Metadata
        metadata = CommandMetadata(
            command_type="CREATE_USER",
            user_id=new_user_id,  # Self-registered
            timestamp=datetime.now(UTC),
            description=f"Registration: {user_data.email}",
        )

        # Create Command
        command = CreateUserCommand(
            metadata=metadata,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            department=user_data.department,
            id=new_user_id,
        )

        # Execute Command
        return await command.execute(self.session)

    async def update_user_profile(
        self, user_id: UUID, changes: dict[str, Any], actor_id: UUID
    ) -> UserVersion:
        """
        Update user profile using Snapshot Pattern (via Command).
        """
        metadata = CommandMetadata(
            command_type="UPDATE_USER",
            user_id=actor_id,
            timestamp=datetime.now(UTC),
            description="Profile update",
        )

        command = UpdateUserCommand(metadata=metadata, user_id=user_id, changes=changes)

        return await command.execute(self.session)

    async def authenticate_user(self, login_data: UserLogin) -> User | None:
        """
        Authenticate a user by email and password.
        """
        user = await self.user_repo.get_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            return None
        return user

    def create_token(self, user: User) -> str:
        """
        Create an access token for a user.
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(subject=user.id, expires_delta=access_token_expires)
