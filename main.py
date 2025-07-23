from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import (
    create_user, 
    get_user_by_email, 
    get_all_conversations, 
    get_conversations_by_user_id
)
from livekit_service import generate_token
from jose import jwt
import os

app = FastAPI()

JWT_SECRET = os.getenv("JWT_SECRET")
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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status": exc.status_code,
            "message": exc.detail,
            "data": None,
            "errors": exc.detail if isinstance(exc.detail, dict) else {"detail": exc.detail}
        },
    )

@app.post("/register")
def register(data: RegisterRequest):
    existing_user = get_user_by_email(data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail={"email": ["The email has already been taken."]})
    
    user = create_user(data.name, data.email, data.phone, data.address, data.password)
    
    if not user:
        raise HTTPException(status_code=500, detail="Could not create user")

    # Generate JWT token for your app's authentication
    jwt_token = jwt.encode({"user_id": user[0], "email": user[2]}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Generate LiveKit data
    livekit_data = generate_token(user[0])

    return {
        "success": True,
        "status": 200,
        "message": "Registration successful",
        "data": {
            "user": {
                "user_id": user[0],
                "name": user[1],
                "email": user[2],
                "token": jwt_token,
                "livekit_token": livekit_data["token"],
                "room": livekit_data["room"]
            }
        },
        "errors": None
    }


@app.post("/login")
def login(data: LoginRequest):
    user = get_user_by_email(data.email)
    if not user or user[5] != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate JWT token for your app's authentication
    jwt_token = jwt.encode({"user_id": user[0], "email": user[2]}, JWT_SECRET, algorithm=JWT_ALGORITHM)

    # Generate LiveKit data
    livekit_data = generate_token(user[0])

    return {
        "success": True,
        "status": 200,
        "message": "Login successful",
        "data": {
            "user": {
                "user_id": user[0],
                "name": user[1],
                "email": user[2],
                "token": jwt_token,
                "livekit_token": livekit_data["token"],
                "room": livekit_data["room"]
            }
        },
        "errors": None
    }

@app.post("/token")
def get_room_token(data: TokenRequest):
    return generate_token(data.user_id)

@app.get("/conversations")
def get_all_conversations_api():
    conversations = get_all_conversations()
    return {
        "success": True,
        "status": 200,
        "message": "Conversations retrieved successfully",
        "data": {
            "conversations": conversations
        },
        "errors": None
    }

@app.get("/conversations/{user_id}")
def get_conversations_by_user_id_api(user_id: int):
    conversations = get_conversations_by_user_id(user_id)
    return {
        "success": True,
        "status": 200,
        "message": "User conversations retrieved successfully",
        "data": {
            "conversations": conversations
        },
        "errors": None
    }