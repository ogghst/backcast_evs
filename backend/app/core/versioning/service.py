"""Generic TemporalService for versioned entities.

Implements the TemporalService pattern from ADR-005 for entities
following the VersionableProtocol.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TemporalService[TVersionable]:
    """Base service for versioned entities (VersionableProtocol).

    Provides common operations for entities with bitemporal tracking:
    - Get current version (as of now)
    - Time travel queries (as of specific timestamp)
    - Create new version
    - Update (creates new version)
    - Soft delete

    Note: Temporal queries using TSTZRANGE operators need proper setup.
    Currently simplified for basic operations.
    """

    def __init__(self, entity_class: type[TVersionable], session: AsyncSession) -> None:
        self.entity_class = entity_class
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> TVersionable | None:
        """Get entity by ID (returns current version as of now)."""
        return await self.session.get(self.entity_class, entity_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[TVersionable]:
        """Get all entities (current versions) with pagination.

        TODO: Filter by valid_time @> now() and deleted_at IS NULL
        once TSTZRANGE operators are properly configured.
        """
        stmt = select(self.entity_class).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_as_of(self, entity_id: UUID, as_of: datetime) -> TVersionable | None:
        """Time travel: Get entity as it was at specific timestamp.

        TODO: Implement proper temporal query with valid_time @> as_of
        """
        stmt = (
            select(self.entity_class)
            .where(self.entity_class.id == entity_id)  # type: ignore[arg-type]
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # TODO: Implement create, update, delete using VersionedCommandABC
    async def create(self, **fields: object) -> TVersionable:
        """Create new versioned entity - TODO: use CreateVersionCommand."""
        raise NotImplementedError("Use CreateVersionCommand")

    async def update(self, entity_id: UUID, **updates: object) -> TVersionable:
        """Update entity (creates new version) - TODO: use UpdateVersionCommand."""
        raise NotImplementedError("Use UpdateVersionCommand")

    async def soft_delete(self, entity_id: UUID) -> None:
        """Soft delete entity - TODO: use SoftDeleteCommand."""
        raise NotImplementedError("Use SoftDeleteCommand")
