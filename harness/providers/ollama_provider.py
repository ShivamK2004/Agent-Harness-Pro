"""Ollama adapter with chat and generate endpoint compatibility."""
from __future__ import annotations

import requests

from .base import BaseProvider


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate with /api/chat, falling back to /api/generate on legacy servers."""
        chat_url = f"{self.base_url}/api/chat"
        chat_payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.2},
        }

        try:
            response = requests.post(chat_url, json=chat_payload, timeout=self.timeout)
            if response.status_code not in (404, 405):
                response.raise_for_status()
                data = response.json()
                content = (data.get("message") or {}).get("content", "")
                if content:
                    return str(content).strip()
                raise RuntimeError(f"Ollama /api/chat returned no message content: {data}")
        except requests.Timeout as exc:
            raise RuntimeError(
                f"Ollama chat request timed out after {self.timeout}s at {chat_url}. "
                "Check that the model is loaded and increase OLLAMA_TIMEOUT_SECONDS if needed."
            ) from exc
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not reach Ollama at {chat_url}: {exc}. "
                "Check that Ollama is running at OLLAMA_BASE_URL."
            ) from exc

        # Older/custom Ollama-compatible servers may not expose /api/chat.
        # The /api/generate endpoint accepts a single prompt instead.
        generate_url = f"{self.base_url}/api/generate"
        combined_prompt = (
            f"SYSTEM INSTRUCTIONS\n{system_prompt}\n\nUSER INPUT\n{user_prompt}"
        )
        generate_payload = {
            "model": self.model,
            "prompt": combined_prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        try:
            response = requests.post(
                generate_url, json=generate_payload, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        except requests.Timeout as exc:
            raise RuntimeError(
                f"Ollama generate request timed out after {self.timeout}s at {generate_url}."
            ) from exc
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Ollama endpoints /api/chat and /api/generate could not complete a request. "
                f"Last error from {generate_url}: {exc}. Verify your Ollama version and model."
            ) from exc

        content = data.get("response", "")
        if not content:
            raise RuntimeError(f"Ollama /api/generate returned no response text: {data}")
        return str(content).strip()

    def health(self) -> dict:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = [item.get("name") for item in response.json().get("models", [])]
            return {
                "provider": self.name,
                "model": self.model,
                "configured": True,
                "reachable": True,
                "model_available": self.model in models,
                "available_models": models,
            }
        except requests.RequestException as exc:
            return {
                "provider": self.name,
                "model": self.model,
                "configured": True,
                "reachable": False,
                "error": str(exc),
            }
