"""Deterministic intent routing for common task types."""
from __future__ import annotations
import re

_WORD_OPS = {
    r"\b(multiplied\s+by|times)\b": "*",
    r"\b(divided\s+by|over)\b": "/",
    r"\b(plus|added\s+to)\b": "+",
    r"\b(minus|subtract(?:ed)?\s+from)\b": "-",
}

_FILE_ACTION = re.compile(r"\b(create|make|write|generate)\b", re.I)
_FILE_NAME = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z0-9_-][A-Za-z0-9_.-]*\.(?:txt|text|md|json|csv|py))\b",
    re.I,
)


def parse_file_creation_request(task: str) -> dict[str, str] | None:
    """Extract a simple sandbox file request; never infer arbitrary paths."""
    if not _FILE_ACTION.search(task) or not re.search(r"\bfile\b", task, re.I):
        return None
    match = _FILE_NAME.search(task)
    if not match:
        return None
    # Only accept a filename, not a user-supplied path. Workspace subfolders can
    # be requested separately through the explicit workspace tool API.
    filename = match.group(1).strip().replace("\\", "")
    content_match = re.search(
        r"\b(?:with\s+content|containing|that\s+says)\s*[:=]?\s*[\"']?(.*?)[\"']?\s*$",
        task,
        re.I | re.S,
    )
    content = content_match.group(1).strip() if content_match else ""
    return {"path": filename, "content": content}


def extract_arithmetic_expression(task: str) -> str | None:
    text = task.lower().replace(",", "")
    for pattern, symbol in _WORD_OPS.items():
        text = re.sub(pattern, symbol, text)
    match = re.search(r"(?<![a-z])\d+(?:\.\d+)?\s*(?:[+*/%-]|\*\*)\s*\d+(?:\.\d+)?(?:\s*(?:[+*/%-]|\*\*)\s*\d+(?:\.\d+)?)*", text)
    if not match:
        return None
    expr = match.group(0).strip()
    if len(expr) > 120:
        return None
    return expr


def classify_task(task: str) -> str:
    file_request = parse_file_creation_request(task)
    if file_request:
        return "file_creation"
    if _FILE_ACTION.search(task) and re.search(r"\bfile\b", task, re.I):
        return "file_creation"
    if extract_arithmetic_expression(task):
        return "calculation"
    text = task.lower()
    knowledge_terms = (
        "policy", "document", "knowledge base", "local file", "uploaded",
        "according to", "in the provided", "refund window", "security principles",
        "support response", "contact support", "billing issue", "invoice", "order id",
    )
    if any(term in text for term in knowledge_terms):
        return "knowledge"
    return "general"
