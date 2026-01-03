"""Data seeding module for initializing database with default entities.

Provides flexible JSON-based seeding that uses Pydantic schemas for validation.
"""

import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas.department import DepartmentCreate
from app.models.schemas.user import UserRegister

logger = logging.getLogger(__name__)


class DataSeeder:
    """Handles database seeding from JSON files."""

    def __init__(self, seed_dir: Path | None = None) -> None:
        """Initialize DataSeeder with seed directory.

        Args:
            seed_dir: Path to directory containing seed JSON files.
                     Defaults to backend/seed relative to project root.
        """
        if seed_dir is None:
            # Default to backend/seed directory
            backend_dir = Path(__file__).parent.parent.parent
            seed_dir = backend_dir / "seed"

        self.seed_dir = seed_dir
        logger.info(f"DataSeeder initialized with seed directory: {self.seed_dir}")

    def load_seed_file(self, filename: str) -> list[dict[str, Any]]:
        """Load and parse a JSON seed file.

        Args:
            filename: Name of the JSON file in seed directory

        Returns:
            List of dictionaries from JSON file

        Raises:
            FileNotFoundError: If seed file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        file_path = self.seed_dir / filename
        if not file_path.exists():
            logger.warning(f"Seed file not found: {file_path}")
            return []

        try:
            with open(file_path) as f:
                data = json.load(f)
                if not isinstance(data, list):
                    logger.error(f"Seed file {filename} must contain a JSON array")
                    return []
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in seed file {filename}: {e}")
            return []

    async def seed_users(self, session: AsyncSession) -> None:
        """Seed users from users.json file.

        Args:
            session: Database session
        """
        from app.services.user import UserService

        logger.info("Starting user seeding...")
        user_data = self.load_seed_file("users.json")

        if not user_data:
            logger.info("No user seed data found or file is empty")
            return

        user_service = UserService(session)
        created_count = 0
        skipped_count = 0

        for idx, user_dict in enumerate(user_data):
            try:
                # Validate with Pydantic schema
                user_in = UserRegister(**user_dict)

                # Check if user already exists
                existing_user = await user_service.get_by_email(user_in.email)
                if existing_user:
                    logger.debug(f"User {user_in.email} already exists, skipping")
                    skipped_count += 1
                    continue

                # Create user (actor_id can be None for seed operation)
                from uuid import uuid4

                actor_id = uuid4()  # System actor for seeding
                await user_service.create_user(user_in, actor_id)
                created_count += 1
                logger.info(f"Created user: {user_in.email}")

            except Exception as e:
                logger.error(f"Failed to seed user at index {idx}: {e}")
                continue

        logger.info(
            f"User seeding complete: {created_count} created, {skipped_count} skipped"
        )

    async def seed_departments(self, session: AsyncSession) -> None:
        """Seed departments from departments.json file.

        Args:
            session: Database session
        """
        from app.services.department import DepartmentService

        logger.info("Starting department seeding...")
        dept_data = self.load_seed_file("departments.json")

        if not dept_data:
            logger.info("No department seed data found or file is empty")
            return

        dept_service = DepartmentService(session)
        created_count = 0
        skipped_count = 0

        for idx, dept_dict in enumerate(dept_data):
            try:
                # Validate with Pydantic schema
                dept_in = DepartmentCreate(**dept_dict)

                # Check if department already exists
                existing_dept = await dept_service.get_by_code(dept_in.code)
                if existing_dept:
                    logger.debug(f"Department {dept_in.code} already exists, skipping")
                    skipped_count += 1
                    continue

                # Create department (actor_id can be None for seed operation)
                from uuid import uuid4

                actor_id = uuid4()  # System actor for seeding
                await dept_service.create_department(dept_in, actor_id)
                created_count += 1
                logger.info(f"Created department: {dept_in.code}")

            except Exception as e:
                logger.error(f"Failed to seed department at index {idx}: {e}")
                continue

        logger.info(
            f"Department seeding complete: {created_count} created, "
            f"{skipped_count} skipped"
        )

    async def seed_all(self, session: AsyncSession) -> None:
        """Execute all seeding operations in the correct order.

        Departments are seeded before users to satisfy potential foreign key
        constraints.

        Args:
            session: Database session
        """
        logger.info("=== Starting database seeding ===")

        try:
            # Seed departments first (may be referenced by users)
            await self.seed_departments(session)

            # Then seed users
            await self.seed_users(session)

            # Commit all changes
            await session.commit()
            logger.info("=== Database seeding completed successfully ===")

        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            await session.rollback()
            raise
