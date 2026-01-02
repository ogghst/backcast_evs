from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user, get_user_service
from app.db.session import get_db
from app.models.domain.user import User
from app.models.schemas.user import UserPublic, UserRegister, UserUpdate
from app.schemas import preference
from app.services.user import UserService

router = APIRouter()


@router.get("", response_model=list[UserPublic])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> Sequence[User]:
    """
    Retrieve users.
    Only Admins can list all users.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    return await service.get_users(skip=skip, limit=limit)


@router.post("", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserRegister,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Create a new user.
    Admin only.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    try:
        # Pydantic model (UserRegister) to dict
        user_data = user_in.model_dump()
        # Hash password? In the old code, UserService.create_user likely expected hashed_password
        # OR it expected plain password and hashed it.
        # The schema UserRegister has 'password'.
        # The new CreateVersionCommand expects fields.
        # Wait, the User model has 'hashed_password'.
        # I need to hash the password here or in the service.
        # Let's check UserService.create_user. It passes **user_data to CreateVersionCommand.
        # CreateVersionCommand(User, ...) -> User(**fields).
        # User model has 'hashed_password'. It does NOT handle 'password' argument.
        # So I MUST hash it.

        # Using existing utility (assuming it exists, from app.core.security)
        from app.core.security import get_password_hash

        user_data["hashed_password"] = get_password_hash(user_data.pop("password"))

        user = await service.create_user(user_data=user_data, actor_id=current_user.id)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/me/preferences", response_model=preference.UserPreferenceResponse)
async def get_my_preferences(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get current user's preferences.
    """
    from app.services.user_preference import UserPreferenceService

    service = UserPreferenceService(session)

    # Note: UserPreferenceService.get_by_user_id takes root ID?
    # Or version ID? We decided it links to 'users.id' which is version ID.
    # So we pass current_user.id
    pref = await service.get_by_user_id(current_user.id)
    if not pref:
        # Return default?
        from app.models.domain.user_preference import UserPreference

        return UserPreference(user_id=current_user.id, theme="light")
    return pref


@router.put("/me/preferences", response_model=preference.UserPreferenceResponse)
async def update_my_preferences(
    pref_in: preference.UserPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update current user's preferences.
    """
    from app.services.user_preference import UserPreferenceService

    service = UserPreferenceService(session)

    # Create or update
    pref = await service.get_by_user_id(current_user.id)
    if pref:
        return await service.update_preference(current_user.id, pref_in.theme)
    else:
        return await service.create_preference(current_user.id, pref_in.theme)


@router.get("/{user_id}", response_model=UserPublic)
async def read_user(
    user_id: UUID,  # This fetches by version ID (PK)
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Get a specific user by id.
    Admin can get any user. Users can only get themselves.
    """
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Update a user.
    Admin can update any user. Users can only update themselves.
    """
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    # Filter None values from update data
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        from app.core.security import get_password_hash

        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    try:
        updated_user = await service.update_user(
            user_id=user_id, update_data=update_data, actor_id=current_user.id
        )
        return updated_user
    except ValueError as e:  # Entity not found or version conflict
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


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
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )

    await service.delete_user(user_id=user_id, actor_id=current_user.id)
