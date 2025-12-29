from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


@dataclass
class CommandMetadata:
    """Metadata for version control commands."""

    command_type: str
    user_id: UUID
    timestamp: datetime
    description: str
    branch: str = "main"  # Default for non-branching entities


class VersionCommand[T](ABC):
    """
    Abstract base class for version control commands.
    Each command represents an atomic operation on an entity.
    """

    def __init__(self, metadata: CommandMetadata):
        self.metadata = metadata

    @abstractmethod
    async def execute(self, session: AsyncSession) -> T:
        """Execute the command and return the result."""
        pass

    @abstractmethod
    async def undo(self, session: AsyncSession) -> None:
        """Undo the command (if possible)."""
        pass

    def to_commit_message(self) -> str:
        """Generate commit message for this command."""
        return f"[{self.metadata.command_type}] {self.metadata.description}"
