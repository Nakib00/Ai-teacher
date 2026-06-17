import logging
import json
import os
from livekit.agents import function_tool, RunContext

EDUCATIONAL_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "educational_data.json")

def load_educational_data():
    try:
        with open(EDUCATIONAL_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load educational data: {e}")
        return {}

educational_data = load_educational_data()
from user_progress import save_Youtube


@function_tool()
async def get_educational_content(
    context: RunContext,
    subject: str,
    chapter_name: str
) -> str:
    """
    Get reference content for a subject and chapter to help teach students.
    subject must be one of: 'robotics', 'programming', 'ai_and_ml'
    chapter_name examples: 'Chapter 1', 'Chapter 2', 'Chapter 3'
    Use this to fetch structured topic content, examples, and questions.
    """
    try:
        processed_subject = subject.lower().strip().replace(" ", "_")
        processed_chapter = chapter_name.strip().title()

        subject_data = educational_data.get(processed_subject)
        if not subject_data:
            available = list(educational_data.keys())
            return f"Subject '{subject}' পাইনি। Available: {available}"

        chapter_content = subject_data.get(processed_chapter)
        if not chapter_content:
            available = list(subject_data.keys())
            return f"'{chapter_name}' পাইনি। Available chapters: {available}"

        logging.info(f"Fetched '{processed_chapter}' from '{processed_subject}'.")
        return json.dumps(chapter_content, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Error fetching content: {e}")
        return "Content load করতে সমস্যা হয়েছে। আবার try করো!"


@function_tool()
async def record_answer(
    context: RunContext,
    user_id: int,
    chapter: str,
    topic: str,
    question: str,
    answer: str,
    grading: int,
):
    """
    Records the student's answer to a question and its grading.
    grading: 0=cannot answer, 1=very poor, 2=poor, 3=average, 4=good, 5=excellent.
    If student cannot answer, set answer='CANNOT ANSWER' and grading=0.
    """
    try:
        logging.info(f"Recording: user={user_id}, topic='{topic}', grade={grading}")
        save_Youtube(
            user_id=user_id,
            chapter=chapter,
            topic=topic,
            question=question,
            answer=answer,
            grading=grading
        )
        return "Answer recorded successfully."
    except Exception as e:
        logging.error(f"Failed to record answer: {e}")
        return "Answer save করতে সমস্যা হয়েছে।"
