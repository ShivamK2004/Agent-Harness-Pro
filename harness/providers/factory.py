"""Provider construction and provider override support."""
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider
from .mock_provider import MockProvider
from .base import BaseProvider
from harness.config import settings


def get_provider(provider_name: str | None = None) -> BaseProvider:
    name = (provider_name or settings.llm_provider).strip().lower()
    if name == "gemini":
        return GeminiProvider(settings.gemini_api_key, settings.gemini_model)
    if name == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.ollama_model, settings.ollama_timeout_seconds)
    if name == "mock":
        return MockProvider()
    raise ValueError(f"Unsupported provider '{name}'. Choose gemini, ollama, or mock.")
