import json
import os
import logging
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types
from user_progress import save_Youtube

load_dotenv()
logging.basicConfig(level=logging.WARNING)

EDUCATIONAL_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "educational_data.json")

def load_educational_data():
    try:
        with open(EDUCATIONAL_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load educational data: {e}")
        return {}

educational_data = load_educational_data()

def get_educational_content(grade: str, subject: str, chapter_name: str) -> str:
    processed_grade = grade.lower()
    processed_subject = subject.lower()
    processed_chapter = chapter_name.title()

    grade_data = educational_data.get(processed_grade)
    if not grade_data:
        return f"I don't have any books for {grade} right now. Let's try another class!"

    subject_data = grade_data.get("subjects", {}).get(processed_subject)
    if not subject_data:
        return f"I can't find the {subject} book for {grade}. Let's try another subject."

    chapter_content = subject_data.get(processed_chapter)
    if not chapter_content:
        return f"I couldn't find '{chapter_name}' in the {subject} book for {grade}. Maybe we can try another chapter?"

    return json.dumps(chapter_content)

def record_answer(user_id: int, chapter: str, topic: str, question: str, answer: str, grading: int) -> str:
    try:
        save_Youtube(user_id=user_id, chapter=chapter, topic=topic,
                     question=question, answer=answer, grading=grading)
        return "Answer has been successfully recorded."
    except Exception as e:
        return f"There was an error trying to save the answer: {e}"

TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="get_educational_content",
            description="Get educational content for a specific grade, subject, and chapter.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "grade": types.Schema(type=types.Type.STRING, description="e.g. 'class_3'"),
                    "subject": types.Schema(type=types.Type.STRING, description="e.g. 'basic science'"),
                    "chapter_name": types.Schema(type=types.Type.STRING, description="e.g. 'Chapter 1'"),
                },
                required=["grade", "subject", "chapter_name"],
            ),
        ),
        types.FunctionDeclaration(
            name="record_answer",
            description="Records the user's answer to a question and its grading.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "user_id": types.Schema(type=types.Type.INTEGER),
                    "chapter": types.Schema(type=types.Type.STRING),
                    "topic": types.Schema(type=types.Type.STRING),
                    "question": types.Schema(type=types.Type.STRING),
                    "answer": types.Schema(type=types.Type.STRING),
                    "grading": types.Schema(type=types.Type.INTEGER, description="Score from 1-5, 0 if cannot answer"),
                },
                required=["user_id", "chapter", "topic", "question", "answer", "grading"],
            ),
        ),
    ])
]

SYSTEM_INSTRUCTION = """
# Persona
You are Namira, a friendly and cheerful AI-powered home tutor.
Your personality is that of a kind, patient, and encouraging older sister who makes learning a joyful and happy experience for young children.
You are always positive, gentle, and love to celebrate every small achievement.

# Conversational Flow
You MUST follow this exact conversation flow step-by-step:
1. Ask for Class: Ask the user what class they are in. Wait for their response.
2. Ask for Subject: After they provide the class, ask them which subject they want to learn. Wait for their response.
3. Ask for Chapter: After they provide the subject, ask them which chapter they want to learn. Wait for their response.
4. Fetch Chapter Content: Once you have the class, subject, and chapter name, you MUST use the get_educational_content tool to fetch the entire content for that chapter.
5. Teach and Question Sequentially:
   - For EACH topic in the chapter:
     a. Teach the topic's description and examples in a simple, friendly way.
     b. Ask the questions from the questions_answer list one by one.
     c. Evaluate the answer (1-5) and use record_answer to save it (user_id=0).
   - After finishing the chapter, ask if they want to learn another chapter.

# Language and Tone
- Default Language: Friendly, conversational Bangla.
- Language Switching: Switch to English if requested.
- Tone: Sweet, warm, and happy. Use words like "Shabash!", "Khub bhalo korecho!".
"""

TOOL_DISPATCH = {
    "get_educational_content": get_educational_content,
    "record_answer": record_answer,
}

def handle_tool_calls(response):
    tool_results = []
    for part in response.candidates[0].content.parts:
        if part.function_call:
            fn = part.function_call
            func = TOOL_DISPATCH.get(fn.name)
            if func:
                result = func(**dict(fn.args))
                tool_results.append(
                    types.Part.from_function_response(name=fn.name, response={"result": result})
                )
    return tool_results

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not set in .env file.")
        return

    client = genai.Client(api_key=api_key)
    history = []

    greeting = "হ্যালো সোনামণি আমি তোমার নামিরা আপু! চলো আজকে মজার ছলে কিছু নতুন শিখি! তুমি কোন ক্লাসে পড়ো?"
    print(f"\nNamira: {greeting}\n")
    history.append(types.Content(role="model", parts=[types.Part.from_text(greeting)]))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=TOOLS,
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        history.append(types.Content(role="user", parts=[types.Part.from_text(user_input)]))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=history,
            config=config,
        )

        while response.candidates[0].content.parts and any(
            p.function_call for p in response.candidates[0].content.parts
        ):
            history.append(response.candidates[0].content)
            tool_results = handle_tool_calls(response)
            history.append(types.Content(role="user", parts=tool_results))
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=history,
                config=config,
            )

        reply = response.text
        history.append(types.Content(role="model", parts=[types.Part.from_text(reply)]))
        print(f"\nNamira: {reply}\n")

if __name__ == "__main__":
    main()
