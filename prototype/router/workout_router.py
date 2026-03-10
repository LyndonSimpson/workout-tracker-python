from functools import lru_cache
from uuid import UUID

from eventsourcing.application import AggregateNotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schema.workout import WorkoutResponse

router = APIRouter(prefix="/workouts", tags=["Basic workout tracker for reps and max weights progress"])


@router.post("/sanity_check")
def sanity():
    return {"message": "Sanity check ok"}

## need to create the controller now:
router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: UUID,
    controller: WorkoutController = Depends(get_workout_controller),
) -> WorkoutResponse:
    try:
        data = controller.get_workout(workout_id)
        return WorkoutResponse(**data)
    except AggregateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found") from exc
