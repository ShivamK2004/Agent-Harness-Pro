from __future__ import annotations

import requests

from harness.providers.ollama_provider import OllamaProvider


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_ollama_uses_chat_endpoint(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append((url, json, timeout))
        return FakeResponse(200, {"message": {"content": "hello from chat"}})

    monkeypatch.setattr("harness.providers.ollama_provider.requests.post", fake_post)
    provider = OllamaProvider("http://localhost:11434", "llama3:latest")

    assert provider.generate("system", "user") == "hello from chat"
    assert calls[0][0] == "http://localhost:11434/api/chat"
    assert calls[0][1]["model"] == "llama3:latest"


def test_ollama_falls_back_to_generate_after_chat_404(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append((url, json, timeout))
        if url.endswith("/api/chat"):
            return FakeResponse(404, {"error": "not found"})
        return FakeResponse(200, {"response": "hello from generate"})

    monkeypatch.setattr("harness.providers.ollama_provider.requests.post", fake_post)
    provider = OllamaProvider("http://localhost:11434", "llama3:latest")

    assert provider.generate("system", "user") == "hello from generate"
    assert calls[0][0].endswith("/api/chat")
    assert calls[1][0].endswith("/api/generate")
    assert "SYSTEM INSTRUCTIONS" in calls[1][1]["prompt"]


def test_ollama_health_reports_model_availability(monkeypatch):
    class FakeGetResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"models": [{"name": "llama3:latest"}]}

    monkeypatch.setattr("harness.providers.ollama_provider.requests.get", lambda *a, **k: FakeGetResponse())
    provider = OllamaProvider("http://localhost:11434", "llama3:latest")
    result = provider.health()

    assert result["reachable"] is True
    assert result["model_available"] is True
