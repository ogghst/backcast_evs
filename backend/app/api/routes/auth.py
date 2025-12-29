from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_active_user
from app.db.session import get_db
from app.models.domain.user import User
from app.models.schemas.user import Token, UserLogin, UserPublic, UserRegister
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: UserRegister,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """
    Register a new user.
    """
    auth_service = AuthService(session)
    try:
        user = await auth_service.register_user(user_in)
        # We need to construct UserPublic from User + UserVersion
        # Since our User model doesn't flattened fields directly mapping to UserPublic
        # (UserPublic has full_name, is_active etc, which are on UserVersion)

        # We manually map it here or rely on Pydantic's from_attributes if the User object
        # has these attributes/properties proxying to the latest version.

        # Manually mapping for safety given the complexity of EVCS:
        return UserPublic.from_entity(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    auth_service = AuthService(session)
    user = await auth_service.authenticate_user(
        UserLogin(email=form_data.username, password=form_data.password)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.create_token(user)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Any:
    """
    Get current user.
    """
    # Map to schema
    return UserPublic.from_entity(current_user)
