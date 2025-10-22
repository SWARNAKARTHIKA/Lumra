from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr
from typing import Optional

import sqlalchemy
from databases import Database

DATABASE_URL = "sqlite:///./elderly.db"

# SQLAlchemy metadata and engine
metadata = sqlalchemy.MetaData()
database = Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Define the elderly table
elderly = sqlalchemy.Table(
    "elderly",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("age", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("gender", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("phone", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("address", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("medical", sqlalchemy.String),
    sqlalchemy.Column("guardian", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
)

# Create tables
metadata.create_all(engine)

app = FastAPI()

class ElderlySignup(BaseModel):
    name: constr(min_length=1)
    age: int = Field(..., gt=0, lt=150)
    gender: constr(min_length=1)
    phone: constr(min_length=7, max_length=15)
    address: constr(min_length=1)
    medical: Optional[str] = None
    guardian: constr(min_length=1)
    password: constr(min_length=6)
    confirm: constr(min_length=6)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/elderly/signup")
async def signup(data: ElderlySignup):
    if data.password != data.confirm:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Save to DB
    query = elderly.insert().values(
        name=data.name,
        age=data.age,
        gender=data.gender,
        phone=data.phone,
        address=data.address,
        medical=data.medical,
        guardian=data.guardian,
        password=data.password,  # In production, hash passwords!
    )
    last_record_id = await database.execute(query)

    return {"message": f"User {data.name} signed up successfully.", "id": last_record_id}
