from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_positive_duration"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        viewonly=True,
        back_populates="workouts",
    )

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise ValueError("duration_minutes must be a positive integer")
        return value


class Exercise(db.Model):
    __tablename__ = "exercises"
    __table_args__ = (
        db.CheckConstraint("length(name) > 0", name="ck_exercise_nonempty_name"),
        db.CheckConstraint("length(category) > 0", name="ck_exercise_nonempty_category"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        viewonly=True,
        back_populates="exercises",
    )

    @validates("name", "category")
    def validate_nonempty_text(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} must be a non-empty string")
        return value.strip()

    @validates("equipment_needed")
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be true or false")
        return value


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise_pair"),
        CheckConstraint("reps IS NULL OR reps >= 0", name="ck_workout_exercise_nonnegative_reps"),
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_workout_exercise_positive_sets"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 0",
            name="ck_workout_exercise_nonnegative_duration",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps")
    def validate_reps(self, key, value):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            raise ValueError("reps must be a non-negative integer")
        return value

    @validates("sets")
    def validate_sets(self, key, value):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value <= 0):
            raise ValueError("sets must be a positive integer")
        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        if value is not None and (
            not isinstance(value, int) or isinstance(value, bool) or value < 0
        ):
            raise ValueError("duration_seconds must be a non-negative integer")
        return value
