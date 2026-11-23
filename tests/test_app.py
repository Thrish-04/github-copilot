from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    try:
        yield TestClient(app)
    finally:
        activities.clear()
        activities.update(original_activities)


def test_get_activities(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant(client):
    # Arrange
    email = "student@mergington.edu"
    endpoint = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_is_rejected(client):
    # Arrange
    email = "michael@mergington.edu"
    endpoint = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_unregister_removes_participant(client):
    # Arrange
    email = "michael@mergington.edu"
    endpoint = "/activities/Chess%20Club/unregister"

    # Act
    response = client.delete(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_signup_unknown_activity_returns_not_found(client):
    # Arrange
    endpoint = "/activities/Unknown/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unknown_activity_returns_not_found(client):
    # Arrange
    endpoint = "/activities/Unknown/unregister"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unknown_participant_returns_not_found(client):
    # Arrange
    endpoint = "/activities/Chess%20Club/unregister"
    email = "unknown@mergington.edu"

    # Act
    response = client.delete(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"
