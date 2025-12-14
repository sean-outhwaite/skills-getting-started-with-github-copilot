import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307)
    assert resp.headers["location"].endswith("/static/index.html")


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Ensure known activity exists
    assert "Basketball" in data


def test_signup_success_then_unregister_success():
    activity = "Science Club"
    email = "newstudent@mergington.edu"

    # Ensure clean state
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_duplicate_error():
    activity = "Drama Club"
    existing_email = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup", params={"email": existing_email})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_not_signed_up_error():
    activity = "Basketball"
    email = "not-enrolled@mergington.edu"
    # Ensure email not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"] == "Student not signed up for this activity"
