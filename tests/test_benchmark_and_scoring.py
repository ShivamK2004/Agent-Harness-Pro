import json
from harness.evaluation.scoring import evaluate_answer
from harness.evaluation.benchmark import BenchmarkRunner
from harness.agents.orchestrator import AgentOrchestrator

def test_scoring_has_expected_fields():
    result = evaluate_answer("The policy says support@example.com", ["support@example.com"], "support@example.com")
    assert result["keyword_coverage"] == 1.0
    assert "overall_score" in result
    assert result["heuristic_only"] is True

def test_benchmark_dataset_schema(tmp_path):
    dataset = tmp_path / "tasks.json"
    dataset.write_text(json.dumps([{"id": "T1", "task": "hello"}]), encoding="utf-8")
    assert BenchmarkRunner.load_dataset(dataset)[0]["id"] == "T1"


def test_benchmark_forces_expected_knowledge_tool(tmp_path):
    from tests.test_orchestrator import IsolatedOrchestrator
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "support.md").write_text("Support aims to respond within 24 hours on business days.", encoding="utf-8")
    orchestrator = IsolatedOrchestrator(tmp_path)
    dataset = tmp_path / "tasks.json"
    dataset.write_text(json.dumps([{
        "id": "KB-ROUTE", "task": "What is the sample support response time?",
        "expected_keywords": ["24 hours"], "expected_tools": ["knowledge_search"],
    }]), encoding="utf-8")
    result = BenchmarkRunner(orchestrator).run(dataset)
    row = result["results"][0]
    assert row["status"] == "completed"
    assert "knowledge_search" in orchestrator.store.get_run(row["run_id"])["tools_used"]
    assert row["metrics"]["tool_use_score"] == 1.0


def test_benchmark_keeps_failed_case_as_complete_row(tmp_path):
    class BrokenOrchestrator:
        def run(self, task, benchmark_meta=None):
            raise RuntimeError("synthetic test failure")

    dataset = tmp_path / "tasks.json"
    dataset.write_text(json.dumps([{"id": "T-FAIL", "task": "Do the test", "expected_keywords": ["done"]}]), encoding="utf-8")
    result = BenchmarkRunner(BrokenOrchestrator()).run(dataset)
    assert result["total_tasks"] == 1
    assert result["failed_tasks"] == 1
    row = result["results"][0]
    assert row["status"] == "failed"
    assert row["metrics"]["overall_score"] == 0.0
    assert "synthetic test failure" in row["error"]
    assert "latency_ms" in row["metrics"]
