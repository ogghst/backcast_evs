"""
User domain models for authentication and authorization.

User is a special case in the EVCS architecture:
- User identity (head) does NOT support branching (no change orders for users)
- User profile (version) tracks mutable attributes with temporal validity
- Security credentials (hashed_password) are stored in head table only
- Uses BaseHeadMixin and BaseVersionMixin instead of branch-aware mixins

Architecture:
- User (Head): Immutable identity (id, email) + security (hashed_password)
- UserVersion (Version): Mutable profile (full_name, role, department, is_active)
"""

from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.domain.base import Base
from app.models.mixins.versionable import BaseHeadMixin, BaseVersionMixin


class User(BaseHeadMixin, Base):
    """
    User head table - stable identity and security credentials.

    This table stores:
    - Immutable identity: id (UUID), email
    - Security: hashed_password (never versioned for security reasons)

    Mutable profile data (full_name, role, department, is_active) is stored
    in UserVersion table with full temporal history.

    Note: User does NOT use VersionableHeadMixin because users don't support
    branching. There are no "change orders" for user profiles.
    """

    __tablename__ = "user"

    # Identity fields (immutable)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    # Security credentials (never versioned)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationship to versions (ordered by valid_from descending)
    versions: Mapped[list["UserVersion"]] = relationship(
        "UserVersion",
        back_populates="user",
        primaryjoin="User.id == UserVersion.head_id",
        order_by="desc(UserVersion.valid_from)",
        lazy="selectin",  # Automatically load versions with user
    )

    # User Preferences (One-to-One)
    preference: Mapped["UserPreference"] = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

    def to_dict(self) -> dict[str, Any]:
        """Serialize entity to dictionary (excludes sensitive data)."""
        data = super().to_dict()
        data.pop("hashed_password", None)
        return data


class UserVersion(BaseVersionMixin, Base):
    """
    User version table - immutable profile snapshots.

    This table stores temporal history of mutable user attributes:
    - full_name: Display name
    - role: User role (admin, editor, viewer)
    - department: Optional department assignment
    - is_active: Account status

    Each update creates a new version with:
    - valid_from: When this version became active
    - valid_to: When this version was superseded (NULL = current)
    - created_by_id: Who made the change

    Note: UserVersion does NOT use VersionSnapshotMixin because it doesn't
    need branch support or version chain (parent_version_id, version number).
    The composite PK is (head_id, valid_from) instead of (head_id, branch, valid_from).
    """

    __tablename__ = "user_version"

    # Override head_id to add ForeignKey constraint
    head_id: Mapped[UUID] = mapped_column(
        SQLUUID,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    # Profile fields (versioned)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="viewer")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationship back to head
    user: Mapped["User"] = relationship(
        "User",
        back_populates="versions",
    )

    def __repr__(self) -> str:
        return f"<UserVersion(head_id={self.head_id}, full_name={self.full_name}, valid_from={self.valid_from})>"

    # Note: to_dict() is inherited from BaseVersionMixin and is generic.
    # It will automatically include full_name, role, department, and is_active.
