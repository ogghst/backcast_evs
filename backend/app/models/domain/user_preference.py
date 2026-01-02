"""User preference domain model.

Simple (non-versioned) entity storing user UI preferences.
Satisfies SimpleEntityProtocol.
"""

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import SimpleEntityBase


class UserPreference(SimpleEntityBase):
    """User preferences - non-versioned, mutable.

    Stores:
    - theme: UI theme (light/dark)
    - (future: locale, timezone, etc.)

    Satisfies: SimpleEntityProtocol
    """

    __tablename__ = "user_preferences"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    theme: Mapped[str] = mapped_column(String(20), default="light")

    # Relationships (commented out to avoid circular dependency during TDD)
    # user: Mapped["User"] = relationship("User", back_populates="preference")  # type: ignore

    def __repr__(self) -> str:
        return f"<UserPreference(id={self.id}, user_id={self.user_id}, theme={self.theme})>"
