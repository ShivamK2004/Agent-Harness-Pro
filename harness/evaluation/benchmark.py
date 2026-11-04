"""Robust, per-case benchmark runner with explicit failed rows."""
from __future__ import annotations
import json
import time
from pathlib import Path
from harness.agents.orchestrator import AgentOrchestrator
from harness.evaluation.scoring import evaluate_answer

_METRIC_KEYS = ("overall_score", "keyword_coverage", "token_overlap", "citation_score", "tool_use_score", "latency_ms")

class BenchmarkRunner:
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator

    @staticmethod
    def load_dataset(path: Path) -> list[dict]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Benchmark dataset must be a JSON array")
        for index, row in enumerate(data):
            if not isinstance(row, dict) or "id" not in row or "task" not in row:
                raise ValueError(f"Benchmark row {index} must be an object containing id and task")
            if not isinstance(row["task"], str) or not row["task"].strip():
                raise ValueError(f"Benchmark row {index} has an empty task")
            for field in ("expected_keywords", "expected_tools"):
                if field in row and not isinstance(row[field], list):
                    raise ValueError(f"Benchmark row {index} field '{field}' must be an array")
        return data

    @staticmethod
    def _failed_metrics(task: dict, latency_ms: float) -> dict:
        metrics = evaluate_answer("", task.get("expected_keywords", []), task.get("reference_answer", ""),
                                  0, [], task.get("expected_tools", []), latency_ms)
        metrics["overall_score"] = 0.0
        metrics["latency_ms"] = round(latency_ms, 2)
        return metrics

    def run(self, path: Path) -> dict:
        tasks = self.load_dataset(path)
        results = []
        for task in tasks:
            started = time.perf_counter()
            try:
                run = self.orchestrator.run(task["task"], benchmark_meta=task)
                metrics = run.evaluation or evaluate_answer(
                    run.answer or "", task.get("expected_keywords", []), task.get("reference_answer", ""),
                    len(run.sources or []), run.tools_used or [], task.get("expected_tools", []), run.latency_ms,
                )
                # Normalize old/incomplete run objects so the UI always receives all metric keys.
                metrics = dict(metrics)
                for key in _METRIC_KEYS:
                    metrics.setdefault(key, 0.0)
                if run.status != "completed":
                    metrics["overall_score"] = 0.0
                error = next((str(e.details.get("message", e.message)) for e in run.trace
                              if e.status == "error"), None)
                results.append({
                    "task_id": task["id"], "task": task["task"], "run_id": run.run_id,
                    "answer": run.answer or "", "metrics": metrics, "status": run.status,
                    "error": error, "task_type": metrics.get("task_type"),
                })
            except Exception as exc:
                latency_ms = (time.perf_counter() - started) * 1000
                results.append({
                    "task_id": task["id"], "task": task["task"], "run_id": None,
                    "answer": "", "metrics": self._failed_metrics(task, latency_ms),
                    "status": "failed", "error": f"{type(exc).__name__}: {exc}", "task_type": None,
                })

        def average(key: str) -> float:
            values = [float((row.get("metrics") or {}).get(key, 0) or 0) for row in results]
            return round(sum(values) / max(1, len(values)), 4)

        failed = sum(1 for row in results if row.get("status") != "completed")
        return {
            "dataset": str(path), "total_tasks": len(results),
            "successful_tasks": len(results) - failed, "failed_tasks": failed,
            "aggregate": {
                "overall_score": average("overall_score"),
                "keyword_coverage": average("keyword_coverage"),
                "token_overlap": average("token_overlap"),
                "citation_score": average("citation_score"),
                "tool_use_score": average("tool_use_score"),
                "avg_latency_ms": average("latency_ms"),
            },
            "results": results,
        }
