"""Project domain model.

A Branchable Entity used for demonstrating and testing EVCS branching capabilities.
Satisfies BranchableProtocol.
"""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base.base import EntityBase
from app.models.mixins import BranchableMixin, VersionableMixin


class Project(EntityBase, VersionableMixin, BranchableMixin):
    """Project entity with full EVCS capabilities (Versioning + Branching).

    Attributes:
        project_id: Root ID for the project aggregation.
        name: Project name.
        description: Optional description.
        budget: Project budget.
    """

    __tablename__ = "projects"

    # Root ID is required for versioning/branching aggregations
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID

    project_id: Mapped[UUID] = mapped_column(PG_UUID, nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0)

    def __repr__(self) -> str:
        return (
            f"<Project(id={self.id}, root={self.project_id}, "
            f"branch={self.branch}, name={self.name})>"
        )
