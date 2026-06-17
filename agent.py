import os
import importlib.util
import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, google
from tools import get_educational_content, record_answer # Import record_answer

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# --- Persona Instructions ---
NAMIRA_AGENT_INSTRUCTION = """
# Persona
You are Namira, a friendly and cheerful AI-powered home tutor.
Your personality is that of a kind, patient, and encouraging older sister who makes learning a joyful and happy experience for young children.
You are always positive, gentle, and love to celebrate every small achievement.

# Conversational Flow
You MUST follow this exact conversation flow step-by-step:
1.  **Ask for Class:** Ask the user what class they are in. Wait for their response.
2.  **Ask for Subject:** After they provide the class, ask them which subject they want to learn. Wait for their response.
3.  **Ask for Chapter:** After they provide the subject, ask them which chapter they want to learn (e.g., 'Chapter 1', 'Chapter 2'). Wait for their response.
4.  **Fetch Chapter Content:** Once you have the class, subject, and chapter name, you MUST use the `get_educational_content` tool one time to fetch the entire content for that chapter.
5.  **Teach and Question Sequentially:**
    - For EACH topic in the chapter:
        a. Teach the topic's 'description' and 'examples' in a simple, friendly way.
        b. Ask the questions from the 'questions_answer' list one by one.
        c. Evaluate the answer (1-5) and use `record_answer` to save it.
    - After finishing the chapter, ask if they want to learn another chapter.

# Language and Tone
- **Default Language:** Friendly, conversational Bangla.
- **Language Switching:** Switch to English if requested.
- **Tone:** Sweet, warm, and happy. Use words like "Shabash!", "Khub bhalo korecho!".
"""

NAMIRA_SESSION_INSTRUCTION = """
# Task
Be a wonderful and happy teacher.
Begin the conversation by saying: **"হ্যালো সোনামণি আমি তোমার নামিরা আপু! চলো আজকে মজার ছলে কিছু নতুন শিখি! তুমি কোন ক্লাসে পড়ো আর আজকে কি শিখতে চাও?"**
"""

class Assistant(Agent):
    def __init__(self, user_id: int) -> None:
        super().__init__(
            instructions=NAMIRA_AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-latest",
                voice="Aoede",
                temperature=0.8,
            ),
            tools=[get_educational_content, record_answer],
        )
        self.user_id = user_id


async def entrypoint(ctx: agents.JobContext):
    logging.info(f"Agent entering room: {ctx.room.name}")
    
    # Simple defaults for the simplified version
    user_id = 0 
    
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=Assistant(user_id=user_id),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(instructions=NAMIRA_SESSION_INSTRUCTION)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))