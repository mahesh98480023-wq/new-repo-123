import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://appuser:apppassword@localhost:3306/userdb"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # For a simple demo, create the table at startup.
    # Use Alembic migrations for production applications.
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE
            )
        """))
    yield

app = FastAPI(title="User Management API", version="1.0.0", lifespan=lifespan)

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=255)

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/api/users")
def list_users():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, name, email FROM users ORDER BY id DESC")
        ).mappings().all()
        return [dict(row) for row in rows]

@app.post("/api/users", status_code=201)
def create_user(user: UserCreate):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text("INSERT INTO users (name, email) VALUES (:name, :email)"),
                {"name": user.name, "email": user.email}
            )
            return {"id": result.lastrowid, "name": user.name, "email": user.email}
    except Exception as exc:
        if "Duplicate entry" in str(exc):
            raise HTTPException(status_code=409, detail="Email already exists")
        raise
