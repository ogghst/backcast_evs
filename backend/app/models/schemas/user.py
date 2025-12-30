from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

if TYPE_CHECKING:
    from app.models.domain.user import User


# Shared properties
class UserBase(BaseModel):
    email: EmailStr = Field(
        description="The email address of the user", examples=["user@example.com"]
    )
    full_name: str = Field(
        description="The full name of the user", examples=["John Doe"]
    )
    department: str | None = Field(
        default=None, description="The department the user belongs to", examples=["IT"]
    )
    role: str = Field(
        default="viewer",
        description="The role of the user (e.g., admin, viewer)",
        examples=["viewer"],
    )


# Properties to receive via API on creation
class UserRegister(UserBase):
    password: str = Field(
        min_length=8,
        description="Password must be at least 8 characters",
        examples=["S3cur3P@ssw0rd"],
    )


# Properties to receive via API on update
class UserUpdate(BaseModel):
    full_name: str | None = None
    department: str | None = None
    role: str | None = None
    password: str | None = None


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
