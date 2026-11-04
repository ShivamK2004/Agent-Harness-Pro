"""Small local retrieval engine with line-aware citations (no external embedding service)."""
from __future__ import annotations
from pathlib import Path
import re
from collections import Counter
from harness.schemas import Source

WORD_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_'-]*")

class LocalKnowledgeBase:
    SUPPORTED = {".md", ".txt"}

    def __init__(self, root: Path, chunk_chars: int = 1100, overlap_lines: int = 1):
        self.root = Path(root).resolve()
        self.chunk_chars = chunk_chars
        self.overlap_lines = overlap_lines
        self.documents: list[Source] = []
        self.reload()

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [t.lower() for t in WORD_RE.findall(text) if len(t) > 1]

    def reload(self) -> int:
        self.root.mkdir(parents=True, exist_ok=True)
        docs: list[Source] = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in self.SUPPORTED:
                continue
            try:
                # Reject symbolic-link escapes and very large files.
                resolved = path.resolve()
                resolved.relative_to(self.root)
                if resolved.stat().st_size > 1_000_000:
                    continue
                text = resolved.read_text(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                continue
            lines = text.splitlines()
            chunks: list[tuple[int, int, str]] = []
            current: list[str] = []
            start = 1
            for index, line in enumerate(lines, start=1):
                if not current:
                    start = index
                current.append(line)
                if sum(len(x) + 1 for x in current) >= self.chunk_chars:
                    chunks.append((start, index, "\n".join(current)))
                    carry = current[-self.overlap_lines:] if self.overlap_lines else []
                    current = list(carry)
                    start = index - len(carry) + 1
            if current:
                chunks.append((start, len(lines), "\n".join(current)))
            for n, (line_start, line_end, chunk) in enumerate(chunks, 1):
                rel = resolved.relative_to(self.root).as_posix()
                title = next((l.lstrip("# ").strip() for l in chunk.splitlines() if l.startswith("#")), path.stem)
                docs.append(Source(f"KB{len(docs)+1:03d}", rel, title, line_start, line_end, chunk))
        self.documents = docs
        return len(docs)

    def search(self, query: str, top_k: int = 4) -> list[Source]:
        terms = self._tokens(query)
        if not terms or not self.documents:
            return []
        query_counts = Counter(terms)
        scored: list[Source] = []
        for doc in self.documents:
            doc_terms = self._tokens(doc.text)
            counts = Counter(doc_terms)
            # Simple weighted lexical rank: term frequency + a small exact phrase bonus.
            score = sum(min(counts[t], 3) * (1 + 0.25 * (query_counts[t] - 1)) for t in query_counts)
            if query.lower().strip() in doc.text.lower():
                score += 2.0
            if score > 0:
                scored.append(Source(doc.source_id, doc.path, doc.title, doc.start_line,
                                     doc.end_line, doc.text, float(score)))
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:max(1, top_k)]

    def list_documents(self) -> list[dict]:
        unique = {}
        for doc in self.documents:
            unique[doc.path] = {"path": doc.path, "title": doc.title}
        return list(unique.values())

    @staticmethod
    def format_sources(sources: list[Source]) -> str:
        if not sources:
            return "No matching local knowledge was retrieved."
        blocks = []
        for src in sources:
            blocks.append(f"[{src.source_id}] {src.title} — {src.path}:{src.start_line}-{src.end_line}\n{src.text}")
        return "\n\n".join(blocks)
