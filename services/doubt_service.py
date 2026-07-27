import os
from google import genai
from google.genai import types

class DoubtSolverService:
    @staticmethod
    def answer_doubt(lesson_title: str, lesson_content: str, question: str) -> str:
        """Sends the lesson context and student question to Gemini AI to generate an instant explanation."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Doubt solver service is currently offline (API Key missing)."

        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are an encouraging, expert AI tutor for the online platform SkillPro. "
            "Help the student understand their doubt concisely based on the lesson context provided. "
            "Keep answers clear, friendly, and structured in under 150 words."
        )

        prompt = f"""
        [LESSON TITLE]: {lesson_title}
        [LESSON CONTENT]: {lesson_content}

        [STUDENT QUESTION]: {question}
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            return f"Unable to process doubt right now: {str(e)}"