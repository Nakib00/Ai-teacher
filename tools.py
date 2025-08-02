import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import json
from educational_data import educational_data

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
        grade_data = educational_data.get(grade.lower())
        if not grade_data:
            return f"I don't have any books for {grade} right now. Let's try another class!"

        subject_data = grade_data.get("subjects", {}).get(subject.lower())
        if not subject_data:
            return f"I can't find the {subject} book for {grade}. Let's try another subject."

        chapter_content = subject_data.get(chapter_name)
        if not chapter_content:
            return f"I couldn't find '{chapter_name}' in the {subject} book for {grade}. Maybe we can try another chapter?"

        logging.info(f"Found '{chapter_name}' in {subject} for {grade}.")
        return json.dumps(chapter_content)

    except Exception as e:
        logging.error(f"Error fetching educational content: {e}")
        return "Oops! My magic book seems to be stuck. Can we try again?"