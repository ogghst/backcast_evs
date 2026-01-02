"""UserService extending TemporalService.

Provides User-specific operations on top of generic temporal service.
"""

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.versioning.commands import (
    CreateVersionCommand,
    SoftDeleteCommand,
    UpdateVersionCommand,
)
from app.core.versioning.service import TemporalService
from app.models.domain.user import User


class UserService(TemporalService[User]):  # type: ignore[type-var]
    """Service for User entity operations.

    Extends TemporalService with user-specific methods like get_by_email.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_user(self, user_id: UUID) -> User | None:
        """Get user by ID (current version)."""
        return await self.get_by_id(user_id)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        return await self.get_all(skip, limit)

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address (current active version)."""
        # TODO: Use proper temporal operators when configured
        # For now, just getting latest one that isn't deleted
        stmt = (
            select(User)
            .where(User.email == email, User.deleted_at.is_(None))
            .order_by(User.valid_time.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: dict[str, Any], actor_id: UUID) -> User:
        """Create new user using CreateVersionCommand."""
        # Ensure root user_id exists
        root_id = user_data.get("user_id")
        if not root_id:
            root_id = uuid4()
            user_data["user_id"] = root_id

        # Ideally, we should validate user_data against Pydantic schema here
        # For now, we assume it matches User model fields

        cmd = CreateVersionCommand(
            entity_class=User,  # type: ignore[type-var]
            root_id=root_id,
            **user_data,
        )
        return await cmd.execute(self.session)

    async def update_user(
        self, user_id: UUID, update_data: dict[str, Any], actor_id: UUID
    ) -> User:
        """Update user using UpdateVersionCommand (creates new version)."""
        cmd = UpdateVersionCommand(
            entity_class=User,  # type: ignore[type-var]
            root_id=user_id,
            **update_data,
        )
        return await cmd.execute(self.session)

    async def delete_user(self, user_id: UUID, actor_id: UUID) -> None:
        """Soft delete user using SoftDeleteCommand."""
        cmd = SoftDeleteCommand(
            entity_class=User,  # type: ignore[type-var]
            root_id=user_id,
        )
        await cmd.execute(self.session)
