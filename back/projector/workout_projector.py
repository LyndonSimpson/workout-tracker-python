import json
from typing import Any
from uuid import UUID

from eventsourcing.application import AggregateNotFoundError

from application.workout_service import WorkoutApplication
from datamapper.workout_mapper import WorkoutDataMapper
from db.postgres import PostgresConnectionFactory


class WorkoutProjector:
    _projection_table = "workout_projection"
    _offset_table = "workout_projection_offsets"

    def __init__(
        self,
        application: WorkoutApplication,
        db: PostgresConnectionFactory,
        mapper: WorkoutDataMapper,
        projector_name: str,
    ) -> None:
        self._application = application
        self._db = db
        self._mapper = mapper
        self._projector_name = projector_name

    def ensure_tables(self) -> None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._projection_table} (
                        workout_id UUID PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        workout_type TEXT NOT NULL,
                        performed_on DATE NOT NULL,
                        status TEXT NOT NULL,
                        notes TEXT,
                        exercise_count INTEGER NOT NULL,
                        total_sets INTEGER NOT NULL,
                        total_reps INTEGER NOT NULL,
                        exercises JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL,
                        last_event_version BIGINT NOT NULL
                    )
                    """
                )
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self._offset_table} (
                        projector_name TEXT PRIMARY KEY,
                        last_notification_id BIGINT NOT NULL DEFAULT 0
                    )
                    """
                )
                cur.execute(
                    f"""
                    INSERT INTO {self._offset_table} (projector_name, last_notification_id)
                    VALUES (%s, 0)
                    ON CONFLICT (projector_name) DO NOTHING
                    """,
                    (self._projector_name,),
                )

    def catch_up(self, batch_size: int = 100) -> None:
        with self._db.connection() as conn:
            last_notification_id = self._get_last_notification_id(conn)

            while True:
                selected = self._application.notification_log.select(
                    start=last_notification_id + 1,
                    limit=batch_size,
                )
                notifications = list(getattr(selected, "items", selected))
                if not notifications:
                    break

                for notification in notifications:
                    workout_id = self._coerce_uuid(notification.originator_id)

                    try:
                        workout = self._application.get_workout(workout_id)
                    except AggregateNotFoundError:
                        last_notification_id = int(notification.id)
                        continue

                    row = self._mapper.aggregate_to_projection_row(workout)
                    self._upsert_projection(conn, row)
                    last_notification_id = int(notification.id)

                self._set_last_notification_id(conn, last_notification_id)

    def list_workouts(self, user_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                if user_id:
                    cur.execute(
                        f"""
                        SELECT *
                        FROM {self._projection_table}
                        WHERE user_id = %s
                        ORDER BY performed_on DESC, updated_at DESC
                        LIMIT %s
                        """,
                        (user_id, limit),
                    )
                else:
                    cur.execute(
                        f"""
                        SELECT *
                        FROM {self._projection_table}
                        ORDER BY performed_on DESC, updated_at DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                return list(cur.fetchall())

    def get_workout_projection(self, workout_id: UUID) -> dict[str, Any] | None:
        with self._db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT *
                    FROM {self._projection_table}
                    WHERE workout_id = %s
                    """,
                    (str(workout_id),),
                )
                return cur.fetchone()

    def _get_last_notification_id(self, conn: Any) -> int:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT last_notification_id
                FROM {self._offset_table}
                WHERE projector_name = %s
                """,
                (self._projector_name,),
            )
            row = cur.fetchone()
            if row is None:
                return 0
            return int(row["last_notification_id"])

    def _set_last_notification_id(self, conn: Any, last_notification_id: int) -> None:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE {self._offset_table}
                SET last_notification_id = %s
                WHERE projector_name = %s
                """,
                (last_notification_id, self._projector_name),
            )

    def _upsert_projection(self, conn: Any, row: dict[str, Any]) -> None:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {self._projection_table} (
                    workout_id,
                    user_id,
                    workout_type,
                    performed_on,
                    status,
                    notes,
                    exercise_count,
                    total_sets,
                    total_reps,
                    exercises,
                    created_at,
                    updated_at,
                    last_event_version
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s::jsonb, %s, %s, %s
                )
                ON CONFLICT (workout_id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    workout_type = EXCLUDED.workout_type,
                    performed_on = EXCLUDED.performed_on,
                    status = EXCLUDED.status,
                    notes = EXCLUDED.notes,
                    exercise_count = EXCLUDED.exercise_count,
                    total_sets = EXCLUDED.total_sets,
                    total_reps = EXCLUDED.total_reps,
                    exercises = EXCLUDED.exercises,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at,
                    last_event_version = EXCLUDED.last_event_version
                """,
                (
                    row["workout_id"],
                    row["user_id"],
                    row["workout_type"],
                    row["performed_on"],
                    row["status"],
                    row["notes"],
                    row["exercise_count"],
                    row["total_sets"],
                    row["total_reps"],
                    json.dumps(row["exercises"]),
                    row["created_at"],
                    row["updated_at"],
                    row["last_event_version"],
                ),
            )

    @staticmethod
    def _coerce_uuid(value: Any) -> UUID:
        if isinstance(value, UUID):
            return value
        return UUID(str(value))

