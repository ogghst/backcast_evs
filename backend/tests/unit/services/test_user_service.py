"""Unit tests for UserService.

Following TDD RED-GREEN-REFACTOR cycle.
"""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.user import User
from app.services.user import UserService


class TestUserServiceGetUser:
    """Test UserService.get_user() method."""

    @pytest.mark.asyncio
    async def test_get_user_returns_none_when_not_found(
        self, db_session: AsyncSession
    ) -> None:
        """RED: Test that get_user returns None for non-existent user."""
        # Arrange
        service = UserService(db_session)
        non_existent_id = uuid4()

        # Act
        result = await service.get_user(non_existent_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_returns_user_when_found(
        self, db_session: AsyncSession
    ) -> None:
        """RED: Test that get_user returns User when found."""
        # Arrange
        service = UserService(db_session)

        # Create a user directly in DB for testing
        user = User(
            user_id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pw",
            full_name="Test User",
            role="viewer",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Act
        result = await service.get_user(user.id)

        # Assert
        assert result is not None
        assert result.id == user.id
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"


class TestUserServiceCreate:
    """Test UserService.create_user() method."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession) -> None:
        """RED: Test successfully creating a user."""
        service = UserService(db_session)
        user_id = uuid4()
        user_data = {
            "user_id": user_id,
            "email": "newuser@example.com",
            "hashed_password": "hashed_secret",
            "full_name": "New User",
            "role": "editor",
            "department": "Engineering",
            "is_active": True,
        }

        # Act
        created_user = await service.create_user(user_data, actor_id=uuid4())

        # Assert
        assert created_user is not None
        assert created_user.email == "newuser@example.com"
        assert created_user.user_id == user_id
        # Verify persistence
        fetched = await service.get_user(created_user.id)
        assert fetched is not None
        assert fetched.email == "newuser@example.com"


class TestUserServiceUpdate:
    """Test UserService.update_user() method."""

    @pytest.mark.asyncio
    async def test_update_user_versions(self, db_session: AsyncSession) -> None:
        """RED: Test updating a user creates a new version."""
        service = UserService(db_session)
        user_id = uuid4()
        user_data = {
            "user_id": user_id,
            "email": "update_test@example.com",
            # Add other required fields if necessary for valid model
            "hashed_password": "pwd",
            "full_name": "Original Name",
            "role": "user",
            "department": "Sales",
            "is_active": True,
        }
        # Create initial version
        v1 = await service.create_user(user_data, actor_id=uuid4())

        # Act
        update_data = {"full_name": "Updated Name"}
        v2 = await service.update_user(user_id, update_data, actor_id=uuid4())

        # Assert
        assert v2 is not None
        assert v2.id != v1.id  # Different version IDs
        assert v2.user_id == user_id  # Same user ID
        assert v2.full_name == "Updated Name"

        # Verify persistence of new version
        fetched = await service.get_user(v2.id)
        assert fetched is not None
        assert fetched.full_name == "Updated Name"


class TestUserServiceDelete:
    """Test UserService.delete_user() method."""

    @pytest.mark.asyncio
    async def test_delete_user_soft_deletes(self, db_session: AsyncSession) -> None:
        """RED: Test deleting a user soft-deletes the current version."""
        service = UserService(db_session)
        user_id = uuid4()
        user_data = {
            "user_id": user_id,
            "email": "delete_test@example.com",
            # Add other required fields if necessary for valid model
            "hashed_password": "pwd",
            "full_name": "To Be Deleted",
            "role": "user",
            "department": "Engineering",
            "is_active": True,
        }
        # Create user
        v1 = await service.create_user(user_data, actor_id=uuid4())

        # Act
        await service.delete_user(user_id, actor_id=uuid4())

        # Assert
        # 1. Fetching by ID should show it as deleted (if I check is_deleted)
        # OR fetch invalidates it?
        deleted_user = await service.get_user(v1.id)
        assert deleted_user is not None
        assert deleted_user.is_deleted is True
        assert deleted_user.deleted_at is not None

        # 2. get_by_email should return None
        result = await service.get_by_email("delete_test@example.com")
        assert result is None
