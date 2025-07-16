import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.models.ride import Ride, RideStatus
from src.models.ride_participation import RideParticipation, RPStatus
from datetime import datetime
import pytest

# Success: Ride occupied/free spaces calculation
def test_ride_occupied_free_spaces():
    ride = Ride(
        id=1,
        ride_date_and_time=datetime.now(),
        final_address="123 Main St",
        allowed_spaces=2,
        ride_driver="testuser",
        status=RideStatus.ready,
        participants=[
            RideParticipation(occupied_spaces=1, status=RPStatus.confirmed, participant_alias="p1", destination="A", confirmation=None),
            RideParticipation(occupied_spaces=1, status=RPStatus.waiting, participant_alias="p2", destination="B", confirmation=None)
        ]
    )
    assert ride.occupied == 1  # Only confirmed counts
    assert ride.free_spaces == 1

# Success: request_join works for new participant
def test_ride_request_join_success():
    ride = Ride(
        id=2,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[]
    )
    rp = RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)
    ride.request_join(rp)
    assert ride.get_participation("p1") is not None

# Error: request_join when ride not ready
def test_ride_request_join_not_ready():
    ride = Ride(
        id=3,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.done,
        participants=[]
    )
    rp = RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)
    with pytest.raises(ValueError):
        ride.request_join(rp)

# Error: request_join duplicate
def test_ride_request_join_duplicate():
    ride = Ride(
        id=4,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)]
    )
    rp = RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)
    with pytest.raises(ValueError):
        ride.request_join(rp)

# Error: request_join not enough free spaces
def test_ride_request_join_no_space():
    ride = Ride(
        id=5,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=1,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.confirmed, confirmation=None)]
    )
    rp = RideParticipation(participant_alias="p2", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)
    with pytest.raises(ValueError):
        ride.request_join(rp)

# Success: accept a waiting participant
def test_ride_accept_success():
    ride = Ride(
        id=6,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)]
    )
    ride.accept("p1")
    assert ride.get_participation("p1").status == RPStatus.confirmed

# Error: accept with no waiting request
def test_ride_accept_no_waiting():
    ride = Ride(
        id=7,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.confirmed, confirmation=None)]
    )
    with pytest.raises(ValueError):
        ride.accept("p1")

# Error: accept with no free seats
def test_ride_accept_no_seats():
    ride = Ride(
        id=8,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=1,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None),
                      RideParticipation(participant_alias="p2", destination="X", occupied_spaces=1, status=RPStatus.confirmed, confirmation=None)]
    )
    with pytest.raises(ValueError):
        ride.accept("p1")

# Success: reject a waiting participant
def test_ride_reject_success():
    ride = Ride(
        id=9,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)]
    )
    ride.reject("p1")
    assert ride.get_participation("p1").status == RPStatus.rejected

# Error: reject with no waiting request
def test_ride_reject_no_waiting():
    ride = Ride(
        id=10,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.confirmed, confirmation=None)]
    )
    with pytest.raises(ValueError):
        ride.reject("p1")

# Success: start ride
def test_ride_start_success():
    ride = Ride(
        id=11,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.confirmed, confirmation=None),
                      RideParticipation(participant_alias="p2", destination="X", occupied_spaces=1, status=RPStatus.waiting, confirmation=None)]
    )
    ride.start()
    assert ride.status == RideStatus.inprogress
    assert ride.get_participation("p1").status == RPStatus.inprogress
    assert ride.get_participation("p2").status == RPStatus.missing

# Error: start ride not ready
def test_ride_start_not_ready():
    ride = Ride(
        id=12,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.done,
        participants=[]
    )
    with pytest.raises(ValueError):
        ride.start()

# Success: end ride
def test_ride_end_success():
    ride = Ride(
        id=13,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.inprogress,
        participants=[RideParticipation(participant_alias="p1", destination="X", occupied_spaces=1, status=RPStatus.inprogress, confirmation=None),
                      RideParticipation(participant_alias="p2", destination="X", occupied_spaces=1, status=RPStatus.confirmed, confirmation=None)]
    )
    ride.end()
    assert ride.status == RideStatus.done
    assert ride.get_participation("p1").status == RPStatus.notmarked

# Error: end ride not in progress
def test_ride_end_not_inprogress():
    ride = Ride(
        id=14,
        ride_date_and_time=datetime.now(),
        final_address="X",
        allowed_spaces=2,
        ride_driver="drv",
        status=RideStatus.ready,
        participants=[]
    )
    with pytest.raises(ValueError):
        ride.end() 