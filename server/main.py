from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, EmailStr
from typing import Optional
import sqlalchemy
from databases import Database

DATABASE_URL = "sqlite:///./elderly.db"

metadata = sqlalchemy.MetaData()
database = Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

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

