from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from src.models.data_handler import DataHandler
from src.models.ride_participation import RideParticipation
from src.models.user import User
from src.models.ride import Ride
from src.schemas import UserSchema, RideSchema, RideParticipationSchema

app = FastAPI()
data_handler = DataHandler()

# --- User Endpoints ---
@app.get("/usuarios", response_model=List[UserSchema])
def list_users():
    return [UserSchema(
        alias=u.alias,
        name=u.name,
        carPlate=u.carPlate,
        rides=[i for i in range(len(u.rides))]  # Just index for demo
    ) for u in data_handler.users]

@app.post("/usuarios", response_model=UserSchema)
def create_user(user: UserSchema):
    if data_handler.get_user(user.alias):
        raise HTTPException(status_code=422, detail="User already exists")  # Badi was here >:p
    new_user = User(
        alias=user.alias,
        name=user.name,
        carPlate=user.carPlate,
        rides=[]
    )
    data_handler.add_user(new_user)
    return user

@app.get("/usuarios/{alias}", response_model=UserSchema)
def get_user(alias: str):
    user = data_handler.get_user(alias)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  # Badi was here >:p
    stats = user.get_ride_stats()
    return UserSchema(
        alias=user.alias,
        name=user.name,
        carPlate=user.carPlate,
        rides=[i for i in range(len(user.rides))],
        **stats
    )

# --- Ride Endpoints ---
@app.post("/rides", response_model=RideSchema)
def create_ride(
    rideDateAndTime: datetime,
    finalAddress: str,
    allowedSpaces: int,
    rideDriver: str
):
    driver = data_handler.get_user(rideDriver)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")  # Badi was here >:p
    ride = Ride(
        id=data_handler.next_ride_id,
        ride_date_and_time=rideDateAndTime,
        final_address=finalAddress,
        allowed_spaces=allowedSpaces,
        ride_driver=rideDriver,
        status="ready",
        participants=[]
    )
    data_handler.add_ride(ride)
    driver.rides.append(ride)  # Add ride to driver's rides
    return RideSchema(
        id=ride.id,
        rideDateAndTime=ride.ride_date_and_time,
        finalAddress=ride.final_address,
        allowedSpaces=ride.allowed_spaces,
        rideDriver=ride.ride_driver,
        status=ride.status,
        participants=[]
    )

@app.get("/rides", response_model=List[RideSchema])
def list_active_rides(status: Optional[str] = Query(None)):
    rides = data_handler.rides
    if status:
        rides = [r for r in rides if r.status == status]
    return [RideSchema(
        id=r.id,
        rideDateAndTime=r.ride_date_and_time,
        finalAddress=r.final_address,
        allowedSpaces=r.allowed_spaces,
        rideDriver=r.ride_driver,
        status=r.status,
        participants=[RideParticipationSchema(
            confirmation=p.confirmation,
            destination=p.destination,
            occupiedSpaces=p.occupiedSpaces,
            status=p.status,
            participant_alias=p.participant_alias
        ) for p in r.participants]
    ) for r in rides]

# --- Ride Participation Endpoints ---
@app.post("/usuarios/{alias}/rides/{rideid}/unloadParticipant")
def unload_participant(alias: str, rideid: int):
    ride = data_handler.get_ride(rideid)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")  # Badi was here >:p
    part = next((p for p in ride.participants if p.participant_alias == alias), None)
    if not part:
        raise HTTPException(status_code=404, detail="Participation not found")  # Badi was here >:p
    if part.status != "inprogress":
        raise HTTPException(status_code=422, detail="Can only unload inprogress participants")  # Badi was here >:p
    part.status = "done"
    return {"message": "Participant unloaded"}

# --- Ayudas internas ----------------------------------
def _ride_or_404(rideid: int) -> Ride:
    ride = data_handler.get_ride(rideid)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride

def _user_or_404(alias: str) -> User:
    user = data_handler.get_user(alias)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Rides por usuario ---------------------------------
@app.get("/usuarios/{alias}/rides", response_model=List[RideSchema])
def rides_by_user(alias: str):
    user = _user_or_404(alias)
    return [
        RideSchema(
            id=r.id,
            rideDateAndTime=r.ride_date_and_time,
            finalAddress=r.final_address,
            allowedSpaces=r.allowed_spaces,
            rideDriver=r.ride_driver,
            status=r.status.value,
            participants=[],
        )
        for r in user.rides                    # aquí r son objetos Ride
        if isinstance(r, Ride)                 # (driver.rides.append(ride))
    ]

@app.get("/usuarios/{alias}/rides/{rideid}", response_model=RideSchema)
def ride_detail(alias: str, rideid: int):
    _user_or_404(alias)
    ride = _ride_or_404(rideid)
    # construir respuesta enriquecida
    def _build_part_schema(p: RideParticipation):
        u = data_handler.get_user(p.participant_alias)
        return RideParticipationSchema(
            confirmation=p.confirmation,
            destination=p.destination,
            occupiedSpaces=p.occupied_spaces,
            status=p.status.value,
            participant=UserSchema(
                alias=u.alias,
                name=u.name,
                carPlate=u.carPlate,
                rides=[],
                **u.get_ride_stats(),
            )
            if u
            else None,
        )

    return RideSchema(
        id=ride.id,
        rideDateAndTime=ride.ride_date_and_time,
        finalAddress=ride.final_address,
        allowedSpaces=ride.allowed_spaces,
        rideDriver=ride.ride_driver,
        status=ride.status.value,
        participants=[_build_part_schema(p) for p in ride.participants],
    )

# --- Solicitar unirse ----------------------------------
@app.post("/usuarios/{driver}/rides/{rideid}/requestToJoin/{alias}")
def request_to_join(driver: str, rideid: int, alias: str,
                    destination: str, occupiedSpaces: int = 1):
    _user_or_404(alias)
    ride = _ride_or_404(rideid)
    try:
        ride.request_join(
            RideParticipation(
                participant_alias=alias,
                destination=destination,
                occupied_spaces=occupiedSpaces,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"message": "Request registered"}

# --- Aceptar / rechazar --------------------------------
@app.post("/usuarios/{driver}/rides/{rideid}/accept/{alias}")
def accept_participant(driver: str, rideid: int, alias: str):
    ride = _ride_or_404(rideid)
    try:
        ride.accept(alias)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"message": "Accepted"}

@app.post("/usuarios/{driver}/rides/{rideid}/reject/{alias}")
def reject_participant(driver: str, rideid: int, alias: str):
    ride = _ride_or_404(rideid)
    try:
        ride.reject(alias)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"message": "Rejected"}

# --- Iniciar / terminar -------------------------------
@app.post("/usuarios/{driver}/rides/{rideid}/start")
def start_ride(driver: str, rideid: int):
    ride = _ride_or_404(rideid)
    try:
        ride.start()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"message": "Ride started"}

@app.post("/usuarios/{driver}/rides/{rideid}/end")
def end_ride(driver: str, rideid: int):
    ride = _ride_or_404(rideid)
    try:
        ride.end()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"message": "Ride finished"}

# --- Bajar participante (ya existía, solo actualiza) ---
@app.post("/usuarios/{driver}/rides/{rideid}/unloadParticipant/{alias}")
def unload_participant(driver: str, rideid: int, alias: str):
    ride = _ride_or_404(rideid)
    part = ride.get_participation(alias)
    if not part:
        raise HTTPException(status_code=404, detail="Participation not found")
    try:
        part.mark_unloaded()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"message": "Participant unloaded"}


# --- SOMEONE COOKED HERE AND IT WAS ME, DIO!!! ---