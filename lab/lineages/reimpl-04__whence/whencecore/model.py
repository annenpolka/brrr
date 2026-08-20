from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class Frame:
    kind: str
    pred: str
    line: int
    end_line: int = 0

    def path_piece(self) -> str:
        if self.kind == "for-else":
            return "for-else (no break)"
        if self.kind == "try-else":
            return "try-else (no raise)"
        if self.kind == "guard-else":
            return f"guard-else ¬({self.pred})" if self.pred else "guard-else"
        if self.kind == "else" and self.pred:
            return f"else ¬({self.pred})"
        if self.pred:
            return f"{self.kind} {self.pred}"
        return self.kind


@dataclass
class Locus:
    file: str
    line: int
    col: int | None = None
    here: str = ""
    function: str | None = None
    depth: int = 0
    path: str = ""
    engine: str = ""
    error: str | None = None
    side: str | None = None
    after: list[str] = field(default_factory=list)
    frames: list[Frame] = field(default_factory=list)

    def finalize(self) -> Locus:
        self.depth = len(self.frames)
        self.path = " | ".join(f.path_piece() for f in self.frames)
        fn = next((f.pred for f in self.frames if f.kind == "fn"), None)
        self.function = fn
        return self


def format_path(frames: Iterable[Frame]) -> str:
    return " | ".join(f.path_piece() for f in frames)


BRACE_EXTS = {
    ".rs",
    ".go",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".swift",
    ".java",
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".cs",
    ".kt",
    ".kts",
    ".m",
    ".mm",
    ".scala",
}

PYTHON_EXTS = {".py", ".pyi"}


def engine_for(path: str | Path) -> str:
    suf = Path(path).suffix.lower()
    if suf in PYTHON_EXTS:
        return "python-ast"
    if suf in BRACE_EXTS:
        return "braces"
    return "braces"


def is_source_path(path: str | Path) -> bool:
    suf = Path(path).suffix.lower()
    return suf in PYTHON_EXTS or suf in BRACE_EXTS
