from datetime import datetime, timezone
from typing import Any

from eventsourcing.domain import Aggregate, event


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


class Workout(Aggregate):
    @event("Created")
    def __init__(
        self,
        user_id: str,
        workout_type: str,
        performed_on: str,
        notes: str | None = None,
    ) -> None:
        if not user_id:
            raise ValueError("user_id is required")
        if not workout_type:
            raise ValueError("workout_type is required")

        self.user_id = user_id
        self.workout_type = workout_type
        self.performed_on = performed_on
        self.notes = notes
        self.status = "in_progress"
        self.exercises: list[dict[str, Any]] = []
        self.created_at = utc_now_iso()
        self.updated_at = self.created_at

    @event("ExerciseLogged")
    def log_exercise(
        self,
        name: str,
        sets: int,
        reps: int,
        weight_kg: float | None = None,
        notes: str | None = None,
    ) -> None:
        if self.status == "completed":
            raise ValueError("Cannot log an exercise on a completed workout")
        if sets <= 0 or reps <= 0:
            raise ValueError("sets and reps must be positive")

        self.exercises.append(
            {
                "name": name,
                "sets": sets,
                "reps": reps,
                "weight_kg": weight_kg,
                "notes": notes,
            }
        )
        self.updated_at = utc_now_iso()

    @event("Completed")
    def complete(self) -> None:
        if self.status == "completed":
            raise ValueError("Workout is already completed")

        self.status = "completed"
        self.updated_at = utc_now_iso()
