# tests/test_user.py
# Pruebas unitarias para la clase User: creación, estadísticas y casos de error.
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.models.user import User
from src.models.ride_participation import RideParticipation
from datetime import datetime
import pytest

# Success: User stats with one completed ride
def test_user_stats_success():
    user = User(alias="testuser", name="Test User", carPlate="ABC123")
    participation = RideParticipation(
        confirmation=datetime.now(),
        destination="123 Main St",
        occupied_spaces=1,
        status="done",
        participant_alias="testuser"
    )
    user.rides.append(participation)
    stats = user.get_ride_stats()
    assert stats["previousRidesCompleted"] == 1
    assert stats["previousRidesTotal"] == 1

# Error: User with missing alias
def test_user_missing_alias():
    with pytest.raises(TypeError):
        User(name="Test User", carPlate="ABC123")

# Error: User with invalid carPlate (simulate logic, as no validation)
def test_user_invalid_carplate():
    user = User(alias="testuser", name="Test User", carPlate=None)
    assert user.carPlate is None

# Error: User stats for empty rides
def test_user_stats_empty():
    user = User(alias="testuser", name="Test User", carPlate="ABC123")
    stats = user.get_ride_stats()
    assert stats["previousRidesTotal"] == 0 