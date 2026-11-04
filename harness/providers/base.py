"""LLM provider interface."""
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    name = "base"
    model = "unknown"

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return a text completion. Implementations must raise clear exceptions on failure."""

    def health(self) -> dict:
        return {"provider": self.name, "model": self.model, "configured": True}
