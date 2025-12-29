"""
Generic repository implementation following backend architecture.

Architecture:
- BaseRepository: For non-branching entities (e.g. User).
- VersionedRepository: For branch-aware entities (e.g. Project).
"""

from datetime import datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mixins import (
    BaseHeadMixin,
    BaseVersionMixin,
    VersionableHeadMixin,
    VersionSnapshotMixin,
)

# Type variables for BaseRepository (non-branching)
HeadT = TypeVar("HeadT", bound=BaseHeadMixin)
VersionT = TypeVar("VersionT", bound=BaseVersionMixin)

# Type variables for VersionedRepository (branch-aware)
BranchHeadT = TypeVar("BranchHeadT", bound=VersionableHeadMixin)
BranchVersionT = TypeVar("BranchVersionT", bound=VersionSnapshotMixin)


class BaseRepository[HeadT: BaseHeadMixin, VersionT: BaseVersionMixin]:
    """
    Base repository for versioned entities (non-branching support).

    Used by UserRepository.
    """

    def __init__(
        self,
        session: AsyncSession,
        head_model: type[HeadT],
        version_model: type[VersionT],
    ):
        self.session = session
        self.head_model = head_model
        self.version_model = version_model

    async def get(self, id: UUID) -> HeadT | None:
        """Get entity by ID."""
        stmt = select(self.head_model).where(self.head_model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_version(self, id: UUID) -> HeadT | None:
        """get entity by ID with version loaded."""
        # This assumes the model has a 'versions' relationship configured
        # or we might need to do an explicit join if strictly following the patterns,
        # but typically ORM relationship loading is handled via options in the specific repo
        # or defaults.
        # For base, we'll stick to simple get.
        return await self.get(id)


class VersionedRepository(BaseRepository[BranchHeadT, BranchVersionT]):
    """
    Repository for branch-aware versioned entities.

    Extends BaseRepository to add branch filtering and time-travel.
    """

    async def get(self, id: UUID, branch: str = "main") -> BranchHeadT | None:
        """Get current head for entity in specific branch."""
        stmt = select(self.head_model).where(
            self.head_model.id == id,
            self.head_model.branch == branch,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_at_date(
        self,
        id: UUID,
        branch: str,
        control_date: datetime,
    ) -> BranchVersionT | None:
        """Time-travel: get entity version at specific date."""
        stmt = (
            select(self.version_model)
            .where(
                self.version_model.head_id == id,
                self.version_model.branch == branch,
                self.version_model.valid_from <= control_date,
                (
                    self.version_model.valid_to.is_(None)
                    | (self.version_model.valid_to > control_date)
                ),
            )
            .order_by(self.version_model.valid_from.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
