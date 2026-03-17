"""Pytest tests for the Mergington High School API.

This suite uses the Arrange-Act-Assert (AAA) pattern and resets the in-memory
`activities` state before each test to ensure isolation.
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities before each test."""
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))

    yield

    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_all_activities():
    # Arrange (state reset by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_removes_email():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": participant_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "notfound@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": missing_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
