import os
from google import genai  # new package
from typing import List, Dict

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("MODEL_NAME", "models/gemini-2.5-flash")

    def build_prompt(self, system_prompt: str, user_input: str, history: List[Dict] = None) -> str:
        prompt = ""
        if system_prompt:
            prompt += f"System: {system_prompt}\n\n"
        if history:
            for msg in history:
                role = msg["role"]
                content = msg["content"]
                prompt += f"{role.capitalize()}: {content}\n"
        prompt += f"User: {user_input}\nAssistant:"
        return prompt

    def generate_response(self, user_input: str, system_prompt: str = "", history=None) -> str:
        prompt = self.build_prompt(system_prompt, user_input, history)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        return (response.text or "").strip()