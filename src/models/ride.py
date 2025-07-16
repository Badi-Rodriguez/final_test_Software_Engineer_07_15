# src/models/ride.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, validator

from .ride_participation import RideParticipation, RPStatus


class RideStatus(str, Enum):
    ready       = "ready"
    inprogress  = "inprogress"
    done        = "done"


class Ride(BaseModel):
    id: int
    ride_date_and_time: datetime
    final_address: str
    allowed_spaces: int = Field(..., gt=0)
    ride_driver: str                      # alias del conductor
    status: RideStatus = RideStatus.ready
    participants: List[RideParticipation] = []

    # ---------- métricas ------------
    @property
    def occupied(self) -> int:
        return sum(p.occupied_spaces
                   for p in self.participants
                   if p.status in {RPStatus.confirmed,
                                   RPStatus.inprogress,
                                   RPStatus.done})

    @property
    def free_spaces(self) -> int:
        return self.allowed_spaces - self.occupied

    # ---------- utilidades ----------
    def get_participation(self, alias: str) -> RideParticipation | None:
        for p in self.participants:
            if p.participant_alias == alias:
                return p
        return None

    # ---------- validaciones ----------
    def request_join(self, participant: RideParticipation):
        if self.status is not RideStatus.ready:
            raise ValueError("Ride already started")
        if self.get_participation(participant.participant_alias):
            raise ValueError("Duplicate request")
        if participant.occupied_spaces > self.free_spaces:
            raise ValueError("Not enough free spaces")
        self.participants.append(participant)

    def accept(self, alias: str):
        p = self.get_participation(alias)
        if not p or p.status is not RPStatus.waiting:
            raise ValueError("No waiting request to accept")
        if p.occupied_spaces > self.free_spaces:
            raise ValueError("No free seats")
        p.status = RPStatus.confirmed
        p.confirmation = datetime.now()

    def reject(self, alias: str):
        p = self.get_participation(alias)
        if not p or p.status is not RPStatus.waiting:
            raise ValueError("No waiting request to reject")
        p.status = RPStatus.rejected

    def start(self):
        if self.status is not RideStatus.ready:
            raise ValueError("Ride already started/finished")
        # marcar ausentes
        for p in self.participants:
            if p.status is RPStatus.confirmed:
                p.status = RPStatus.inprogress
            elif p.status is RPStatus.waiting:
                p.status = RPStatus.missing
        self.status = RideStatus.inprogress

    def end(self):
        if self.status is not RideStatus.inprogress:
            raise ValueError("Ride not in progress")
        for p in self.participants:
            if p.status is RPStatus.inprogress:
                p.status = RPStatus.notmarked
        self.status = RideStatus.done
