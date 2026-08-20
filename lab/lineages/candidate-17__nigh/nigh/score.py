from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from nigh.extract import Corpus, Gate, Loc, Producer

STATUS_CLOSED = "CLOSED"
STATUS_NIGH = "NIGH"
STATUS_BRINK = "BRINK"
STATUS_ONESIDED = "ONE-SIDED"
STATUS_BALANCED = "BALANCED"
STATUS_HIT = "HIT"
STATUS_MISS = "MISS"

# Default report: the distance primitive, not "tests only ever use the true side".
ACTIONABLE = {STATUS_CLOSED, STATUS_NIGH}


@dataclass
class Evidence:
    value: str | int | float
    loc: Loc
    reason: str
    dist: int | None = None
    field: str | None = None


@dataclass
class Finding:
    status: str
    gate: Gate
    hits: list[Evidence] = field(default_factory=list)
    nighes: list[Evidence] = field(default_factory=list)
    misses: list[Evidence] = field(default_factory=list)
    brinks: list[Evidence] = field(default_factory=list)
    family: list[Evidence] = field(default_factory=list)
    note: str = ""

    @property
    def key(self) -> tuple:
        return (self.status, self.gate.loc.path, self.gate.loc.line, self.gate.raw)


@dataclass
class Index:
    strings: dict[str, list[Producer]]
    numbers: list[Producer]
    by_field: dict[str, list[Producer]]
    by_family: dict[str, list[Producer]]


def build_index(producers: Iterable[Producer]) -> Index:
    strings: dict[str, list[Producer]] = {}
    numbers: list[Producer] = []
    by_field: dict[str, list[Producer]] = {}
    by_family: dict[str, list[Producer]] = {}
    for p in producers:
        if p.kind == "string" and isinstance(p.value, str):
            strings.setdefault(p.value, []).append(p)
            fam = family_of(p.value)
            if fam:
                by_family.setdefault(fam, []).append(p)
        elif p.kind == "number":
            numbers.append(p)
        if p.field:
            by_field.setdefault(p.field, []).append(p)
    return Index(strings, numbers, by_field, by_family)


def family_of(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    if "." in value and re.match(r"^[A-Za-z][\w-]*\.", value):
        return value.split(".", 1)[0]
    if "/" in value and re.match(r"^[A-Za-z][\w-]+/", value):
        return value.split("/", 1)[0]
    return None


def shape(value: str) -> tuple[str, ...]:
    parts = re.split(r"[-_.]+", value)
    out: list[str] = []
    for part in parts:
        chunks = re.findall(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+", part)
        if chunks:
            out.extend(c.lower() for c in chunks)
        elif part:
            out.append(part.lower())
    return tuple(p for p in out if p)


def levenshtein(a: str, b: str, limit: int = 2) -> int | None:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > limit:
        return None
    if la > lb:
        a, b = b, a
        la, lb = lb, la
    prev = list(range(la + 1))
    for i, cb in enumerate(b, 1):
        cur = [i]
        row_min = i
        for j, ca in enumerate(a, 1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            val = min(ins, delete, sub)
            cur.append(val)
            if val < row_min:
                row_min = val
        if row_min > limit:
            return None
        prev = cur
    return prev[-1] if prev[-1] <= limit else None


def near_string(want: str, got: str, *, allow_typo: bool = True) -> tuple[str, int] | None:
    if want == got:
        return None
    if want.lower() == got.lower():
        return "case", 0
    if shape(want) and shape(want) == shape(got):
        return "inflection", 0
    if _affix(want, got):
        extra = abs(len(want) - len(got))
        return "affix", extra
    if not allow_typo:
        return None
    if not want or not got or want[0].lower() != got[0].lower():
        return None
    limit = 1
    if min(len(want), len(got)) >= 8:
        prefix = 0
        for a, b in zip(want.lower(), got.lower()):
            if a != b:
                break
            prefix += 1
        if prefix >= 3:
            limit = 2
    dist = levenshtein(want.lower(), got.lower(), limit)
    if dist is not None and dist > 0:
        return "typo", dist
    return None


def _affix(want: str, got: str) -> bool:
    if len(want) < 4 or len(got) < 4:
        return False
    shorter, longer = (want, got) if len(want) <= len(got) else (got, want)
    if not (longer.startswith(shorter) or longer.endswith(shorter)):
        # dotted extra segment: want="beam" got="kind.beam" no; action.x vs action.x.y
        if longer.startswith(shorter + ".") or longer.startswith(shorter + "-"):
            rest = longer[len(shorter) + 1 :]
            return "." not in rest and len(rest) <= 16
        return False
    extra = len(longer) - len(shorter)
    if extra <= 4:
        return True
    if longer.startswith(shorter) and longer[len(shorter)] in ".-_/":
        return extra <= 12
    return False


def same_span(a: Loc, b: Loc) -> bool:
    return a.path == b.path and a.line == b.line


def classify_gate(gate: Gate, index: Index) -> Finding:
    if gate.kind == "number":
        return _classify_number(gate, index)
    return _classify_string(gate, index)


def _classify_string(gate: Gate, index: Index) -> Finding:
    hits: list[Evidence] = []
    nighes: list[Evidence] = []
    family: list[Evidence] = []
    seen_nigh: set[tuple] = set()

    wanted = [v for v in gate.rhs if isinstance(v, str)]
    wanted_set = set(wanted)

    def string_hit(producer: str, want: str) -> bool:
        if gate.op in {"==", "===", "in"}:
            return producer == want
        if gate.op in {"!=", "!=="}:
            return producer == want  # a producer of the excluded value trips the false side
        if gate.op == "startswith":
            return producer.startswith(want)
        if gate.op == "endswith":
            return producer.endswith(want)
        if gate.op == "contains":
            return want in producer
        return producer == want

    for want in wanted:
        if gate.op in {"==", "===", "in", "!=", "!=="}:
            pool = index.strings.get(want, [])
        else:
            pool = [p for plist in index.strings.values() for p in plist]
        for p in pool:
            if not isinstance(p.value, str) or same_span(p.loc, gate.loc):
                continue
            if string_hit(p.value, want):
                hits.append(
                    Evidence(value=p.value, loc=p.loc, reason="exact", field=p.field)
                )

    scoped: list[Producer] = []
    if gate.field and gate.field in index.by_field:
        scoped.extend(p for p in index.by_field[gate.field] if p.kind == "string")
    for want in wanted:
        fam = family_of(want)
        if fam and fam in index.by_family:
            scoped.extend(index.by_family[fam])

    global_shape: list[Producer] = []
    global_typo: list[Producer] = []
    if not hits:
        for value, plist in index.strings.items():
            if not isinstance(value, str) or value in wanted_set:
                continue
            if any(
                value.lower() == w.lower() or (shape(value) and shape(value) == shape(w))
                for w in wanted
            ):
                global_shape.extend(plist)
            elif any(
                w
                and value
                and w[0].lower() == value[0].lower()
                and abs(len(w) - len(value)) <= 2
                and min(len(w), len(value)) >= 5
                for w in wanted
            ):
                global_typo.extend(plist)

    def consider(p: Producer, allow_typo: bool) -> None:
        if not isinstance(p.value, str) or p.value in wanted_set:
            return
        key = (p.value, p.loc.path, p.loc.line)
        if key in seen_prod or same_span(p.loc, gate.loc):
            return
        seen_prod.add(key)
        for want in wanted:
            near = near_string(want, p.value, allow_typo=allow_typo)
            if near is None:
                fam_w, fam_p = family_of(want), family_of(p.value)
                if fam_w and fam_w == fam_p and len(family) < 8:
                    family.append(
                        Evidence(value=p.value, loc=p.loc, reason="family", field=p.field)
                    )
                continue
            reason, dist = near
            nkey = (p.value, reason)
            if nkey in seen_nigh:
                return
            seen_nigh.add(nkey)
            nighes.append(
                Evidence(value=p.value, loc=p.loc, reason=reason, dist=dist, field=p.field)
            )
            return

    seen_prod: set[tuple] = set()
    for p in scoped:
        consider(p, True)
    for p in global_shape:
        consider(p, False)
    for p in global_typo:
        consider(p, True)

    nighes.sort(key=lambda e: (e.dist if e.dist is not None else 9, e.reason, str(e.value)))
    nighes = nighes[:8]
    hits = _dedupe_ev(hits)[:8]
    family = _dedupe_ev(family)[:6]

    if hits:
        # other values of same field / family → both sides exist
        other_domain = _other_domain(gate, index, wanted_set)
        if other_domain:
            return Finding(STATUS_BALANCED, gate, hits=hits, family=other_domain)
        return Finding(
            STATUS_ONESIDED,
            gate,
            hits=hits,
            note="corpus only ever constructs the true side",
        )

    if nighes:
        return Finding(
            STATUS_NIGH,
            gate,
            nighes=nighes,
            family=family,
            note="no exact producer; nearest vocabulary grazes the cut",
        )

    return Finding(
        STATUS_CLOSED,
        gate,
        family=family,
        note="compared-to value is never constructed in-repo",
    )


def _other_domain(gate: Gate, index: Index, wanted: set[str]) -> list[Evidence]:
    ev: list[Evidence] = []
    pool: list[Producer] = []
    if gate.field and gate.field in index.by_field:
        pool.extend(p for p in index.by_field[gate.field] if p.kind == "string")
    for want in wanted:
        fam = family_of(want)
        if fam:
            pool.extend(index.by_family.get(fam, []))
    seen: set[str] = set()
    for p in pool:
        if not isinstance(p.value, str) or p.value in wanted or p.value in seen:
            continue
        seen.add(p.value)
        ev.append(Evidence(value=p.value, loc=p.loc, reason="domain", field=p.field))
        if len(ev) >= 6:
            break
    return ev


def _classify_number(gate: Gate, index: Index) -> Finding:
    if not gate.rhs:
        return Finding(STATUS_CLOSED, gate, note="empty rhs")
    cut = gate.rhs[0]
    if not isinstance(cut, (int, float)):
        return Finding(STATUS_CLOSED, gate, note="non-numeric")

    hits: list[Evidence] = []
    misses: list[Evidence] = []
    brinks: list[Evidence] = []

    for p in index.numbers:
        if same_span(p.loc, gate.loc):
            continue
        if not isinstance(p.value, (int, float)):
            continue
        side = _side(gate.op, p.value, cut)
        ev = Evidence(value=p.value, loc=p.loc, reason=side or "other", field=p.field)
        if side == "hit":
            hits.append(ev)
        elif side == "miss":
            misses.append(ev)
        if _is_brink(gate.op, p.value, cut):
            brinks.append(
                Evidence(value=p.value, loc=p.loc, reason="brink", field=p.field)
            )

    hits = _dedupe_ev(hits)[:8]
    misses = _dedupe_ev(misses)[:8]
    brinks = _dedupe_ev(brinks)[:6]

    if gate.op in {"==", "==="}:
        if hits:
            if misses or any(p.value != cut for p in index.numbers):
                # other numbers exist; equality is live
                return Finding(STATUS_BALANCED, gate, hits=hits, misses=misses)
            return Finding(STATUS_ONESIDED, gate, hits=hits)
        near = [
            Evidence(value=p.value, loc=p.loc, reason="nearby", field=p.field)
            for p in index.numbers
            if isinstance(p.value, (int, float))
            and gate.field
            and p.field == gate.field
            and abs(float(p.value) - float(cut)) <= max(1.0, abs(float(cut)) * 0.05)
        ]
        if near:
            return Finding(STATUS_NIGH, gate, nighes=_dedupe_ev(near)[:6])
        return Finding(STATUS_CLOSED, gate, note="no numeric producer equals the cut")

    if gate.op in {"!=", "!=="}:
        # inverted equality
        if misses or hits:
            if hits and misses:
                return Finding(STATUS_BALANCED, gate, hits=misses, misses=hits)
            return Finding(STATUS_ONESIDED, gate, hits=hits or misses)

    if hits and misses:
        if brinks:
            return Finding(
                STATUS_BRINK,
                gate,
                hits=hits,
                misses=misses,
                brinks=brinks,
                note="corpus sits on the cut",
            )
        return Finding(STATUS_BALANCED, gate, hits=hits, misses=misses)
    if hits and not misses:
        status = STATUS_BRINK if brinks else STATUS_ONESIDED
        return Finding(
            status,
            gate,
            hits=hits,
            brinks=brinks,
            note="corpus never produces the false side",
        )
    if misses and not hits:
        if brinks:
            return Finding(
                STATUS_BRINK,
                gate,
                misses=misses,
                brinks=brinks,
                note="values touch the cut but never cross it",
            )
        return Finding(
            STATUS_ONESIDED,
            gate,
            misses=misses,
            note="corpus never produces the true side",
        )
    return Finding(STATUS_CLOSED, gate, note="no numeric producers against this cut")


def _side(op: str, value: int | float, cut: int | float) -> str | None:
    if op in {">"}:
        return "hit" if value > cut else "miss"
    if op in {">="}:
        return "hit" if value >= cut else "miss"
    if op in {"<"}:
        return "hit" if value < cut else "miss"
    if op in {"<="}:
        return "hit" if value <= cut else "miss"
    if op in {"==", "==="}:
        return "hit" if value == cut else "miss"
    if op in {"!=", "!=="}:
        return "hit" if value != cut else "miss"
    return None


def _is_brink(op: str, value: int | float, cut: int | float) -> bool:
    if op in {">", "<="}:
        # cut itself is the last miss / first hit boundary
        if value == cut:
            return True
        if isinstance(cut, int) and isinstance(value, int) and value == cut + 1 and op == ">":
            return True
        if isinstance(cut, int) and isinstance(value, int) and value == cut - 1 and op == "<=":
            return True
    if op in {"<", ">="}:
        if value == cut:
            return True
        if isinstance(cut, int) and isinstance(value, int) and value == cut - 1 and op == "<":
            return True
        if isinstance(cut, int) and isinstance(value, int) and value == cut + 1 and op == ">=":
            return True
    if isinstance(cut, float) or isinstance(value, float):
        span = max(1e-9, abs(float(cut)) * 0.05, 0.01)
        return abs(float(value) - float(cut)) <= span
    return False


def _dedupe_ev(items: list[Evidence]) -> list[Evidence]:
    seen: set[tuple] = set()
    out: list[Evidence] = []
    for e in items:
        key = (e.value, e.loc.path, e.loc.line, e.reason)
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def classify_corpus(corpus: Corpus) -> list[Finding]:
    index = build_index(corpus.producers)
    findings = [classify_gate(g, index) for g in corpus.gates]
    findings.sort(key=lambda f: (_rank(f.status), f.gate.loc.path, f.gate.loc.line))
    return findings


def _rank(status: str) -> int:
    order = {
        STATUS_NIGH: 0,
        STATUS_CLOSED: 1,
        STATUS_BRINK: 2,
        STATUS_ONESIDED: 3,
        STATUS_BALANCED: 4,
    }
    return order.get(status, 9)


def probe_value(value: str, corpus: Corpus) -> list[Finding]:
    """Which gates would this value trip or graze?"""
    num: int | float | None
    try:
        num = int(value) if re.fullmatch(r"-?\d+", value) else float(value) if re.fullmatch(r"-?\d+\.\d+", value) else None
    except ValueError:
        num = None

    out: list[Finding] = []
    for gate in corpus.gates:
        if gate.kind == "string":
            wanted = [v for v in gate.rhs if isinstance(v, str)]
            if any(_string_hits(gate.op, w, value) for w in wanted):
                ev = Evidence(value=value, loc=Loc("<probe>", 0, 0), reason="probe-hit")
                out.append(Finding(STATUS_HIT, gate, hits=[ev]))
                continue
            nighes = []
            for w in wanted:
                near = near_string(w, value)
                if near:
                    reason, dist = near
                    nighes.append(
                        Evidence(value=value, loc=Loc("<probe>", 0, 0), reason=reason, dist=dist)
                    )
            if nighes:
                out.append(Finding(STATUS_NIGH, gate, nighes=nighes))
        elif gate.kind == "number" and num is not None:
            cut = gate.rhs[0]
            if not isinstance(cut, (int, float)):
                continue
            side = _side(gate.op, num, cut)
            brink = _is_brink(gate.op, num, cut)
            ev = Evidence(value=num, loc=Loc("<probe>", 0, 0), reason=side or "other")
            if brink:
                out.append(Finding(STATUS_BRINK, gate, brinks=[ev], hits=[ev] if side == "hit" else [], misses=[ev] if side == "miss" else []))
            elif side == "hit":
                out.append(Finding(STATUS_HIT, gate, hits=[ev]))
            else:
                out.append(Finding(STATUS_MISS, gate, misses=[ev]))
    out.sort(key=lambda f: (_rank(f.status), f.gate.loc.path, f.gate.loc.line))
    return out


def _string_hits(op: str, want: str, got: str) -> bool:
    if op in {"==", "===", "in"}:
        return got == want
    if op in {"!=", "!=="}:
        return got != want
    if op == "startswith":
        return got.startswith(want)
    if op == "endswith":
        return got.endswith(want)
    if op == "contains":
        return want in got or got in want
    return False
