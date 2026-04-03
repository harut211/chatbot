import os
from google import genai
from typing import List, Dict, Optional


class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("MODEL_NAME", "models/gemini-2.5-flash")

        self.system_prompt = (
            "You must answer in maximum 30 words. The answer must be clean and concise."
        )

    def build_prompt(
        self,
        user_input: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        prompt = f"System: {self.system_prompt}\n\n"

        if history:
            for msg in history:
                role = msg.get("role", "")
                content = msg.get("content", "")
                prompt += f"{role.capitalize()}: {content}\n"

        prompt += f"User: {user_input}\nAssistant:"
        return prompt

    def generate_response(
        self,
        user_input: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        prompt = self.build_prompt(user_input, history)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        return (response.text or "").strip()

    def build_grounded_prompt(
        self,
        room_context: str,
        user_question: str,
        target_language: str,
    ) -> str:
        """
        Construct a grounded prompt that:
        - Instructs the assistant to use DB context for availability/prices
        - Prioritizes budget and client count suggestions
        - Enforces response language
        """
        return ("You are a hotel assistant. Use the provided database context as source of truth for availability and prices. " 
        "If user asks for suggestions, prioritize matching rooms by budget and client count from the database. " "If there is no exact match, suggest closest alternatives and explain why. " f"You MUST answer only in {target_language}.\n\n" f"{room_context}\n\n" f"User question: {user_question}")
