from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

from .model import Locus, Query
from .query import FileIndex, query_file

HUNK_RE = re.compile(
    r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@"
)
GREP_RE = re.compile(
    r"^(?P<file>[^:\n]+):(?P<line>\d+)(?::(?P<col>\d+))?:(?P<rest>.*)$"
)
BARE_LINE_RE = re.compile(r"^(?P<line>\d+)[:\-](?P<rest>.*)$")


@dataclass
class DiffHit:
    path: str
    line: int  # 1-based in the chosen side
    side: str  # '+' or '-'
    text: str
    old_path: Optional[str] = None


def parse_unified_diff(text: str) -> list[DiffHit]:
    hits: list[DiffHit] = []
    old_path = ""
    new_path = ""
    old_ln = 0
    new_ln = 0
    for raw in text.splitlines():
        if raw.startswith("--- "):
            old_path = _diff_path(raw[4:])
            continue
        if raw.startswith("+++ "):
            new_path = _diff_path(raw[4:])
            continue
        if raw.startswith("diff --git "):
            old_path = new_path = ""
            continue
        m = HUNK_RE.match(raw)
        if m:
            old_ln = int(m.group(1))
            new_ln = int(m.group(3))
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            path = new_path or old_path
            if path and path != "/dev/null":
                hits.append(DiffHit(path=path, line=new_ln, side="+", text=raw[1:], old_path=old_path))
            new_ln += 1
            continue
        if raw.startswith("-") and not raw.startswith("---"):
            path = old_path or new_path
            if path and path != "/dev/null":
                hits.append(
                    DiffHit(path=path, line=old_ln, side="-", text=raw[1:], old_path=old_path)
                )
            old_ln += 1
            continue
        if raw.startswith("\\"):
            continue
        # context line
        if raw.startswith(" "):
            old_ln += 1
            new_ln += 1
    return hits


def _diff_path(spec: str) -> str:
    spec = spec.strip()
    if spec.startswith("a/") or spec.startswith("b/"):
        spec = spec[2:]
    if spec == "/dev/null":
        return "/dev/null"
    # strip tab timestamp
    if "\t" in spec:
        spec = spec.split("\t", 1)[0]
    if spec.startswith('"') and spec.endswith('"'):
        spec = spec[1:-1]
    return spec


def parse_grep_lines(text: str, default_file: Optional[str] = None) -> list[Query]:
    """Parse rg/grep -n output.

    Accepts:
      path:line:text          (rg -nH, git grep -n)
      path:line:col:text      (rg -n --column)
      line:text               (rg FILE with no -H) when default_file is set
    """
    out: list[Query] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        m = GREP_RE.match(raw)
        if m and not m.group("file").isdigit():
            path = m.group("file")
            if path.startswith("<stdin>") or path == "-":
                continue
            out.append(
                Query(
                    file=path,
                    line=int(m.group("line")),
                    here=m.group("rest").lstrip(),
                )
            )
            continue
        b = BARE_LINE_RE.match(raw)
        if b and default_file:
            out.append(
                Query(
                    file=default_file,
                    line=int(b.group("line")),
                    here=b.group("rest").lstrip(),
                )
            )
    return out


def parse_colon_target(spec: str) -> Optional[Query]:
    # FILE:LINE or FILE:LINE:col
    m = re.match(r"^(.*):(\d+)(?::\d+)?$", spec)
    if not m:
        return None
    path = m.group(1)
    if not path:
        return None
    return Query(file=path, line=int(m.group(2)))


def git_show(repo: Path, revision: str, relpath: str) -> Optional[str]:
    proc = subprocess.run(
        ["git", "show", f"{revision}:{relpath}"],
        cwd=repo,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", errors="replace")


def git_diff(repo: Path, paths: list[str], extra: Optional[list[str]] = None) -> str:
    cmd = ["git", "diff", "--no-color", "-U0"]
    if extra:
        cmd.extend(extra)
    cmd.append("--")
    cmd.extend(paths or [])
    proc = subprocess.run(cmd, cwd=repo, capture_output=True)
    return proc.stdout.decode("utf-8", errors="replace")


def git_repo_root(start: Optional[Path] = None) -> Optional[Path]:
    start = start or Path.cwd()
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return Path(proc.stdout.strip())


@dataclass
class SourceBag:
    """Cache of working-tree and revision snapshots."""

    repo: Optional[Path] = None
    indexes: dict[tuple[str, str], FileIndex] = field(default_factory=dict)

    def index_for(self, path: str, revision: Optional[str] = None) -> Optional[FileIndex]:
        key = (path, revision or ":wt")
        if key in self.indexes:
            return self.indexes[key]
        source: Optional[str] = None
        if revision and self.repo is not None:
            source = git_show(self.repo, revision, path)
        else:
            p = Path(path)
            if not p.is_absolute() and self.repo is not None:
                p = self.repo / path
            try:
                source = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                source = None
        if source is None:
            return None
        idx = FileIndex(source, path)
        self.indexes[key] = idx
        return idx

    def resolve_hit(self, hit: DiffHit, old_rev: str = "HEAD") -> Locus:
        rev = old_rev if hit.side == "-" else None
        lookup_path = hit.old_path if (hit.side == "-" and hit.old_path and hit.old_path != "/dev/null") else hit.path
        idx = self.index_for(lookup_path, rev)
        if idx is None:
            return Locus(
                file=hit.path,
                line=hit.line,
                here=hit.text,
                engine="none",
                error="source unavailable",
                side=hit.side,
            )
        loc = idx.at(hit.line)
        loc.file = hit.path
        loc.side = hit.side
        if hit.text and not loc.here:
            loc.here = hit.text
        return loc

    def resolve_query(self, q: Query) -> Locus:
        idx = self.index_for(q.file, q.revision)
        if idx is None:
            return Locus(file=q.file, line=q.line, here=q.here or "", engine="none", error="source unavailable")
        loc = idx.at(q.line)
        loc.file = q.file
        loc.side = q.side
        if q.here and not loc.here:
            loc.here = q.here
        return loc


def iter_scan_files(root: Path, extra_exts: Optional[set[str]] = None) -> Iterator[Path]:
    skip = {
        ".git",
        "node_modules",
        "target",
        "dist",
        "__pycache__",
        ".venv",
        "venv",
        "vendor",
        ".tox",
        "build",
        ".next",
        "coverage",
        ".build",
        "Pods",
    }
    from .query import BRACE_EXTS, PYTHON_EXTS

    exts = set(PYTHON_EXTS) | set(BRACE_EXTS)
    if extra_exts:
        exts |= extra_exts
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in skip for part in p.parts):
            continue
        if p.suffix.lower() in exts:
            yield p
