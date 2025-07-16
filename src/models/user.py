from __future__ import annotations
from typing import List, Optional
from dataclasses import dataclass, field
from .ride_participation import RideParticipation

@dataclass
class User:
    alias: str
    name: str
    carPlate: Optional[str] = None  # Can be None for participants
    rides: List[RideParticipation] = field(default_factory=list)

    def get_ride_stats(self) -> dict:
        """Return statistics about the user's ride participations."""
        total = len(self.rides)
        completed = sum(rp.status == "done" for rp in self.rides)
        missing = sum(rp.status == "missing" for rp in self.rides)
        not_marked = sum(rp.status == "notmarked" for rp in self.rides)
        rejected = sum(rp.status == "rejected" for rp in self.rides)
        return {
            "previousRidesTotal": total,
            "previousRidesCompleted": completed,
            "previousRidesMissing": missing,
            "previousRidesNotMarked": not_marked,
            "previousRidesRejected": rejected,
        } 