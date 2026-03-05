from datetime import date
from typing import Any

from pydantic import BaseModel, Field

class CreateWorkoutResponse(BaseModel):
    user_id: str = Field(min_lenght=1)
    type: str = Field(min_lenght=1)
    stats: str = Field(min_lenght=1)
    date: date

class UpdateWorkoutRequest(BaseModel):
    user_id: str = Field(min_lenght=1)
    stats: str = Field(min_lenght=1)
