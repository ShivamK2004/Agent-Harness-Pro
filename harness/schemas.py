"""Shared typed records used by orchestration, API, and storage."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())

@dataclass
class TraceEvent:
    stage: str
    status: str
    message: str
    timestamp: str = field(default_factory=utc_now)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Source:
    source_id: str
    path: str
    title: str
    start_line: int
    end_line: int
    text: str
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class AgentRun:
    run_id: str
    task: str
    provider: str
    model: str
    answer: str
    status: str
    latency_ms: float
    trace: list[TraceEvent]
    sources: list[Source]
    tools_used: list[str]
    evaluation: dict[str, Any]
    created_at: str = field(default_factory=utc_now)
    verifier_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id, "task": self.task, "provider": self.provider,
            "model": self.model, "answer": self.answer, "status": self.status,
            "latency_ms": self.latency_ms, "trace": [e.to_dict() for e in self.trace],
            "sources": [s.to_dict() for s in self.sources], "tools_used": self.tools_used,
            "evaluation": self.evaluation, "created_at": self.created_at,
            "verifier_notes": self.verifier_notes,
        }
