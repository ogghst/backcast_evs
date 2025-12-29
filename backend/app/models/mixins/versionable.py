"""
Versioning mixins for entity version control system (EVCS).

This module provides a hierarchy of mixins for implementing versioning:
- Base mixins: For non-branching entities (e.g., User)
- Branch-aware mixins: For entities that support branching (e.g., Project, WBE)

Architecture follows sections 5.2.2 (Generic Type Pattern) and 5.2.3 (Mixin Pattern)
from backend_architecture.md.
"""

from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, inspect
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

# ============================================================================
# Base Mixins (Non-Branching)
# ============================================================================


class BaseHeadMixin:
    """
    Base mixin for head tables (stable identity).

    Provides only the logical entity ID without branching support.
    Use this for entities that don't require branch isolation (e.g., User).

    For branch-aware entities, use VersionableHeadMixin instead.
    """

    @declared_attr
    def id(cls) -> Mapped[UUID]:
        """Logical entity ID (stable identity)."""
        return mapped_column(SQLUUID, primary_key=True, default=uuid4)

    def to_dict(self) -> dict[str, Any]:
        """Serialize entity to dictionary using SQLAlchemy inspection."""
        from sqlalchemy.orm import Mapper

        data = {}
        mapper = inspect(self.__class__)
        if isinstance(mapper, Mapper):
            for column in mapper.column_attrs:
                value = getattr(self, column.key)
                if isinstance(value, UUID):
                    data[column.key] = str(value)
                elif isinstance(value, datetime):
                    data[column.key] = value.isoformat()
                else:
                    data[column.key] = value
        return data


class BaseVersionMixin:
    """
    Base mixin for version tables (immutable snapshots).

    Provides temporal validity and audit fields without branching support.
    Use this for entities that don't require branch isolation (e.g., UserVersion).

    For branch-aware entities, use VersionSnapshotMixin instead.
    """

    @declared_attr
    def head_id(cls) -> Mapped[UUID]:
        """Reference to logical entity ID in head table."""
        return mapped_column(SQLUUID, primary_key=True, index=True)

    @declared_attr
    def valid_from(cls) -> Mapped[datetime]:
        """Start of temporal validity (inclusive)."""
        return mapped_column(
            DateTime(timezone=True),
            primary_key=True,
            index=True,
            default=lambda: datetime.now(UTC),
        )

    @declared_attr
    def valid_to(cls) -> Mapped[datetime | None]:
        """End of temporal validity (exclusive). NULL = current version."""
        return mapped_column(DateTime(timezone=True), nullable=True, index=True)

    @declared_attr
    def created_by_id(cls) -> Mapped[UUID | None]:
        """User who created this version."""
        return mapped_column(SQLUUID, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        """Serialize version to dictionary using SQLAlchemy inspection."""
        from sqlalchemy.orm import Mapper

        data = {}
        mapper = inspect(self.__class__)
        if isinstance(mapper, Mapper):
            for column in mapper.column_attrs:
                value = getattr(self, column.key)
                if isinstance(value, datetime):
                    data[column.key] = value.isoformat()
                elif isinstance(value, UUID):
                    data[column.key] = str(value)
                else:
                    data[column.key] = value
        return data


# ============================================================================
# Branch-Aware Mixins (Extends Base Mixins)
# ============================================================================


class VersionableHeadMixin(BaseHeadMixin):
    """
    Mixin for branch-aware head tables (stable identity with branching).

    Extends BaseHeadMixin to add composite primary key (id, branch) and
    version tracking for entities that support branch isolation.

    Use this for entities like Project, WBE, CostElement that need
    change order branching capabilities.
    """

    @declared_attr
    def branch(cls) -> Mapped[str]:
        """Branch name (part of composite PK). Default is 'main'."""
        return mapped_column(String(100), primary_key=True, default="main")

    @declared_attr
    def current_version_id(cls) -> Mapped[UUID | None]:
        """Pointer to current version (mutable)."""
        return mapped_column(SQLUUID, nullable=True)

    @declared_attr
    def status(cls) -> Mapped[str]:
        """Entity status (active, deleted, merged)."""
        return mapped_column(String(20), default="active", index=True)

    # Uses BaseHeadMixin.to_dict() which is generic


class VersionSnapshotMixin(BaseVersionMixin):
    """
    Mixin for branch-aware version tables (immutable snapshots with branching).

    Extends BaseVersionMixin to add branch support, version chain (DAG structure),
    and sequential version numbering within branches.

    Use this for entities like ProjectVersion, WBEVersion, CostElementVersion
    that need to track changes across multiple branches.
    """

    @declared_attr
    def branch(cls) -> Mapped[str]:
        """Branch this version belongs to."""
        return mapped_column(String(100), primary_key=True, index=True)

    @declared_attr
    def parent_version_id(cls) -> Mapped[UUID | None]:
        """Previous version in the chain (DAG structure)."""
        return mapped_column(SQLUUID, nullable=True, index=True)

    @declared_attr
    def version(cls) -> Mapped[int]:
        """Sequential version number within branch."""
        return mapped_column(nullable=False)

    # Uses BaseVersionMixin.to_dict() which is generic


# ============================================================================
# Type Protocols (for Generic Type Pattern - Section 5.2.2)
# ============================================================================


class VersionableEntity(Protocol):
    """
    Protocol defining the interface for versionable entities.

    This is used for type hints in generic repositories and services
    to ensure compile-time type safety (MyPy strict mode).
    """

    id: UUID
    branch: str
    current_version_id: UUID | None
    status: str

    def to_dict(self) -> dict[str, Any]: ...


class VersionSnapshot(Protocol):
    """
    Protocol defining the interface for version snapshots.

    This is used for type hints in generic repositories and services
    to ensure compile-time type safety (MyPy strict mode).
    """

    id: UUID
    head_id: UUID
    branch: str
    parent_version_id: UUID | None
    version: int
    valid_from: datetime
    valid_to: datetime | None
    created_by_id: UUID | None

    def to_dict(self) -> dict[str, Any]: ...
