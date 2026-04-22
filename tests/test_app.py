import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert "Swimming Club" in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_valid_activity():
    """Test POST /activities/{name}/signup with valid activity"""
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up newstudent@mergington.edu for Chess Club" == data["message"]


def test_signup_invalid_activity():
    """Test POST /activities/{name}/signup with non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]


def test_root_redirect():
    """Test GET / redirects to static index"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]


def test_signup_duplicate_email():
    """Test that duplicate signups are allowed (current app behavior)"""
    email = "duplicate@mergington.edu"
    # First signup
    response1 = client.post(f"/activities/Programming Class/signup?email={email}")
    assert response1.status_code == 200

    # Second signup with same email
    response2 = client.post(f"/activities/Programming Class/signup?email={email}")
    assert response2.status_code == 200  # Currently allowed


def test_signup_over_capacity():
    """Test signup when activity is at max capacity (current app behavior allows it)"""
    # Swimming Club has max_participants: 15, participants: []
    email = "capacity@mergington.edu"
    response = client.post(f"/activities/Swimming Club/signup?email={email}")
    assert response.status_code == 200  # Currently no capacity check