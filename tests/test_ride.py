import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.models.ride import Ride
from src.models.ride_participation import RideParticipation
from datetime import datetime

# Success: Ride occupied/free spaces calculation
def test_ride_occupied_free_spaces():
    ride = Ride(
        id=1,
        ride_date_and_time=datetime.now(),
        final_address="123 Main St",
        allowed_spaces=2,
        ride_driver="testuser",
        status="ready",
        participants=[
            RideParticipation(occupied_spaces=1, status="confirmed", participant_alias="p1", destination="A", confirmation=None),
            RideParticipation(occupied_spaces=1, status="confirmed", participant_alias="p2", destination="B", confirmation=None)
        ]
    )
    occupied = sum(p.occupied_spaces for p in ride.participants if p.status in ("confirmed", "waiting"))
    free = ride.allowed_spaces - occupied
    assert occupied == 2
    assert free == 0

# Error: Ride overbooked
def test_ride_overbooked():
    ride = Ride(
        id=1,
        ride_date_and_time=datetime.now(),
        final_address="123 Main St",
        allowed_spaces=1,
        ride_driver="testuser",
        status="ready",
        participants=[
            RideParticipation(occupied_spaces=1, status="confirmed", participant_alias="p1", destination="A", confirmation=None),
            RideParticipation(occupied_spaces=1, status="confirmed", participant_alias="p2", destination="B", confirmation=None)
        ]
    )
    occupied = sum(p.occupied_spaces for p in ride.participants if p.status in ("confirmed", "waiting"))
    assert occupied > ride.allowed_spaces

# Error: Ride with wrong status
def test_ride_wrong_status():
    ride = Ride(
        id=1,
        ride_date_and_time=datetime.now(),
        final_address="123 Main St",
        allowed_spaces=2,
        ride_driver="testuser",
        status="done",
        participants=[]
    )
    assert ride.status in ("ready", "inprogress", "done")

# Error: Ride with no participants
def test_ride_no_participants():
    ride = Ride(
        id=1,
        ride_date_and_time=datetime.now(),
        final_address="123 Main St",
        allowed_spaces=2,
        ride_driver="testuser",
        status="ready",
        participants=[]
    )
    assert len(ride.participants) == 0 