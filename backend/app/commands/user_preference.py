from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.versioning.commands import CommandMetadata, VersionCommand
from app.models.domain.user_preference import UserPreferenceVersion


class UpdateUserPreferenceCommand(VersionCommand[UserPreferenceVersion]):
    """Command to update user preference (New Version)."""

    def __init__(
        self,
        metadata: CommandMetadata,
        head_id: UUID,  # Preference Head ID
        theme: str,
    ):
        super().__init__(metadata)
        self.head_id = head_id
        self.theme = theme
        self.new_version_pk: tuple[UUID, datetime] | None = None
        self.previous_version_pk: tuple[UUID, datetime] | None = None

    async def execute(self, session: AsyncSession) -> UserPreferenceVersion:
        # Get current active version
        stmt = (
            select(UserPreferenceVersion)
            .where(UserPreferenceVersion.head_id == self.head_id, UserPreferenceVersion.valid_to.is_(None))
            .order_by(UserPreferenceVersion.valid_from.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        current_version = result.scalar_one_or_none()
        
        if current_version:
             self.previous_version_pk = (current_version.head_id, current_version.valid_from)
             current_version.valid_to = self.metadata.timestamp
             session.add(current_version)

        # Create new version
        new_version = UserPreferenceVersion(
            head_id=self.head_id,
            valid_from=self.metadata.timestamp,
            created_by_id=self.metadata.user_id,
            theme=self.theme
        )
        session.add(new_version)
        await session.flush()

        self.new_version_pk = (new_version.head_id, new_version.valid_from)

        return new_version

    async def undo(self, session: AsyncSession) -> None:
        """Undo update: delete new version, reopen previous."""
        if hasattr(self, "new_version_pk") and self.new_version_pk:
            # Delete new version
            del_stmt = delete(UserPreferenceVersion).where(
                UserPreferenceVersion.head_id == self.new_version_pk[0],
                UserPreferenceVersion.valid_from == self.new_version_pk[1],
            )
            await session.execute(del_stmt)

        if hasattr(self, "previous_version_pk") and self.previous_version_pk:
            # Reopen previous version
            upd_stmt = (
                update(UserPreferenceVersion)
                .where(
                    UserPreferenceVersion.head_id == self.previous_version_pk[0],
                    UserPreferenceVersion.valid_from == self.previous_version_pk[1],
                )
                .values(valid_to=None)
            )
            await session.execute(upd_stmt)
