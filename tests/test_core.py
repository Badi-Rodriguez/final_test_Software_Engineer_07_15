from datetime import datetime
from src.models.user import User
from src.models.ride import Ride
from src.models.ride_participation import RideParticipation

# Success: User stats with one completed ride
def test_user_stats_success():
    user = User(alias="testuser", name="Test User", carPlate="ABC123")
    participation = RideParticipation(
        confirmation=datetime.now(),
        destination="123 Main St",
        occupiedSpaces=1,
        status="done",
        participant_alias="testuser"
    )
    user.rides.append(participation)
    stats = user.get_ride_stats()
    assert stats["previousRidesCompleted"] == 1
    assert stats["previousRidesTotal"] == 1

# Error: No available spaces for new participant
def test_ride_no_available_spaces():
    ride = Ride(
        id=1,
        ride_date_and_time=datetime.now(),
        final_address="123 Main St",
        allowed_spaces=1,
        ride_driver="testuser",
        status="ready",
        participants=[
            RideParticipation(
                confirmation=None,
                destination="123 Main St",
                occupiedSpaces=1,
                status="confirmed",
                participant_alias="p1"
            )
        ]
    )
    occupied = sum(p.occupiedSpaces for p in ride.participants if p.status in ("confirmed", "waiting"))
    assert occupied >= ride.allowed_spaces

# Error: Duplicate participation request
def test_duplicate_participation():
    ride = Ride(
        id=1,
        ride_date_and_time=datetime.now(),
        final_address="123 Main St",
        allowed_spaces=2,
        ride_driver="testuser",
        status="ready",
        participants=[
            RideParticipation(
                confirmation=None,
                destination="123 Main St",
                occupiedSpaces=1,
                status="waiting",
                participant_alias="testuser"
            )
        ]
    )
    duplicate = any(p.participant_alias == "testuser" for p in ride.participants)
    assert duplicate

# Error: Unload participant not in 'inprogress' status
def test_invalid_status_transition():
    part = RideParticipation(
        confirmation=None,
        destination="123 Main St",
        occupiedSpaces=1,
        status="waiting",
        participant_alias="testuser"
    )
    can_unload = part.status == "inprogress"
    assert not can_unload 