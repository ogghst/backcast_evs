"""Service for branchable entities (EVCS Core).

Extends the command pattern to provide business-level operations for
entities implementing BranchableProtocol (e.g. Projects).
"""

from typing import Any, cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.versioning.commands import (
    CreateBranchCommand,
    CreateVersionCommand,
    MergeBranchCommand,
    RevertCommand,
    UpdateCommand,
)


class BranchableService[TBranchable]:
    """Service for managing branchable entities."""

    def __init__(self, entity_class: type[TBranchable], session: AsyncSession) -> None:
        self.entity_class = entity_class
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> TBranchable | None:
        """Get specific version by its version ID (primary key)."""
        return await self.session.get(self.entity_class, entity_id)

    async def get_current(
        self, root_id: UUID, branch: str = "main"
    ) -> TBranchable | None:
        """Get the current active version for a root entity on a specific branch."""
        """Get the current active version for a root entity on a specific branch."""
        # We need _root_field_name logic here or use a standard mixin field if available.
        # But protocols don't enforce field names for root relationship (except conceptually).
        # We can inspect the entity class or use the command which has the logic.
        # But commands assume we have root_id.
        # Let's assume standard field naming or introspection.
        # Actually, if TBranchable is used, we know it has mixin fields?
        # Protocol defines 'branch'. Mixin defines 'root_id'? No, Mixin varies.
        # User/Dept/Project use 'user_id', 'department_id', 'project_id' as root.
        # We should probably adapt _root_field_name logic or require it.

        # Helper to get root field name
        class_name = self.entity_class.__name__.lower()
        if class_name.endswith("version"):
            class_name = class_name[:-7]
        root_field = f"{class_name}_id"

        stmt = (
            select(self.entity_class)
            .where(
                getattr(self.entity_class, root_field) == root_id,
                cast(Any, self.entity_class).branch == branch,
                cast(Any, self.entity_class).valid_time.op("@>")(
                    func.current_timestamp()
                ),
                cast(Any, self.entity_class).deleted_at.is_(None),
            )
            .order_by(cast(Any, self.entity_class).valid_time.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_root(
        self, root_id: UUID, branch: str = "main", **data: Any
    ) -> TBranchable:
        """Create the initial version of an entity (new root)."""
        # Ensure root_id field is in data
        class_name = self.entity_class.__name__.lower()
        if class_name.endswith("version"):
            class_name = class_name[:-7]
        root_field = f"{class_name}_id"

        data[root_field] = root_id

        cmd = CreateVersionCommand(
            entity_class=self.entity_class, root_id=root_id, branch=branch, **data
        )
        return await cmd.execute(self.session)

    async def update(self, root_id: UUID, branch: str, **updates: Any) -> TBranchable:
        """Update entity on a specific branch (creates new version)."""
        cmd = UpdateCommand(
            entity_class=self.entity_class,
            root_id=root_id,
            branch=branch,
            updates=updates,
        )
        return await cmd.execute(self.session)

    async def create_branch(
        self, root_id: UUID, new_branch: str, from_branch: str = "main"
    ) -> TBranchable:
        """Create a new branch from an existing branch."""
        cmd = CreateBranchCommand(
            entity_class=self.entity_class,
            root_id=root_id,
            new_branch=new_branch,
            from_branch=from_branch,
        )
        return await cmd.execute(self.session)

    async def merge_branch(
        self, root_id: UUID, source_branch: str, target_branch: str
    ) -> TBranchable:
        """Merge source branch into target branch."""
        cmd = MergeBranchCommand(
            entity_class=self.entity_class,
            root_id=root_id,
            source_branch=source_branch,
            target_branch=target_branch,
        )
        return await cmd.execute(self.session)

    async def revert(
        self, root_id: UUID, branch: str, to_version_id: UUID | None = None
    ) -> TBranchable:
        """Revert branch to a previous state."""
        cmd = RevertCommand(
            entity_class=self.entity_class,
            root_id=root_id,
            branch=branch,
            to_version_id=to_version_id,
        )
        return await cmd.execute(self.session)
