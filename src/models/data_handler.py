from dataclasses import dataclass, field
from typing import List, Optional
from .user import User
from .ride import Ride

@dataclass
class DataHandler:
    users: List[User] = field(default_factory=list)
    rides: List[Ride] = field(default_factory=list)
    next_ride_id: int = 1

    def get_user(self, alias: str) -> Optional[User]:
        for user in self.users:
            if user.alias == alias:
                return user
        return None

    def get_ride(self, rideid: int) -> Optional[Ride]:
        for ride in self.rides:
            if ride.id == rideid:
                return ride
        return None

    def add_user(self, user: User):
        self.users.append(user)

    def add_ride(self, ride: Ride):
        self.rides.append(ride)
        self.next_ride_id += 1 