"""Scan named files for loci that peal with a seed stack.

Default is one file at a time (the files stdin locators named). Tree
walk is opt-in via scan_paths / --walk.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator, Optional

from .diffio import iter_scan_files
from .model import Locus
from .query import index_source
from .rhyme import Hit, hit_for


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


def hits_in_file(
    path: Path,
    seed: Locus,
    *,
    exact: bool = False,
    include_eval: bool = False,
    any_fn: bool = False,
) -> list[Hit]:
    out: list[Hit] = []
    for loc in iter_file_loci(path):
        h = hit_for(
            seed,
            loc,
            exact=exact,
            include_eval=include_eval,
            any_fn=any_fn,
        )
        if h is not None:
            out.append(h)
    return out


_NOISE = {
    "{",
    "}",
    "};",
    "},",
    ")",
    ");",
    "]",
    "];",
    "else",
    "else:",
    "else {",
    "} else {",
    "try:",
    "finally:",
    "pass",
}


def is_noise(loc: Locus) -> bool:
    """Brace-only / blank / else-header lines. Not a statement in the arm."""
    here = loc.here.strip()
    if not here:
        return True
    if here in _NOISE:
        return True
    if here and all(ch in "{}();,[]" for ch in here):
        return True
    # The test line itself is not a statement under the current stack.
    if any(fr.kind == "eval" for fr in loc.frames):
        return True
    return False


def payload_score(loc: Locus, *, seed: bool = False) -> int:
    here = loc.here.strip()
    if is_noise(loc):
        return -4
    score = 1
    low = here.lstrip()
    for tok in (
        "return",
        "raise",
        "throw",
        "break",
        "continue",
        "let ",
        "var ",
        "Some(",
        "Ok(",
        "Err(",
    ):
        if low.startswith(tok) or f" {tok}" in f" {low}":
            score += 3
    if any(fr.kind == "eval" for fr in loc.frames):
        score -= 2
    if seed:
        score += 1
    return score


def collapse_hits(hits: Iterable[Hit], *, payload: bool = True) -> list[Hit]:
    """Merge contiguous same-stack rhymes into one span.

    The representative line is the highest payload_score in the span
    (statements beat `}` / blank), with a tie-break toward the seed.
    """
    collapsed: list[Hit] = []
    cur: Optional[Hit] = None
    cur_rep_seed = False
    for h in hits:
        if (
            cur is not None
            and h.loc.file == cur.loc.file
            and h.loc.path_key == cur.loc.path_key
            and h.relation == cur.relation
            and h.loc.line == cur.end + 1
        ):
            cur.end = h.loc.line
            cur.seed = cur.seed or h.seed
            if payload:
                h_score = payload_score(h.loc, seed=h.seed)
                c_score = payload_score(cur.loc, seed=cur_rep_seed)
                if h_score > c_score:
                    cur.loc = h.loc
                    cur.extra = h.extra
                    cur_rep_seed = h.seed
            else:
                cur.loc = h.loc
                cur.extra = h.extra
                cur_rep_seed = h.seed
            continue
        if cur is not None:
            collapsed.append(cur)
        cur = Hit(
            loc=h.loc,
            relation=h.relation,
            extra=h.extra,
            start=h.loc.line,
            end=h.loc.line,
            seed=h.seed,
        )
        cur_rep_seed = h.seed
    if cur is not None:
        collapsed.append(cur)
    return collapsed


def drop_noise(hits: Iterable[Hit], *, braces: bool = False) -> list[Hit]:
    if braces:
        return list(hits)
    return [h for h in hits if h.seed or not is_noise(h.loc)]


def _kw_hits(
    path: Path,
    seed: Locus,
    *,
    exact: bool,
    include_eval: bool,
    any_fn: bool,
) -> list[Hit]:
    return hits_in_file(
        path,
        seed,
        exact=exact,
        include_eval=include_eval,
        any_fn=any_fn,
    )


def scan_file(
    path: Path,
    seed: Locus,
    *,
    exact: bool = False,
    include_eval: bool = False,
    any_fn: bool = False,
    collapse: bool = True,
    payload: bool = True,
    braces: bool = False,
) -> list[Hit]:
    hits = _kw_hits(
        path,
        seed,
        exact=exact,
        include_eval=include_eval,
        any_fn=any_fn,
    )
    hits = drop_noise(hits, braces=braces)
    return collapse_hits(hits, payload=payload) if collapse else hits


def scan_paths(
    paths: list[Path],
    seed: Locus,
    *,
    exact: bool = False,
    include_eval: bool = False,
    any_fn: bool = False,
    collapse: bool = True,
    payload: bool = True,
    braces: bool = False,
) -> list[Hit]:
    hits: list[Hit] = []
    for root in paths:
        for fp in iter_scan_files(root):
            hits.extend(
                _kw_hits(
                    fp,
                    seed,
                    exact=exact,
                    include_eval=include_eval,
                    any_fn=any_fn,
                )
            )
    hits = drop_noise(hits, braces=braces)
    return collapse_hits(hits, payload=payload) if collapse else hits


def filter_loci(
    loci: Iterable[Locus],
    seed: Locus,
    *,
    exact: bool = False,
    include_eval: bool = False,
    any_fn: bool = False,
    collapse: bool = True,
    payload: bool = True,
    braces: bool = False,
) -> list[Hit]:
    hits = []
    for loc in loci:
        h = hit_for(
            seed,
            loc,
            exact=exact,
            include_eval=include_eval,
            any_fn=any_fn,
        )
        if h is not None:
            hits.append(h)
    hits = drop_noise(hits, braces=braces)
    return collapse_hits(hits, payload=payload) if collapse else hits
