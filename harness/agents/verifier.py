"""Verifier agent: deterministic checks with optional bounded model review."""
from __future__ import annotations
import json, re

SYSTEM = """You are the VERIFIER agent. Review the proposed answer only against the provided task and evidence. Return JSON with keys status, supported_points, unsupported_points, citation_check, risk_flags, recommendation. Do not invent evidence. You are a review aid, not an oracle. If the answer is a mock-provider response, explicitly note that it is a mock demonstration."""

class VerifierAgent:
    def __init__(self, provider, model_review_enabled: bool = False):
        self.provider = provider
        self.model_review_enabled = model_review_enabled

    def verify(self, task: str, answer: str, sources: list[dict],
               task_type: str | None = None, tool_outputs: list[dict] | None = None) -> dict:
        tool_outputs = tool_outputs or []
        source_ids = {s["source_id"] for s in sources}
        used_ids = set(re.findall(r"\[(KB\d{3})\]", answer))
        unknown_ids = sorted(used_ids - source_ids)
        notes = []
        if unknown_ids:
            notes.append(f"Unknown citation IDs: {', '.join(unknown_ids)}")
        if sources and not used_ids:
            notes.append("Retrieved sources exist but the answer contains no KB citation markers.")
        if not sources and task_type == "knowledge":
            notes.append("No local source was retrieved for a knowledge task.")

        tool_check = None
        if task_type == "calculation":
            tool_check = any(x.get("tool") == "calculator" and x.get("ok") for x in tool_outputs)
            notes.append("Calculator tool result verified." if tool_check else "Calculator tool did not return a successful result.")
        elif task_type == "file_creation":
            tool_check = any(x.get("tool") == "workspace_write" and x.get("ok") for x in tool_outputs)
            notes.append("Workspace file write verified." if tool_check else "Workspace file was not verified after writing.")

        review = {
            "status": "passed" if not unknown_ids and tool_check is not False else "review_required",
            "supported_points": [],
            "unsupported_points": [],
            "citation_check": "Citation IDs match retrieved sources." if not unknown_ids else "One or more citation IDs are not in the retrieved source set.",
            "risk_flags": [],
            "recommendation": "Deterministic checks completed. Model review is disabled; treat this as an engineering check, not proof of factual correctness.",
        }

        if self.model_review_enabled:
            prompt = (f"Task:\n{task}\n\nProposed answer:\n{answer}\n\nEvidence:\n" +
                      "\n\n".join(f"[{s['source_id']}] {s['text']}" for s in sources))
            raw = self.provider.generate(SYSTEM, prompt)
            try:
                match = re.search(r"\{.*\}", raw, re.S)
                model_review = json.loads(match.group(0) if match else raw)
                if isinstance(model_review, dict):
                    review.update(model_review)
            except (ValueError, TypeError, json.JSONDecodeError):
                review["recommendation"] = "Deterministic checks completed; optional model review could not be parsed."

        review["deterministic_checks"] = notes
        review["citation_ids_used"] = sorted(used_ids)
        review["citation_ids_available"] = sorted(source_ids)
        review["review_is_advisory"] = True
        review["model_review_enabled"] = self.model_review_enabled
        return review
