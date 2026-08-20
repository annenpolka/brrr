"""Walk sources and invert: predicate snippet → loci."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

from .diffio import iter_scan_files
from .match import Matcher, STRUCT_KINDS
from .model import Frame, Locus
from .query import index_source


@dataclass
class Hit:
    loc: Locus
    matched: list[Frame]
    start: int = 0
    end: int = 0

    def __post_init__(self) -> None:
        if not self.start:
            self.start = self.loc.line
        if not self.end:
            self.end = self.loc.line

    @property
    def nlines(self) -> int:
        return self.end - self.start + 1

    @property
    def matched_text(self) -> str:
        return " | ".join(fr.render() for fr in self.matched)

    @property
    def rest_path(self) -> str:
        keys = {(fr.kind, fr.pred) for fr in self.matched}
        kept = [fr for fr in self.loc.frames if (fr.kind, fr.pred) not in keys]
        return " | ".join(fr.render() for fr in kept) if kept else "(only this)"


def iter_file_loci(path: Path) -> Iterator[Locus]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    idx = index_source(source, str(path))
    for ln in range(1, idx.nlines + 1):
        loc = idx.at(ln)
        loc.file = str(path)
        if loc.error:
            continue
        yield loc


def hits_in_file(path: Path, matcher: Matcher) -> list[Hit]:
    out: list[Hit] = []
    for loc in iter_file_loci(path):
        matched = matcher.matching_frames(loc)
        if matched:
            out.append(Hit(loc=loc, matched=matched))
    return out


def collapse_hits(hits: Iterable[Hit]) -> list[Hit]:
    """Merge contiguous same-stack matches into one span."""
    collapsed: list[Hit] = []
    cur: Optional[Hit] = None
    for h in hits:
        if (
            cur is not None
            and h.loc.file == cur.loc.file
            and h.loc.path_key == cur.loc.path_key
            and h.loc.line == cur.end + 1
        ):
            cur.end = h.loc.line
            # prefer a payload line as the representative
            if _payload_score(h.loc) > _payload_score(cur.loc):
                cur.loc = h.loc
            continue
        if cur is not None:
            collapsed.append(cur)
        cur = Hit(loc=h.loc, matched=h.matched, start=h.loc.line, end=h.loc.line)
    if cur is not None:
        collapsed.append(cur)
    return collapsed


def _payload_score(loc: Locus) -> int:
    here = loc.here.strip()
    if not here or here.endswith(":"):
        return 0
    score = 1
    low = here.lstrip()
    for tok in ("return", "raise", "throw", "break", "continue", "let ", "var "):
        if low.startswith(tok) or f" {tok}" in f" {low}":
            score += 3
    if any(fr.kind == "eval" for fr in loc.frames):
        score -= 2
    return score


def scan_paths(paths: list[Path], matcher: Matcher, *, collapse: bool = True) -> list[Hit]:
    hits: list[Hit] = []
    for root in paths:
        for fp in iter_scan_files(root):
            hits.extend(hits_in_file(fp, matcher))
    return collapse_hits(hits) if collapse else hits


def filter_loci(loci: Iterable[Locus], matcher: Matcher, *, collapse: bool = True) -> list[Hit]:
    hits = []
    for loc in loci:
        matched = matcher.matching_frames(loc)
        if matched:
            hits.append(Hit(loc=loc, matched=matched))
    return collapse_hits(hits) if collapse else hits


def matcher_from_locus(loc: Locus) -> Matcher:
    """AND of that line's in-force condition frames."""
    snippets: list[str] = []
    for fr in loc.frames:
        if fr.kind in STRUCT_KINDS or fr.kind == "eval":
            continue
        text = fr.pred.strip() or fr.render()
        if text:
            snippets.append(text)
    return Matcher(snippets=snippets)
