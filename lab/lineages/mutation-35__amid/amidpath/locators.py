"""Stream locators: rg / grep / heading / json / bare LINE:text."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

from .diffio import parse_unified_diff
from .model import Query

GREP_RE = re.compile(
    r"^(?P<file>[^:\n]+):(?P<line>\d+)(?::(?P<col>\d+))?:(?P<rest>.*)$"
)
BARE_LINE_RE = re.compile(r"^(?P<line>\d+)[:\-](?P<rest>.*)$")

@dataclass
class StreamNote:
    """Side channel for why a stream produced no queries."""

    bare_no_file: int = 0
    json_matches: int = 0


_SOURCE_EXT = {
    ".py",
    ".pyi",
    ".rs",
    ".go",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".swift",
    ".java",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".hpp",
    ".cs",
    ".kt",
    ".kts",
    ".m",
    ".mm",
    ".scala",
    ".php",
    ".zig",
    ".rb",
    ".md",
}


def looks_like_diff(text: str) -> bool:
    return (
        text.startswith("diff --git ")
        or text.startswith("--- ")
        or text.startswith("+++ ")
        or "\n@@ " in text[:4000]
        or text.startswith("@@ ")
    )


def _as_heading(line: str) -> Optional[str]:
    s = line.strip()
    if not s or s.startswith(("#", "-", "+", "@@", " ", "\t")):
        return None
    if GREP_RE.match(s) and not s.split(":", 1)[0].isdigit():
        return None
    if BARE_LINE_RE.match(s):
        return None
    p = Path(s)
    if p.is_file():
        return s
    if "/" in s or "\\" in s:
        return s
    if p.suffix.lower() in _SOURCE_EXT:
        return s
    return None


def parse_rg_json_line(line: str) -> tuple[Optional[Query], Optional[str]]:
    """rg --json. Returns (query, heading). Begin events set heading only."""
    s = line.strip()
    if not s.startswith("{"):
        return None, None
    try:
        obj = json.loads(s)
    except json.JSONDecodeError:
        return None, None
    kind = obj.get("type")
    data = obj.get("data") or {}
    path_obj = data.get("path") or {}
    path = path_obj.get("text") if isinstance(path_obj, dict) else None
    if kind == "begin" and path:
        return None, path
    if kind != "match":
        return None, None
    ln = data.get("line_number")
    if not path or not ln:
        return None, None
    text = ""
    lines = data.get("lines") or {}
    if isinstance(lines, dict):
        text = lines.get("text") or ""
    text = text.replace("\n", "").replace("\r", "").lstrip()
    return Query(file=path, line=int(ln), here=text), path


def parse_locator_line(
    line: str,
    *,
    default_file: Optional[str] = None,
    heading: Optional[str] = None,
) -> Optional[Query]:
    raw = line.rstrip("\n\r")
    if not raw.strip():
        return None
    m = GREP_RE.match(raw)
    if m and not m.group("file").isdigit():
        path = m.group("file")
        if path.startswith("<stdin>") or path == "-":
            return None
        return Query(
            file=path,
            line=int(m.group("line")),
            here=m.group("rest").lstrip(),
        )
    b = BARE_LINE_RE.match(raw)
    if b:
        path = default_file or heading
        if not path:
            return None
        return Query(
            file=path,
            line=int(b.group("line")),
            here=b.group("rest").lstrip(),
        )
    return None


def iter_queries(
    lines: Iterable[str],
    *,
    default_file: Optional[str] = None,
    note: Optional[StreamNote] = None,
) -> Iterator[Query]:
    """Yield locators as they arrive. Understands rg --heading and --json."""
    heading: Optional[str] = None
    for raw in lines:
        line = raw.rstrip("\n\r")
        if not line.strip():
            continue
        if line.lstrip().startswith("{"):
            q, head = parse_rg_json_line(line)
            if head:
                heading = head
            if q is not None:
                if note is not None:
                    note.json_matches += 1
                heading = q.file
                yield q
            continue
        q = parse_locator_line(line, default_file=default_file, heading=heading)
        if q is not None:
            heading = q.file
            yield q
            continue
        b = BARE_LINE_RE.match(line)
        if b and not (default_file or heading):
            if note is not None:
                note.bare_no_file += 1
            continue
        h = _as_heading(line)
        if h:
            heading = h


def queries_from_text(text: str, *, default_file: Optional[str] = None) -> list[Query]:
    return list(iter_queries(text.splitlines(), default_file=default_file))


def files_from_diff(text: str) -> list[str]:
    seen: list[str] = []
    have: set[str] = set()
    for hit in parse_unified_diff(text):
        path = hit.path
        if not path or path == "/dev/null" or path in have:
            continue
        have.add(path)
        seen.append(path)
    return seen
