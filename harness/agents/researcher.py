"""Researcher agent: gathers local evidence through the allowlisted registry."""
from __future__ import annotations

class ResearcherAgent:
    def __init__(self, provider, tools):
        self.provider, self.tools = provider, tools

    def research(self, task: str, task_type: str | None = None) -> tuple[list, list[dict], str]:
        outputs, sources = [], []
        for call in self.tools.suggested_tool_calls(task, task_type=task_type):
            result = self.tools.call(call["name"], **call["kwargs"])
            outputs.append(result)
            if call["name"] == "knowledge_search":
                sources = result.get("sources", [])

        # Summarize tool output deterministically. This avoids spending a full
        # model call merely paraphrasing evidence that the Executor will receive.
        if sources:
            summary = f"Retrieved {len(sources)} local source(s). Use only these snippets and cite their KB IDs."
        elif outputs:
            summary = "Tool execution completed. Use the returned tool output as the evidence."
        else:
            summary = "No retrieval or tool execution was required for this task."
        return sources, outputs, summary
