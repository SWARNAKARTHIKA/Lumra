import enum
import math
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr, EmailStr, Field
from typing import Optional, List, Annotated
import sqlalchemy
from databases import Database

DATABASE_URL = "sqlite:///./elderly.db"

metadata = sqlalchemy.MetaData()
database = Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ============================
# ENUM for request status
# ============================
class RequestStatus(str, enum.Enum):
    requested = "requested"
    accepted = "accepted"
    rejected = "rejected"

# ============================
# TABLES
# ============================

elderly = sqlalchemy.Table(
    "elderly",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("age", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("gender", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("phone", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("address", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("medical", sqlalchemy.String),
    sqlalchemy.Column("guardian", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
)

guardian = sqlalchemy.Table(
    "guardian",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("phone", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("address", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("relation", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
)

guardian_requests = sqlalchemy.Table(
    "guardian_requests",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("guardian_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("guardian.id")),
    sqlalchemy.Column("elderly_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("elderly.id")),
    sqlalchemy.Column("status", sqlalchemy.String, default=RequestStatus.requested.value),
)

geofence = sqlalchemy.Table(
    "geofence",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("elderly_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("elderly.id"), unique=True),
    sqlalchemy.Column("latitude", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column("longitude", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column("radius", sqlalchemy.Float, nullable=False),
)

elderly_location = sqlalchemy.Table(
    "elderly_location",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("elderly_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("elderly.id")),
    sqlalchemy.Column("latitude", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column("longitude", sqlalchemy.Float, nullable=False),
    sqlalchemy.Column("last_updated", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("is_inside", sqlalchemy.Boolean, default=True),
)

metadata.create_all(engine)

# ============================
# APP INIT
# ============================
app = FastAPI()

# ============================
# CORS CONFIGURATION
# ============================
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# Pydantic Models
# ============================

class ElderlySignup(BaseModel):
    name: constr(min_length=1)
    age: int
    gender: constr(min_length=1)
    phone: constr(min_length=1, max_length=15)
    address: constr(min_length=1)
    medical: Optional[str] = None
    guardian: constr(min_length=1)
    password: constr(min_length=1)
    confirm: constr(min_length=1)

class GuardianSignup(BaseModel):
    name: constr(min_length=1)
    email: EmailStr
    phone: constr(min_length=1, max_length=15)
    address: constr(min_length=1)
    relation: constr(min_length=1)
    password: constr(min_length=1)
    confirm: constr(min_length=1)

class LoginRequest(BaseModel):
    username: constr(min_length=1)
    password: constr(min_length=1)

class GuardianRequestCreate(BaseModel):
    elderly_phone: constr(min_length=1)
    guardian_id: int

class ElderlyRequestResponse(BaseModel):
    request_id: int
    guardian_id: int
    guardian_name: str
    status: RequestStatus

class GuardianResponse(BaseModel):
    guardian_id: int
    guardian_name: str
    relation: str

class ElderlyResponse(BaseModel):
    elderly_id: int
    elderly_name: str
    phone: str

class GuardianRequestUpdate(BaseModel):
    request_id: int
    action: Annotated[str, Field(pattern="^(accept|reject)$")]

class SetGeofence(BaseModel):
    elderly_id: int
    latitude: float
    longitude: float
    radius: float

class LocationUpdate(BaseModel):
    elderly_id: int
    latitude: float
    longitude: float

# ============================
# DB CONNECTION EVENTS
# ============================

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ============================
# HELPER FUNCTIONS
# ============================

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# ============================
# AUTH & USER MANAGEMENT
# ============================

@app.post("/elderly/signup")
async def elderly_signup(data: ElderlySignup):
    if data.password != data.confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    last_record_id = await database.execute(elderly.insert().values(
        name=data.name, age=data.age, gender=data.gender,
        phone=data.phone, address=data.address,
        medical=data.medical, guardian=data.guardian,
        password=data.password,
    ))
    return {"message": "Elderly signup success", "id": last_record_id}

@app.post("/guardian/signup")
async def guardian_signup(data: GuardianSignup):
    if data.password != data.confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    exists_email = await database.fetch_one(guardian.select().where(guardian.c.email == data.email))
    if exists_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    exists_phone = await database.fetch_one(guardian.select().where(guardian.c.phone == data.phone))
    if exists_phone:
        raise HTTPException(status_code=400, detail="Phone already registered")
    last_record_id = await database.execute(guardian.insert().values(
        name=data.name, email=data.email, phone=data.phone,
        address=data.address, relation=data.relation,
        password=data.password,
    ))
    return {"message": "Guardian signup success", "id": last_record_id}

@app.post("/login")
async def login(data: LoginRequest):
    user_elderly = await database.fetch_one(elderly.select().where(elderly.c.phone == data.username))
    if user_elderly and data.password == user_elderly["password"]:
        return {"role": "elderly", "user_id": user_elderly["id"]}
    user_guardian = await database.fetch_one(guardian.select().where(guardian.c.phone == data.username))
    if user_guardian and data.password == user_guardian["password"]:
        return {"role": "guardian", "user_id": user_guardian["id"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# ============================
# REQUEST CONNECT SYSTEM
# ============================

@app.post("/guardian/request")
async def guardian_request(data: GuardianRequestCreate):
    elderly_user = await database.fetch_one(elderly.select().where(elderly.c.phone == data.elderly_phone))
    if not elderly_user:
        raise HTTPException(status_code=404, detail="Elderly not found")
    existing_request = await database.fetch_one(
        guardian_requests.select().where(
            (guardian_requests.c.guardian_id == data.guardian_id)
            & (guardian_requests.c.elderly_id == elderly_user["id"])
        )
    )
    if existing_request:
        raise HTTPException(status_code=400, detail="Already requested")
    request_id = await database.execute(guardian_requests.insert().values(
        guardian_id=data.guardian_id,
        elderly_id=elderly_user["id"],
        status=RequestStatus.requested.value,
    ))
    return {"message": "Request sent", "request_id": request_id}

@app.get("/guardian/{guardian_id}/elderlies", response_model=List[ElderlyResponse])
async def get_guardian_elderlies(guardian_id: int):
    rows = await database.fetch_all(sqlalchemy.select(
        elderly.c.id.label("elderly_id"),
        elderly.c.name.label("elderly_name"),
        elderly.c.phone
    ).select_from(
        guardian_requests.join(elderly)
    ).where(
        (guardian_requests.c.guardian_id == guardian_id) &
        (guardian_requests.c.status == RequestStatus.accepted.value)
    ))
    return [ElderlyResponse(**row) for row in rows]

# ============================
# GEOFENCING
# ============================

@app.post("/geofence/set")
async def set_geofence(data: SetGeofence):
    existing_elderly = await database.fetch_one(elderly.select().where(elderly.c.id == data.elderly_id))
    if not existing_elderly:
        raise HTTPException(status_code=404, detail="Elderly not found")
    fence = await database.fetch_one(geofence.select().where(geofence.c.elderly_id == data.elderly_id))
    if fence:
        await database.execute(geofence.update().where(
            geofence.c.elderly_id == data.elderly_id
        ).values(
            latitude=data.latitude,
            longitude=data.longitude,
            radius=data.radius
        ))
        return {"message": "Geofence updated"}
    else:
        await database.execute(geofence.insert().values(
            elderly_id=data.elderly_id,
            latitude=data.latitude,
            longitude=data.longitude,
            radius=data.radius
        ))
        return {"message": "Geofence set"}

@app.post("/location/update")
async def update_location(data: LocationUpdate):
    await database.execute(elderly_location.insert().values(
        elderly_id=data.elderly_id,
        latitude=data.latitude,
        longitude=data.longitude,
        last_updated="NOW"
    ))
    fence = await database.fetch_one(geofence.select().where(geofence.c.elderly_id == data.elderly_id))
    if not fence:
        return {"inside": True, "message": "No geofence set"}
    distance = calculate_distance(data.latitude, data.longitude, fence["latitude"], fence["longitude"])
    is_inside = distance <= fence["radius"]
    await database.execute(elderly_location.update().where(
        elderly_location.c.elderly_id == data.elderly_id
    ).values(is_inside=is_inside))
    return {
        "inside": is_inside,
        "distance_meters": round(distance, 2),
        "message": "Inside safe area" if is_inside else "⚠ OUTSIDE safe area!"
    }

@app.get("/geofence/{elderly_id}")
async def get_geofence(elderly_id: int):
    fence = await database.fetch_one(geofence.select().where(geofence.c.elderly_id == elderly_id))
    if not fence:
        raise HTTPException(status_code=404, detail="No geofence set")
    return fence