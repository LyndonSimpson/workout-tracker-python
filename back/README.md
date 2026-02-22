# Workout Tracker Event Sourcing API

## Environment Variables

Set these before running the API:

- `POSTGRES_HOST` (default: `localhost`)
- `POSTGRES_PORT` (default: `5432`)
- `POSTGRES_DB` (default: `workout_tracker`)
- `POSTGRES_USER` (default: `postgres`)
- `POSTGRES_PASSWORD` (default: `postgres`)
- `PROJECTOR_NAME` (default: `workout_tracker_projector`)

## Install and run

```bash
cd back
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Event commands (write side)

- `POST /workouts` -> creates a workout aggregate and emits `Created`
- `POST /workouts/{workout_id}/exercises` -> emits `ExerciseLogged`
- `POST /workouts/{workout_id}/complete` -> emits `Completed`

## Queries (read side)

- `GET /workouts/{workout_id}` -> aggregate state rebuilt from events
- `GET /workouts?user_id=<id>&limit=50` -> read model from projector table
