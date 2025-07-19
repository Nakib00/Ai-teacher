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
    topic: str
) -> str:
    """
    Get educational content for a specific grade, subject, and topic for a student.
    The grade should be like 'class_1', 'class_2', etc.
    The subject should be 'bangla', 'english', or 'math'.
    The topic should be a keyword from the lesson, like 'Vowels' or 'Subtraction'.
    """
    try:
        grade_data = educational_data.get(grade.lower())
        if not grade_data:
            return f"I don't have a book for {grade} right now. Let's try another class!"

        subject_data = grade_data.get(subject.lower())
        if not subject_data:
            return f"I can't find the {subject} book for {grade}. Should we try another subject?"

        # A simple search to see if the topic keyword exists in the content
        if topic.lower() in subject_data.get("topic", "").lower():
            return json.dumps(subject_data)
        else:
             return f"I couldn't find the topic '{topic}' in the {subject} book for {grade}. Maybe we can try another topic?"

    except Exception as e:
        logging.error(f"Error fetching educational content: {e}")
        return "Oops! My magic book seems to be stuck. Can we try again?"


@function_tool()
async def get_weather(
    context: RunContext,
    city: str) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}." 

@function_tool()
async def search_web(
    context: RunContext, 
    query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."