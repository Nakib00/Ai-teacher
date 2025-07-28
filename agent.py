import os
import importlib.util
import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, google
from tools import get_educational_content

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

def load_persona_from_file(persona_id: str):
    """Dynamically loads persona instructions from a file."""
    # Ensure persona_id is lowercase to match filenames
    persona_id = persona_id.lower()
    persona_file = os.path.join("personas", f"{persona_id}.py")

    logging.info(f"Attempting to load persona from: {persona_file}")

    if not os.path.exists(persona_file):
        logging.error(f"Persona file not found: {persona_file}")
        raise FileNotFoundError(f"Persona file not found: {persona_file}")

    spec = importlib.util.spec_from_file_location(persona_id, persona_file)
    persona_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(persona_module)
    
    logging.info(f"Successfully loaded persona: {persona_id}")
    return persona_module.AGENT_INSTRUCTION, persona_module.SESSION_INSTRUCTION

class Assistant(Agent):
    def __init__(self, agent_instruction: str) -> None:
        super().__init__(
            instructions=agent_instruction,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede", # Note: You may want different voices for different personas
                temperature=0.8,
            ),
            tools=[get_educational_content],
        )

async def entrypoint(ctx: agents.JobContext):
    room_name = ctx.room.name
    logging.info(f"Agent entering room: {room_name}")

    try:
        # Extract the persona_id from the room name (e.g., user_3_teacher_ahmed -> ahmed)
        persona_id = room_name.split('_teacher_')[1]
        agent_instruction, session_instruction = load_persona_from_file(persona_id)
    except (IndexError, FileNotFoundError) as e:
        logging.warning(f"Could not determine persona from room name '{room_name}'. Reason: {e}. Using default 'namira' persona.")
        # Fallback to a default persona
        agent_instruction, session_instruction = load_persona_from_file('namira')


    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=Assistant(agent_instruction),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(instructions=session_instruction)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))