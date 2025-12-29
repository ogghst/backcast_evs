from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.versioning.commands import CommandMetadata, VersionCommand
from app.models.domain.user import User, UserVersion


class CreateUserCommand(VersionCommand[User]):
    """Command to create a new user (Head + Initial Version)."""

    def __init__(
        self,
        metadata: CommandMetadata,
        email: str,
        hashed_password: str,
        full_name: str,
        role: str,
        department: str | None = None,
        id: UUID | None = None,
    ):
        super().__init__(metadata)
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.department = department
        self.id = id
        self.created_head_id: UUID | None = None

    async def execute(self, session: AsyncSession) -> User:
        # Create head entity (identity)
        user_kwargs: dict[str, Any] = {
            "email": self.email,
            "hashed_password": self.hashed_password,
        }
        if self.id:
            user_kwargs["id"] = self.id

        user = User(**user_kwargs)
        session.add(user)
        await session.flush()  # Generate ID if not provided, or verify uniqueness
        self.created_head_id = user.id

        # Create initial version (state)
        # Uses metadata.timestamp for valid_from
        version = UserVersion(
            head_id=user.id,
            full_name=self.full_name,
            role=self.role,
            department=self.department,
            is_active=True,
            valid_from=self.metadata.timestamp,
            created_by_id=self.metadata.user_id,
        )
        session.add(version)
        await session.flush()

        # Refresh with versions loaded
        stmt = (
            select(User).options(selectinload(User.versions)).where(User.id == user.id)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one()

    async def undo(self, session: AsyncSession) -> None:
        """Undo creation by deleting the user (cascade deletes versions)."""
        if self.created_head_id:
            stmt = delete(User).where(User.id == self.created_head_id)
            await session.execute(stmt)


class UpdateUserCommand(VersionCommand[UserVersion]):
    """Command to update user profile (New Version)."""

    def __init__(
        self,
        metadata: CommandMetadata,
        user_id: UUID,
        changes: dict[str, Any],
    ):
        super().__init__(metadata)
        self.user_id = user_id
        self.changes = changes
        self.new_version_id: UUID | None = None
        self.previous_version_id: UUID | None = None

    async def execute(self, session: AsyncSession) -> UserVersion:
        # Get current active version
        stmt = (
            select(UserVersion)
            .where(UserVersion.head_id == self.user_id, UserVersion.valid_to.is_(None))
            .order_by(UserVersion.valid_from.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        current_version = result.scalar_one_or_none()

        if not current_version:
            raise ValueError(f"No active version found for user {self.user_id}")

        self.previous_version_id = current_version.head_id  # Wait, ID isn't separate?
        # UserVersion PK is (head_id, valid_from). It does NOT have a separate ID?
        # BaseVersionMixin: head_id, valid_from are PKs.
        # So I can't identify version just by UUID.
        # I need (head_id, valid_from).

        # Undo logic will be tricky without unique ID for version.
        # But I can use the same (head_id, valid_from) tuple.
        self.previous_version_pk = (current_version.head_id, current_version.valid_from)

        # Close current version
        # We need to update the valid_to
        current_version.valid_to = self.metadata.timestamp
        session.add(current_version)  # Mark for update

        # Prepare new version data
        # Use to_dict() to get all fields, then filter out metadata
        # that shouldn't be copied or is overridden
        source_data = current_version.to_dict()
        exclude_fields = {
            "head_id",
            "valid_from",
            "valid_to",
            "created_by_id",
        }
        new_data = {k: v for k, v in source_data.items() if k not in exclude_fields}
        new_data.update(self.changes)

        # Create new version
        new_version = UserVersion(
            head_id=self.user_id,
            valid_from=self.metadata.timestamp,
            created_by_id=self.metadata.user_id,
            **new_data,
        )
        session.add(new_version)
        await session.flush()

        self.new_version_pk = (new_version.head_id, new_version.valid_from)

        return new_version

    async def undo(self, session: AsyncSession) -> None:
        """Undo update: delete new version, reopen previous."""
        if hasattr(self, "new_version_pk") and hasattr(self, "previous_version_pk"):
            # Delete new version
            del_stmt = delete(UserVersion).where(
                UserVersion.head_id == self.new_version_pk[0],
                UserVersion.valid_from == self.new_version_pk[1],
            )
            await session.execute(del_stmt)

            # Reopen previous version
            upd_stmt = (
                update(UserVersion)
                .where(
                    UserVersion.head_id == self.previous_version_pk[0],
                    UserVersion.valid_from == self.previous_version_pk[1],
                )
                .values(valid_to=None)
            )
            await session.execute(upd_stmt)
