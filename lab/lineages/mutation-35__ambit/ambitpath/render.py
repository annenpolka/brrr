from __future__ import annotations

import json
from collections import defaultdict

from .scan import Hit


def _span(h: Hit) -> str:
    if h.start == h.end:
        return f"{h.loc.file}:{h.start}"
    return f"{h.loc.file}:{h.start}-{h.end}"


def tsv_line(h: Hit) -> str:
    loc = h.loc
    side = loc.side or "."
    here = loc.here.replace("\t", " ").strip()
    return "\t".join(
        [
            _span(h),
            str(h.nlines),
            side,
            str(loc.depth),
            loc.function or "",
            h.matched_text,
            loc.cond_path,
            here,
            loc.engine,
        ]
    )


def explain(h: Hit) -> str:
    loc = h.loc
    lines = [_span(h)]
    if loc.error:
        lines.append(f"  error  {loc.error}")
    lines.append(f"  match  {h.matched_text}")
    if loc.function:
        lines.append(f"  in     {loc.function}")
    for fr in loc.frames:
        if fr.kind in {"fn", "class", "impl", "struct", "enum", "protocol", "extension"}:
            continue
        mark = "←" if any(fr is m or (fr.kind, fr.pred, fr.line) == (m.kind, m.pred, m.line) for m in h.matched) else " "
        lines.append(f"  {fr.kind:<6} {fr.pred}  (L{fr.line}){mark}")
    here = loc.here.strip()
    if here:
        prefix = loc.side or "here"
        if prefix in {"+", "-"}:
            lines.append(f"  {prefix}      {here}")
        else:
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
    rec["matched"] = [
        {"kind": fr.kind, "pred": fr.pred, "line": fr.line} for fr in h.matched
    ]
    return json.dumps(rec, ensure_ascii=False)


def group_hits(hits: list[Hit]) -> str:
    """Cluster by the matched predicate, then by remaining path-condition."""
    buckets: dict[str, list[Hit]] = defaultdict(list)
    order: list[str] = []
    for h in hits:
        key = h.matched_text or "(none)"
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
            rest = h.loc.cond_path or "(top-level)"
            if rest not in by_rest:
                rest_order.append(rest)
            by_rest[rest].append(h)
        for rest in rest_order:
            members = by_rest[rest]
            depth = max(m.loc.depth for m in members)
            out.append(f"  [{rest}]  depth={depth}  spans={len(members)}")
            for h in members:
                side = h.loc.side or " "
                here = h.loc.here.strip()
                out.append(f"    {_span(h):<28}{side} {here}")
    return "\n".join(out)


def render(hits: list[Hit], *, mode: str) -> str:
    if mode == "json":
        return "\n".join(json_line(h) for h in hits)
    if mode == "explain":
        return "\n\n".join(explain(h) for h in hits)
    if mode == "group":
        return group_hits(hits)
    return "\n".join(tsv_line(h) for h in hits)


def render_chunk(hits: list[Hit], *, mode: str) -> str:
    """Render a batch of hits. --group is not chunkable; caller buffers."""
    if mode == "group":
        return ""
    return render(hits, mode=mode)


def write_chunk(out, hits: list[Hit], *, mode: str, already: int) -> int:
    """Write one file's hits. Returns new total. Flushes for streaming."""
    if not hits or mode == "group":
        return already
    text = render(hits, mode=mode)
    if not text:
        return already
    if already:
        out.write("\n\n" if mode == "explain" else "\n")
    out.write(text)
    if not text.endswith("\n"):
        out.write("\n")
    out.flush()
    return already + len(hits)
