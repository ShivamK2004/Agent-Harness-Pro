"""Google Gemini adapter using the official google-genai SDK."""
from __future__ import annotations
from .base import BaseProvider

class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Add it to your .env file or use mock/ollama mode.")
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("Gemini support requires google-genai. Run: pip install -r requirements.txt") from exc
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Interactions API is the current unified interface in the Google Gen AI SDK.
        prompt = f"SYSTEM INSTRUCTIONS\n{system_prompt}\n\nUSER INPUT\n{user_prompt}"
        interactions = getattr(self.client, "interactions", None)
        if interactions is not None and hasattr(interactions, "create"):
            response = interactions.create(model=self.model, input=prompt)
            output = getattr(response, "output_text", None)
            if output:
                return str(output).strip()
            return str(response).strip()
        # Compatibility fallback for SDK installations that expose the classic models API.
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        output = getattr(response, "text", None)
        if not output:
            raise RuntimeError("Gemini returned an empty response")
        return str(output).strip()

    def health(self) -> dict:
        return {"provider": self.name, "model": self.model, "configured": True,
                "note": "Key is configured; live API connectivity is checked on generation."}
