#!/usr/bin/env python3
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise


with app.app_context():
    # Clear existing records so running this file repeatedly won't duplicate data.
    db.drop_all()
    db.create_all()

    strength = Exercise(name="Squat", category="Strength", equipment_needed=False)
    cardio = Exercise(name="Jump Rope", category="Cardio", equipment_needed=True)
    core = Exercise(name="Plank", category="Core", equipment_needed=False)

    workout_one = Workout(
        date=date(2026, 10, 25),
        duration_minutes=45,
        notes="Full body strength session",
    )
    workout_two = Workout(
        date=date(2026, 10, 24),
        duration_minutes=30,
        notes="Cardio and core",
    )

    db.session.add_all([strength, cardio, core, workout_one, workout_two])
    db.session.flush()

    db.session.add_all([
        WorkoutExercise(workout=workout_one, exercise=strength, reps=12, sets=3),
        WorkoutExercise(workout=workout_one, exercise=core, duration_seconds=45, sets=3),
        WorkoutExercise(workout=workout_two, exercise=cardio, duration_seconds=60, sets=5),
    ])
    db.session.commit()
    print("Database seeded successfully.")
