from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.versioning.commands import CommandMetadata, VersionCommand
from app.models.domain.department import Department, DepartmentVersion


class CreateDepartmentCommand(VersionCommand[Department]):
    """Command to create a new department (Head + Initial Version)."""

    def __init__(
        self,
        metadata: CommandMetadata,
        code: str,
        name: str,
        manager_id: UUID | None = None,
        is_active: bool = True,
        id: UUID | None = None,
    ):
        super().__init__(metadata)
        self.code = code
        self.name = name
        self.manager_id = manager_id
        self.is_active = is_active
        self.id = id
        self.created_head_id: UUID | None = None

    async def execute(self, session: AsyncSession) -> Department:
        # Create head entity (identity)
        dept_kwargs: dict[str, Any] = {
            "code": self.code,
        }
        if self.id:
            dept_kwargs["id"] = self.id

        department = Department(**dept_kwargs)
        session.add(department)
        await session.flush()
        self.created_head_id = department.id

        # Create initial version (state)
        version = DepartmentVersion(
            head_id=department.id,
            name=self.name,
            manager_id=self.manager_id,
            is_active=self.is_active,
            valid_from=self.metadata.timestamp,
            created_by_id=self.metadata.user_id,
        )
        session.add(version)
        await session.flush()

        # Refresh with versions loaded
        stmt = (
            select(Department)
            .options(selectinload(Department.versions))
            .where(Department.id == department.id)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one()

    async def undo(self, session: AsyncSession) -> None:
        """Undo creation by deleting the department."""
        if self.created_head_id:
            stmt = delete(Department).where(Department.id == self.created_head_id)
            await session.execute(stmt)


class UpdateDepartmentCommand(VersionCommand[DepartmentVersion]):
    """Command to update department details (New Version)."""

    def __init__(
        self,
        metadata: CommandMetadata,
        department_id: UUID,
        changes: dict[str, Any],
    ):
        super().__init__(metadata)
        self.department_id = department_id
        self.changes = changes
        self.new_version_pk: tuple[UUID, datetime] | None = None
        self.previous_version_pk: tuple[UUID, datetime] | None = None

    async def execute(self, session: AsyncSession) -> DepartmentVersion:
        # Get current active version
        stmt = (
            select(DepartmentVersion)
            .where(
                DepartmentVersion.head_id == self.department_id,
                DepartmentVersion.valid_to.is_(None),
            )
            .order_by(DepartmentVersion.valid_from.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        current_version = result.scalar_one_or_none()

        if not current_version:
            raise ValueError(f"No active version found for department {self.department_id}")

        self.previous_version_pk = (current_version.head_id, current_version.valid_from)

        # Close current version
        current_version.valid_to = self.metadata.timestamp
        session.add(current_version)

        # Prepare new version data
        source_data = current_version.to_dict()
        exclude_fields = {
            "head_id",
            "valid_from",
            "valid_to",
            "created_by_id",
        }
        new_data = {k: v for k, v in source_data.items() if k not in exclude_fields}
        new_data.update(self.changes)

        # Create new version
        new_version = DepartmentVersion(
            head_id=self.department_id,
            valid_from=self.metadata.timestamp,
            created_by_id=self.metadata.user_id,
            **new_data,
        )
        session.add(new_version)
        await session.flush()

        self.new_version_pk = (new_version.head_id, new_version.valid_from)
        return new_version

    async def undo(self, session: AsyncSession) -> None:
        """Undo update: delete new version, reopen previous."""
        if self.new_version_pk and self.previous_version_pk:
            # Delete new version
            del_stmt = delete(DepartmentVersion).where(
                DepartmentVersion.head_id == self.new_version_pk[0],
                DepartmentVersion.valid_from == self.new_version_pk[1],
            )
            await session.execute(del_stmt)

            # Reopen previous version
            upd_stmt = (
                update(DepartmentVersion)
                .where(
                    DepartmentVersion.head_id == self.previous_version_pk[0],
                    DepartmentVersion.valid_from == self.previous_version_pk[1],
                )
                .values(valid_to=None)
            )
            await session.execute(upd_stmt)


class DeleteDepartmentCommand(VersionCommand[DepartmentVersion]):
    """
    Command to soft-delete a department.
    Creates a new version with is_active=False.
    """

    def __init__(
        self,
        metadata: CommandMetadata,
        department_id: UUID,
    ):
        super().__init__(metadata)
        self.department_id = department_id
        self.new_version_pk: tuple[UUID, datetime] | None = None
        self.previous_version_pk: tuple[UUID, datetime] | None = None

    async def execute(self, session: AsyncSession) -> DepartmentVersion:
        # Get current active version
        stmt = (
            select(DepartmentVersion)
            .where(
                DepartmentVersion.head_id == self.department_id,
                DepartmentVersion.valid_to.is_(None),
            )
            .order_by(DepartmentVersion.valid_from.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        current_version = result.scalar_one_or_none()

        if not current_version:
            raise ValueError(f"No active version found for department {self.department_id}")

        self.previous_version_pk = (current_version.head_id, current_version.valid_from)

        # Close current version
        current_version.valid_to = self.metadata.timestamp
        session.add(current_version)

        # Create new version (Copy of old + is_active=False)
        source_data = current_version.to_dict()
        exclude_fields = {
            "head_id",
            "valid_from",
            "valid_to",
            "created_by_id",
        }
        new_data = {k: v for k, v in source_data.items() if k not in exclude_fields}
        new_data["is_active"] = False

        new_version = DepartmentVersion(
            head_id=self.department_id,
            valid_from=self.metadata.timestamp,
            created_by_id=self.metadata.user_id,
            **new_data,
        )
        session.add(new_version)
        await session.flush()

        self.new_version_pk = (new_version.head_id, new_version.valid_from)
        return new_version

    async def undo(self, session: AsyncSession) -> None:
        """Undo soft delete: remove inactive version, reopen previous."""
        if self.new_version_pk and self.previous_version_pk:
            # Delete new version
            del_stmt = delete(DepartmentVersion).where(
                DepartmentVersion.head_id == self.new_version_pk[0],
                DepartmentVersion.valid_from == self.new_version_pk[1],
            )
            await session.execute(del_stmt)

            # Reopen previous version
            upd_stmt = (
                update(DepartmentVersion)
                .where(
                    DepartmentVersion.head_id == self.previous_version_pk[0],
                    DepartmentVersion.valid_from == self.previous_version_pk[1],
                )
                .values(valid_to=None)
            )
            await session.execute(upd_stmt)
