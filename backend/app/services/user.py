from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.user import CreateUserCommand, DeleteUserCommand, UpdateUserCommand
from app.core.security import get_password_hash
from app.core.versioning.commands import CommandMetadata
from app.models.domain.user import User, UserVersion
from app.models.schemas.user import UserRegister, UserUpdate
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_user(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)

    async def get_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Get all users with pagination."""
        return await self.user_repo.get_all(skip=skip, limit=limit)

    async def update_user(
        self, user_id: UUID, update_data: UserUpdate, actor_id: UUID
    ) -> UserVersion:
        """
        Update user profile and/or password.
        Profile changes are versioned via UpdateUserCommand.
        Password changes update the Head entity directly (no history for security/simplicity).
        """
        # 1. Handle Password Update (Head Entity)
        if update_data.password:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            hashed_password = get_password_hash(update_data.password)
            user.hashed_password = hashed_password
            self.session.add(user)
            # We don't flush here, wait for command execution to flush all

        # 2. Handle Profile Update (Version Entity)
        # Filter out None values and password
        changes = update_data.model_dump(exclude_unset=True)
        if "password" in changes:
            del changes["password"]

        if not changes:
            # If only password was updated, we need to return the current version
            # or maybe just flush user update.
            # But the return type implies returning a specific version.
            # Let's get the current active version to return.
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.versions:
                raise ValueError("User or version not found")

            # Since we modified the session (password), we should flush
            await self.session.flush()
            return user.versions[0]  # Return generic latest version

        metadata = CommandMetadata(
            command_type="UPDATE_USER",
            user_id=actor_id,
            timestamp=datetime.now(UTC),
            description="User Update",
        )

        command = UpdateUserCommand(metadata=metadata, user_id=user_id, changes=changes)
        return await command.execute(self.session)

    async def delete_user(self, user_id: UUID, actor_id: UUID) -> None:
        """
        Soft delete user.
        """
        metadata = CommandMetadata(
            command_type="DELETE_USER",
            user_id=actor_id,
            timestamp=datetime.now(UTC),
            description="User Soft Delete",
        )

        command = DeleteUserCommand(metadata=metadata, user_id=user_id)
        await command.execute(self.session)

    async def create_user(self, user_data: UserRegister, actor_id: UUID) -> User:
        """
        Create a new user.
        """
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        new_user_id = UUID(int=uuid4().int)  # Ensure standard UUID generation

        metadata = CommandMetadata(
            command_type="CREATE_USER",
            user_id=actor_id,
            timestamp=datetime.now(UTC),
            description=f"Admin created user: {user_data.email}",
        )

        command = CreateUserCommand(
            metadata=metadata,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role,
            department=user_data.department,
            id=new_user_id,
        )

        return await command.execute(self.session)
