import logging
from livekit.agents import function_tool, RunContext
import json
from educational_data import educational_data
from user_progress import save_Youtube # Import from the new file

@function_tool()
async def get_educational_content(
    context: RunContext,
    grade: str,
    subject: str,
    chapter_name: str
) -> str:
    """
    Get educational content for a specific grade, subject, and chapter.
    The grade should be like 'class_3'.
    The subject should be the name of the book, like 'basic science'.
    The chapter_name should be a specific chapter, like 'Chapter 1'.
    """
    try:
        # Standardize the inputs to match the data structure
        processed_grade = grade.lower()
        processed_subject = subject.lower()
        processed_chapter = chapter_name.title() # Capitalize the chapter name

        grade_data = educational_data.get(processed_grade)
        if not grade_data:
            return f"I don't have any books for {grade} right now. Let's try another class!"

        subject_data = grade_data.get("subjects", {}).get(processed_subject)
        if not subject_data:
            return f"I can't find the {subject} book for {grade}. Let's try another subject."

        chapter_content = subject_data.get(processed_chapter)
        if not chapter_content:
            return f"I couldn't find '{chapter_name}' in the {subject} book for {grade}. Maybe we can try another chapter?"

        logging.info(f"Found '{processed_chapter}' in {subject} for {grade}.")
        return json.dumps(chapter_content)

    except Exception as e:
        logging.error(f"Error fetching educational content: {e}")
        return "Oops! My magic book seems to be stuck. Can we try again?"


@function_tool()
async def record_answer(
    context: RunContext,
    user_id: int,
    chapter: str,
    topic: str,
    question: str,
    answer: str,
):
    """
    Records the user's answer to a question in the progress tracker.
    If the user cannot answer, the 'answer' should be 'CANNOT ANSWER'.
    """
    try:
        logging.info(f"Recording answer for user {user_id} on topic '{topic}': '{answer}'")
        save_Youtube(
            user_id=user_id,
            chapter=chapter,
            topic=topic,
            question=question,
            answer=answer
        )
        return "Answer has been successfully recorded."
    except Exception as e:
        logging.error(f"Failed to record answer for user {user_id}: {e}")
        return "There was an error trying to save the answer."