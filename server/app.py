from datetime import date

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    ExerciseSchema,
    WorkoutSchema,
    WorkoutExerciseSchema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify({"errors": error.messages}), 400


@app.get("/")
def index():
    return jsonify({"message": "Workout Tracker API is running"}), 200


@app.get("/workouts")
def get_workouts():
    return jsonify(workouts_schema.dump(Workout.query.order_by(Workout.id).all())), 200


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify(workout_schema.dump(workout)), 200


@app.post("/workouts")
def create_workout():
    data = workout_schema.load(request.get_json(silent=True) or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return jsonify(workout_schema.dump(workout)), 201


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted"}), 200


@app.get("/exercises")
def get_exercises():
    return jsonify(exercises_schema.dump(Exercise.query.order_by(Exercise.id).all())), 200


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404
    return jsonify(exercise_schema.dump(exercise)), 200


@app.post("/exercises")
def create_exercise():
    data = exercise_schema.load(request.get_json(silent=True) or {})
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": "Exercise deleted"}), 200


@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)
    if workout is None:
        return jsonify({"error": "Workout not found"}), 404
    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    data = workout_exercise_schema.load(request.get_json(silent=True) or {})
    association = WorkoutExercise(
        workout=workout,
        exercise=exercise,
        **data,
    )
    db.session.add(association)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "This exercise is already attached to this workout, or the data violates a database constraint"}), 400
    return jsonify(workout_exercise_schema.dump(association)), 201


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    return jsonify({"error": "Database constraint failed; check for duplicate or invalid values"}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
