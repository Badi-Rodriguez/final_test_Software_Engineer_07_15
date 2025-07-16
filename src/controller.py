from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from src.models.data_handler import DataHandler
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

# --- SOMEONE COOKED HERE AND IT WAS ME, DIO!!! ---