from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.user_preference import UpdateUserPreferenceCommand
from app.core.versioning.commands import CommandMetadata
from app.models.domain.user import User
from app.models.domain.user_preference import UserPreference, UserPreferenceVersion
from app.repositories.user_preference import UserPreferenceRepository


class UserPreferenceService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserPreferenceRepository(session)

    async def get_my_preference(self, user: User) -> UserPreferenceVersion:
        """
        Get preference for a user. If not exists, create default.
        """
        pref = await self.repo.get_by_user_id(user.id)
        
        if not pref:
            # Create default preference (Initialization logic)
            # This is technical initialization, not necessarily a "Command" in business sense,
            # but for strictness we could use one. For now, simple init like in User creation.
            pref_id = UUID(int=uuid4().int)
            new_pref = UserPreference(id=pref_id, user_id=user.id)
            new_version = UserPreferenceVersion(
                head_id=pref_id,
                valid_from=date.today(),
                created_by_id=user.id,
                theme="light"
            )
            self.session.add(new_pref)
            self.session.add(new_version)
            await self.session.flush() # Ensure ID availability
            await self.session.commit()
            
            # Fetch again to ensure everything is loaded correctly via repo
            pref = await self.repo.get_by_user_id(user.id)
        
        if not pref or not pref.versions:
             # Should not happen after init
             raise ValueError("Preference versions not found")
             
        return pref.versions[0]

    async def update_my_preference(
        self, user: User, theme: str
    ) -> UserPreferenceVersion:
        """
        Update user preference using Command.
        """
        # Ensure existence first and get current version
        current_version = await self.get_my_preference(user)
        
        if current_version.theme == theme:
            return current_version

        metadata = CommandMetadata(
            command_type="UPDATE_USER_PREFERENCE",
            user_id=user.id,
            timestamp=datetime.now(UTC),
            description="Update Theme Preference",
        )
        
        command = UpdateUserPreferenceCommand(
            metadata=metadata,
            head_id=current_version.head_id,
            theme=theme
        )
        
        return await command.execute(self.session)
