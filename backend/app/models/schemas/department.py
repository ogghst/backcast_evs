from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from app.models.domain.department import Department


class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=255, description="Department display name")
    manager_id: UUID | None = Field(None, description="UUID of the department manager")
    is_active: bool = Field(True, description="Whether the department is active")


class DepartmentCreate(DepartmentBase):
    code: str = Field(
        ...,
        max_length=50,
        pattern="^[A-Z0-9_-]+$",
        description="Unique department code (immutable)",
    )


class DepartmentUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    manager_id: UUID | None = None
    is_active: bool | None = None


class DepartmentPublic(DepartmentBase):
    id: UUID
    code: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, department: "Department") -> "DepartmentPublic":
        if not department.versions:
            raise ValueError("Department has no versions")
        latest = department.versions[0]
        return cls(
            id=department.id,
            code=department.code,
            name=latest.name,
            manager_id=latest.manager_id,
            is_active=latest.is_active,
            created_at=latest.valid_from,
        )
