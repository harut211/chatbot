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