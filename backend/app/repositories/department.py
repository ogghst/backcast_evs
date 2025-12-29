from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.domain.department import Department, DepartmentVersion
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department, DepartmentVersion]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Department, DepartmentVersion)

    async def get_by_id(self, id: UUID) -> Department | None:
        """Get department by ID."""
        stmt = (
            select(Department)
            .options(selectinload(Department.versions))
            .where(Department.id == id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_code(self, code: str) -> Department | None:
        """
        Get department by code, including latest versions.
        """
        stmt = (
            select(Department)
            .options(selectinload(Department.versions))
            .where(Department.code == code)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Department]:
        """
        Get all departments with pagination.
        """
        stmt = (
            select(Department)
            .options(selectinload(Department.versions))
            .offset(skip)
            .limit(limit)
            .order_by(Department.code)  # Order by code for departments
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
