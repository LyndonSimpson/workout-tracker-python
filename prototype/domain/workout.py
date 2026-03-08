from datetime import datetime, timezone
from typing import Any

from eventsourcing.domain import Aggregate, event

def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()

class Workout(Aggregate):
    @event("Registered")
    def __init__(
        self,
        user_id: str,
        type: str,
        stats: str,
    ) -> None:
        if not user_id:
            raise ValueError("user_id is required to register workout.")
        if not type:
            raise ValueError("type is required to register workout.")
        if not stats:
            raise ValueError("stats are reauired tor register workout")

        now = utc_now_iso()
        self.user_id = user_id
        self.type = type
        self.stats = stats
        self.date = now
        self.created_at = now
        self.updated_at = now


    @event("Progressed")
    def update(self, stats: str) -> None:
        if not stats:
            raise ValueError("stats are reauired to update workout stats")
        self.stats = stats
        self.updated_at = utc_now_iso()
        
    ########################## README ###########################
    #remove this event and just do a updated event to track at how 
    # many reps and how many weights we are at for each exercise - simple MVP
    # @event("Completed")
    # def complete(self) -> None:
    #     if self.status == "completed":
    #         raise ValueError("set already completed.")
    #     self.status = "completed"
    #     self.updated_at = utc_now_iso()
    
    