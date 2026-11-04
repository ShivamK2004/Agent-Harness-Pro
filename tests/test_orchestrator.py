from harness.agents.orchestrator import AgentOrchestrator
from harness.storage.database import RunStore
from harness.retrieval.knowledge_base import LocalKnowledgeBase
from harness.tools.workspace import WorkspaceTool
from harness.tools.registry import ToolRegistry
from harness.providers.mock_provider import MockProvider
from pathlib import Path

class IsolatedOrchestrator(AgentOrchestrator):
    def __init__(self, tmp_path):
        self.provider = MockProvider()
        self.knowledge_base = LocalKnowledgeBase(tmp_path / "kb")
        self.tool_registry = ToolRegistry(self.knowledge_base, WorkspaceTool(tmp_path / "workspace"))
        from harness.agents.planner import PlannerAgent
        from harness.agents.researcher import ResearcherAgent
        from harness.agents.executor import ExecutorAgent
        from harness.agents.verifier import VerifierAgent
        self.planner = PlannerAgent(self.provider)
        self.researcher = ResearcherAgent(self.provider, self.tool_registry)
        self.executor = ExecutorAgent(self.provider)
        self.verifier = VerifierAgent(self.provider)
        self.store = RunStore(tmp_path / "runs.db")

def test_mock_orchestration_persists_run(tmp_path):
    (tmp_path / "kb").mkdir()
    (tmp_path / "kb" / "info.md").write_text("# Info\nThe service responds in 24 hours.", encoding="utf-8")
    orchestrator = IsolatedOrchestrator(tmp_path)
    run = orchestrator.run("What is the service response time?")
    assert run.status == "completed"
    assert run.provider == "mock"
    assert any(event.stage == "planner" for event in run.trace)
    assert orchestrator.store.get_run(run.run_id) is not None


def test_calculator_request_uses_restricted_tool(tmp_path):
    (tmp_path / "kb").mkdir()
    orchestrator = IsolatedOrchestrator(tmp_path)
    run = orchestrator.run("Calculate 125 * 8 + 40")
    assert run.status == "completed"
    assert "calculator" in run.tools_used
    assert "1040" in run.answer


def test_create_text_file_executes_workspace_tool(tmp_path):
    (tmp_path / "kb").mkdir()
    orchestrator = IsolatedOrchestrator(tmp_path)
    run = orchestrator.run("Can you create a shivam.text file?")
    output = tmp_path / "workspace" / "shivam.text"
    assert run.status == "completed"
    assert "workspace_write" in run.tools_used
    assert output.is_file()
    assert "Successfully created" in run.answer
