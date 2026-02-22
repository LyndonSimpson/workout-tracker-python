from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class CreateWorkoutRequest(BaseModel):
    user_id: str = Field(min_length=1)
    workout_type: str = Field(min_length=1)
    performed_on: date
    notes: str | None = None


class LogExerciseRequest(BaseModel):
    name: str = Field(min_length=1)
    sets: int = Field(ge=1)
    reps: int = Field(ge=1)
    weight_kg: float | None = Field(default=None, ge=0)
    notes: str | None = None


class WorkoutResponse(BaseModel):
    id: str
    user_id: str
    workout_type: str
    performed_on: str
    status: str
    notes: str | None
    exercise_count: int
    total_sets: int
    total_reps: int
    exercises: list[dict[str, Any]]
    created_at: str
    updated_at: str
    version: int


class WorkoutSummaryResponse(BaseModel):
    id: str
    user_id: str
    workout_type: str
    performed_on: str
    status: str
    exercise_count: int
    total_sets: int
    total_reps: int
    updated_at: str
