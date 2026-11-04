"""Planner agent: creates bounded plans from deterministic task routing."""
from __future__ import annotations
import json
import re

SYSTEM = """You are the PLANNER agent in a constrained agent harness. Return one JSON object only, with keys goal (string), steps (array of short strings), tools (array of registered tool names), and risk (low/medium/high). Never request shell, network, arbitrary Python, credentials, or unregistered tools. Available tools: knowledge_search, calculator, workspace_write, workspace_read. Limit to 4 steps."""

class PlannerAgent:
    def __init__(self, provider, max_steps: int = 5):
        self.provider, self.max_steps = provider, max_steps

    def plan(self, task: str, task_type: str | None = None) -> dict:
        """Use bounded templates for known intents; reserve model planning for unknown types."""
        templates = {
            "calculation": {
                "goal": "Calculate the requested arithmetic expression",
                "steps": ["Extract the arithmetic expression", "Run the restricted calculator", "Return the verified result"],
                "tools": ["calculator"], "risk": "low",
            },
            "knowledge": {
                "goal": "Answer using relevant local knowledge-base evidence",
                "steps": ["Search local knowledge documents", "Compose an evidence-grounded answer", "Check source citations"],
                "tools": ["knowledge_search"], "risk": "low",
            },
            "file_creation": {
                "goal": "Create the requested text file in the sandbox workspace",
                "steps": ["Validate the requested filename", "Write the file in the sandbox workspace", "Verify that the file exists"],
                "tools": ["workspace_write"], "risk": "low",
            },
            "general": {
                "goal": "Answer the user's general question",
                "steps": ["Prepare a direct response", "Review the response for unsupported claims"],
                "tools": [], "risk": "low",
            },
        }
        if task_type in templates:
            plan = dict(templates[task_type])
            plan["steps"] = plan["steps"][:self.max_steps]
            return plan

        raw = self.provider.generate(SYSTEM, f"User task:\n{task}\n\nReturn a bounded plan as JSON.")
        try:
            match = re.search(r"\{.*\}", raw, re.S)
            plan = json.loads(match.group(0) if match else raw)
            if not isinstance(plan, dict):
                raise ValueError("Plan is not an object")
            steps = plan.get("steps", [])
            if not isinstance(steps, list):
                steps = []
            plan["steps"] = [str(s)[:180] for s in steps[:self.max_steps]]
            allowed = {"knowledge_search", "calculator", "workspace_write", "workspace_read"}
            plan["tools"] = [t for t in plan.get("tools", []) if t in allowed]
            return plan
        except (ValueError, TypeError, json.JSONDecodeError):
            return {"goal": "Answer the user task safely", "steps": ["Review the request", "Compose response", "Verify response"], "tools": [], "risk": "medium"}
