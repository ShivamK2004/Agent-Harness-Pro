"""SQLite persistence for agent runs and trace events."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any
from harness.config import settings

class RunStore:
    def __init__(self, path: Path | None = None):
        self.path = Path(path or settings.sqlite_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self):
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, task TEXT NOT NULL,
                    provider TEXT NOT NULL, model TEXT NOT NULL, status TEXT NOT NULL,
                    answer TEXT NOT NULL, latency_ms REAL NOT NULL, evaluation_json TEXT NOT NULL,
                    sources_json TEXT NOT NULL, tools_json TEXT NOT NULL, verifier_notes TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS trace_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
                    stage TEXT NOT NULL, status TEXT NOT NULL, timestamp TEXT NOT NULL,
                    message TEXT NOT NULL, details_json TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_runs_created ON runs(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_trace_run ON trace_events(run_id);
            """)

    def save_run(self, run) -> None:
        payload = run.to_dict()
        with self._connect() as conn:
            conn.execute("""INSERT OR REPLACE INTO runs
                (run_id,created_at,task,provider,model,status,answer,latency_ms,evaluation_json,sources_json,tools_json,verifier_notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (payload["run_id"], payload["created_at"], payload["task"], payload["provider"],
                 payload["model"], payload["status"], payload["answer"], payload["latency_ms"],
                 json.dumps(payload["evaluation"]), json.dumps(payload["sources"]),
                 json.dumps(payload["tools_used"]), payload["verifier_notes"]))
            conn.execute("DELETE FROM trace_events WHERE run_id=?", (payload["run_id"],))
            for event in payload["trace"]:
                conn.execute("""INSERT INTO trace_events
                    (run_id,stage,status,timestamp,message,details_json) VALUES (?,?,?,?,?,?)""",
                    (payload["run_id"], event["stage"], event["status"], event["timestamp"],
                     event["message"], json.dumps(event["details"])))

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (max(1, min(limit, 500)),)).fetchall()
        return [self._row_to_dict(row, include_trace=False) for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                return None
            result = self._row_to_dict(row, include_trace=False)
            traces = conn.execute("SELECT * FROM trace_events WHERE run_id=? ORDER BY id", (run_id,)).fetchall()
        result["trace"] = [{"stage": r["stage"], "status": r["status"], "timestamp": r["timestamp"],
                             "message": r["message"], "details": json.loads(r["details_json"])} for r in traces]
        return result

    @staticmethod
    def _row_to_dict(row, include_trace=False):
        return {"run_id": row["run_id"], "created_at": row["created_at"], "task": row["task"],
                "provider": row["provider"], "model": row["model"], "status": row["status"],
                "answer": row["answer"], "latency_ms": row["latency_ms"],
                "evaluation": json.loads(row["evaluation_json"]), "sources": json.loads(row["sources_json"]),
                "tools_used": json.loads(row["tools_json"]), "verifier_notes": row["verifier_notes"]}
