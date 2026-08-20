from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


def collapse(text: str, limit: int = 100) -> str:
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


@dataclass(frozen=True)
class Frame:
    kind: str
    pred: str
    line: int
    end_line: int = 0

    def render(self) -> str:
        pred = self.pred.strip()
        if self.kind in {"fn", "class", "impl", "struct", "enum", "protocol", "extension"}:
            return f"{self.kind} {pred}".strip()
        if self.kind == "eval":
            return f"eval {pred}"
        if self.kind == "given":
            return f"given {pred}"
        if self.kind == "else":
            if pred:
                return f"else ¬({pred})"
            return "else"
        if self.kind == "try-else":
            return "try-else (no raise)"
        if self.kind == "for-else":
            return "for-else (no break)"
        if self.kind == "while-else":
            return "while-else (no break)"
        if self.kind == "guard-else":
            return f"guard-else ¬({pred})" if pred else "guard-else"
        if self.kind == "guard":
            return f"guard {pred}"
        if self.kind in {"if", "elif", "for", "while", "except", "catch", "finally", "try", "with", "match", "case", "switch", "arm"}:
            return f"{self.kind} {pred}".strip()
        if pred:
            return f"{self.kind} {pred}"
        return self.kind

    def key(self) -> tuple[str, str]:
        return (self.kind, collapse(self.pred, 160))


@dataclass
class Locus:
    file: str
    line: int
    here: str
    frames: list[Frame] = field(default_factory=list)
    after: list[str] = field(default_factory=list)
    engine: str = ""
    error: Optional[str] = None
    side: Optional[str] = None  # '+' | '-' | None
    col: Optional[int] = None

    @property
    def function(self) -> Optional[str]:
        for kind in ("fn", "class"):
            for fr in reversed(self.frames):
                if fr.kind == kind:
                    return fr.pred
        return None

    @property
    def depth(self) -> int:
        skip = {"class", "impl", "struct", "enum", "protocol", "extension", "module"}
        return sum(1 for fr in self.frames if fr.kind not in skip)

    @property
    def path(self) -> str:
        return " | ".join(fr.render() for fr in self.frames)

    @property
    def cond_path(self) -> str:
        skip = {"class", "impl", "struct", "enum", "protocol", "extension", "module"}
        return " | ".join(fr.render() for fr in self.frames if fr.kind not in skip)

    @property
    def path_key(self) -> tuple[tuple[str, str], ...]:
        return tuple(fr.key() for fr in self.frames)

    def to_record(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "col": self.col,
            "here": self.here,
            "function": self.function,
            "depth": self.depth,
            "path": self.path,
            "engine": self.engine,
            "error": self.error,
            "side": self.side,
            "after": self.after,
            "frames": [
                {"kind": fr.kind, "pred": fr.pred, "line": fr.line, "end_line": fr.end_line}
                for fr in self.frames
            ],
        }


@dataclass
class Query:
    file: str
    line: int
    side: Optional[str] = None
    revision: Optional[str] = None  # None = working tree
    here: Optional[str] = None
