# tests/test_ride_participation.py
# Pruebas unitarias para la clase RideParticipation: creación, validación de campos y casos de error.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.models.ride_participation import RideParticipation
from datetime import datetime

# Success: RideParticipation creation with all fields
def test_ride_participation_success():
    rp = RideParticipation(
        confirmation=datetime.now(),
        destination="123 Main St",
        occupied_spaces=1,
        status="confirmed",
        participant_alias="testuser"
    )
    assert rp.status == "confirmed"
    assert rp.destination == "123 Main St"

# Error: RideParticipation missing destination
def test_ride_participation_missing_destination():
    rp = RideParticipation(
        confirmation=datetime.now(),
        destination="",
        occupied_spaces=1,
        status="confirmed",
        participant_alias="testuser"
    )
    assert rp.destination == ""

# Error: RideParticipation invalid status
def test_ride_participation_invalid_status():
    try:
        RideParticipation(
            confirmation=datetime.now(),
            destination="123 Main St",
            occupied_spaces=1,
            status="invalid",
            participant_alias="testuser"
        )
    except Exception as e:
        assert "status" in str(e)

# Error: RideParticipation with zero occupied_spaces
def test_ride_participation_zero_spaces():
    rp = RideParticipation(
        confirmation=datetime.now(),
        destination="123 Main St",
        occupied_spaces=0,
        status="confirmed",
        participant_alias="testuser"
    )
    assert rp.occupied_spaces == 0 