from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field

if TYPE_CHECKING:
    pass


def convert_range_to_list(v: Any) -> list[datetime | None] | None:
    """Convert PostgreSQL Range object to list of [lower, upper]."""
    if v is None:
        return None
    if hasattr(v, "lower") and hasattr(v, "upper"):
        return [v.lower, v.upper]
    return v  # type: ignore[no-any-return]


# Type alias for range fields that need conversion
RangeToList = Annotated[
    list[datetime | None] | None, BeforeValidator(convert_range_to_list)
]


# Shared properties
class UserBase(BaseModel):
    """Base generic User schema."""

    email: EmailStr
    full_name: str
    department: str | None = None
    role: str = "viewer"


# Properties to receive via API on creation
class UserRegister(UserBase):
    """Schema for user registration."""

    password: str = Field(
        min_length=8, description="Password must be at least 8 characters"
    )


# Properties to receive via API on update
class UserUpdate(BaseModel):
    """Schema for user updates."""

    full_name: str | None = None
    department: str | None = None
    role: str | None = None
    password: str | None = None
    is_active: bool | None = None


# Properties to return to client (public implementation)
class UserRead(UserBase):
    """Schema for reading user data (excludes password)."""

    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime | None = None  # For temporal compatibility
    password_changed_at: datetime | None = None  # Track password changes
    preferences: dict[str, Any] | None = None  # User preferences as JSON

    model_config = ConfigDict(from_attributes=True)


# Alias for backward compatibility with routes
UserPublic = UserRead


# Schema for version history - includes temporal fields
class UserHistory(UserRead):
    """Schema for reading user version history (includes temporal fields)."""

    valid_time: RangeToList = Field(
        None, description="Valid time range for this version"
    )
    transaction_time: RangeToList = Field(
        None, description="Transaction time range for this version"
    )

    model_config = ConfigDict(from_attributes=True)


# Login schema
class UserLogin(BaseModel):
    """Schema for user login credentials."""

    email: EmailStr
    password: str


# Token schema
class Token(BaseModel):
    """Schema for authentication token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload data."""

    sub: str | None = None
