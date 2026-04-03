import os
from typing import Dict, List, Optional

from google import genai

# Defaults
DEFAULT_MODEL_NAME = "models/gemini-2.5-flash"
DEFAULT_SYSTEM_PROMPT = (
    "You must answer in maximum 30 words. The answer must be clean and concise."
)


class GeminiService:
    """Lightweight wrapper around Google Gemini for text generation.

    Exposes:
      - build_prompt: construct a simple chat-style prompt
      - generate_response: call the model and return plain text
      - build_grounded_prompt: construct a DB-grounded assistant prompt
    """

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        self.client = genai.Client(api_key=api_key)
        self.model_name = os.getenv("MODEL_NAME", DEFAULT_MODEL_NAME)
        self.system_prompt = DEFAULT_SYSTEM_PROMPT

    def build_prompt(
        self,
        user_input: str,
        history: Optional[List[Dict]] = None,
    ) -> str:
        """Build a simple prompt with optional message history."""
        sections: List[str] = [f"System: {self.system_prompt}", ""]

        if history:
            for msg in history:
                role = (msg.get("role") or "").capitalize()
                content = msg.get("content") or ""
                sections.append(f"{role}: {content}")

        sections.append(f"User: {user_input}")
        sections.append("Assistant:")
        return "\n".join(sections)

    def generate_response(
        self,
        user_input: str,
        history: Optional[List[Dict]] = None,
    ) -> str:
        """Generate a response using the configured Gemini model."""
        prompt = self.build_prompt(user_input, history)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return (getattr(response, "text", "") or "").strip()

    def build_grounded_prompt(
        self,
        room_context: str,
        user_question: str,
        target_language: str,
    ) -> str:
        """Build a grounded prompt that enforces language and DB-backed guidance."""
        lines = [
            (
                "You are a hotel assistant. Use the provided database context as source of "
                "truth for availability and prices. If user asks for suggestions, prioritize "
                "matching rooms by budget and client count from the database. If there is no "
                "exact match, suggest closest alternatives and explain why."
            ),
            f"You MUST answer only in {target_language}.",
            "",
            room_context,
            "",
            f"User question: {user_question}",
        ]
        return "\n".join(lines)
