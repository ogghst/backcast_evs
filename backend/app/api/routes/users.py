from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.models.domain.user import User
from app.models.schemas.user import UserPublic, UserRegister, UserUpdate
from app.services.user import UserService

router = APIRouter()


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


@router.get("", response_model=list[UserPublic])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> Sequence[UserPublic]:
    """
    Retrieve a list of users.

    - **skip**: Number of users to skip (pagination).
    - **limit**: Maximum number of users to return (max 100).

    Only Admins can list all users.
    """
    # Assuming role is in the latest version (current_user.versions[0])
    # Ideally, we should have a dependency helper for this or helpers on User object
    latest_version = current_user.versions[0]
    if latest_version.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required to perform this action",
        )

    # We return the User entities. Pydantic UserPublic schema's from_attributes=True
    # + from_entity classmethod (if we use it) or basic mapping will handle conversion.
    # UserPublic expects flat fields.
    # Pydantic's from_attributes with SQLAlchemy works if attributes match.
    # UserPublic has fields like 'full_name' which are NOT on User, but on UserVersion.
    # Direct Pydantic conversion will fail if attributes are missing on the object.
    # We verified UserPublic uses `from_entity` manually?
    # No, ConfigDict(from_attributes=True) handles attributes.
    # But User entity doesn't have 'full_name'.
    # We must use the `from_entity` method or manual mapping.
    # FastAPI response_model handles validation, but `from_attributes` only works if the object HAS those attributes.

    # Solution: We need to map entities to UserPublic instances before returning.
    users = await service.get_users(skip=skip, limit=limit)
    return [UserPublic.from_entity(u) for u in users]


@router.post("", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserRegister,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    """
    Create a new user.
    Admin only.
    """
    latest_version = current_user.versions[0]
    if latest_version.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required to perform this action",
        )

    try:
        user = await service.create_user(user_data=user_in, actor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    # Refresh versions to ensure proper serialization

    return UserPublic.from_entity(user)


@router.get("/{user_id}", response_model=UserPublic)
async def read_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    """
    Get a specific user by id.
    Admin can get any user. Users can only get themselves.
    """
    latest_version = current_user.versions[0]
    if latest_version.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required to perform this action",
        )

    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserPublic.from_entity(user)


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> UserPublic:
    """
    Update a user.
    Admin can update any user. Users can only update themselves.
    """
    latest_version = current_user.versions[0]
    if latest_version.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required to perform this action",
        )

    await service.update_user(
        user_id=user_id, update_data=user_in, actor_id=current_user.id
    )

    # We need to return the UserPublic representation.
    # updated_version is a UserVersion.
    # UserPublic expects a User object or similar structure.
    # But UserPublic fields match UserVersion fields + email/id from head.
    # We should re-fetch the user to get a consistent generic object,
    # OR construct UserPublic carefully.

    # Easier to return the User entity which contains everything.
    # Wait, update_user service returns UserVersion.
    # We should probably get the full user again to ensure structure.
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Refresh versions to ensure we see the update

    # Refresh versions to ensure we see the update (Identity Map fix)
    await service.session.refresh(user, attribute_names=["versions"])
    return UserPublic.from_entity(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> None:
    """
    Soft delete a user.
    Admin only.
    """
    latest_version = current_user.versions[0]
    if latest_version.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required to perform this action",
        )

    await service.delete_user(user_id=user_id, actor_id=current_user.id)
