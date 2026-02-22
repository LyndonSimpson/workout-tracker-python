from uuid import UUID

from eventsourcing.application import Application

from domain.workout import Workout


class WorkoutApplication(Application):
    env = {"IS_SNAPSHOTTING_ENABLED": "y"}

    def create_workout(
        self,
        user_id: str,
        workout_type: str,
        performed_on: str,
        notes: str | None = None,
    ) -> UUID:
        workout = Workout(
            user_id=user_id,
            workout_type=workout_type,
            performed_on=performed_on,
            notes=notes,
        )
        self.save(workout)
        return workout.id

    def log_exercise(
        self,
        workout_id: UUID,
        name: str,
        sets: int,
        reps: int,
        weight_kg: float | None = None,
        notes: str | None = None,
    ) -> None:
        workout: Workout = self.repository.get(workout_id)
        workout.log_exercise(
            name=name,
            sets=sets,
            reps=reps,
            weight_kg=weight_kg,
            notes=notes,
        )
        self.save(workout)

    def complete_workout(self, workout_id: UUID) -> None:
        workout: Workout = self.repository.get(workout_id)
        workout.complete()
        self.save(workout)

    def get_workout(self, workout_id: UUID) -> Workout:
        return self.repository.get(workout_id)
