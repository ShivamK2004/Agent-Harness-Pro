
"""FastAPI application exposing agent execution and benchmark endpoints."""
from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from harness.agents.orchestrator import AgentOrchestrator
from harness.config import settings
from harness.evaluation.benchmark import BenchmarkRunner
from harness.providers.factory import get_provider
from harness.storage.database import RunStore
from harness.tools.registry import ToolRegistry


app = FastAPI(
    title="Agent Harness Pro API",
    version="1.3.0",
    description="Multi-provider agent workflow, evaluation, and run-history API",
)


# ---------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://agent-harness-pro.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ---------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    task: str = Field(min_length=1, max_length=5000)
    provider: Literal["mock", "gemini", "ollama"] | None = None


class BenchmarkRequest(BaseModel):
    provider: Literal["mock", "gemini", "ollama"] | None = None


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": app.version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health():
    try:
        provider_info = get_provider().health()
    except Exception as exc:
        provider_info = {
            "configured": False,
            "error": str(exc),
        }

    return {
        "status": "ok",
        "app": settings.app_name,
        "configured_provider": settings.llm_provider,
        "provider": provider_info,
    }


# ---------------------------------------------------------
# REGISTERED TOOLS
# ---------------------------------------------------------

@app.get("/tools")
def tools():
    return {
        "tools": ToolRegistry().descriptions()
    }


# ---------------------------------------------------------
# AGENT PLAYGROUND
# ---------------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        run = AgentOrchestrator(request.provider).run(
            request.task
        )

        return run.to_dict()

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not execute task: {exc}",
        ) from exc


# ---------------------------------------------------------
# BENCHMARK LAB
# ---------------------------------------------------------

@app.post("/benchmark/run")
def benchmark(request: BenchmarkRequest):
    try:
        runner = BenchmarkRunner(
            AgentOrchestrator(request.provider)
        )

        return runner.run(settings.benchmark_dataset)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Benchmark failed: {exc}",
        ) from exc


# ---------------------------------------------------------
# RUN HISTORY
# ---------------------------------------------------------

@app.get("/runs")
def runs(limit: int = 50):
    limit = max(1, min(limit, 500))

    return {
        "runs": RunStore().list_runs(limit)
    }


@app.get("/runs/{run_id}")
def run_detail(run_id: str):
    result = RunStore().get_run(run_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found",
        )

    return result


# ---------------------------------------------------------
# DASHBOARD STATISTICS
# ---------------------------------------------------------

@app.get("/stats")
def stats():
    """Return dashboard aggregates based on persisted run history."""

    recent = RunStore().list_runs(500)

    total = len(recent)

    completed = sum(
        1 for item in recent
        if item.get("status") == "completed"
    )

    latencies = [
        float(item.get("latency_ms") or 0)
        for item in recent
    ]

    scores = [
        float(
            (item.get("evaluation") or {}).get(
                "overall_score"
            ) or 0
        )
        for item in recent
    ]

    return {
        "total_runs": total,
        "completed_runs": completed,
        "failed_runs": total - completed,

        "success_rate": round(
            (completed / total) * 100, 2
        ) if total else 0,

        "average_latency_ms": round(
            sum(latencies) / len(latencies), 2
        ) if latencies else 0,

        "average_score": round(
            sum(scores) / len(scores), 4
        ) if scores else 0,

        "recent_runs": recent[:8],
    }
