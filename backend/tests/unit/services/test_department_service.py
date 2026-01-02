
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.department import DepartmentService

# from app.models.domain.department import Department
# Note: We assume app.services.department and app.models.domain.department exist/will be created.

class TestDepartmentServiceCreate:
    """Test DepartmentService.create_department() method."""

    @pytest.mark.asyncio
    async def test_create_department_success(self, db_session: AsyncSession) -> None:
        """RED: Test successfully creating a department."""
        service = DepartmentService(db_session)
        dept_id = uuid4()
        dept_data = {
            "department_id": dept_id, # Root ID
            "name": "Engineering",
            "code": "ENG",
            "is_active": True,
            "manager_id": None
        }

        # Act
        created_dept = await service.create_department(dept_data, actor_id=uuid4())

        # Assert
        assert created_dept is not None
        assert created_dept.name == "Engineering"

        # Verify persistence
        fetched = await service.get_department(created_dept.id)
        assert fetched is not None
        assert fetched.name == "Engineering"


class TestDepartmentServiceUpdate:
    """Test DepartmentService.update_department() method."""

    @pytest.mark.asyncio
    async def test_update_department_versions(self, db_session: AsyncSession) -> None:
        """Test updating a department creates a new version."""
        service = DepartmentService(db_session)
        dept_id = uuid4()
        dept_data = {
            "department_id": dept_id,
            "name": "Original Name",
            "code": "DEPT1",
            "is_active": True,
        }
        # Create initial
        v1 = await service.create_department(dept_data, actor_id=uuid4())

        # Act
        update_data = {"name": "Updated Name"}
        v2 = await service.update_department(v1.department_id, update_data, actor_id=uuid4())

        # Assert
        assert v2.id != v1.id  # New version ID
        assert v2.department_id == dept_id # Same root ID
        assert v2.name == "Updated Name"

        # Verify persistence
        fetched = await service.get_department(v2.id)
        assert fetched is not None
        assert fetched.name == "Updated Name"


class TestDepartmentServiceDelete:
    """Test DepartmentService.delete_department() method."""

    @pytest.mark.asyncio
    async def test_delete_department_soft_deletes(self, db_session: AsyncSession) -> None:
        """Test deleting a department soft-deletes current version."""
        service = DepartmentService(db_session)
        dept_id = uuid4()
        dept_data = {
            "department_id": dept_id,
            "name": "To Delete",
            "code": "DEL",
            "is_active": True,
        }
        # Create
        v1 = await service.create_department(dept_data, actor_id=uuid4())

        # Act
        await service.delete_department(dept_id, actor_id=uuid4())

        # Assert
        deleted = await service.get_department(v1.id)
        assert deleted is not None
        assert deleted.is_deleted is True

        # Verify get_by_code filters it out
        result = await service.get_by_code("DEL")
        assert result is None
