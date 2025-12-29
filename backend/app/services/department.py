from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.department import (
    CreateDepartmentCommand,
    DeleteDepartmentCommand,
    UpdateDepartmentCommand,
)
from app.core.versioning.commands import CommandMetadata
from app.models.domain.department import Department, DepartmentVersion
from app.models.schemas.department import DepartmentCreate, DepartmentUpdate
from app.repositories.department import DepartmentRepository


class DepartmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.dept_repo = DepartmentRepository(session)

    async def get_department(self, department_id: UUID) -> Department | None:
        """Get department by ID."""
        return await self.dept_repo.get_by_id(department_id)

    async def get_departments(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Department]:
        """Get all departments with pagination."""
        return await self.dept_repo.get_all(skip=skip, limit=limit)

    async def create_department(
        self, dept_data: DepartmentCreate, actor_id: UUID
    ) -> Department:
        """Create a new department."""
        existing_dept = await self.dept_repo.get_by_code(dept_data.code)
        if existing_dept:
            raise ValueError(f"Department code '{dept_data.code}' already exists")

        new_id = UUID(int=uuid4().int)

        metadata = CommandMetadata(
            command_type="CREATE_DEPARTMENT",
            user_id=actor_id,
            timestamp=datetime.now(UTC),
            description=f"Created department: {dept_data.code}",
        )

        command = CreateDepartmentCommand(
            metadata=metadata,
            code=dept_data.code,
            name=dept_data.name,
            manager_id=dept_data.manager_id,
            is_active=dept_data.is_active,
            id=new_id,
        )

        return await command.execute(self.session)

    async def update_department(
        self, department_id: UUID, update_data: DepartmentUpdate, actor_id: UUID
    ) -> DepartmentVersion:
        """Update department details."""
        changes = update_data.model_dump(exclude_unset=True)
        if not changes:
            # If no changes, return current version but verify existence
            dept = await self.dept_repo.get_by_id(department_id)
            if not dept or not dept.versions:
                raise ValueError("Department or version not found")
            return dept.versions[0]

        metadata = CommandMetadata(
            command_type="UPDATE_DEPARTMENT",
            user_id=actor_id,
            timestamp=datetime.now(UTC),
            description="Department Update",
        )

        command = UpdateDepartmentCommand(
            metadata=metadata, department_id=department_id, changes=changes
        )
        return await command.execute(self.session)

    async def delete_department(self, department_id: UUID, actor_id: UUID) -> None:
        """Soft delete department."""
        metadata = CommandMetadata(
            command_type="DELETE_DEPARTMENT",
            user_id=actor_id,
            timestamp=datetime.now(UTC),
            description="Department Soft Delete",
        )

        command = DeleteDepartmentCommand(
            metadata=metadata, department_id=department_id
        )
        await command.execute(self.session)
