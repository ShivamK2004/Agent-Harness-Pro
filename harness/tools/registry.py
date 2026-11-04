"""Allowlisted tool registry used by agents and API."""
from __future__ import annotations
import re
from harness.config import settings
from harness.retrieval.knowledge_base import LocalKnowledgeBase
from .calculator import calculate
from .task_router import classify_task, extract_arithmetic_expression, parse_file_creation_request
from .workspace import WorkspaceTool

class ToolRegistry:
    def __init__(self, knowledge_base: LocalKnowledgeBase | None = None,
                 workspace: WorkspaceTool | None = None):
        self.knowledge_base = knowledge_base or LocalKnowledgeBase(settings.knowledge_base_dir)
        self.workspace = workspace or WorkspaceTool(settings.workspace_dir, settings.max_workspace_file_bytes)

    def descriptions(self) -> list[dict]:
        return [
            {"name": "knowledge_search", "description": "Search local Markdown/text knowledge documents for supporting evidence."},
            {"name": "calculator", "description": "Evaluate a basic arithmetic expression safely."},
            {"name": "workspace_write", "description": "Write a small text file inside the isolated workspace folder."},
            {"name": "workspace_read", "description": "Read a text file already inside the isolated workspace folder."},
        ]

    def call(self, name: str, **kwargs) -> dict:
        if name == "knowledge_search":
            query = str(kwargs.get("query", ""))
            sources = self.knowledge_base.search(query, int(kwargs.get("top_k", 4)))
            return {"tool": name, "ok": True, "sources": [s.to_dict() for s in sources],
                    "text": self.knowledge_base.format_sources(sources)}
        if name == "calculator":
            result = calculate(str(kwargs.get("expression", "")))
            return {"tool": name, "ok": True, "result": result, "text": result}
        if name == "workspace_write":
            relative_path = str(kwargs.get("path", "note.txt"))
            content = str(kwargs.get("content", ""))
            result = self.workspace.write(relative_path, content)
            safe_path = self.workspace._safe_path(relative_path)
            return {"tool": name, "ok": safe_path.is_file(),
                    "path": safe_path.relative_to(self.workspace.root).as_posix(),
                    "bytes_written": safe_path.stat().st_size, "text": result}
        if name == "workspace_read":
            result = self.workspace.read(str(kwargs.get("path", "")))
            return {"tool": name, "ok": True, "text": result[:settings.max_tool_output_chars]}
        raise ValueError(f"Tool '{name}' is not registered or permitted")

    def suggested_tool_calls(self, task: str, task_type: str | None = None) -> list[dict]:
        """Route only to tools relevant to the detected task; never retrieve by default."""
        task_type = task_type or classify_task(task)
        if task_type == "calculation":
            expression = extract_arithmetic_expression(task)
            return [{"name": "calculator", "kwargs": {"expression": expression}}] if expression else []
        if task_type == "knowledge":
            return [{"name": "knowledge_search", "kwargs": {"query": task, "top_k": 4}}]
        if task_type == "file_creation":
            request = parse_file_creation_request(task)
            if not request:
                return []
            return [{"name": "workspace_write", "kwargs": request}]
        return []
