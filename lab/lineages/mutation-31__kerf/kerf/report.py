from __future__ import annotations

from collections import Counter

from kerf.extract import Corpus
from kerf.score import ACTIONABLE, Evidence, Finding


TSV_COLS = (
    "value",
    "status",
    "path",
    "line",
    "lhs",
    "op",
    "rhs",
    "reason",
    "field",
)


def format_human(findings: list[Finding], corpus: Corpus) -> str:
    lines: list[str] = []
    for f in findings:
        g = f.gate
        rhs = _fmt_rhs(g.rhs)
        shown = f.value if f.value is not None else ""
        header = f"{_cell(shown):<8} {f.status:<10} {g.loc}  {g.lhs} {g.op} {rhs}"
        lines.append(header)
        if f.note:
            lines.append(f"         {f.note}")
        lines.append("")
    return "\n".join(lines).rstrip() + ("\n" if findings else "")


def format_summary(findings: list[Finding], corpus: Corpus) -> str:
    counts = Counter(f.status for f in findings)
    bits = [
        f"files={corpus.files}",
        f"gates={len(corpus.gates)}",
        f"producers={len(corpus.producers)}",
        f"enums={len(corpus.enums)}",
    ]
    for key in ("HIT", "OFFBY", "BRINK", "SENTINEL", "NEIGHBOR", "MISS"):
        if counts.get(key):
            bits.append(f"{key}={counts[key]}")
    if corpus.skipped:
        bits.append(f"skipped={corpus.skipped}")
    return "kerf " + " ".join(bits)


def format_tsv(findings: list[Finding], *, header: bool) -> str:
    rows: list[str] = []
    if header:
        rows.append("\t".join(TSV_COLS))
    for f in findings:
        g = f.gate
        reason = f.cuts[0].reason if f.cuts else ""
        val = f.value
        if val is None and f.cuts:
            val = f.cuts[0].value
        rows.append(
            "\t".join(
                [
                    _cell(val if val is not None else ""),
                    f.status,
                    g.loc.path,
                    str(g.loc.line),
                    g.lhs,
                    g.op,
                    _fmt_rhs(g.rhs),
                    reason.replace("\t", " "),
                    g.field,
                ]
            )
        )
    if not rows:
        return ""
    return "\n".join(rows) + "\n"


def format_json(findings: list[Finding], corpus: Corpus) -> str:
    import json

    payload = {
        "files": corpus.files,
        "gates": len(corpus.gates),
        "producers": len(corpus.producers),
        "enums": [
            {"name": e.name, "members": e.members, "path": e.loc.path, "via": e.via}
            for e in corpus.enums
        ],
        "findings": [_finding_json(f) for f in findings],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _finding_json(f: Finding) -> dict:
    return {
        "value": f.value,
        "status": f.status,
        "path": f.gate.loc.path,
        "line": f.gate.loc.line,
        "lhs": f.gate.lhs,
        "op": f.gate.op,
        "rhs": f.gate.rhs,
        "kind": f.gate.kind,
        "raw": f.gate.raw,
        "note": f.note,
        "reason": f.cuts[0].reason if f.cuts else "",
        "field": f.gate.field,
        "cuts": [_ev_json(e) for e in f.cuts],
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
    return ",".join(_cell(x) for x in rhs)


def _cell(value: object) -> str:
    if isinstance(value, str):
        return value.replace("\t", " ").replace("\n", " ")
    return str(value)


# keep ACTIONABLE imported so --scan summaries stay aligned with the linter set
_ = ACTIONABLE
