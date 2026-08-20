from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GrepHit:
    file: str
    line: int
    text: str = ""


@dataclass
class DiffHit:
    path: str
    line: int
    side: str
    text: str = ""


_GREP = re.compile(r"^(?P<file>.+):(?P<line>\d+)(?::(?P<rest>.*))?$")
_BARE = re.compile(r"^(?P<line>\d+):(?P<rest>.*)$")


def parse_grep_lines(text: str, default_file: str | None = None) -> list[GrepHit]:
    hits: list[GrepHit] = []
    for raw in text.splitlines():
        s = raw.rstrip("\n")
        if not s.strip():
            continue
        m = _GREP.match(s)
        if m and _looks_like_path(m.group("file")):
            hits.append(GrepHit(m.group("file"), int(m.group("line")), m.group("rest") or ""))
            continue
        b = _BARE.match(s)
        if b and default_file:
            hits.append(GrepHit(default_file, int(b.group("line")), b.group("rest") or ""))
    return hits


def _looks_like_path(file: str) -> bool:
    if not file:
        return False
    if file.isdigit():
        return False
    if "/" in file or "\\" in file:
        return True
    if "." in file.split(":")[0]:
        return True
    return False


def parse_unified_diff(text: str) -> list[DiffHit]:
    hits: list[DiffHit] = []
    path = ""
    new_ln = 0
    old_ln = 0
    hunk = False
    for raw in text.splitlines():
        if raw.startswith("diff --git "):
            hunk = False
            continue
        if raw.startswith("+++ "):
            path = _diff_path(raw[4:])
            continue
        if raw.startswith("--- "):
            continue
        if raw.startswith("@@"):
            old_ln, new_ln = _hunk_starts(raw)
            hunk = True
            continue
        if not hunk or not path:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            hits.append(DiffHit(path, new_ln, "+", raw[1:]))
            new_ln += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            hits.append(DiffHit(path, old_ln, "-", raw[1:]))
            old_ln += 1
        elif raw.startswith("\\"):
            continue
        else:
            # context
            old_ln += 1
            new_ln += 1
    return hits


def looks_like_diff(text: str) -> bool:
    return bool(
        re.search(r"^diff --git ", text, re.M)
        or re.search(r"^@@ ", text, re.M)
        or (re.search(r"^--- ", text, re.M) and re.search(r"^\+\+\+ ", text, re.M))
    )


def looks_like_grep(text: str, default_file: str | None = None) -> bool:
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if _GREP.match(s) and _looks_like_path(_GREP.match(s).group("file")):
            return True
        if default_file and _BARE.match(s):
            return True
    return False


def _diff_path(spec: str) -> str:
    spec = spec.strip()
    if spec.startswith("b/") or spec.startswith("a/"):
        spec = spec[2:]
    if spec == "/dev/null":
        return spec
    # drop tab-tab junk from `git diff`
    if "\t" in spec:
        spec = spec.split("\t", 1)[0]
    return spec


def _hunk_starts(header: str) -> tuple[int, int]:
    m = re.search(r"@@\s+-(\d+)(?:,\d+)?\s+\+(\d+)", header)
    if not m:
        return 0, 0
    return int(m.group(1)), int(m.group(2))


def walk_sources(root: Path) -> list[Path]:
    from .model import is_source_path

    skip = {".git", "node_modules", "target", "dist", "build", ".venv", "venv", "__pycache__"}
    out: list[Path] = []
    if root.is_file():
        return [root]
    for p in sorted(root.rglob("*")):
        if any(part in skip for part in p.parts):
            continue
        if p.is_file() and is_source_path(p):
            out.append(p)
    return out
