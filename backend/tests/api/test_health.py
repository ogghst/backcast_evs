"""
API tests for health check endpoint.

Tests basic API functionality and response format.
"""

from fastapi.testclient import TestClient


def test_health_endpoint_returns_200(client: TestClient) -> None:
    """Verify root endpoint returns 200 OK."""
    # Arrange: Test client fixture
    # Act: GET /
    response = client.get("/")

    # Assert: Status code is 200 and response contains expected data
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Backcast EVS API"}


def test_health_endpoint_response_structure(client: TestClient) -> None:
    """Verify root endpoint returns correct JSON structure."""
    # Arrange: Test client
    # Act: GET /
    response = client.get("/")
    data = response.json()

    # Assert: Response has expected structure
    assert "message" in data
    assert isinstance(data["message"], str)
