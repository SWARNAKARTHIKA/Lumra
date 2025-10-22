import enum
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, EmailStr,Field
from typing import Optional, List,Annotated
import sqlalchemy
from databases import Database

DATABASE_URL = "sqlite:///./elderly.db"

metadata = sqlalchemy.MetaData()
database = Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
class RequestStatus(str, enum.Enum):
    requested = "requested"
    accepted = "accepted"
    rejected = "rejected"
# Elderly table (existing)
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

# Guardian table (new)
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

metadata.create_all(engine)

app = FastAPI()


# Pydantic model for Elderly signup
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

# Pydantic models for Guardian signup
class GuardianSignup(BaseModel):
    name: constr(min_length=1)
    email: EmailStr
    phone: constr(min_length=1, max_length=15)
    address: constr(min_length=1)
    relation: constr(min_length=1)
    password: constr(min_length=1)
    confirm: constr(min_length=1)

# Login request shared by both Elderly and Guardian
class LoginRequest(BaseModel):
    username: constr(min_length=1)  # can be phone or email
    password: constr(min_length=1)

class GuardianRequestCreate(BaseModel):
    elderly_phone: constr(min_length=1)  # input elderly phone
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

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Elderly signup route (store plain password)
@app.post("/elderly/signup")
async def elderly_signup(data: ElderlySignup):
    if data.password != data.confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    query = elderly.insert().values(
        name=data.name,
        age=data.age,
        gender=data.gender,
        phone=data.phone,
        address=data.address,
        medical=data.medical,
        guardian=data.guardian,
        password=data.password,  # store plain password
    )
    last_record_id = await database.execute(query)
    return {"message": f"Elderly user {data.name} signed up successfully.", "id": last_record_id}

# Guardian signup route (store plain password)
@app.post("/guardian/signup")
async def guardian_signup(data: GuardianSignup):
    if data.password != data.confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if email or phone already exists
    query_email = guardian.select().where(guardian.c.email == data.email)
    exists_email = await database.fetch_one(query_email)
    if exists_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    query_phone = guardian.select().where(guardian.c.phone == data.phone)
    exists_phone = await database.fetch_one(query_phone)
    if exists_phone:
        raise HTTPException(status_code=400, detail="Phone already registered")

    query = guardian.insert().values(
        name=data.name,
        email=data.email,
        phone=data.phone,
        address=data.address,
        relation=data.relation,
        password=data.password,  # store plain password
    )
    last_record_id = await database.execute(query)
    return {"message": f"Guardian user {data.name} signed up successfully.", "id": last_record_id}

# Login route checks both tables for username (phone or email)
@app.post("/login")
async def login(data: LoginRequest):
    # Try Elderly first (match by phone)
    query_elderly = elderly.select().where(elderly.c.phone == data.username)
    user_elderly = await database.fetch_one(query_elderly)

    if user_elderly and data.password == user_elderly["password"]:
        return {
            "message": f"Welcome back, {user_elderly['name']}!",
            "role": "elderly",
            "user_id": user_elderly["id"],
        }

    # Try Guardian next (match by phone ONLY)
    query_guardian = guardian.select().where(guardian.c.phone == data.username)
    user_guardian = await database.fetch_one(query_guardian)

    if user_guardian and data.password == user_guardian["password"]:
        return {
            "message": f"Welcome back, {user_guardian['name']}!",
            "role": "guardian",
            "user_id": user_guardian["id"],
        }

    # No match or wrong password
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/guardian/request")
async def guardian_request(data: GuardianRequestCreate):
    # Find elderly by phone
    query_elderly = elderly.select().where(elderly.c.phone == data.elderly_phone)
    elderly_user = await database.fetch_one(query_elderly)
    if not elderly_user:
        raise HTTPException(status_code=404, detail="Elderly user not found")

    # Check if request already exists
    query_existing = guardian_requests.select().where(
        (guardian_requests.c.guardian_id == data.guardian_id) &
        (guardian_requests.c.elderly_id == elderly_user["id"])
    )
    existing_request = await database.fetch_one(query_existing)
    if existing_request:
        raise HTTPException(status_code=400, detail="Request already exists")

    # Insert new request
    query_insert = guardian_requests.insert().values(
        guardian_id=data.guardian_id,
        elderly_id=elderly_user["id"],
        status=RequestStatus.requested.value,
    )
    request_id = await database.execute(query_insert)
    return {"message": "Request sent successfully", "request_id": request_id}

# 2. Elderly views incoming requests
@app.get("/elderly/{elderly_id}/requests", response_model=List[ElderlyRequestResponse])
async def view_elderly_requests(elderly_id: int):
    query = sqlalchemy.select(
        guardian_requests.c.id.label("request_id"),
        guardian.c.id.label("guardian_id"),
        guardian.c.name.label("guardian_name"),
        guardian_requests.c.status,
    ).select_from(
        guardian_requests.join(guardian, guardian_requests.c.guardian_id == guardian.c.id)
    ).where(
        (guardian_requests.c.elderly_id == elderly_id) & 
        (guardian_requests.c.status == RequestStatus.requested.value)
    )
    rows = await database.fetch_all(query)
    return [ElderlyRequestResponse(**row) for row in rows]

# 3. Elderly accepts or rejects request
@app.post("/elderly/request/respond")
async def respond_to_request(data: GuardianRequestUpdate):
    # Fetch the request
    query = guardian_requests.select().where(guardian_requests.c.id == data.request_id)
    request = await database.fetch_one(query)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request["status"] != RequestStatus.requested.value:
        raise HTTPException(status_code=400, detail="Request already processed")

    new_status = RequestStatus.accepted.value if data.action == "accept" else RequestStatus.rejected.value
    query_update = guardian_requests.update().where(
        guardian_requests.c.id == data.request_id
    ).values(status=new_status)
    await database.execute(query_update)
    return {"message": f"Request {data.action}ed successfully"}

# 4. Given guardian id, list accepted elderlies (limit none)
@app.get("/guardian/{guardian_id}/elderlies", response_model=List[ElderlyResponse])
async def get_guardian_elderlies(guardian_id: int):
    query = sqlalchemy.select(
        elderly.c.id.label("elderly_id"),
        elderly.c.name.label("elderly_name"),
        elderly.c.phone
    ).select_from(
        guardian_requests.join(elderly, guardian_requests.c.elderly_id == elderly.c.id)
    ).where(
        (guardian_requests.c.guardian_id == guardian_id) &
        (guardian_requests.c.status == RequestStatus.accepted.value)
    )
    rows = await database.fetch_all(query)
    return [ElderlyResponse(**row) for row in rows]

# 5. Given elderly id, show up to 7 accepted guardians
@app.get("/elderly/{elderly_id}/guardians", response_model=List[GuardianResponse])
async def get_elderly_guardians(elderly_id: int):
    query = sqlalchemy.select(
        guardian.c.id.label("guardian_id"),
        guardian.c.name.label("guardian_name"),
        guardian.c.relation,
    ).select_from(
        guardian_requests.join(guardian, guardian_requests.c.guardian_id == guardian.c.id)
    ).where(
        (guardian_requests.c.elderly_id == elderly_id) &
        (guardian_requests.c.status == RequestStatus.accepted.value)
    ).limit(7)
    rows = await database.fetch_all(query)
    return [GuardianResponse(**row) for row in rows]    

