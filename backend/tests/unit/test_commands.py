from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select

from app.commands.user import CreateUserCommand, UpdateUserCommand
from app.core.versioning.commands import CommandMetadata
from app.models.domain.user import User, UserVersion


@pytest.mark.asyncio
async def test_create_and_update_user_command(db_session):
    # 1. Create User Command
    user_id = uuid4()
    metadata = CommandMetadata(
        command_type="CREATE",
        user_id=user_id,
        timestamp=datetime.now(UTC),
        description="Test Create",
    )

    create_cmd = CreateUserCommand(
        metadata=metadata,
        email=f"test_cmd_{user_id}@example.com",
        hashed_password="hashed_secret",
        full_name="Test Command User",
        role="viewer",
        id=user_id,
    )

    user = await create_cmd.execute(db_session)

    assert user.id == user_id
    assert len(user.versions) == 1
    v1 = user.versions[0]
    assert v1.full_name == "Test Command User"
    assert v1.valid_to is None
    assert v1.valid_to is None
    # UserVersion doesn't have 'version' number col (from BaseVersionMixin)

    # 2. Update User Command (Snapshot Pattern)
    update_metadata = CommandMetadata(
        command_type="UPDATE",
        user_id=user_id,
        timestamp=datetime.now(UTC),
        description="Test Update",
    )

    changes = {"full_name": "Updated Name", "department": "IT"}
    update_cmd = UpdateUserCommand(
        metadata=update_metadata, user_id=user_id, changes=changes
    )

    v2 = await update_cmd.execute(db_session)

    assert v2.full_name == "Updated Name"
    assert v2.department == "IT"
    assert v2.valid_to is None

    # Verify old version is closed
    stmt = select(UserVersion).where(
        UserVersion.head_id == user_id, UserVersion.valid_to.is_not(None)
    )
    result = await db_session.execute(stmt)
    closed_versions = result.scalars().all()
    assert len(closed_versions) == 1
    assert closed_versions[0].full_name == "Test Command User"
    assert closed_versions[0].valid_to == update_metadata.timestamp


@pytest.mark.asyncio
async def test_undo_create_user(db_session):
    user_id = uuid4()
    metadata = CommandMetadata(
        command_type="CREATE",
        user_id=user_id,
        timestamp=datetime.now(UTC),
        description="Test Undo Create",
    )

    create_cmd = CreateUserCommand(
        metadata=metadata,
        email=f"undo_{user_id}@example.com",
        hashed_password="hashed",
        full_name="Undo Me",
        role="viewer",
        id=user_id,
    )

    await create_cmd.execute(db_session)

    # Undo
    await create_cmd.undo(db_session)

    # Verify deleted
    stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None

    # Verify versions deleted (cascade)
    stmt = select(UserVersion).where(UserVersion.head_id == user_id)
    result = await db_session.execute(stmt)
    assert len(result.scalars().all()) == 0


@pytest.mark.asyncio
async def test_undo_update_user(db_session):
    # 1. Create initial user
    user_id = uuid4()
    init_cmd = CreateUserCommand(
        metadata=CommandMetadata("CREATE", user_id, datetime.now(UTC), "Init"),
        email=f"update_undo_{user_id}@example.com",
        hashed_password="pw",
        full_name="Original Name",
        role="viewer",
        id=user_id,
    )
    user = await init_cmd.execute(db_session)
    v1_created_at = user.versions[0].valid_from

    # 2. Update user
    change_time = datetime.now(UTC)
    update_cmd = UpdateUserCommand(
        metadata=CommandMetadata("UPDATE", user_id, change_time, "Update"),
        user_id=user_id,
        changes={"full_name": "New Name"},
    )
    v2 = await update_cmd.execute(db_session)

    assert v2.full_name == "New Name"
    # Verify v1 closed
    await db_session.refresh(user)  # Refresh head, but versions?
    # Better query versions directly
    stmt = select(UserVersion).where(
        UserVersion.head_id == user_id, UserVersion.valid_to.is_not(None)
    )
    v1_closed = (await db_session.execute(stmt)).scalar_one()
    assert v1_closed.full_name == "Original Name"
    assert v1_closed.valid_to == change_time

    # 3. Undo Update
    await update_cmd.undo(db_session)

    # Verify v2 deleted
    stmt = select(UserVersion).where(
        UserVersion.head_id == user_id, UserVersion.valid_from == change_time
    )
    assert (await db_session.execute(stmt)).scalar_one_or_none() is None

    # Verify v1 reopened
    stmt = select(UserVersion).where(
        UserVersion.head_id == user_id, UserVersion.valid_from == v1_created_at
    )
    v1_reopened = (await db_session.execute(stmt)).scalar_one()
    assert v1_reopened.valid_to is None
    assert v1_reopened.full_name == "Original Name"
