from typing import Any, Mapping

from domain.workout import Workout


class WorkoutDataMapper:
    @staticmethod
    def aggregate_to_projection_row(workout: Workout) -> dict[str, Any]:
        exercise_count = len(workout.exercises)
        total_sets = sum(int(exercise["sets"]) for exercise in workout.exercises)
        total_reps = sum(
            int(exercise["sets"]) * int(exercise["reps"])
            for exercise in workout.exercises
        )

        return {
            "workout_id": str(workout.id),
            "user_id": workout.user_id,
            "workout_type": workout.workout_type,
            "performed_on": workout.performed_on,
            "status": workout.status,
            "notes": workout.notes,
            "exercise_count": exercise_count,
            "total_sets": total_sets,
            "total_reps": total_reps,
            "exercises": workout.exercises,
            "created_at": workout.created_at,
            "updated_at": workout.updated_at,
            "last_event_version": int(workout.version),
        }

    @staticmethod
    def aggregate_to_detail(workout: Workout) -> dict[str, Any]:
        row = WorkoutDataMapper.aggregate_to_projection_row(workout)
        return {
            "id": row["workout_id"],
            "user_id": row["user_id"],
            "workout_type": row["workout_type"],
            "performed_on": row["performed_on"],
            "status": row["status"],
            "notes": row["notes"],
            "exercise_count": row["exercise_count"],
            "total_sets": row["total_sets"],
            "total_reps": row["total_reps"],
            "exercises": row["exercises"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "version": row["last_event_version"],
        }

    @staticmethod
    def projection_row_to_summary(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "id": str(row["workout_id"]),
            "user_id": row["user_id"],
            "workout_type": row["workout_type"],
            "performed_on": str(row["performed_on"]),
            "status": row["status"],
            "exercise_count": int(row["exercise_count"]),
            "total_sets": int(row["total_sets"]),
            "total_reps": int(row["total_reps"]),
            "updated_at": str(row["updated_at"]),
        }
