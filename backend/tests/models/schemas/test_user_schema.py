from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.domain.user import User, UserVersion
from app.models.schemas.user import UserPublic, UserRegister


def test_user_public_from_entity() -> None:
    # 1. Create User
    user_id = uuid4()
    user = User(id=user_id, email="test@example.com", hashed_password="pw")

    # 2. Create Active Version
    version = UserVersion(
        head_id=user_id,
        full_name="Test User",
        role="viewer",
        department="Engineering",
        is_active=True,
        valid_from=datetime.now(UTC),
        created_by_id=user_id
    )
    # Link manually for unit test (without DB session, SA relationships might not auto-populate unless we mock or set list)
    user.versions = [version]

    # 3. Convert
    public = UserPublic.from_entity(user)

    # 4. Verify
    assert public.id == user_id
    assert public.email == "test@example.com"
    assert public.full_name == "Test User"
    assert public.role == "viewer"
    assert public.department == "Engineering"
    assert public.is_active is True
    assert public.created_at == version.valid_from


def test_user_register_validation() -> None:
    # Valid
    valid_data = UserRegister(
        email="valid@test.com",
        password="securepassword",
        full_name="Valid Name",
        role="viewer"
    )
    assert valid_data.email == "valid@test.com"

    # Invalid email
    with pytest.raises(ValidationError):
        UserRegister(
            email="not-an-email",
            password="securepassword",
            full_name="Name",
            role="viewer"
        )

    # Short password
    with pytest.raises(ValidationError):
        UserRegister(
            email="valid@test.com",
            password="short",
            full_name="Name",
            role="viewer"
        )
