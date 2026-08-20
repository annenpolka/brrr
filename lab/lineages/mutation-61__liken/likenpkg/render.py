from __future__ import annotations

import json
from collections import defaultdict
from typing import Iterable, List, Optional, Sequence, Tuple

from .model import Frame, Locus, is_payload


def tsv_line(loc: Locus) -> str:
    side = loc.side or "."
    here = loc.here.replace("\t", " ").strip()
    err = loc.error or ""
    placed = "ok" if loc.placed and not loc.error else "unplaced"
    return "\t".join(
        [
            "{}:{}".format(loc.file, loc.line),
            side,
            str(loc.depth),
            loc.function or "",
            loc.cond_path,
            here,
            loc.engine,
            loc.image,
            placed,
            err,
        ]
    )


def _common_prefix(loci: Sequence[Locus]) -> List[Frame]:
    if not loci:
        return []
    frames_list = [list(loc.cond_frames) for loc in loci]
    prefix: List[Frame] = []
    for i, fr in enumerate(frames_list[0]):
        if all(len(fs) > i and fs[i].key() == fr.key() for fs in frames_list):
            prefix.append(fr)
        else:
            break
    return prefix


def explain_hits(
    loci: Sequence[Locus],
    *,
    query: Optional[str] = None,
    payload: bool = False,
) -> str:
    shown = [loc for loc in loci if (not payload or is_payload(loc.here))]
    if not shown:
        shown = list(loci)
    lines: List[str] = []
    if query:
        lines.append("same-as {}".format(query))
    shared = _common_prefix(shown)
    if shared:
        lines.append("shared {}".format(" | ".join(fr.render() for fr in shared)))
        fn = next((fr for fr in shared if fr.kind == "fn"), None)
        if fn:
            lines.append("  in     {}".format(fn.pred))
        for fr in shared:
            if fr.kind in {"fn", "class"}:
                continue
            lines.append("  {:<6} {}  (L{})".format(fr.kind, fr.pred, fr.line))
    lines.append("n      {}  files={}".format(len(shown), len({loc.file for loc in shown})))
    buckets: dict = defaultdict(list)
    order: List[Tuple[str, Tuple]] = []
    nshared = len(shared)
    for loc in shown:
        extra = tuple(fr.key() for fr in loc.cond_frames[nshared:])
        key = (loc.file, extra)
        if key not in buckets:
            order.append(key)
        buckets[key].append(loc)
    current_file = None
    for file, extra_key in order:
        group = buckets[(file, extra_key)]
        if file != current_file:
            lines.append("")
            lines.append("{}  [{}]".format(file, group[0].image))
            current_file = file
        extra_frames = group[0].cond_frames[nshared:]
        if extra_frames:
            lines.append("  + {}".format(" | ".join(fr.render() for fr in extra_frames)))
        else:
            lines.append("  [same]")
        for loc in group:
            side = loc.side or "+"
            here = loc.here.strip()
            mark = "" if loc.placed and not loc.error else " UNPLACED"
            lines.append("    L{:<5}{} {}{}".format(loc.line, side, here, mark))
    return "\n".join(lines)


def group_loci(loci: Iterable[Locus], *, payload: bool = False) -> str:
    buckets = defaultdict(list)
    order: List[Tuple[str, str]] = []
    for loc in loci:
        if payload and not is_payload(loc.here):
            continue
        key = (loc.file, loc.cond_path or "(top-level)")
        if key not in buckets:
            order.append(key)
        buckets[key].append(loc)
    out: List[str] = []
    current_file = None
    for file, path in order:
        if file != current_file:
            out.append(file)
            current_file = file
        group = buckets[(file, path)]
        depth = max((g.depth for g in group), default=0)
        out.append("  [{}]  depth={}  n={}".format(path, depth, len(group)))
        for loc in group:
            side = loc.side or " "
            here = loc.here.strip()
            mark = "" if loc.placed and not loc.error else " UNPLACED"
            out.append("    L{:<5}{} {}{}".format(loc.line, side, here, mark))
    return "\n".join(out)


def render(
    loci: List[Locus],
    *,
    mode: str,
    query: Optional[str] = None,
    payload: bool = False,
) -> str:
    if mode == "json":
        return "\n".join(json.dumps(loc.to_record(), ensure_ascii=False) for loc in loci)
    if mode == "tsv":
        return "\n".join(tsv_line(loc) for loc in loci)
    if mode == "group":
        return group_loci(loci, payload=payload)
    return explain_hits(loci, query=query, payload=payload)
