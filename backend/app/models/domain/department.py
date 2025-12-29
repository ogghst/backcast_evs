"""
Department domain models.
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.domain.base import Base
from app.models.mixins.versionable import BaseHeadMixin, BaseVersionMixin

if TYPE_CHECKING:
    from app.models.domain.user import User


class Department(BaseHeadMixin, Base):
    """
    Department Head Entity.

    Stores immutable identity:
    - id: UUID (from BaseHeadMixin)
    - code: Unique department code (e.g. "ENG", "HR")
    """

    __tablename__ = "department"

    code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    # Relationships
    versions: Mapped[list["DepartmentVersion"]] = relationship(
        "DepartmentVersion",
        back_populates="department",
        primaryjoin="Department.id == DepartmentVersion.head_id",
        order_by="desc(DepartmentVersion.valid_from)",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Department(id={self.id}, code={self.code})>"


class DepartmentVersion(BaseVersionMixin, Base):
    """
    Department Version Entity.

    Stores mutable profile data:
    - name: Department display name
    - manager_id: Optional link to User
    - is_active: Status
    """

    __tablename__ = "department_version"

    head_id: Mapped[UUID] = mapped_column(
        SQLUUID,
        ForeignKey("department.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    manager_id: Mapped[UUID | None] = mapped_column(
        SQLUUID, ForeignKey("user.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped["Department"] = relationship(
        "Department",
        back_populates="versions",
    )

    manager: Mapped["User"] = relationship("User", foreign_keys=[manager_id])

    def __repr__(self) -> str:
        return f"<DepartmentVersion(head_id={self.head_id}, name={self.name}, valid_from={self.valid_from})>"
