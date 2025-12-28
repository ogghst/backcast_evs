"""
Unit tests for configuration module.

Tests the Settings class and configuration loading.
"""

from app.core.config import settings


def test_settings_loads_from_environment() -> None:
    """Verify Settings class loads configuration from environment."""
    # Arrange: Environment variables are loaded via .env file
    # Act: Access settings instance
    # Assert: DATABASE_URL is populated correctly
    assert settings.DATABASE_URL is not None
    assert str(settings.DATABASE_URL).startswith("postgresql")


def test_settings_has_required_fields() -> None:
    """Verify Settings has all required configuration fields."""
    # Arrange & Act: Access settings
    # Assert: All required fields are present
    assert hasattr(settings, "DATABASE_URL")
    assert hasattr(settings, "SECRET_KEY")
    assert hasattr(settings, "PROJECT_NAME")
    assert hasattr(settings, "API_V1_STR")


def test_settings_default_values() -> None:
    """Verify Settings has correct default values."""
    # Arrange & Act: Access settings
    # Assert: Default values are correct
    assert settings.PROJECT_NAME == "Backcast EVS"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PORT == 8020
    assert settings.LOG_LEVEL == "INFO"
