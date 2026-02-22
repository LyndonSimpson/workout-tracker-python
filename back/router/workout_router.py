from functools import lru_cache
from uuid import UUID

from eventsourcing.application import AggregateNotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.workout_service import WorkoutApplication
from controller.workout_controller import WorkoutController
from core.config import Settings
from datamapper.workout_mapper import WorkoutDataMapper
from db.postgres import PostgresConnectionFactory
from projector.workout_projector import WorkoutProjector
from schema.workout import (
    CreateWorkoutRequest,
    LogExerciseRequest,
    WorkoutResponse,
    WorkoutSummaryResponse,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


@lru_cache(maxsize=1)
def get_workout_controller() -> WorkoutController:
    settings = Settings.from_env()
    application = WorkoutApplication(env=settings.eventsourcing_env)
    mapper = WorkoutDataMapper()
    projector = WorkoutProjector(
        application=application,
        db=PostgresConnectionFactory(settings.postgres_dsn),
        mapper=mapper,
        projector_name=settings.projector_name,
    )
    projector.ensure_tables()
    return WorkoutController(
        application=application,
        mapper=mapper,
        projector=projector,
    )


@router.post("", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(
    payload: CreateWorkoutRequest,
    controller: WorkoutController = Depends(get_workout_controller),
) -> WorkoutResponse:
    try:
        data = controller.create_workout(payload)
        return WorkoutResponse(**data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{workout_id}/exercises", response_model=WorkoutResponse)
def log_exercise(
    workout_id: UUID,
    payload: LogExerciseRequest,
    controller: WorkoutController = Depends(get_workout_controller),
) -> WorkoutResponse:
    try:
        data = controller.log_exercise(workout_id, payload)
        return WorkoutResponse(**data)
    except AggregateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{workout_id}/complete", response_model=WorkoutResponse)
def complete_workout(
    workout_id: UUID,
    controller: WorkoutController = Depends(get_workout_controller),
) -> WorkoutResponse:
    try:
        data = controller.complete_workout(workout_id)
        return WorkoutResponse(**data)
    except AggregateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{workout_id}", response_model=WorkoutResponse)
def get_workout(
    workout_id: UUID,
    controller: WorkoutController = Depends(get_workout_controller),
) -> WorkoutResponse:
    try:
        data = controller.get_workout(workout_id)
        return WorkoutResponse(**data)
    except AggregateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found") from exc


@router.get("", response_model=list[WorkoutSummaryResponse])
def list_workouts(
    user_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    controller: WorkoutController = Depends(get_workout_controller),
) -> list[WorkoutSummaryResponse]:
    items = controller.list_workouts(user_id=user_id, limit=limit)
    return [WorkoutSummaryResponse(**item) for item in items]

