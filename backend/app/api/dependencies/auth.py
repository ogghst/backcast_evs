from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.domain.user import User
from app.models.schemas.user import TokenPayload
from app.repositories.user import UserRepository

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.
    validates the token and retrieves the user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    token_data = TokenPayload(**payload)
    if token_data.sub is None:
        raise credentials_exception

    user_repo = UserRepository()
    # The sub claim contains the user ID
    try:
        user_id = token_data.sub
        # We need to convert string UUID to UUID object if repository expects it
        # But get_by_id likely expects UUID object
        from uuid import UUID

        user_uuid = UUID(user_id)
        user = await user_repo.get_by_id(session, user_uuid)
    except (ValueError, TypeError):
        raise credentials_exception from None

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to ensure the current user is active.
    This requires looking up the user's active status from their latest version.
    """
    # In EVCS, active status is in UserVersion.
    # Our get_by_id repository method should populate 'versions' or we need to access it.
    # However, since User (head) doesn't have is_active, we rely on the latest version.
    # The User domain model has a relationship 'versions'.

    # Simple check if versions are loaded, otherwise assume active or fetch
    # Ideally, repository should join latest version.
    # For now, let's implement a simple check if we have access to the status.
    # If the User object returned by repo only has head fields + simple relationship,
    # we might need to rely on what UserRepository.get_by_id does.

    # In my User domain model:
    # versions: Mapped[list["UserVersion"]] = relationship(..., order_by="desc(UserVersion.valid_from)")

    # If versions are loaded, we can check [0].is_active.
    # If not loaded, we might fail or need to lazy load (async issue).

    # Let's trust that the repository returns the user.
    # But wait, User.is_active is NOT on the User model I defined!
    # I defined: User(id, email, hashed_password)
    # UserVersion(..., is_active, ...)
    # So I CANNOT check current_user.is_active directly unless I mapped it to the head object via property or if I access versions[0].

    if not current_user.versions:
        # Fallback or error if no version exists (should not happen for valid users)
        raise HTTPException(status_code=400, detail="User has no profile version")

    latest_version = current_user.versions[0]
    if not latest_version.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
