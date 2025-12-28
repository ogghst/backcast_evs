import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.domain.base import Base


class User(Base):
    """
    User head entity containing stable identity and authentication secrets.
    Attempts to follow the EVCS pattern where identity is separated from state.
    """

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship to versions
    # We use a string reference "UserVersion" to avoid circular imports if defined in same file
    versions: Mapped[list["UserVersion"]] = relationship(
        "UserVersion",
        back_populates="head",
        cascade="all, delete-orphan",
        order_by="desc(UserVersion.valid_from)",
        foreign_keys="[UserVersion.head_id]",
    )


class UserVersion(Base):
    """
    Immutable version snapshot of user profile data.
    Composite primary key includes head_id, branch, and valid_from.
    """

    __tablename__ = "user_version"

    head_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    branch: Mapped[str] = mapped_column(
        String, primary_key=True, default="main", index=True
    )
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        default=lambda: datetime.now(UTC),
    )

    # Payload fields (mutable profile data)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default="viewer")  # Could use Enum
    department: Mapped[str | None] = mapped_column(String, nullable=True)

    # Audit fields
    valid_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )

    # Relationships
    head: Mapped["User"] = relationship(
        "User", back_populates="versions", foreign_keys=[head_id]
    )
