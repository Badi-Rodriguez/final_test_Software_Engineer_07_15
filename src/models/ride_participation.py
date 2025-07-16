# src/models/ride_participation.py
from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RideParticipation(BaseModel):
    participant: "User"
    destination: str
    occupied_spaces: int
    confirmation: Optional[datetime] = None
    status: str = Field(
        default="waiting",
        pattern=r"^(waiting|rejected|confirmed|missing|notmarked|inprogress|done)$",
    )

    # Cambia el estado, garantizando consistencia
    def set_status(self, new_status: str):
        allowed = {
            "waiting",
            "rejected",
            "confirmed",
            "missing",
            "not-marked",
            "in-progress",
            "done",
        }
        if new_status not in allowed:
            raise ValueError("Invalid status")
        self.status = new_status