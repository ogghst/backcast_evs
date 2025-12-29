from datetime import UTC, datetime

# We will mock the User entity since we can't easily instantiate the full SqlAlchemy model with versions without DB
# Or we can use a simple class that mimics the structure if we want to avoid complex Mocks
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.models.schemas.user import UserPublic


class TestUserPublicSchema:
    def test_from_entity_creates_valid_schema(self):
        # Arrange
        user_id = uuid4()
        email = "test@example.com"
        full_name = "Test User"
        department = "Engineering"
        role = "admin"
        is_active = True
        valid_from = datetime.now(UTC)

        # Mock User and UserVersion
        mock_version = MagicMock()
        mock_version.full_name = full_name
        mock_version.department = department
        mock_version.role = role
        mock_version.is_active = is_active
        mock_version.valid_from = valid_from

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.email = email
        mock_user.versions = [mock_version]

        # Act
        user_public = UserPublic.from_entity(mock_user)

        # Assert
        assert user_public.id == user_id
        assert user_public.email == email
        assert user_public.full_name == full_name
        assert user_public.department == department
        assert user_public.role == role
        assert user_public.is_active == is_active
        assert user_public.created_at == valid_from

    def test_from_entity_raises_value_error_if_no_versions(self):
        # Arrange
        mock_user = MagicMock()
        mock_user.versions = []

        # Act & Assert
        with pytest.raises(ValueError, match="User has no versions"):
            UserPublic.from_entity(mock_user)
