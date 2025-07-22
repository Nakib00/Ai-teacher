from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

def generate_token(user_id: int):
    room = f"user_{user_id}"
    
    # Define the permissions (grants) for the user
    video_grant = api.VideoGrants(
        room_join=True,
        room=room,
    )

    # Use the builder pattern to construct the token
    token = api.AccessToken(os.getenv("API7r2xQnvDNeMd"), os.getenv("HQunvS5D6GMOsvxDTFeftuRxNfY31pSWMvZDUA0TVWUA")) \
        .with_identity(str(user_id)) \
        .with_name(f"user_{user_id}") \
        .with_grants(video_grant)

    # Return the final signed JWT token
    return {"room": room, "token": token.to_jwt()}