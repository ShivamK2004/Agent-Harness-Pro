"""Path-safe file tools constrained to a dedicated workspace."""
from __future__ import annotations
from pathlib import Path

ALLOWED_EXTENSIONS = {".txt", ".text", ".md", ".json", ".csv", ".py"}

class WorkspaceTool:
    def __init__(self, root: Path, max_file_bytes: int = 200_000):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.max_file_bytes = max_file_bytes

    def _safe_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("Path is outside the sandbox workspace") from exc
        if candidate.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension not allowed. Allowed: {sorted(ALLOWED_EXTENSIONS)}")
        return candidate

    def write(self, relative_path: str, content: str) -> str:
        data = content.encode("utf-8")
        if len(data) > self.max_file_bytes:
            raise ValueError("File exceeds configured size limit")
        path = self._safe_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {len(data)} bytes to workspace/{path.relative_to(self.root).as_posix()}"

    def read(self, relative_path: str) -> str:
        path = self._safe_path(relative_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Workspace file not found: {relative_path}")
        if path.stat().st_size > self.max_file_bytes:
            raise ValueError("File exceeds configured size limit")
        return path.read_text(encoding="utf-8", errors="replace")

    def list_files(self) -> list[str]:
        return [p.relative_to(self.root).as_posix() for p in self.root.rglob("*")
                if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS]
