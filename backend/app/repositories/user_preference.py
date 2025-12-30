from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.domain.user_preference import UserPreference, UserPreferenceVersion
from app.repositories.base import BaseRepository


class UserPreferenceRepository(BaseRepository[UserPreference, UserPreferenceVersion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserPreference, UserPreferenceVersion)

    async def get_by_user_id(self, user_id: UUID) -> UserPreference | None:
        """
        Get preference by user ID.
        """
        stmt = (
            select(UserPreference)
            .options(selectinload(UserPreference.versions))
            .where(UserPreference.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
