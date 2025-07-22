from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_user, get_user_by_email
from livekit_service import generate_token
from jose import jwt
import os

app = FastAPI()

JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-key")
JWT_ALGORITHM = "HS256"

class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenRequest(BaseModel):
    user_id: int

@app.post("/register")
def register(data: RegisterRequest):
    existing_user = get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(data.name, data.email, data.phone, data.address, data.password)

@app.post("/login")
def login(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or user[5] != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token
    jwt_token = jwt.encode({"user_id": user[0], "email": user[2]}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Generate LiveKit token
    livekit_token = generate_token(user[0])

    return {
        "user_id": user[0],
        "name": user[1],
        "email": user[2],
        "token": jwt_token,
        "livekit_token": livekit_token["token"],
        "room": livekit_token["room"]
    }

@app.post("/token")
def get_room_token(data: TokenRequest):
    return generate_token(data.user_id)
