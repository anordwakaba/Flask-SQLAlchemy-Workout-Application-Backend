# Workout Tracker API

A Flask REST API for tracking workouts and reusable exercises. It uses Flask-SQLAlchemy for database models and relationships, Flask-Migrate for migrations, and Marshmallow for request validation and JSON serialization.

## Features
- Create, list, view, and delete workouts.
- Create, list, view, and delete exercises.
- Add an existing exercise to a workout with reps, sets, and/or duration.
- Many-to-many relationship between workouts and exercises through `WorkoutExercise`.
- Database constraints, model validations, and Marshmallow schema validations.
- Repeatable seed script and basic endpoint tests.

## Requirements
- Python 3.12 (the Pipfile is configured for Python 3.12; Python 3.8.13+ is acceptable if you adjust the Pipfile)
- Pipenv
- Git

## Installation

From the project root:

```bash
pipenv install
cd server
pipenv run flask --app app db init
pipenv run flask --app app db migrate -m "create workout and exercise tables"
pipenv run flask --app app db upgrade
pipenv run python seed.py
```

If `server/migrations` already exists in the repository, skip `db init` and run only `db migrate` (if you changed the models) and `db upgrade`.

## Run the API

From the `server` directory:

```bash
pipenv run flask --app app run --port 5555 --debug
```

The API runs at `http://127.0.0.1:5555`.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/workouts` | List all workouts with their exercises |
| GET | `/workouts/<id>` | Show one workout and exercise details |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout and its join records |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show one exercise and its associated workouts |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise and its join records |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps, sets, and/or duration |

### Example requests

Create a workout:

```bash
curl -X POST http://127.0.0.1:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-10-25","duration_minutes":45,"notes":"Full body session"}'
```

Create an exercise:

```bash
curl -X POST http://127.0.0.1:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name":"Squat","category":"Strength","equipment_needed":false}'
```

Add an exercise to workout 1:

```bash
curl -X POST http://127.0.0.1:5555/workouts/1/exercises/1/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps":12,"sets":3}'
```

## Validations and constraints

- Database check constraints require positive workout duration and non-negative exercise metrics.
- A workout cannot contain the same exercise twice (unique constraint on `workout_id`, `exercise_id`).
- Model validators reject blank exercise names/categories and invalid numeric values.
- Marshmallow schemas validate required fields, dates, booleans, string lengths, and numeric ranges.

## Tests

From the project root:

```bash
pipenv run pytest
```

## Git workflow

Use small, meaningful commits, for example:
- `Set up Flask application and dependencies`
- `Add workout, exercise, and join models`
- `Add model and database validations`
- `Add Marshmallow schemas`
- `Implement workout and exercise endpoints`
- `Add seed data, tests, and documentation`
