from datetime import date
from pathlib import Path
import sys

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1] / "server"
sys.path.insert(0, str(SERVER_DIR))

from app import app
from models import db


@pytest.fixture()
def client():
    # Use an isolated in-memory database for every test.
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


def make_workout(client):
    response = client.post("/workouts", json={
        "date": str(date.today()),
        "duration_minutes": 40,
        "notes": "Test session",
    })
    assert response.status_code == 201
    return response.get_json()


def make_exercise(client):
    response = client.post("/exercises", json={
        "name": "Lunge",
        "category": "Strength",
        "equipment_needed": False,
    })
    assert response.status_code == 201
    return response.get_json()


def test_home_route(client):
    assert client.get("/").status_code == 200


def test_create_list_show_and_delete_workout(client):
    workout = make_workout(client)
    workout_id = workout["id"]
    assert client.get("/workouts").status_code == 200
    assert client.get(f"/workouts/{workout_id}").status_code == 200
    assert client.delete(f"/workouts/{workout_id}").status_code == 200
    assert client.get(f"/workouts/{workout_id}").status_code == 404


def test_create_list_show_and_delete_exercise(client):
    exercise = make_exercise(client)
    exercise_id = exercise["id"]
    assert client.get("/exercises").status_code == 200
    assert client.get(f"/exercises/{exercise_id}").status_code == 200
    assert client.delete(f"/exercises/{exercise_id}").status_code == 200
    assert client.get(f"/exercises/{exercise_id}").status_code == 404


def test_missing_resources_return_404(client):
    assert client.get("/workouts/999").status_code == 404
    assert client.get("/exercises/999").status_code == 404
    assert client.delete("/workouts/999").status_code == 404
    assert client.delete("/exercises/999").status_code == 404


def test_blank_exercise_name_is_rejected(client):
    response = client.post("/exercises", json={
        "name": "   ",
        "category": "Strength",
        "equipment_needed": False,
    })
    assert response.status_code == 400


def test_workout_requires_positive_duration(client):
    response = client.post("/workouts", json={
        "date": str(date.today()),
        "duration_minutes": 0,
        "notes": "Invalid workout",
    })
    assert response.status_code == 400


def test_add_exercise_to_workout(client):
    workout = make_workout(client)
    exercise = make_exercise(client)
    response = client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={"reps": 10, "sets": 3},
    )
    assert response.status_code == 201
    assert response.get_json()["reps"] == 10
    assert response.get_json()["sets"] == 3


def test_join_requires_at_least_one_metric(client):
    workout = make_workout(client)
    exercise = make_exercise(client)
    response = client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={},
    )
    assert response.status_code == 400
