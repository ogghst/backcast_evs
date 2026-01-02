from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.models.domain.department import Department
from app.models.domain.user import User
from app.models.schemas.department import (
    DepartmentCreate,
    DepartmentPublic,
    DepartmentUpdate,
)
from app.services.department import DepartmentService

router = APIRouter()


def get_department_service(
    session: AsyncSession = Depends(get_db),
) -> DepartmentService:
    return DepartmentService(session)


def check_admin(current_user: User) -> None:
    """Helper to check admin privileges."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )


@router.get("", response_model=list[DepartmentPublic])
async def read_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> Sequence[Department]:
    """Retrieve departments."""
    return await service.get_departments(skip=skip, limit=limit)

@router.post("", response_model=DepartmentPublic, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_in: DepartmentCreate,
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> Department:
    """Create a new department. Admin only."""
    check_admin(current_user)

    try:
        dept = await service.create_department(
            dept_in=dept_in, actor_id=current_user.id
        )
        return dept
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/{department_id}", response_model=DepartmentPublic)
async def read_department(
    department_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> Department:
    """Get a specific department by id."""
    dept = await service.get_department(department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return dept


@router.put("/{department_id}", response_model=DepartmentPublic)
async def update_department(
    department_id: UUID,
    dept_in: DepartmentUpdate,
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> Department:
    """Update a department. Admin only."""
    check_admin(current_user)

    try:
        updated_dept = await service.update_department(
            department_id=department_id,
            dept_in=dept_in,
            actor_id=current_user.id,
        )
        return updated_dept
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> None:
    """Soft delete a department. Admin only."""
    check_admin(current_user)

    try:
        await service.delete_department(
            department_id=department_id, actor_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
