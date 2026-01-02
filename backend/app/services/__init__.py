"""Services package."""

from app.services.department import DepartmentService
from app.services.user import UserService
from app.services.user_preference import UserPreferenceService

__all__ = ["UserService", "DepartmentService", "UserPreferenceService"]
