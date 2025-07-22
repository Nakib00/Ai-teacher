from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

def generate_token(user_id: int):
    room = f"user_{user_id}"

    # Create the video grant
    video_grant = api.VideoGrants(room_join=True, room=room)

    # Create token and pass grants at once
    token = api.AccessToken(
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        identity=str(user_id),
        name=f"user_{user_id}",
        grants={"video": video_grant}
    )

    return {"room": room, "token": token.to_jwt()}
