
from datetime import date
from pathlib import Path
import sys

import pytest

# Let the tests import the application and models from the server folder.
SERVER_DIR = Path(__file__).resolve().parents[1] / "server"
sys.path.insert(0, str(SERVER_DIR))

from app import app
from models import db


@pytest.fixture()
def client():
    """Give each test a clean, temporary database."""
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()


def create_sample_workout(client):
    """Create a workout that can be used by other tests."""
    response = client.post(
        "/workouts",
        json={
            "date": str(date.today()),
            "duration_minutes": 40,
            "notes": "Test workout session",
        },
    )

    assert response.status_code == 201
    return response.get_json()


def create_sample_exercise(client):
    """Create an exercise that can be used by other tests."""
    response = client.post(
        "/exercises",
        json={
            "name": "Lunge",
            "category": "Strength",
            "equipment_needed": False,
        },
    )

    assert response.status_code == 201
    return response.get_json()


def test_home_page_confirms_api_is_running(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Workout Tracker API is running"


def test_workout_can_be_created_viewed_and_deleted(client):
    workout = create_sample_workout(client)
    workout_id = workout["id"]

    assert client.get("/workouts").status_code == 200
    assert client.get(f"/workouts/{workout_id}").status_code == 200
    assert client.delete(f"/workouts/{workout_id}").status_code == 200

    # The deleted workout should no longer be available.
    assert client.get(f"/workouts/{workout_id}").status_code == 404


def test_exercise_can_be_created_viewed_and_deleted(client):
    exercise = create_sample_exercise(client)
    exercise_id = exercise["id"]

    assert client.get("/exercises").status_code == 200
    assert client.get(f"/exercises/{exercise_id}").status_code == 200
    assert client.delete(f"/exercises/{exercise_id}").status_code == 200

    # The deleted exercise should no longer be available.
    assert client.get(f"/exercises/{exercise_id}").status_code == 404


def test_missing_workouts_and_exercises_return_404(client):
    assert client.get("/workouts/999").status_code == 404
    assert client.get("/exercises/999").status_code == 404
    assert client.delete("/workouts/999").status_code == 404
    assert client.delete("/exercises/999").status_code == 404


def test_exercise_name_cannot_be_blank(client):
    response = client.post(
        "/exercises",
        json={
            "name": "   ",
            "category": "Strength",
            "equipment_needed": False,
        },
    )

    assert response.status_code == 400


def test_workout_duration_must_be_greater_than_zero(client):
    response = client.post(
        "/workouts",
        json={
            "date": str(date.today()),
            "duration_minutes": 0,
            "notes": "Invalid workout",
        },
    )

    assert response.status_code == 400


def test_exercise_can_be_added_to_a_workout(client):
    workout = create_sample_workout(client)
    exercise = create_sample_exercise(client)

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"reps": 10, "sets": 3},
    )

    assert response.status_code == 201
    assert response.get_json()["reps"] == 10
    assert response.get_json()["sets"] == 3


def test_workout_exercise_needs_at_least_one_measurement(client):
    workout = create_sample_workout(client)
    exercise = create_sample_exercise(client)

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={},
    )

    assert response.status_code == 400
