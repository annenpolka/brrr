from __future__ import annotations

import json
from collections import defaultdict
from typing import Iterable

from .model import Locus


def tsv_line(loc: Locus) -> str:
    side = loc.side or "."
    here = loc.here.replace("\t", " ").strip()
    err = loc.error or ""
    return "\t".join(
        [
            f"{loc.file}:{loc.line}",
            side,
            str(loc.depth),
            loc.function or "",
            loc.cond_path,
            here,
            loc.engine,
            err,
        ]
    )


def explain(loc: Locus) -> str:
    lines = [f"{loc.file}:{loc.line}"]
    if loc.error:
        lines.append(f"  error  {loc.error}")
    if loc.function:
        lines.append(f"  in     {loc.function}")
    for fr in loc.frames:
        if fr.kind in {"fn", "class", "impl", "struct", "enum", "protocol", "extension"}:
            continue
        lines.append(f"  {fr.kind:<6} {fr.pred}  (L{fr.line})")
    if loc.after:
        lines.append(f"  after  {loc.after[-1]}")
    here = loc.here.strip()
    if here:
        prefix = loc.side or "here"
        if prefix in {"+", "-"}:
            lines.append(f"  {prefix}      {here}")
        else:
            lines.append(f"  here   {here}")
    if loc.engine:
        lines.append(f"  engine {loc.engine}  depth={loc.depth}")
    return "\n".join(lines)


def json_line(loc: Locus) -> str:
    return json.dumps(loc.to_record(), ensure_ascii=False)


def group_loci(loci: Iterable[Locus]) -> str:
    """Group changed/queried lines by (file, path-condition)."""
    buckets: dict[tuple[str, str], list[Locus]] = defaultdict(list)
    order: list[tuple[str, str]] = []
    for loc in loci:
        key = (loc.file, loc.cond_path or "(top-level)")
        if key not in buckets:
            order.append(key)
        buckets[key].append(loc)
    out: list[str] = []
    current_file = None
    for file, path in order:
        if file != current_file:
            out.append(file)
            current_file = file
        group = buckets[(file, path)]
        depth = max(g.depth for g in group)
        out.append(f"  [{path}]  depth={depth}  n={len(group)}")
        for loc in group:
            side = loc.side or " "
            here = loc.here.strip()
            out.append(f"    L{loc.line:<5}{side} {here}")
    return "\n".join(out)


def render(loci: list[Locus], *, mode: str) -> str:
    if mode == "json":
        return "\n".join(json_line(loc) for loc in loci)
    if mode == "explain":
        return "\n\n".join(explain(loc) for loc in loci)
    if mode == "group":
        return group_loci(loci)
    return "\n".join(tsv_line(loc) for loc in loci)
