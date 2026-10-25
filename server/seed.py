
from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise


with app.app_context():
    # Create any tables that do not exist yet.
    db.create_all()

    # Add a few sample exercises.
    squat = Exercise(
        name="Squat",
        category="Strength",
        equipment_needed=False
    )

    jump_rope = Exercise(
        name="Jump Rope",
        category="Cardio",
        equipment_needed=True
    )

    plank = Exercise(
        name="Plank",
        category="Core",
        equipment_needed=False
    )

    # Add two sample workout sessions.
    strength_workout = Workout(
        date=date(2026, 10, 25),
        duration_minutes=45,
        notes="A full-body strength session"
    )

    cardio_workout = Workout(
        date=date(2026, 10, 24),
        duration_minutes=30,
        notes="A cardio and core session"
    )

    db.session.add_all([
        squat,
        jump_rope,
        plank,
        strength_workout,
        cardio_workout
    ])

    # Save these records first so the database assigns their IDs.
    db.session.flush()

    # Connect exercises to the workouts and record the training details.
    db.session.add_all([
        WorkoutExercise(
            workout=strength_workout,
            exercise=squat,
            reps=12,
            sets=3
        ),
        WorkoutExercise(
            workout=strength_workout,
            exercise=plank,
            duration_seconds=45,
            sets=3
        ),
        WorkoutExercise(
            workout=cardio_workout,
            exercise=jump_rope,
            duration_seconds=60,
            sets=5
        )
    ])

    db.session.commit()

    print("Sample workouts and exercises have been added successfully.")
