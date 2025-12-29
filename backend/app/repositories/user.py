from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.domain.user import User, UserVersion
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserVersion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User, UserVersion)

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email, including latest version data.
        """
        stmt = (
            select(User)
            .options(joinedload(User.versions))  # Optimize if we need version data
            .where(User.email == email)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Get user by ID.
        """
        stmt = (
            select(User).options(selectinload(User.versions)).where(User.id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
