# AI Teacher Project

An interactive learning platform featuring a conversational AI tutor named **Namira**. This project uses **LiveKit** for real-time video/audio and a **FastAPI** backend to manage users and authentication.

---

## 📌 Project Overview

The AI Teacher is built with a Python backend that serves two primary functions:

- **FastAPI Web Server**  
  Handles user authentication (register/login) and provides tokens to connect to the video service.

- **LiveKit Agent**  
  Manages the AI tutor’s logic, interacts with users in real-time over video, processes their questions, and gives helpful responses.

> Uses **SQLite** for data storage and **Google’s AI API** for the AI magic!

---

## 🔧 Prerequisites

Make sure you have these ready:

- ✅ Python 3.8+ → [Download Python](https://www.python.org/downloads/)
- ✅ Git → [Download Git](https://git-scm.com/downloads)
- ✅ LiveKit Account → [LiveKit Cloud](https://cloud.livekit.io/)
- ✅ Google API Key → From [Google AI Studio](https://makersuite.google.com/)

---

## 🚀 Setup Instructions

### 1. Clone the Repo

```bash
git clone <your-repository-url>
cd <your-project-directory>
```

### 2. Create Virtual Environment

```bash
# Create it
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate

# macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Environment Variables
Create a file named .env in the root directory and add:

```bash
# LiveKit Credentials
LIVEKIT_API_KEY=API...
LIVEKIT_API_SECRET=...

# Google API Key
GOOGLE_API_KEY=AIza...

# JWT Secret Key
JWT_SECRET=your-super-secret-key
```

## Running the Application
You'll need two terminals open:

### Terminal 1: FastAPI Web Server
```bash
uvicorn main:app --reload
```
Runs at: http://127.0.0.1:8000

### Terminal 2: LiveKit Agent Server
```bash
python ./agent.py dev
```
Connects to your LiveKit cloud project and waits for users to join the room.

## API Endpoints
### Create a new user.

URL: http://127.0.0.1:8000/register

Body:
```bash
    {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "1234567890",
    "address": "123 Test Street",
    "password": "a-secure-password"
    }
```

Success Response:
```bash
{
  "success": true,
  "status": 200,
  "message": "Registration successful",
  "data": {
    "user": {
      "user_id": 1,
      "name": "Test User",
      "email": "test@example.com",
      "token": "your_jwt_token",
      "livekit_token": "your_livekit_token",
      "room": "user_1"
    }
  },
  "errors": null
}
```

500 Internal Server Error (Could not create user)
```bash
{
    "success": false,
    "status": 500,
    "message": "Could not create user",
    "data": null,
    "errors": {
        "detail": "Could not create user"
    }
}
```

400 Bad Request (Email already registered)
```bash
{
  "success": false,
  "status": 400,
  "message": {
    "email": [
      "The email has already been taken."
    ]
  },
  "data": null,
  "errors": {
    "email": [
      "The email has already been taken."
    ]
  }
}
```

### POST /login
Authenticate user and get tokens.

URL: http://127.0.0.1:8000/login

Body:
```bash
{
  "email":"test@gmail.com",
  "password":12345678
}
```
Success Response:
```bash
{
  "success": true,
  "status": 200,
  "message": "Login successful",
  "data": {
    "user": {
      "user_id": 1,
      "name": "Test User",
      "email": "test@example.com",
      "token": "your_jwt_token",
      "livekit_token": "your_livekit_token",
      "room": "user_1"
    }
  },
  "errors": null
}
```

Error:
```bash
{
  "success": false,
  "status": 401,
  "message": "Invalid email or password",
  "data": null,
  "errors": {
    "detail": "Invalid email or password"
  }
}
```





