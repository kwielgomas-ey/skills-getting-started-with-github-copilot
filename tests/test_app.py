from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # deep copy current activities state and restore after each test
    original = {k: {"description": v["description"],
                    "schedule": v["schedule"],
                    "max_participants": v["max_participants"],
                    "participants": list(v["participants"])} for k, v in activities.items()}
    yield
    activities.clear()
    for k, v in original.items():
        activities[k] = v


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Soccer Team" in data
    assert isinstance(data["Soccer Team"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Gym Class"
    email = "testuser@example.com"

    # ensure clean start
    assert email not in activities[activity]["participants"]

    # sign up
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup should fail
    res2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert res2.status_code == 400

    # unregister
    res3 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert res3.status_code == 200
    assert email not in activities[activity]["participants"]

    # unregistering again should fail
    res4 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert res4.status_code == 400


def test_signup_nonexistent_activity():
    res = client.post("/activities/NoSuchActivity/signup?email=a@b.com")
    assert res.status_code == 404
