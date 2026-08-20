from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


def collapse(text: str, limit: int = 0) -> str:
    text = " ".join(text.split())
    if limit and len(text) > limit:
        return text[: limit - 1] + "…"
    return text


@dataclass(frozen=True)
class Frame:
    kind: str
    pred: str
    line: int = 0
    end_line: int = 0

    def render(self) -> str:
        pred = self.pred.strip()
        if self.kind in {
            "fn",
            "class",
            "impl",
            "struct",
            "enum",
            "protocol",
            "extension",
        }:
            return ("{} {}".format(self.kind, pred)).strip()
        if self.kind == "given":
            return "given {}".format(pred)
        if self.kind == "else":
            return "else ¬({})".format(pred) if pred else "else"
        if self.kind == "guard-else":
            return "guard-else ¬({})".format(pred) if pred else "guard-else"
        if self.kind == "guard":
            return "guard {}".format(pred)
        if self.kind == "try-else":
            return "try-else (no raise)"
        if self.kind == "for-else":
            return "for-else (no break)"
        if self.kind == "while-else":
            return "while-else (no break)"
        if pred:
            return "{} {}".format(self.kind, pred)
        return self.kind

    def key(self) -> Tuple[str, str]:
        return (self.kind, collapse(self.pred))


_TYPE_SKIP = {"class", "impl", "struct", "enum", "protocol", "extension", "module"}


@dataclass
class Locus:
    file: str
    line: int
    here: str
    frames: List[Frame] = field(default_factory=list)
    engine: str = ""
    error: Optional[str] = None
    side: Optional[str] = None
    image: str = "post"
    placed: bool = True

    @property
    def function(self) -> Optional[str]:
        for kind in ("fn", "class"):
            for fr in reversed(self.frames):
                if fr.kind == kind:
                    return fr.pred
        return None

    @property
    def depth(self) -> int:
        return sum(1 for fr in self.frames if fr.kind not in _TYPE_SKIP)

    @property
    def path(self) -> str:
        return " | ".join(fr.render() for fr in self.frames)

    @property
    def cond_path(self) -> str:
        return " | ".join(fr.render() for fr in self.frames if fr.kind not in _TYPE_SKIP)

    @property
    def cond_frames(self) -> List[Frame]:
        return [fr for fr in self.frames if fr.kind not in _TYPE_SKIP]

    @property
    def path_key(self) -> Tuple[Tuple[str, str], ...]:
        return tuple(fr.key() for fr in self.cond_frames)

    def to_record(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "here": self.here,
            "function": self.function,
            "depth": self.depth,
            "path": self.path,
            "cond_path": self.cond_path,
            "engine": self.engine,
            "error": self.error,
            "side": self.side,
            "image": self.image,
            "placed": self.placed,
            "frames": [
                {
                    "kind": fr.kind,
                    "pred": fr.pred,
                    "line": fr.line,
                    "end_line": fr.end_line,
                }
                for fr in self.frames
            ],
        }


def is_payload(text: str) -> bool:
    """True if a line is a reviewable payload, not a brace/comment husk."""
    t = text.strip()
    if not t:
        return False
    if t in {"{", "}", "};", "},", ")", ");", "],", "]", "];"}:
        return False
    if t.startswith("//") or t.startswith("/*") or t.startswith("*") or t.startswith("#"):
        # keep Rust/Swift attributes and Python shebang-less docs? attributes:
        if t.startswith("#[") or t.startswith("#!") or t.startswith("@") or t.startswith("#["):
            return True
        if t.startswith("#") and not t.startswith("///") and not t.startswith("//!"):
            # python comment or rust doc already handled; bare # comment
            if t.startswith("# " ) or t == "#":
                return False
        if t.startswith("//") or t.startswith("/*") or t.startswith("*") or t.startswith("///"):
            return False
    return True
