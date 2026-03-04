from datetime import datetime, timezone
from typing import Any

from eventsourcing.domain import Aggregate, event

def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()

class Set(Aggregate):
    @event("Registered")
    def __init__(
        self,
        user_id: str,
        type: str,
        stats: str,
        status: str,
        date: str,
    ) -> None:
        if not user_id:
            raise ValueError("user_id is required to register workout.")
        if not type:
            raise ValueError("type is required to register workout.")
        if not stats:
            raise ValueError("stats are reauired tor register workout")

        self.user_id = user_id
        self.type = type
        self.stats = stats
        self.status = "in_progress"
        self.date = utc_now_iso()
        self.created_at = self.date
        self.updated_at = self.created_at

    @event("Completed")
    def complete(self) -> None:
        if self.status == "completed":
            raise ValueError("set already completed.")
        self.status = "completed"
        self.updated_at = utc_now_iso()
        