from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

# --- Básicos ---
class UserSchema(BaseModel):
    alias: str
    name: str
    carPlate: Optional[str] = None
    rides: List[int] = []

class RideParticipationSchema(BaseModel):
    confirmation: Optional[datetime] = None
    destination: str
    occupiedSpaces: int
    status: str                 # str para serializar Enum
    participant: UserSchema | None = None  # completo en GET detalle

class RideSchema(BaseModel):
    id: int
    rideDateAndTime: datetime
    finalAddress: str
    allowedSpaces: int
    rideDriver: str
    status: str
    participants: List[RideParticipationSchema] = []
