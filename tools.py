import logging
import json
import os
from livekit.agents import function_tool, RunContext

# --- Load Educational Data ---
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
    grade: str,
    subject: str,
    chapter_name: str
) -> str:
    """
    Get educational content for a specific grade, subject, and chapter.
    The grade should be like 'class_1', 'class_3', 'class_10' etc.
    The subject should be like 'fun with technology', 'robotics and coding',
    'programming and electronics', 'programming and ai basics',
    'ai and robotics', 'ai and machine learning', 'advanced ai and robotics'.
    The chapter_name should be like 'Chapter 1', 'Chapter 2'.
    """
    try:
        processed_grade = grade.lower().strip()
        processed_subject = subject.lower().strip()
        processed_chapter = chapter_name.strip().title()

        grade_data = educational_data.get(processed_grade)
        if not grade_data:
            return f"'{grade}' এর জন্য কোনো content পাইনি। অন্য class try করো!"

        subject_data = grade_data.get("subjects", {}).get(processed_subject)
        if not subject_data:
            available = list(grade_data.get("subjects", {}).keys())
            return f"'{subject}' subject পাইনি। {processed_grade}-এ আছে: {available}"

        chapter_content = subject_data.get(processed_chapter)
        if not chapter_content:
            available = [k for k in subject_data.keys() if k != "publish_date"]
            return f"'{chapter_name}' পাইনি। আছে: {available}"

        logging.info(f"Found '{processed_chapter}' in '{processed_subject}' for '{processed_grade}'.")
        return json.dumps(chapter_content, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Error fetching educational content: {e}")
        return "Content load করতে সমস্যা হয়েছে। আবার try করো!"


@function_tool()
async def search_internet(
    context: RunContext,
    query: str
) -> str:
    """
    Search the internet for information about robotics, programming, AI, or any technology topic.
    Use this when the local educational data doesn't have the answer, or when a student asks
    a question that needs current or detailed information.
    The query should be clear and specific, e.g. 'What is a servo motor in robotics?'
    """
    try:
        from google import genai
        from google.genai.types import Tool, GoogleSearch, GenerateContentConfig

        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            return "Internet search এর জন্য Google API key দরকার।"

        client = genai.Client(api_key=google_api_key)

        prompt = (
            f"You are an expert teacher for ZAN TECH, teaching robotics, programming, and AI to students from Class 1 to 12 in Bangladesh. "
            f"Answer this question clearly and in simple Bengali/English (Banglish) suitable for a student: {query}. "
            f"Keep the answer educational, accurate, and easy to understand. Use examples if helpful."
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=GenerateContentConfig(
                tools=[Tool(google_search=GoogleSearch())],
                temperature=0.7,
            )
        )

        result = response.text
        logging.info(f"Internet search completed for query: {query}")
        return result

    except Exception as e:
        logging.error(f"Internet search failed: {e}")
        return f"Internet search করতে সমস্যা হয়েছে: {str(e)}। আমি নিজের জ্ঞান থেকে উত্তর দেওয়ার চেষ্টা করছি।"


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
    Records the student's answer to a question and its grading in the progress tracker.
    grading scale: 0 = cannot answer, 1 = very poor, 2 = poor, 3 = average, 4 = good, 5 = excellent.
    If the student cannot answer, set answer to 'CANNOT ANSWER' and grading to 0.
    """
    try:
        logging.info(f"Recording answer for user {user_id} on topic '{topic}': grade={grading}")
        save_Youtube(
            user_id=user_id,
            chapter=chapter,
            topic=topic,
            question=question,
            answer=answer,
            grading=grading
        )
        return "Answer successfully recorded."
    except Exception as e:
        logging.error(f"Failed to record answer for user {user_id}: {e}")
        return "Answer save করতে সমস্যা হয়েছে।"
