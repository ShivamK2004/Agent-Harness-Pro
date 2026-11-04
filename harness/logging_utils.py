"""Append-only JSONL event logger."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone
from threading import Lock
from harness.config import settings

_lock = Lock()

def append_jsonl(record: dict, filename: str = "runs.jsonl") -> None:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    payload = {"logged_at": datetime.now(timezone.utc).isoformat(), **record}
    path = settings.log_dir / filename
    with _lock:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
