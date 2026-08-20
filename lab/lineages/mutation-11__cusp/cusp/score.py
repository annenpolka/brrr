from __future__ import annotations

import re
from dataclasses import dataclass, field
from cusp.extract import (
    Corpus,
    is_sentinel_num,
    EnumDecl,
    Gate,
    Loc,
    Producer,
    family_of,
    is_sentinel_num,
    is_sentinel_str,
)

STATUS_BRINK = "BRINK"
STATUS_OFFBY = "OFFBY"
STATUS_SENTINEL = "SENTINEL"
STATUS_NEIGHBOR = "NEIGHBOR"
STATUS_HIT = "HIT"
STATUS_MISS = "MISS"

# The whole report *is* the cut. No CLOSED. No string-edit NIGH.
ACTIONABLE = {STATUS_BRINK, STATUS_OFFBY, STATUS_SENTINEL, STATUS_NEIGHBOR}


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
    cuts: list[Evidence] = field(default_factory=list)
    note: str = ""

    @property
    def key(self) -> tuple:
        return (self.status, self.gate.loc.path, self.gate.loc.line, self.gate.raw)


@dataclass
class Index:
    numbers: list[Producer]
    enums: list[Producer]
    by_field: dict[str, list[Producer]]
    by_family: dict[str, list[Producer]]
    decls: list[EnumDecl]
    members_of: dict[str, EnumDecl]
    member_index: dict[str, list[EnumDecl]]


def build_index(corpus: Corpus) -> Index:
    numbers: list[Producer] = []
    enums: list[Producer] = []
    by_field: dict[str, list[Producer]] = {}
    by_family: dict[str, list[Producer]] = {}
    members_of: dict[str, EnumDecl] = {}
    member_index: dict[str, list[EnumDecl]] = {}
    for p in corpus.producers:
        if p.kind == "number":
            numbers.append(p)
        else:
            enums.append(p)
            if isinstance(p.value, str):
                fam = family_of(p.value)
                if fam:
                    by_family.setdefault(fam, []).append(p)
        if p.field:
            by_field.setdefault(p.field, []).append(p)
    for decl in corpus.enums:
        members_of[decl.name] = decl
        for m in decl.members:
            member_index.setdefault(m, []).append(decl)
            member_index.setdefault(m.lower(), []).append(decl)
    return Index(numbers, enums, by_field, by_family, list(corpus.enums), members_of, member_index)


def same_span(a: Loc, b: Loc) -> bool:
    return a.path == b.path and a.line == b.line


def classify_gate(gate: Gate, index: Index) -> Finding | None:
    if gate.kind == "number" or gate.op == "range":
        return _classify_number(gate, index)
    return _classify_enum(gate, index)


TRIVIAL_NUM = {0, 1, -1, 2, 0.0, 1.0, -1.0, 2.0}


def _numeric_in_scope(gate: Gate, p: Producer) -> bool:
    """Same field always; same-file anonymous literals only on a distinctive cut."""
    if not isinstance(p.value, (int, float)) or isinstance(p.value, bool):
        return False
    if same_span(p.loc, gate.loc):
        return False
    if p.loc.path == "<probe>":
        return True
    if gate.field and p.field:
        return gate.field == p.field
    if p.field and gate.field and p.field != gate.field:
        return False
    if p.field and not gate.field:
        return False
    if p.loc.path != gate.loc.path:
        return False
    # `err != -1` next to `return -1` — anonymous sentinel on an exclusion
    if gate.op in {"!=", "!=="} and any(is_sentinel_num(v) for v in _cut_values(gate)):
        return True
    return any(_distinctive_cut(v) for v in _cut_values(gate))


def _cut_values(gate: Gate) -> list[int | float]:
    if gate.op == "range":
        return [v for v in (gate.lo, gate.hi) if isinstance(v, (int, float))]
    return [v for v in gate.rhs if isinstance(v, (int, float))]


def _distinctive_cut(val: int | float) -> bool:
    """0/1/-1 are ambient. 2 is a real exclusive fence (`n > 2`)."""
    if isinstance(val, float) and val not in {0.0, 1.0, -1.0}:
        return True
    return val not in {0, 1, -1, 0.0, 1.0, -1.0}


def _trivial_offby(cut: int | float, val: int | float) -> bool:
    return cut in TRIVIAL_NUM and val in TRIVIAL_NUM


def _trivial_range(gate: Gate) -> bool:
    if gate.op != "range" or gate.lo is None or gate.hi is None:
        return False
    try:
        span = float(gate.hi) - float(gate.lo)
    except (TypeError, ValueError):
        return False
    # `0..<1`, `1...3`, slice extents — not a domain bound
    return span <= 2 and float(gate.lo) <= 5


def _scoped_numbers(gate: Gate, index: Index) -> list[Producer]:
    out: list[Producer] = []
    seen: set[tuple] = set()

    def take(p: Producer) -> None:
        if not _numeric_in_scope(gate, p):
            return
        key = (p.value, p.loc.path, p.loc.line)
        if key in seen:
            return
        seen.add(key)
        out.append(p)

    if gate.field:
        for p in index.by_field.get(gate.field, []):
            if p.kind == "number":
                take(p)
    for p in index.numbers:
        take(p)
    return out


def _scoped_enums(gate: Gate, index: Index) -> list[Producer]:
    out: list[Producer] = []
    seen: set[tuple] = set()

    def take(p: Producer) -> None:
        if not isinstance(p.value, str):
            return
        if same_span(p.loc, gate.loc):
            return
        key = (p.value, p.loc.path, p.loc.line)
        if key in seen:
            return
        seen.add(key)
        out.append(p)

    if gate.field:
        for p in index.by_field.get(gate.field, []):
            if p.kind in {"enum", "string"}:
                take(p)
    for want in gate.rhs:
        if not isinstance(want, str):
            continue
        fam = family_of(want)
        if fam:
            for p in index.by_family.get(fam, []):
                take(p)
    # same-file constructions only — decls give order, not a global name soup
    for p in index.enums:
        if p.loc.path == gate.loc.path or p.loc.path == "<probe>":
            take(p)
    return out


def _decls_for(want: str, gate: Gate, index: Index) -> list[EnumDecl]:
    found: list[EnumDecl] = []
    seen: set[int] = set()

    def take(decl: EnumDecl) -> None:
        if id(decl) in seen:
            return
        seen.add(id(decl))
        found.append(decl)

    head = gate.lhs.split(".")[0]
    for decl in index.decls:
        name_hit = decl.name in {gate.field, head, gate.lhs}
        same_file = decl.loc.path == gate.loc.path
        member_hit = _member_match(want, decl.members)
        if name_hit or (member_hit and same_file):
            take(decl)
    return found


def _member_match(value: str, members: list[str]) -> bool:
    leaf = value.split(".")[-1]
    low = {m.lower() for m in members}
    return value in members or leaf in members or value.lower() in low or leaf.lower() in low


def _classify_number(gate: Gate, index: Index) -> Finding | None:
    pool = _scoped_numbers(gate, index)
    if gate.op == "range" and gate.lo is not None and gate.hi is not None:
        return _classify_range(gate, pool)

    if not gate.rhs:
        return None
    cut = gate.rhs[0]
    if not isinstance(cut, (int, float)):
        return None

    if gate.op in {"==", "==="}:
        return _classify_num_eq(gate, cut, pool, inverted=False)
    if gate.op in {"!=", "!=="}:
        return _classify_num_eq(gate, cut, pool, inverted=True)
    if gate.op in INEQ:
        return _classify_ineq(gate, cut, pool)
    return None


INEQ = {">", ">=", "<", "<="}


def _classify_ineq(gate: Gate, cut: int | float, pool: list[Producer]) -> Finding | None:
    incl, excl = _bound_points(gate.op, cut)
    on_incl: list[Evidence] = []
    on_excl: list[Evidence] = []
    for p in pool:
        val = p.value
        assert isinstance(val, (int, float))
        if incl is not None and val == incl:
            on_incl.append(
                Evidence(value=val, loc=p.loc, reason="inclusive", field=p.field)
            )
        elif excl is not None and val == excl:
            on_excl.append(
                Evidence(value=val, loc=p.loc, reason="exclusive", field=p.field)
            )
    on_incl = _dedupe_ev(on_incl)[:6]
    on_excl = _dedupe_ev(on_excl)[:6]
    if not on_incl and not on_excl:
        return None
    # Sentinel zero/minus-one bound is labeled SENTINEL, not generic BRINK.
    if is_sentinel_num(cut) and (on_excl or on_incl):
        return Finding(
            STATUS_SENTINEL,
            gate,
            cuts=on_excl + on_incl,
            note=_sentinel_note(gate.op, cut, bool(on_excl)),
        )
    if on_excl and not on_incl:
        shown = on_excl[0].value
        return Finding(
            STATUS_BRINK,
            gate,
            cuts=on_excl,
            note=f"exclusive bound; {shown} is constructed (last miss)",
        )
    if on_incl and not on_excl:
        shown = on_incl[0].value
        return Finding(
            STATUS_BRINK,
            gate,
            cuts=on_incl,
            note=f"inclusive bound; {shown} is constructed (first/last hit)",
        )
    return Finding(
        STATUS_BRINK,
        gate,
        cuts=on_excl + on_incl,
        note="constructed values sit on both sides of the cut",
    )


def _bound_points(op: str, cut: int | float) -> tuple[int | float | None, int | float | None]:
    """Return (inclusive_endpoint, exclusive_endpoint) that sit on this cut."""
    if op == ">":
        incl = cut + 1 if isinstance(cut, int) else None
        return incl, cut
    if op == ">=":
        excl = cut - 1 if isinstance(cut, int) else None
        return cut, excl
    if op == "<":
        incl = cut - 1 if isinstance(cut, int) else None
        return incl, cut
    if op == "<=":
        excl = cut + 1 if isinstance(cut, int) else None
        return cut, excl
    return None, None


def _classify_range(gate: Gate, pool: list[Producer]) -> Finding | None:
    if _trivial_range(gate):
        return None
    lo, hi = gate.lo, gate.hi
    assert lo is not None and hi is not None
    cuts: list[Evidence] = []
    for p in pool:
        val = p.value
        assert isinstance(val, (int, float))
        if val == lo:
            cuts.append(Evidence(value=val, loc=p.loc, reason="inclusive", field=p.field))
        elif val == hi:
            reason = "inclusive" if gate.hi_inclusive else "exclusive"
            cuts.append(Evidence(value=val, loc=p.loc, reason=reason, field=p.field))
        elif (
            isinstance(val, int)
            and isinstance(lo, int)
            and isinstance(hi, int)
            and val in {lo - 1, hi - 1 if not gate.hi_inclusive else hi + 1}
        ):
            cuts.append(Evidence(value=val, loc=p.loc, reason="off-by-one", field=p.field))
    cuts = _dedupe_ev(cuts)[:8]
    if not cuts:
        return None
    kind = "inclusive" if gate.hi_inclusive else "half-open"
    return Finding(
        STATUS_BRINK,
        gate,
        cuts=cuts,
        note=f"{kind} range; constructed value sits on an endpoint",
    )


def _classify_num_eq(
    gate: Gate, cut: int | float, pool: list[Producer], *, inverted: bool
) -> Finding | None:
    hits: list[Evidence] = []
    offbys: list[Evidence] = []
    for p in pool:
        val = p.value
        assert isinstance(val, (int, float))
        if val == cut:
            hits.append(Evidence(value=val, loc=p.loc, reason="exact", field=p.field))
        elif (
            isinstance(val, int)
            and isinstance(cut, int)
            and abs(val - cut) == 1
            and not _trivial_offby(cut, val)
            and _field_compatible(gate, p)
        ):
            offbys.append(
                Evidence(value=val, loc=p.loc, reason="off-by-one", dist=1, field=p.field)
            )
    hits = _dedupe_ev(hits)[:6]
    offbys = _dedupe_ev(offbys)[:6]

    if inverted:
        # `n != -1` / `n != 0` — the excluded sentinel is constructed.
        if hits and is_sentinel_num(cut):
            return Finding(
                STATUS_SENTINEL,
                gate,
                cuts=hits,
                note="excluded sentinel sits on the cut",
            )
        if offbys and is_sentinel_num(cut):
            return Finding(
                STATUS_SENTINEL,
                gate,
                cuts=offbys,
                note="value sits one step from the excluded sentinel",
            )
        return None

    if offbys:
        return Finding(
            STATUS_OFFBY,
            gate,
            cuts=offbys,
            note="same-field neighbor is off by one from the cut",
        )
    # `n == -1` with a constructed -1 is just a hit — not a cusp.
    return None


def _field_compatible(gate: Gate, p: Producer) -> bool:
    if p.loc.path == "<probe>":
        return True
    if gate.field and p.field:
        return gate.field == p.field
    if p.field and gate.field and p.field != gate.field:
        return False
    return p.loc.path == gate.loc.path


def _sentinel_note(op: str, cut: int | float, excl: bool) -> str:
    side = "excluded" if excl or op in {">", "<", "!=", "!=="} else "included"
    return f"{side} numeric sentinel {cut} sits on the cut"


def _classify_enum(gate: Gate, index: Index) -> Finding | None:
    wanted = [v for v in gate.rhs if isinstance(v, str)]
    if not wanted:
        return None
    wanted_set = set(wanted)
    wanted_leaf = {_leaf(v) for v in wanted}
    pool = _scoped_enums(gate, index)
    decls: list[EnumDecl] = []
    seen_d: set[int] = set()
    for w in wanted:
        for d in _decls_for(w, gate, index):
            if id(d) not in seen_d:
                decls.append(d)
                seen_d.add(id(d))

    hits: list[Evidence] = []
    neighbors: list[Evidence] = []
    sentinels: list[Evidence] = []
    seen_val: set[tuple] = set()

    for p in pool:
        val = p.value
        assert isinstance(val, str)
        leaf = _leaf(val)
        key = (leaf, p.loc.path, p.loc.line)
        if key in seen_val:
            continue
        if leaf in wanted_leaf or val in wanted_set:
            seen_val.add(key)
            hits.append(Evidence(value=val, loc=p.loc, reason="exact", field=p.field))
            continue
        adj = _adjacent(leaf, wanted_leaf, decls)
        if adj:
            seen_val.add(key)
            neighbors.append(
                Evidence(value=val, loc=p.loc, reason="neighbor", field=p.field)
            )
            continue
        if is_sentinel_str(val) and (
            any(is_sentinel_str(w) for w in wanted) or _same_decl_sentinel(leaf, wanted_leaf, decls)
        ):
            seen_val.add(key)
            sentinels.append(
                Evidence(value=val, loc=p.loc, reason="sentinel", field=p.field)
            )

    hits = _dedupe_ev(hits)[:6]
    neighbors = _dedupe_ev(neighbors)[:6]
    sentinels = _dedupe_ev(sentinels)[:6]

    inverted = gate.op in {"!=", "!=="}
    wanted_is_sentinel = any(is_sentinel_str(w) for w in wanted) or _first_or_last(
        wanted_leaf, decls
    )

    if inverted and hits and wanted_is_sentinel:
        return Finding(
            STATUS_SENTINEL,
            gate,
            cuts=hits,
            note="excluded sentinel sits on the cut",
        )

    if neighbors:
        # Constructed sibling sits just outside / next to the compared-to set.
        # Prefer this over "the sentinel is also nearby".
        if not hits:
            return Finding(
                STATUS_NEIGHBOR,
                gate,
                cuts=neighbors,
                note="adjacent enum variant is constructed; the compared-to value is not",
            )
        # Both the cut and its neighbor exist — still a fence if the gate is membership
        # that omits the neighbor, or an equality next to a live sibling.
        if gate.op == "in" or (not inverted and wanted_is_sentinel):
            return Finding(
                STATUS_NEIGHBOR,
                gate,
                cuts=neighbors,
                note="constructed variant sits next to the accepted set",
            )

    if wanted_is_sentinel and (hits or sentinels) and not inverted:
        # Equality to a sentinel when the rest of the domain is also constructed:
        # the sentinel is the "other" bucket sitting on the domain edge.
        domain = _domain_elsewhere(wanted_leaf, pool, decls)
        if domain and hits:
            return Finding(
                STATUS_SENTINEL,
                gate,
                cuts=hits,
                note="sentinel is constructed; siblings exist — domain edge is live",
            )
        if sentinels and not hits:
            return Finding(
                STATUS_SENTINEL,
                gate,
                cuts=sentinels,
                note="neighboring sentinel is constructed against this sentinel cut",
            )

    if inverted and hits:
        # != "done" with done constructed is a live exclusion, not a cusp unless sentinel
        return None

    return None


def _leaf(value: str) -> str:
    return value.split(".")[-1].split("/")[-1]


def _first_or_last(wanted_leaf: set[str], decls: list[EnumDecl]) -> bool:
    """First/last member is a domain edge only when that label is a sentinel."""
    want_low = {w.lower() for w in wanted_leaf}
    for decl in decls:
        if len(decl.members) < 2:
            continue
        for edge in (decl.members[0], decl.members[-1]):
            if _leaf(edge).lower() in want_low and is_sentinel_str(edge):
                return True
    return False


def _adjacent(leaf: str, wanted_leaf: set[str], decls: list[EnumDecl]) -> bool:
    for decl in decls:
        members = [_leaf(m) for m in decl.members]
        low = [m.lower() for m in members]
        try:
            i = low.index(leaf.lower())
        except ValueError:
            continue
        want_low = {w.lower() for w in wanted_leaf}
        if i > 0 and members[i - 1].lower() in want_low:
            return True
        if i + 1 < len(members) and members[i + 1].lower() in want_low:
            return True
        # membership set: value sits immediately outside a contiguous wanted run
        in_set = [m.lower() in want_low for m in members]
        if i > 0 and in_set[i - 1] and not in_set[i]:
            return True
        if i + 1 < len(members) and in_set[i + 1] and not in_set[i]:
            return True
    return False


def _same_decl_sentinel(leaf: str, wanted_leaf: set[str], decls: list[EnumDecl]) -> bool:
    for decl in decls:
        members = {_leaf(m).lower() for m in decl.members}
        if leaf.lower() in members and any(w.lower() in members for w in wanted_leaf):
            if is_sentinel_str(leaf):
                return True
    return False


def _domain_elsewhere(
    wanted_leaf: set[str], pool: list[Producer], decls: list[EnumDecl]
) -> bool:
    want_low = {w.lower() for w in wanted_leaf}
    for p in pool:
        if not isinstance(p.value, str):
            continue
        leaf = _leaf(p.value)
        if leaf.lower() in want_low:
            continue
        if decls:
            if any(_member_match(p.value, d.members) for d in decls):
                return True
        elif p.field:
            return True
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
    index = build_index(corpus)
    findings: list[Finding] = []
    for g in corpus.gates:
        f = classify_gate(g, index)
        if f is not None:
            findings.append(f)
    findings.sort(key=lambda f: (_rank(f.status), f.gate.loc.path, f.gate.loc.line))
    return findings


def _rank(status: str) -> int:
    order = {
        STATUS_OFFBY: 0,
        STATUS_BRINK: 1,
        STATUS_SENTINEL: 2,
        STATUS_NEIGHBOR: 3,
        STATUS_HIT: 4,
        STATUS_MISS: 5,
    }
    return order.get(status, 9)


def probe_value(value: str, corpus: Corpus) -> list[Finding]:
    """Which cuts does this value sit on? Corpus decls stay; producers do not leak."""
    num: int | float | None
    try:
        if re.fullmatch(r"-?\d+", value):
            num = int(value)
        elif re.fullmatch(r"-?\d+\.\d+", value):
            num = float(value)
        else:
            num = None
    except ValueError:
        num = None

    index = build_index(corpus)
    probe_loc = Loc("<probe>", 0, 0)
    out: list[Finding] = []
    for gate in corpus.gates:
        if gate.kind == "number" or gate.op == "range":
            if num is None:
                continue
            fake = Producer(value=num, kind="number", loc=probe_loc, field=gate.field)
            finding = _classify_number(gate, _probe_index(index, gate, fake))
            if finding:
                out.append(finding)
        else:
            fake = Producer(value=value, kind="enum", loc=probe_loc, field=gate.field)
            finding = _classify_enum(gate, _probe_index(index, gate, fake))
            if finding:
                out.append(finding)
    out.sort(key=lambda f: (_rank(f.status), f.gate.loc.path, f.gate.loc.line))
    return out


def _probe_index(index: Index, gate: Gate, fake: Producer) -> Index:
    field_map = {gate.field: [fake]} if gate.field else {}
    fam_map: dict[str, list[Producer]] = {}
    if isinstance(fake.value, str):
        fam = family_of(fake.value)
        if fam:
            fam_map[fam] = [fake]
    return Index(
        numbers=[fake] if fake.kind == "number" else [],
        enums=[fake] if fake.kind != "number" else [],
        by_field=field_map,
        by_family=fam_map,
        decls=index.decls,
        members_of=index.members_of,
        member_index=index.member_index,
    )
