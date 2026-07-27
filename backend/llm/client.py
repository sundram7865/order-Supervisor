import os
import json
import re
from typing import Any, Optional
from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLMClient:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.default_model = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")

    async def complete(
        self,
        prompt: str,
        system: str = "You are an AI order supervisor.",
        **kwargs,
    ) -> str:
        response = self.client.models.generate_content(
            model=self.default_model,
            contents=f"{system}\n\n{prompt}",
        )
        return response.text

    async def complete_json(
        self,
        prompt: str,
        system: str = "You are a helpful assistant. Always respond with valid JSON.",
        **kwargs,
    ) -> Any:
        response = self.client.models.generate_content(
            model=self.default_model,
            contents=f"{system}\n\nReturn ONLY valid JSON, no markdown formatting, no code blocks:\n\n{prompt}",
        )
        text = response.text.strip()
        
        # Strip markdown code blocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"JSON parse error. Raw response: {text[:300]}")
            raise e


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client