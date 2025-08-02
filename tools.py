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
    version: str,
    subject: str,
    topic: str
) -> str:
    """
    Get educational content for a specific grade, version, subject, and topic.
    The grade should be like 'class_3'.
    The version should be the language medium, like 'english'.
    The subject should be the name of the book, like 'basic science'.
    The topic should be a specific lesson title, like 'Different Parts of Plant'.
    """
    try:
        # Navigate through the data structure
        grade_data = educational_data.get(grade.lower())
        if not grade_data:
            return f"I don't have any books for {grade} right now. Let's try another class!"

        version_data = grade_data.get("version", {}).get(version.lower())
        if not version_data:
            return f"I can't find the {version} version books for {grade}. Should we try another version?"

        subject_data = version_data.get(subject.lower())
        if not subject_data:
            return f"I can't find the {subject} book in {version} version for {grade}. Let's try another subject."

        # Search for the topic within all chapters of the subject
        topic_to_find = topic.lower()
        for chapter_name, chapter_content in subject_data.items():
            if isinstance(chapter_content, dict) and "topics" in chapter_content:
                for topic_title, topic_details in chapter_content.get("topics", {}).items():
                    if topic_title.lower() == topic_to_find:
                        logging.info(f"Found topic '{topic}' in {subject} for {grade}.")
                        return json.dumps(topic_details)

        # If the loop completes without finding the topic
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