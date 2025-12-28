from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.security import get_password_hash
from app.models.domain.user import User, UserVersion


class UserRepository:
    async def create_user_with_version(
        self,
        session: AsyncSession,
        email: str,
        password: str,
        full_name: str,
        department: str | None = None,
        role: str = "viewer",
        branch: str = "main",
    ) -> User:
        """
        Create a new user with an initial version snapshot.
        """
        # Create head entity (identity)
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
        )
        session.add(user)
        await session.flush()  # Generate ID

        # Create initial version (state)
        version = UserVersion(
            head_id=user.id,
            branch=branch,
            full_name=full_name,
            role=role,
            department=department,
            is_active=True,
            valid_from=datetime.now(UTC),
            created_by_id=user.id,  # Self-reference for initial creation
        )
        session.add(version)

        # Refresh user to populate versions relationship
        await session.flush()
        # We use selectinload to ensure versions are loaded
        stmt = (
            select(User).options(selectinload(User.versions)).where(User.id == user.id)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one()

    async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
        """
        Get user by email, including latest version data.
        """
        stmt = (
            select(User)
            .options(joinedload(User.versions))  # Optimize if we need version data
            .where(User.email == email)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, session: AsyncSession, user_id: UUID) -> User | None:
        """
        Get user by ID.
        """
        stmt = (
            select(User).options(selectinload(User.versions)).where(User.id == user_id)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()
