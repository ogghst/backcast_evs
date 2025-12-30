"""
User Preference domain models.

Stores user-specific settings like UI theme.
Follows the Head/Version pattern but simplified (similar to User) since it's
associated directly with a user and doesn't participate in general project branching.
"""

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.domain.base import Base
from app.models.mixins.versionable import BaseHeadMixin, BaseVersionMixin


class UserPreference(BaseHeadMixin, Base):
    """
    UserPreference head table.
    
    Links preferences to a specific User.
    One-to-One relationship with User (or effectively so, logic enforced).
    """

    __tablename__ = "user_preference"

    # Link to the user who owns these preferences
    user_id: Mapped[UUID] = mapped_column(
        SQLUUID,
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Relationship to user
    user: Mapped["User"] = relationship("User", back_populates="preference")

    # Relationship to versions
    versions: Mapped[list["UserPreferenceVersion"]] = relationship(
        "UserPreferenceVersion",
        back_populates="preference",
        primaryjoin="UserPreference.id == UserPreferenceVersion.head_id",
        order_by="desc(UserPreferenceVersion.valid_from)",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id}, user_id={self.user_id})>"


class UserPreferenceVersion(BaseVersionMixin, Base):
    """
    UserPreference version table.
    
    Stores the actual preference values with history.
    """

    __tablename__ = "user_preference_version"

    # Override head_id
    head_id: Mapped[UUID] = mapped_column(
        SQLUUID,
        ForeignKey("user_preference.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    # Preference fields
    theme: Mapped[str] = mapped_column(String(50), nullable=False, default="light")

    # Relationship back to head
    preference: Mapped["UserPreference"] = relationship(
        "UserPreference",
        back_populates="versions",
    )

    def __repr__(self) -> str:
        return f"<UserPreferenceVersion(head_id={self.head_id}, theme={self.theme})>"
