from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

if TYPE_CHECKING:
    from app.models.domain.user import User


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
class UserPublic(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime | None = (
        None  # Logic to map valid_from to created_at if needed
    )

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_entity(cls, user: "User") -> "UserPublic":
        if not user.versions:
            raise ValueError("User has no versions")
        latest_version = user.versions[0]
        return cls(
            id=user.id,
            email=user.email,
            full_name=latest_version.full_name,
            department=latest_version.department,
            role=latest_version.role,
            is_active=latest_version.is_active,
            created_at=latest_version.valid_from,
        )


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
