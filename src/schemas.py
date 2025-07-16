from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class UserSchema(BaseModel):
    alias: str
    name: str
    carPlate: Optional[str] = None
    rides: List[int] = []

class RideParticipationSchema(BaseModel):
    confirmation: Optional[datetime] = None
    destination: str = ""
    occupiedSpaces: int = 0
    status: str = "waiting"
    participant_alias: str = ""

class RideSchema(BaseModel):
    id: int
    rideDateAndTime: datetime
    finalAddress: str
    allowedSpaces: int
    rideDriver: str
    status: str = "ready"
    participants: List[RideParticipationSchema] = [] 