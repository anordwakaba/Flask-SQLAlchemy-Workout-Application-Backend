
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Workout, Exercise, WorkoutExercise
from schemas import WorkoutSchema, ExerciseSchema, WorkoutExerciseSchema


# Create the Flask application and connect it to our database.
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Flask-Migrate helps us update the database when our models change.
migrate = Migrate(app, db)


# These schemas check incoming data and turn database records into JSON.
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()


# Return validation errors as clear messages instead of a server error.
@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"errors": error.messages}), 400


# Return a helpful response if the database rejects some data.
@app.errorhandler(IntegrityError)
def handle_database_error(error):
    db.session.rollback()
    return jsonify({
        "error": "The data could not be saved. Check for duplicate or invalid values."
    }), 400


@app.get("/")
def home():
    """Let us know that the API is running."""
    return jsonify({"message": "Workout Tracker API is running"}), 200


# -------------------- WORKOUT ROUTES --------------------

@app.get("/workouts")
def get_workouts():
    """Return all workouts, starting with the oldest database ID."""
    workouts = Workout.query.order_by(Workout.id).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    """Find and return one workout."""
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    return jsonify(workout_schema.dump(workout)), 200


@app.post("/workouts")
def create_workout():
    """Create a workout using the details sent in the request."""
    data = workout_schema.load(request.get_json(silent=True) or {})

    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()

    return jsonify(workout_schema.dump(workout)), 201


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    """Delete a workout if it exists."""
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    db.session.delete(workout)
    db.session.commit()

    return jsonify({"message": "Workout deleted successfully"}), 200


# -------------------- EXERCISE ROUTES --------------------

@app.get("/exercises")
def get_exercises():
    """Return all exercises saved in the database."""
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    """Find and return one exercise."""
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    return jsonify(exercise_schema.dump(exercise)), 200


@app.post("/exercises")
def create_exercise():
    """Save a new exercise after checking the submitted data."""
    data = exercise_schema.load(request.get_json(silent=True) or {})

    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()

    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    """Delete an exercise if it exists."""
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    db.session.delete(exercise)
    db.session.commit()

    return jsonify({"message": "Exercise deleted successfully"}), 200


# -------------------- WORKOUT-EXERCISE ROUTE --------------------

@app.post(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises"
)
def add_exercise_to_workout(workout_id, exercise_id):
    """Connect an exercise to a workout and save its training details."""

    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)

    # Both records must exist before we connect them.
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    data = workout_exercise_schema.load(request.get_json(silent=True) or {})

    workout_exercise = WorkoutExercise(
        workout=workout,
        exercise=exercise,
        **data
    )

    db.session.add(workout_exercise)
    db.session.commit()

    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


if __name__ == "__main__":
    # Run the app on port 5555 when this file is started directly.
    app.run(port=5555, debug=True)
