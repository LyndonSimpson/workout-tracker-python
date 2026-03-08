from functools import lru_cache
from uuid import UUID

from eventsourcing.application import AggregateNotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, status

router = APIRouter(prefix="/workouts", tags=["Basic workout tracker for reps and max weights progress"])


@router.post("sanity_check")
def sanity():
    return "sanity check ok"