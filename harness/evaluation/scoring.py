"""Transparent, deterministic heuristic evaluation. No metric implies factual truth."""
from __future__ import annotations
import re
from collections import Counter

STOPWORDS = {"the", "a", "an", "and", "or", "to", "of", "in", "is", "are", "for", "with", "on", "by", "it", "this", "that", "as", "be", "can", "you", "your", "from", "at", "we", "our"}

def tokens(text: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[a-zA-Z0-9]+", text) if len(t) > 1 and t.lower() not in STOPWORDS]

def token_jaccard(a: str, b: str) -> float:
    left, right = set(tokens(a)), set(tokens(b))
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)

def evaluate_answer(answer: str, expected_keywords: list[str] | None = None,
                    reference_answer: str = "", source_count: int = 0,
                    tools_used: list[str] | None = None, expected_tools: list[str] | None = None,
                    latency_ms: float = 0.0) -> dict:
    expected_keywords = expected_keywords or []
    tools_used = tools_used or []
    expected_tools = expected_tools or []
    normalized = answer.lower()
    matched = [word for word in expected_keywords if word.lower() in normalized]
    keyword_coverage = len(matched) / len(expected_keywords) if expected_keywords else 1.0
    overlap = token_jaccard(answer, reference_answer) if reference_answer else 0.0
    citations = re.findall(r"\[KB\d{3}\]", answer)
    citation_score = (min(len(set(citations)), source_count) / max(1, source_count)) if source_count else 1.0
    matched_tools = [tool for tool in expected_tools if tool in tools_used]
    tool_use_score = len(matched_tools) / len(expected_tools) if expected_tools else 1.0
    # Explicitly a heuristic blend, not an accuracy or factuality probability.
    overall = 0.50 * keyword_coverage + 0.20 * overlap + 0.15 * citation_score + 0.15 * tool_use_score
    return {
        "overall_score": round(overall, 4),
        "keyword_coverage": round(keyword_coverage, 4),
        "matched_keywords": matched,
        "missing_keywords": [word for word in expected_keywords if word not in matched],
        "token_overlap": round(overlap, 4),
        "token_overlap_note": "Jaccard token overlap against reference answer; not embedding-based semantic similarity.",
        "citation_score": round(citation_score, 4),
        "citation_count": len(set(citations)),
        "source_count": source_count,
        "tool_use_score": round(tool_use_score, 4),
        "expected_tools": expected_tools,
        "tools_used": tools_used,
        "latency_ms": round(latency_ms, 2),
        "answer_characters": len(answer),
        "heuristic_only": True,
    }
