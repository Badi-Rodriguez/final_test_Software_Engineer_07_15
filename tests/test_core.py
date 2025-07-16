# tests/test_core.py
from datetime import datetime

from src.models.ride import Ride, RideStatus
from src.models.ride_participation import RideParticipation, RPStatus
from src.models.user import User

# ---------- ÉXITO ----------
def test_stats_success():
    """Se contabiliza correctamente un ride completado."""
    u = User(alias="a", name="A")
    rp = RideParticipation(participant_alias="a",
                           destination="X", occupied_spaces=1,
                           status=RPStatus.done)
    u.rides.append(rp)
    stats = u.get_ride_stats()
    assert stats["previousRidesCompleted"] == 1
    assert stats["previousRidesTotal"] == 1

# ---------- ERRORES ----------
def test_duplicate_request_error():
    """No se permite hacer dos solicitudes al mismo ride."""
    ride = Ride(id=1, ride_date_and_time=datetime.now(),
                final_address="X", allowed_spaces=2,
                ride_driver="drv")
    rp1 = RideParticipation(participant_alias="p",
                            destination="X", occupied_spaces=1)
    ride.request_join(rp1)
    rp2 = RideParticipation(participant_alias="p",
                            destination="X", occupied_spaces=1)
    try:
        ride.request_join(rp2)
        assert False, "Se aceptó solicitud duplicada"
    except ValueError as e:
        assert "Duplicate request" in str(e)

def test_no_space_error():
    """No se acepta un participante si no hay asientos."""
    ride = Ride(id=2, ride_date_and_time=datetime.now(),
                final_address="X", allowed_spaces=1,
                ride_driver="drv")
    ride.request_join(RideParticipation(participant_alias="p1",
                                        destination="X",
                                        occupied_spaces=1))
    rp2 = RideParticipation(participant_alias="p2",
                            destination="X", occupied_spaces=1)
    try:
        ride.request_join(rp2)
        assert False
    except ValueError as e:
        assert "Not enough free spaces" in str(e)

def test_unload_status_error():
    """Solo se puede descargar si está inprogress."""
    rp = RideParticipation(participant_alias="p",
                           destination="X", occupied_spaces=1,
                           status=RPStatus.confirmed)
    try:
        rp.mark_unloaded()
        assert False
    except ValueError as e:
        assert "inprogress" in str(e)
