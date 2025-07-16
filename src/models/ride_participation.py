# src/models/ride_participation.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RPStatus(str, Enum):
    waiting     = "waiting"
    rejected    = "rejected"
    confirmed   = "confirmed"
    missing     = "missing"
    notmarked   = "notmarked"
    inprogress  = "inprogress"
    done        = "done"


class RideParticipation(BaseModel):
    participant_alias: str                     # solo guardamos el alias
    destination: str
    occupied_spaces: int = Field(..., gt=-1)
    confirmation: Optional[datetime] = None
    status: RPStatus = RPStatus.waiting

    # ------------ helpers ------------
    def can_be_unloaded(self) -> bool:
        return self.status is RPStatus.inprogress

    def mark_unloaded(self):
        if not self.can_be_unloaded():
            raise ValueError("Can only unload inprogress participants")
        self.status = RPStatus.done
