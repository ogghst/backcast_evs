from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.db.session import get_db
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
    latest_version = current_user.versions[0]
    if latest_version.role != "admin":
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
) -> Sequence[DepartmentPublic]:
    """Retrieve departments."""
    departments = await service.get_departments(skip=skip, limit=limit)
    return [DepartmentPublic.from_entity(d) for d in departments]


@router.post("", response_model=DepartmentPublic, status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_in: DepartmentCreate,
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentPublic:
    """Create a new department. Admin only."""
    check_admin(current_user)

    try:
        dept = await service.create_department(
            dept_data=dept_in, actor_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


    return DepartmentPublic.from_entity(dept)


@router.get("/{department_id}", response_model=DepartmentPublic)
async def read_department(
    department_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentPublic:
    """Get a specific department by id."""
    dept = await service.get_department(department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )
    return DepartmentPublic.from_entity(dept)


@router.put("/{department_id}", response_model=DepartmentPublic)
async def update_department(
    department_id: UUID,
    dept_in: DepartmentUpdate,
    current_user: User = Depends(get_current_active_user),
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentPublic:
    """Update a department. Admin only."""
    check_admin(current_user)

    try:
        await service.update_department(
            department_id=department_id, update_data=dept_in, actor_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    dept = await service.get_department(department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")


    return DepartmentPublic.from_entity(dept)


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
