from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

if TYPE_CHECKING:
    pass


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    department: str | None = None
    role: str = "viewer"


# Properties to receive via API on creation
class UserRegister(UserBase):
    password: str = Field(
        min_length=8, description="Password must be at least 8 characters"
    )


# Properties to receive via API on update
class UserUpdate(BaseModel):
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


# Login schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
