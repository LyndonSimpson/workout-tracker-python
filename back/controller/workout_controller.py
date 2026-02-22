from uuid import UUID

from eventsourcing.application import AggregateNotFound

from application.workout_service import WorkoutApplication
from datamapper.workout_mapper import WorkoutDataMapper
from projector.workout_projector import WorkoutProjector
from schema.workout import CreateWorkoutRequest, LogExerciseRequest


class WorkoutController:
    def __init__(
        self,
        application: WorkoutApplication,
        mapper: WorkoutDataMapper,
        projector: WorkoutProjector,
    ) -> None:
        self._application = application
        self._mapper = mapper
        self._projector = projector

    def create_workout(self, payload: CreateWorkoutRequest) -> dict[str, object]:
        workout_id = self._application.create_workout(
            user_id=payload.user_id,
            workout_type=payload.workout_type,
            performed_on=payload.performed_on.isoformat(),
            notes=payload.notes,
        )
        self._projector.catch_up()
        workout = self._application.get_workout(workout_id)
        return self._mapper.aggregate_to_detail(workout)

    def log_exercise(
        self,
        workout_id: UUID,
        payload: LogExerciseRequest,
    ) -> dict[str, object]:
        self._application.log_exercise(
            workout_id=workout_id,
            name=payload.name,
            sets=payload.sets,
            reps=payload.reps,
            weight_kg=payload.weight_kg,
            notes=payload.notes,
        )
        self._projector.catch_up()
        workout = self._application.get_workout(workout_id)
        return self._mapper.aggregate_to_detail(workout)

    def complete_workout(self, workout_id: UUID) -> dict[str, object]:
        self._application.complete_workout(workout_id)
        self._projector.catch_up()
        workout = self._application.get_workout(workout_id)
        return self._mapper.aggregate_to_detail(workout)

    def get_workout(self, workout_id: UUID) -> dict[str, object]:
        try:
            workout = self._application.get_workout(workout_id)
        except AggregateNotFound:
            raise
        return self._mapper.aggregate_to_detail(workout)

    def list_workouts(self, user_id: str | None = None, limit: int = 50) -> list[dict[str, object]]:
        self._projector.catch_up()
        rows = self._projector.list_workouts(user_id=user_id, limit=limit)
        return [self._mapper.projection_row_to_summary(row) for row in rows]
