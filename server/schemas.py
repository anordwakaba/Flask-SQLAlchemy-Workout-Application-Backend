from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True, load_default=None)
    workout_exercises = fields.Nested("WorkoutExerciseSchema", many=True, dump_only=True)

    @validates("duration_minutes")
    def validate_duration_minutes(self, value, **kwargs):
        if value <= 0:
            raise ValidationError("duration_minutes must be greater than zero")


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(required=True)
    workout_exercises = fields.Nested("WorkoutExerciseSchema", many=True, dump_only=True)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("name cannot be blank")
        if len(value.strip()) > 80:
            raise ValidationError("name must be 80 characters or fewer")

    @validates("category")
    def validate_category(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("category cannot be blank")
        if len(value.strip()) > 50:
            raise ValidationError("category must be 50 characters or fewer")


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, load_default=None)
    sets = fields.Int(allow_none=True, load_default=None)
    duration_seconds = fields.Int(allow_none=True, load_default=None)
    exercise = fields.Nested(ExerciseSchema(only=("id", "name", "category", "equipment_needed")), dump_only=True)
    workout = fields.Nested(WorkoutSchema(only=("id", "date", "duration_minutes")), dump_only=True)

    @validates("reps")
    def validate_reps(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("reps cannot be negative")

    @validates("sets")
    def validate_sets(self, value, **kwargs):
        if value is not None and value <= 0:
            raise ValidationError("sets must be greater than zero")

    @validates("duration_seconds")
    def validate_duration_seconds(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("duration_seconds cannot be negative")

    @validates_schema
    def require_at_least_one_metric(self, data, **kwargs):
        if all(data.get(key) is None for key in ("reps", "sets", "duration_seconds")):
            raise ValidationError(
                "Provide at least one of reps, sets, or duration_seconds."
            )
