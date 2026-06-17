import logging
import json
import os
from livekit.agents import function_tool, RunContext

from user_progress import save_Youtube


@function_tool()
async def record_answer(
    context: RunContext,
    user_id: int,
    topic: str,
    question: str,
    answer: str,
    grading: int,
):
    """
    Records the student's answer to a question with a grade.
    grading: 0=cannot answer, 1=very poor, 2=poor, 3=average, 4=good, 5=excellent.
    If the student says they don't know, set answer='CANNOT ANSWER' and grading=0.
    Use this after each question-answer exchange to track student progress.
    """
    try:
        logging.info(f"Recording: topic='{topic}', grade={grading}, answer='{answer[:30]}...'")
        save_Youtube(
            user_id=user_id,
            chapter=topic,
            topic=topic,
            question=question,
            answer=answer,
            grading=grading
        )
        return "Recorded."
    except Exception as e:
        logging.error(f"Failed to record: {e}")
        return "Could not save."
