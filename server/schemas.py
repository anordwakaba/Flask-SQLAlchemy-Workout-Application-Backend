
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validates,
    validates_schema,
)


class WorkoutSchema(Schema):
    """Check workout data and format it as JSON."""

    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True, load_default=None)

    workout_exercises = fields.Nested(
        "WorkoutExerciseSchema",
        many=True,
        dump_only=True
    )

    @validates("duration_minutes")
    def validate_duration(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("Workout duration must be greater than zero.")


class ExerciseSchema(Schema):
    """Check exercise details before saving them."""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(required=True)

    workout_exercises = fields.Nested(
        "WorkoutExerciseSchema",
        many=True,
        dump_only=True
    )

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Please enter an exercise name.")

        if len(value.strip()) > 80:
            raise ValidationError("Exercise names cannot exceed 80 characters.")

    @validates("category")
    def validate_category(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Please enter an exercise category.")

        if len(value.strip()) > 50:
            raise ValidationError("Categories cannot exceed 50 characters.")


class WorkoutExerciseSchema(Schema):
    """Check the details of an exercise added to a workout."""

    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)

    reps = fields.Int(allow_none=True, load_default=None)
    sets = fields.Int(allow_none=True, load_default=None)
    duration_seconds = fields.Int(allow_none=True, load_default=None)

    # Include a short summary of the linked exercise in the response.
    exercise = fields.Nested(
        ExerciseSchema(
            only=("id", "name", "category", "equipment_needed")
        ),
        dump_only=True
    )

    # Include a short summary of the linked workout in the response.
    workout = fields.Nested(
        WorkoutSchema(only=("id", "date", "duration_minutes")),
        dump_only=True
    )

    @validates("reps")
    def validate_reps(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("Reps cannot be negative.")

    @validates("sets")
    def validate_sets(self, value, **kwargs):
        if value is not None and value <= 0:
            raise ValidationError("Sets must be greater than zero.")

    @validates("duration_seconds")
    def validate_duration(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("Duration cannot be negative.")

    @validates_schema
    def require_a_training_measurement(self, data, **kwargs):
        # At least one measurement is needed to describe the exercise.
        measurements = ("reps", "sets", "duration_seconds")

        if all(data.get(item) is None for item in measurements):
            raise ValidationError(
                "Enter at least one of these: reps, sets or duration_seconds."
            )
