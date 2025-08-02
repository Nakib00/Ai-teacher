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
    def __init__(self, agent_instruction: str, user_id: int) -> None:
        super().__init__(
            instructions=agent_instruction,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede", # Note: You may want different voices for different personas
                temperature=0.8,
            ),
            tools=[get_educational_content, record_answer], # Add the new tool
        )
        self.user_id = user_id


async def entrypoint(ctx: agents.JobContext):
    room_name = ctx.room.name
    logging.info(f"Agent entering room: {room_name}")
    
    user_id = 0
    persona_id = 'namira'  # Default persona

    try:
        # Extract user_id and persona_id from the room name
        # Format: user_{user_id}_teacher_{persona_id}
        parts = room_name.split('_teacher_')
        user_info = parts[0]
        persona_id = parts[1]
        user_id = int(user_info.split('user_')[1])
        
        logging.info(f"Initialized with User ID: {user_id} and Persona: {persona_id}")
        agent_instruction, session_instruction_template = load_persona_from_file(persona_id)

    except (IndexError, FileNotFoundError, ValueError) as e:
        logging.warning(f"Could not determine persona or user from room name '{room_name}'. Reason: {e}. Using default 'namira' persona.")
        agent_instruction, session_instruction_template = load_persona_from_file('namira')

    # Add user_id to the session instructions so the LLM knows which user to track
    session_instruction = f"The user's ID is {user_id}. You MUST use this ID when calling the `record_answer` tool.\n\n{session_instruction_template}"


    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=Assistant(agent_instruction, user_id=user_id), # Pass user_id to agent
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(instructions=session_instruction)

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))