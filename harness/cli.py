"""Command-line interface for a fast local demo."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from harness.agents.orchestrator import AgentOrchestrator
from harness.evaluation.benchmark import BenchmarkRunner
from harness.config import settings, PROJECT_ROOT
from harness.storage.database import RunStore

def main():
    parser = argparse.ArgumentParser(prog="agent-harness", description="Agent Harness Pro CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask", help="Run a single agent task")
    ask.add_argument("task", nargs="+")
    ask.add_argument("--provider", choices=["mock", "gemini", "ollama"])
    bench = sub.add_parser("benchmark", help="Run bundled benchmark cases")
    bench.add_argument("--dataset", default=str(settings.benchmark_dataset))
    bench.add_argument("--provider", choices=["mock", "gemini", "ollama"])
    hist = sub.add_parser("history", help="Show recent persisted runs")
    hist.add_argument("--limit", type=int, default=10)
    sub.add_parser("health", help="Check local app configuration")
    args = parser.parse_args()

    if args.command == "ask":
        run = AgentOrchestrator(args.provider).run(" ".join(args.task))
        print(json.dumps(run.to_dict(), indent=2, ensure_ascii=False))
    elif args.command == "benchmark":
        dataset_path = Path(args.dataset)
        if not dataset_path.is_absolute():
            dataset_path = PROJECT_ROOT / dataset_path
        result = BenchmarkRunner(AgentOrchestrator(args.provider)).run(dataset_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "history":
        print(json.dumps(RunStore().list_runs(args.limit), indent=2, ensure_ascii=False))
    elif args.command == "health":
        from harness.providers.factory import get_provider
        print(json.dumps({"provider": get_provider().health(), "database": str(settings.sqlite_path),
                          "workspace": str(settings.workspace_dir), "knowledge_base": str(settings.knowledge_base_dir)}, indent=2))

if __name__ == "__main__":
    main()
