import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

@pytest.fixture(autouse=True)
def client():
    # keep a copy of the original state so each test starts clean
    original = copy.deepcopy(activities)
    with TestClient(app) as c:
        yield c
    activities.clear()
    activities.update(original)

def test_get_activities_returns_initial_data(client):
    # Arrange – nothing to set up, use the in‑memory dict directly
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert "Debate Team" in data

def test_signup_and_duplicate_prevention(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act – first signup (email is a query parameter in the current API)
    resp1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp1.status_code == 200, resp1.text
    assert "signed up" in resp1.json().get("message", "").lower()

    # Act – duplicate signup
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp2.status_code == 400, resp2.text

def test_remove_participant_success(client):
    # Arrange – add someone first
    email = "removeme@mergington.edu"
    activities["Debate Team"]["participants"].append(email)
    # Act
    resp = client.delete("/activities/Debate Team/participants", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email not in activities["Debate Team"]["participants"]

def test_remove_participant_not_found(client):
    # Arrange
    email = "ghost@mergington.edu"
    # Act
    resp = client.delete("/activities/Debate Team/participants", params={"email": email})
    # Assert
    assert resp.status_code == 400
