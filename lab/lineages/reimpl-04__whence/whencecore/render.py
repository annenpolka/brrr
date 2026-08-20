from __future__ import annotations

import json
from collections import defaultdict

from .model import Locus

EXPLAIN_KIND = {
    "fn": "in",
}


def render_explain(loc: Locus) -> str:
    lines = [f"{loc.file}:{loc.line}"]
    if loc.error:
        lines.append(f"  {'error':<6} {loc.error}")
        lines.append(f"  engine {loc.engine}  depth={loc.depth}")
        return "\n".join(lines)
    for fr in loc.frames:
        kind = EXPLAIN_KIND.get(fr.kind, fr.kind)
        extra = ""
        if fr.line and fr.kind != "fn":
            extra = f"  (L{fr.line})"
        lines.append(f"  {kind:<6} {fr.pred}{extra}".rstrip())
    if loc.after:
        lines.append(f"  {'after':<6} {loc.after[-1]}")
    here_kind = loc.side if loc.side in {"+", "-"} else "here"
    here_txt = loc.here.strip() if loc.here else ""
    if here_txt or here_kind != "here":
        lines.append(f"  {here_kind:<6} {here_txt}".rstrip())
    lines.append(f"  engine {loc.engine}  depth={loc.depth}")
    return "\n".join(lines)


def render_tsv(loc: Locus) -> str:
    side = loc.side if loc.side in {"+", "-"} else "."
    here = loc.here.strip() if loc.here else ""
    err = loc.error or ""
    fn = loc.function or ""
    return "\t".join(
        [
            f"{loc.file}:{loc.line}",
            side,
            str(loc.depth),
            fn,
            loc.path,
            here,
            loc.engine,
            err,
        ]
    )


def render_json(loc: Locus) -> str:
    rec = {
        "file": loc.file,
        "line": loc.line,
        "col": loc.col,
        "here": loc.here,
        "function": loc.function,
        "depth": loc.depth,
        "path": loc.path,
        "engine": loc.engine,
        "error": loc.error,
        "side": loc.side,
        "after": loc.after,
        "frames": [
            {"kind": f.kind, "pred": f.pred, "line": f.line, "end_line": f.end_line}
            for f in loc.frames
        ],
    }
    return json.dumps(rec, ensure_ascii=False)


def render_group(loci: list[Locus]) -> str:
    by_file: dict[str, list[Locus]] = defaultdict(list)
    for loc in loci:
        if loc.error:
            continue
        by_file[loc.file].append(loc)
    chunks: list[str] = []
    for file, items in by_file.items():
        chunks.append(file)
        buckets: dict[str, list[Locus]] = defaultdict(list)
        order: list[str] = []
        for loc in items:
            key = loc.path
            if key not in buckets:
                order.append(key)
            buckets[key].append(loc)
        for key in order:
            group = buckets[key]
            depth = group[0].depth
            chunks.append(f"  [{key}]  depth={depth}  n={len(group)}")
            for loc in group:
                side_ch = loc.side if loc.side in {"+", "-"} else " "
                src = loc.here.strip() if loc.here else ""
                chunks.append(f"    L{loc.line:<5}{side_ch} {src}".rstrip())
    return "\n".join(chunks)
