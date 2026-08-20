from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, TextIO

from .model import Locus, Query
from .query import BRACE_EXTS, PYTHON_EXTS, FileIndex, query_file

HUNK_RE = re.compile(
    r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@"
)
GREP_RE = re.compile(
    r"^(?P<file>[^:\n]+):(?P<line>\d+)(?::(?P<col>\d+))?:(?P<rest>.*)$"
)
FILE_LINE_RE = re.compile(r"^(?P<file>[^:\n]+):(?P<line>\d+)$")
BARE_LINE_RE = re.compile(r"^(?P<line>\d+)[:\-](?P<rest>.*)$")
LINE_ONLY_RE = re.compile(r"^:(\d+)(?::\d+)?$")
SOURCE_EXTS = set(PYTHON_EXTS) | set(BRACE_EXTS)


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


@dataclass
class Locator:
    """One stdin locator: a file to scan, optionally a line to pin."""

    file: str
    line: Optional[int] = None
    here: str = ""


class PrefixedStream:
    """Peek a few KB so we can tell locators from a diff, then replay."""

    def __init__(self, src: TextIO, peek_bytes: int = 8192):
        self._src = src
        self._prefix: list[str] = []
        got = 0
        for line in src:
            self._prefix.append(line)
            got += len(line)
            if got >= peek_bytes:
                break
        self.head = "".join(self._prefix)

    def lines(self) -> Iterator[str]:
        yield from self._prefix
        yield from self._src

    def remainder_text(self) -> str:
        return self.head + self._src.read()


def looks_like_path(text: str) -> bool:
    """rg -l / a bare filename. Refuse chatter like 'error:1' and 'demo ok'."""
    s = text.strip()
    if not s or s.startswith("<") or s == "-":
        return False
    if any(ch.isspace() for ch in s):
        return False
    p = Path(s)
    try:
        if p.is_file():
            return True
    except OSError:
        pass
    return p.suffix.lower() in SOURCE_EXTS


def parse_locator_line(raw: str, default_file: Optional[str] = None) -> Optional[Locator]:
    """Parse one rg/grep line.

    Accepts:
      path:line:text          (rg -nH, git grep -n)
      path:line:col:text      (rg -n --column)
      path:line               (bare address)
      line:text               (rg FILE with no -H) when default_file is set
      path                    (rg -l)
    """
    s = raw.rstrip("\n")
    if not s.strip():
        return None
    if looks_like_path(s):
        return Locator(file=s.strip(), line=None, here="")
    m = GREP_RE.match(s)
    if m and not m.group("file").isdigit():
        path = m.group("file")
        if path.startswith("<stdin>") or path == "-":
            return None
        return Locator(
            file=path,
            line=int(m.group("line")),
            here=m.group("rest").lstrip(),
        )
    fl = FILE_LINE_RE.match(s)
    if fl and not fl.group("file").isdigit():
        return Locator(file=fl.group("file"), line=int(fl.group("line")), here="")
    b = BARE_LINE_RE.match(s)
    if b:
        return Locator(
            file=default_file or "",
            line=int(b.group("line")),
            here=b.group("rest").lstrip(),
        )
    return None


def git_listed_files(repo: Path) -> list[Path]:
    """Tracked + untracked (not ignored). Names, not a content walk."""
    proc = subprocess.run(
        ["git", "ls-files", "-z", "-c", "-o", "--exclude-standard"],
        cwd=repo,
        capture_output=True,
    )
    if proc.returncode != 0:
        return []
    out: list[Path] = []
    for rel in proc.stdout.split(b"\0"):
        if not rel:
            continue
        p = repo / rel.decode("utf-8", errors="replace")
        if p.suffix.lower() in SOURCE_EXTS and p.is_file():
            out.append(p)
    return out


def pin_text(here: str) -> str:
    """Identity of a content pin: the stripped line, not a substring."""
    return (here or "").strip()


def file_matches_pins(path: Path, pins: list[tuple[int, str]]) -> bool:
    """True iff every pin's stripped text *is* the source line at that number.

    Substring containment is not uniqueness: a comment that mentions
    `return None` must not recover that file for pin `return None`.
    Empty `here` only requires the line to exist.
    """
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return False
    for ln, here in pins:
        if ln < 1 or ln > len(lines):
            return False
        if here and lines[ln - 1].strip() != here:
            return False
    return True


def recover_file_from_pins(
    locators: list[Locator],
    *,
    extra_files: Optional[list[Path]] = None,
    repo: Optional[Path] = None,
) -> Optional[Path]:
    """The LINE:text stream is a partial image of one file. Recover which.

    Single-file rg omits the filename. Matching (line, stripped-text)
    identity pins against git-listed sources (and any FILE operands)
    yields the file if unique. Every pin is consulted — a 17th
    disambiguator is not dropped.
    """
    pins = [(loc.line, pin_text(loc.here)) for loc in locators if loc.line]
    if not pins:
        return None
    search: list[Path] = []
    seen: set[str] = set()
    for p in extra_files or []:
        search.append(p)
    root = repo or git_repo_root()
    if root is not None:
        search.extend(git_listed_files(root))
    hits: list[Path] = []
    for p in search:
        try:
            key = str(p.resolve())
        except OSError:
            key = str(p)
        if key in seen:
            continue
        seen.add(key)
        if file_matches_pins(p, pins):
            hits.append(p)
            if len(hits) > 1:
                return None
    return hits[0] if len(hits) == 1 else None


def parse_grep_lines(text: str, default_file: Optional[str] = None) -> list[Query]:
    """Parse rg/grep -n output into Queries (line-pinning; --hits mode)."""
    out: list[Query] = []
    for raw in text.splitlines():
        loc = parse_locator_line(raw, default_file=default_file)
        if loc is None or loc.line is None or not loc.file:
            continue
        out.append(Query(file=loc.file, line=loc.line, here=loc.here or None))
    return out


def iter_locator_files(
    lines: Iterator[str],
    default_file: Optional[str] = None,
) -> Iterator[str]:
    """Yield each file the first time a locator names it. Stream-friendly."""
    seen: set[str] = set()
    for raw in lines:
        loc = parse_locator_line(raw, default_file=default_file)
        if loc is None:
            continue
        key = loc.file
        if key in seen:
            continue
        seen.add(key)
        yield key


def bind_seed_spec(spec: str, default_file: Optional[str]) -> str:
    """`:60` binds to the unique recovered file / FILE operand."""
    if default_file and LINE_ONLY_RE.match(spec):
        return f"{default_file}{spec}"
    return spec


def parse_colon_target(spec: str, default_file: Optional[str] = None) -> Optional[Query]:
    # FILE:LINE or FILE:LINE:col, or :LINE when a file was recovered
    spec = bind_seed_spec(spec, default_file)
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
