import json
import os
from datetime import datetime
import logging

# Define the JSON file path in the project root
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_progress.json')

def init_progress_file():
    """Ensures the progress JSON file exists and is a valid JSON array."""
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'w') as f:
            json.dump([], f)

def save_Youtube(user_id: int, chapter: str, topic: str, question: str, answer: str):
    """Saves a user's answer to a specific question in the JSON file."""
    new_record = {
        'user_id': user_id,
        'chapter': chapter,
        'topic': topic,
        'question': question,
        'answer': answer,
        'timestamp': datetime.now().isoformat()
    }
    try:
        with open(PROGRESS_FILE, 'r+') as f:
            try:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
            data.append(new_record)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
    except Exception as e:
        logging.error(f"Failed to save to JSON file: {e}")

init_progress_file()