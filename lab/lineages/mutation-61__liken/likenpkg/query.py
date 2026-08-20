"""--same-as matching: path-condition snippet or post-image FILE:LINE."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from .model import Frame, Locus, collapse


KINDS = {
    "fn",
    "in",
    "class",
    "impl",
    "struct",
    "enum",
    "protocol",
    "extension",
    "given",
    "if",
    "elif",
    "else",
    "for",
    "while",
    "match",
    "switch",
    "case",
    "arm",
    "guard",
    "guard-else",
    "try",
    "except",
    "catch",
    "finally",
    "with",
    "eval",
    "for-else",
    "while-else",
    "try-else",
}

_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_STRING = re.compile(r'''\bb?"((?:\\.|[^"\\])*)"''')


def parse_colon(spec: str) -> Optional[Tuple[str, int]]:
    if ":" not in spec:
        return None
    file, _, rest = spec.rpartition(":")
    if file and rest.isdigit():
        return file, int(rest)
    parts = spec.rsplit(":", 2)
    if len(parts) == 3 and parts[1].isdigit():
        return parts[0], int(parts[1])
    if len(parts) >= 2 and parts[-1].isdigit():
        return ":".join(parts[:-1]), int(parts[-1])
    return None


def looks_like_pin(spec: str) -> bool:
    pin = parse_colon(spec)
    if not pin:
        return False
    file, _line = pin
    # a path-condition like 'fn foo: bar' is not a pin; pins look like files
    if "|" in file:
        return False
    if "/" in file or "\\" in file or "." in file:
        return True
    # bare basename.rs:12
    return True


def split_clauses(q: str) -> List[str]:
    parts: List[str] = []
    buf: List[str] = []
    depth = 0
    for ch in q:
        if ch in "([":
            depth += 1
            buf.append(ch)
        elif ch in ")]":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif ch == "|" and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf:
        parts.append("".join(buf).strip())
    return [p for p in parts if p]


@dataclass(frozen=True)
class Clause:
    kind: Optional[str]
    pred: str
    inverted: bool = False


def _strip_neg(pred: str) -> Tuple[str, bool]:
    p = pred.strip()
    inv = False
    while True:
        if p.startswith("¬"):
            p = p[1:].strip()
            inv = not inv
            if p.startswith("(") and p.endswith(")"):
                p = p[1:-1].strip()
            continue
        if p.startswith("!") and not p.startswith("!="):
            p = p[1:].strip()
            inv = not inv
            continue
        if p.startswith("not ") and (len(p) == 4 or not p[4].isalnum()):
            p = p[4:].strip()
            inv = not inv
            continue
        break
    return p, inv


def parse_path_query(q: str) -> List[Clause]:
    out: List[Clause] = []
    for raw in split_clauses(q):
        bits = raw.split(None, 1)
        kind: Optional[str] = None
        pred = raw
        if bits and bits[0] in KINDS:
            kind = "fn" if bits[0] == "in" else bits[0]
            pred = bits[1] if len(bits) > 1 else ""
        pred, inv = _strip_neg(pred)
        out.append(Clause(kind=kind, pred=pred, inverted=inv))
    return out


def _unescape(s: str) -> str:
    try:
        return bytes(s, "utf-8").decode("unicode_escape")
    except Exception:
        return s.replace('\\"', '"').replace("\\\\", "\\")


def normalize_pred(pred: str) -> str:
    """Drop b-string wrappers so starts_with(a/) matches bytes.starts_with(b\"a/\")."""

    def repl(m: re.Match) -> str:
        return _unescape(m.group(1))

    s = collapse(pred)
    s = _STRING.sub(repl, s)
    s = s.replace("¬", "!")
    s = re.sub(r"\s+", "", s)
    return s


def _ident_boundary(hay: str, start: int, end: int) -> bool:
    if start > 0 and (hay[start - 1].isalnum() or hay[start - 1] == "_"):
        return False
    if end < len(hay) and (hay[end].isalnum() or hay[end] == "_"):
        return False
    return True


def pred_contains(frame_pred: str, snippet: str) -> bool:
    if not snippet:
        return True
    hay = normalize_pred(frame_pred)
    needle = normalize_pred(snippet)
    if not needle:
        return True
    start = 0
    while True:
        i = hay.find(needle, start)
        if i < 0:
            return False
        if _ident_boundary(hay, i, i + len(needle)):
            return True
        start = i + 1


def frame_inverted(fr: Frame) -> bool:
    if fr.kind in {"else", "guard-else", "try-else", "for-else", "while-else"}:
        return True
    p = fr.pred.strip()
    if p.startswith("¬"):
        return True
    if p.startswith("!") and not p.startswith("!="):
        return True
    return False


def frame_matches(fr: Frame, clause: Clause) -> bool:
    if clause.kind:
        if clause.kind == "fn" and fr.kind != "fn":
            return False
        if clause.kind != "fn" and fr.kind != clause.kind:
            return False
    if not clause.pred:
        return True
    if frame_inverted(fr) != clause.inverted:
        # a given ¬(quoted "a/") must not satisfy given starts_with(a/)
        return False
    body = fr.pred
    if body.startswith("¬"):
        body = body[1:]
        if body.startswith("(") and body.endswith(")"):
            body = body[1:-1]
    return pred_contains(body, clause.pred)


def stack_matches(frames: Sequence[Frame], clauses: Sequence[Clause]) -> bool:
    i = 0
    for cl in clauses:
        found = False
        while i < len(frames):
            if frame_matches(frames[i], cl):
                found = True
                i += 1
                break
            i += 1
        if not found:
            return False
    return True


def under_seed(seed: Sequence[Frame], cand: Sequence[Frame]) -> bool:
    """True if every seed cond-frame is still in force on cand (ordered subsequence)."""
    si = 0
    for fr in cand:
        if si < len(seed) and fr.key() == seed[si].key():
            si += 1
    return si == len(seed)


def path_matches(path: str, spec: str) -> bool:
    if path == spec:
        return True
    if path.endswith("/" + spec) or path.endswith("\\" + spec):
        return True
    from pathlib import Path as _P

    if _P(path).name == spec or _P(path).name == _P(spec).name:
        return True
    return False
