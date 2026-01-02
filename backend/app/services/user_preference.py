"""UserPreferenceService implementation.

Provides UserPreference-specific operations on top of generic simple service.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.simple.service import SimpleService
from app.models.domain.user_preference import UserPreference
from app.models.schemas.preference import UserPreferenceCreate, UserPreferenceUpdate


class UserPreferenceService(SimpleService[UserPreference]):  # type: ignore[type-var]
    """Service for UserPreference entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserPreference)

    async def get_by_user_id(self, user_id: UUID) -> UserPreference | None:
        """Get preference by user ID."""
        stmt = select(UserPreference).where(UserPreference.user_id == user_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_preference(
        self, user_id: UUID, pref_in: UserPreferenceCreate
    ) -> UserPreference:
        """Create new user preference."""
        # Check if exists? schema has unique constraint on user_id
        return await self.create(user_id=user_id, **pref_in.model_dump())

    async def update_preference(
        self, user_id: UUID, pref_in: UserPreferenceUpdate
    ) -> UserPreference:
        """Update preference for user."""
        pref = await self.get_by_user_id(user_id)
        if not pref:
            # Create if not exists? Or raise?
            # For now, let's auto-create if missing, or raise?
            # Let's assume strict update.
            raise ValueError(f"Preferences not found for user {user_id}")

        return await self.update(pref.id, **pref_in.model_dump(exclude_unset=True))
