from __future__ import annotations

import json
from collections import Counter

from nigh.extract import Corpus
from nigh.score import ACTIONABLE, Evidence, Finding


def format_human(findings: list[Finding], corpus: Corpus, *, all_status: bool) -> str:
    shown = findings if all_status else [f for f in findings if f.status in ACTIONABLE]
    lines: list[str] = []
    for f in shown:
        g = f.gate
        rhs = _fmt_rhs(g.rhs)
        header = f"{f.status:<10} {g.loc}  {g.lhs} {g.op} {rhs}"
        lines.append(header)
        if f.note:
            lines.append(f"           {f.note}")
        for ev in f.hits[:5]:
            lines.append(f"           HIT    {_fmt_ev(ev)}")
        for ev in f.nighes[:5]:
            lines.append(f"           NIGH   {_fmt_ev(ev)}")
        for ev in f.brinks[:4]:
            lines.append(f"           BRINK  {_fmt_ev(ev)}")
        for ev in f.misses[:3]:
            lines.append(f"           MISS   {_fmt_ev(ev)}")
        if f.status in {"CLOSED", "NIGH"} and f.family:
            fam = ", ".join(f"{e.value!r}@{e.loc}" for e in f.family[:4])
            lines.append(f"           family {fam}")
        lines.append("")
    return "\n".join(lines).rstrip() + ("\n" if shown else "")


def format_summary(findings: list[Finding], corpus: Corpus) -> str:
    counts = Counter(f.status for f in findings)
    bits = [
        f"files={corpus.files}",
        f"gates={len(corpus.gates)}",
        f"producers={len(corpus.producers)}",
    ]
    for key in ("NIGH", "CLOSED", "BRINK", "ONE-SIDED", "BALANCED", "HIT", "MISS"):
        if counts.get(key):
            bits.append(f"{key}={counts[key]}")
    if corpus.skipped:
        bits.append(f"skipped={corpus.skipped}")
    return "nigh " + " ".join(bits)


def format_tsv(findings: list[Finding], *, all_status: bool) -> str:
    shown = findings if all_status else [f for f in findings if f.status in ACTIONABLE]
    rows = [
        "\t".join(
            [
                "status",
                "path",
                "line",
                "lhs",
                "op",
                "rhs",
                "note",
                "evidence_kind",
                "evidence_value",
                "evidence_reason",
                "evidence_path",
                "evidence_line",
            ]
        )
    ]
    for f in shown:
        evs: list[tuple[str, Evidence]] = (
            [("hit", e) for e in f.hits[:3]]
            + [("nigh", e) for e in f.nighes[:3]]
            + [("brink", e) for e in f.brinks[:3]]
        )
        if not evs:
            rows.append(
                "\t".join(
                    [
                        f.status,
                        f.gate.loc.path,
                        str(f.gate.loc.line),
                        f.gate.lhs,
                        f.gate.op,
                        _fmt_rhs(f.gate.rhs),
                        f.note.replace("\t", " "),
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )
            )
            continue
        for kind, ev in evs:
            rows.append(
                "\t".join(
                    [
                        f.status,
                        f.gate.loc.path,
                        str(f.gate.loc.line),
                        f.gate.lhs,
                        f.gate.op,
                        _fmt_rhs(f.gate.rhs),
                        f.note.replace("\t", " "),
                        kind,
                        _cell(ev.value),
                        ev.reason,
                        ev.loc.path,
                        str(ev.loc.line),
                    ]
                )
            )
    return "\n".join(rows) + "\n"


def format_json(findings: list[Finding], corpus: Corpus, *, all_status: bool) -> str:
    shown = findings if all_status else [f for f in findings if f.status in ACTIONABLE]
    payload = {
        "files": corpus.files,
        "gates": len(corpus.gates),
        "producers": len(corpus.producers),
        "findings": [_finding_json(f) for f in shown],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _finding_json(f: Finding) -> dict:
    return {
        "status": f.status,
        "path": f.gate.loc.path,
        "line": f.gate.loc.line,
        "lhs": f.gate.lhs,
        "op": f.gate.op,
        "rhs": f.gate.rhs,
        "kind": f.gate.kind,
        "raw": f.gate.raw,
        "note": f.note,
        "hits": [_ev_json(e) for e in f.hits],
        "nighes": [_ev_json(e) for e in f.nighes],
        "brinks": [_ev_json(e) for e in f.brinks],
        "misses": [_ev_json(e) for e in f.misses],
        "family": [_ev_json(e) for e in f.family],
    }


def _ev_json(e: Evidence) -> dict:
    return {
        "value": e.value,
        "path": e.loc.path,
        "line": e.loc.line,
        "reason": e.reason,
        "dist": e.dist,
        "field": e.field,
    }


def _fmt_rhs(rhs: list) -> str:
    if len(rhs) == 1:
        return repr(rhs[0])
    return "[" + ", ".join(repr(x) for x in rhs) + "]"


def _fmt_ev(ev: Evidence) -> str:
    extra = ev.reason
    if ev.dist is not None:
        extra += f" d={ev.dist}"
    if ev.field:
        extra += f" field={ev.field}"
    return f"{ev.value!r}  {ev.loc}  ({extra})"


def _cell(value: object) -> str:
    if isinstance(value, str):
        return value.replace("\t", " ").replace("\n", " ")
    return str(value)
