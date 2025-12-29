"""Versioning mixins for EVCS."""

from app.models.mixins.versionable import (
    BaseHeadMixin,
    BaseVersionMixin,
    VersionableEntity,
    VersionableHeadMixin,
    VersionSnapshot,
    VersionSnapshotMixin,
)

__all__ = [
    # Base mixins (non-branching)
    "BaseHeadMixin",
    "BaseVersionMixin",
    # Branch-aware mixins
    "VersionableHeadMixin",
    "VersionSnapshotMixin",
    # Type protocols
    "VersionableEntity",
    "VersionSnapshot",
]
