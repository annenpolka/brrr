from __future__ import annotations

import json
from collections import defaultdict

from .rhyme import Hit


def _span(h: Hit) -> str:
    if h.start == h.end:
        return f"{h.loc.file}:{h.start}"
    return f"{h.loc.file}:{h.start}-{h.end}"


def tsv_line(h: Hit) -> str:
    loc = h.loc
    here = loc.here.replace("\t", " ").strip()
    seed = "seed" if h.seed else "."
    return "\t".join(
        [
            _span(h),
            h.relation,
            seed,
            str(h.nlines),
            str(loc.depth),
            loc.function or "",
            h.extra_text,
            loc.cond_path,
            here,
            loc.engine,
        ]
    )


def explain(h: Hit, *, seed: bool = False) -> str:
    loc = h.loc
    tag = h.relation
    if h.seed:
        tag = "seed" if tag == "same" else f"seed/{tag}"
    lines = [f"{tag:<7} {_span(h)}"]
    if loc.error:
        lines.append(f"  error  {loc.error}")
    if loc.function:
        lines.append(f"  in     {loc.function}")
    if h.relation == "deeper" and h.extra:
        lines.append(f"  extra  {h.extra_text}")
    for fr in loc.cond_frames():
        mark = ""
        if h.extra and any(
            (fr.kind, fr.pred, fr.line) == (m.kind, m.pred, m.line) for m in h.extra
        ):
            mark = " +"
        lines.append(f"  {fr.kind:<6} {fr.pred}  (L{fr.line}){mark}")
    here = loc.here.strip()
    if here:
        lines.append(f"  here   {here}")
    extra = f"  n={h.nlines}" if h.nlines > 1 else ""
    if loc.engine:
        lines.append(f"  engine {loc.engine}  depth={loc.depth}{extra}")
    return "\n".join(lines)


def json_line(h: Hit) -> str:
    rec = h.loc.to_record()
    rec["start"] = h.start
    rec["end"] = h.end
    rec["nlines"] = h.nlines
    rec["relation"] = h.relation
    rec["seed"] = h.seed
    rec["extra"] = [
        {"kind": fr.kind, "pred": fr.pred, "line": fr.line} for fr in h.extra
    ]
    return json.dumps(rec, ensure_ascii=False)


def group_hits(hits: list[Hit]) -> str:
    """Cluster by relation, then by extra frames / remaining path."""
    buckets: dict[str, list[Hit]] = defaultdict(list)
    order: list[str] = []
    for h in hits:
        key = h.relation
        if key not in buckets:
            order.append(key)
        buckets[key].append(h)
    out: list[str] = []
    for key in order:
        group = buckets[key]
        out.append(f"{key}  n={len(group)}")
        by_rest: dict[str, list[Hit]] = defaultdict(list)
        rest_order: list[str] = []
        for h in group:
            rest = h.extra_text or h.loc.cond_path or "(exact)"
            if rest not in by_rest:
                rest_order.append(rest)
            by_rest[rest].append(h)
        for rest in rest_order:
            members = by_rest[rest]
            depth = max(m.loc.depth for m in members)
            label = rest if key == "deeper" else (members[0].loc.cond_path or "(top-level)")
            out.append(f"  [{label}]  depth={depth}  spans={len(members)}")
            for h in members:
                mark = "*" if h.seed else " "
                here = h.loc.here.strip()
                out.append(f"   {mark}{_span(h):<28} {here}")
    return "\n".join(out)


def render(hits: list[Hit], *, mode: str) -> str:
    if mode == "json":
        return "\n".join(json_line(h) for h in hits)
    if mode == "explain":
        return "\n\n".join(explain(h) for h in hits)
    if mode == "group":
        return group_hits(hits)
    return "\n".join(tsv_line(h) for h in hits)
