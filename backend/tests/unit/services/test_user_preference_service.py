
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession



from app.models.schemas.user import UserRegister
from app.models.schemas.preference import UserPreferenceCreate
from app.services.user import UserService
from app.services.user_preference import UserPreferenceService

# assuming app/services/user_preference.py

class TestUserPreferenceService:
    """Test UserPreferenceService."""

    @pytest.mark.asyncio
    async def test_create_preference_success(self, db_session: AsyncSession) -> None:
        """RED: Test creating preference for a user."""
        user_service = UserService(db_session)
        pref_service = UserPreferenceService(db_session)

        # 1. Create a user first (to satisfy FK if needed, or just conceptual)
        user_id = uuid4()
        user_in = UserRegister(
            email="pref_test@example.com",
            password="secret_password",
            full_name="Pref User",
            role="user",
            department="Engineering",
            is_active=True,
        )
        user = await user_service.create_user(user_in, actor_id=uuid4())

        # 2. Create preference
        # Note: If FK is to 'users.id', we must pass user.id (version ID).
        # If FK is to 'users.user_id' (logical), we pass user.user_id (root), but DB FK will fail.
        # Let's try passing the version ID 'user.id' which definitely exists in 'users' table.
        # But wait, UserPreference.user_id field name implies Root ID?
        # The model says `ForeignKey("users.id")`.

        pref = await pref_service.create_preference(
            user_id=user.id, # Linking to specific version for now to satisfy DB
            pref_in=UserPreferenceCreate(theme="dark")
        )

        assert pref is not None
        assert pref.theme == "dark"
        assert pref.user_id == user.id

        fetched = await pref_service.get_by_user_id(user.id)
        assert fetched is not None
        assert fetched.theme == "dark"
