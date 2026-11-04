"""Centralized environment configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _project_path(value: str, fallback: str) -> Path:
    candidate = Path(value or fallback).expanduser()
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Agent Harness Pro")
    app_env: str = os.getenv("APP_ENV", "development")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3:latest")
    ollama_timeout_seconds: int = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/agent_harness.db")
    workspace_dir: Path = _project_path(os.getenv("WORKSPACE_DIR", "workspace"), "workspace")
    knowledge_base_dir: Path = _project_path(os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base"), "knowledge_base")
    log_dir: Path = _project_path(os.getenv("LOG_DIR", "logs"), "logs")
    benchmark_dataset: Path = _project_path(os.getenv("BENCHMARK_DATASET", "benchmarks/tasks.json"), "benchmarks/tasks.json")
    max_tool_output_chars: int = int(os.getenv("MAX_TOOL_OUTPUT_CHARS", "8000"))
    max_workspace_file_bytes: int = int(os.getenv("MAX_WORKSPACE_FILE_BYTES", "200000"))
    max_agent_steps: int = int(os.getenv("MAX_AGENT_STEPS", "5"))
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120"))
    model_verifier_enabled: bool = os.getenv("MODEL_VERIFIER_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}

    @property
    def sqlite_path(self) -> Path:
        prefix = "sqlite:///"
        if not self.database_url.startswith(prefix):
            raise ValueError("Only SQLite DATABASE_URL is supported by this demo, e.g. sqlite:///data/app.db")
        raw = self.database_url[len(prefix):]
        path = Path(raw)
        return path if path.is_absolute() else PROJECT_ROOT / path

    def ensure_directories(self) -> None:
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
