import json
import os
from datetime import datetime

def save_user_progress(user_id: str, subject: str, chapter: str, topic: str, question: str, answer: str, is_correct: bool):
    """
    Saves the user's progress to a JSON file.

    Args:
        user_id (str): The ID of the user.
        subject (str): The subject the user is studying.
        chapter (str): The chapter the user is in.
        topic (str): The topic being discussed.
        question (str): The question that was asked.
        answer (str): The user's answer to the question.
        is_correct (bool): Whether the user's answer was correct.
    """
    file_path = f"user_progress_{user_id}.json"
    progress_data = {
        "subject": subject,
        "chapter": chapter,
        "topic": topic,
        "question": question,
        "user_answer": answer,
        "is_correct": is_correct,
        "timestamp": datetime.now().isoformat()
    }

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([progress_data], f, indent=4)
    else:
        with open(file_path, 'r+') as f:
            data = json.load(f)
            data.append(progress_data)
            f.seek(0)
            json.dump(data, f, indent=4)