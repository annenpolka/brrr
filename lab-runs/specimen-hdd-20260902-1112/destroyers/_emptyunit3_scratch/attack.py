#!/usr/bin/env python3
"""Host attacks on emptyunit mutate-3. Does not import emptyunit for replica."""
from __future__ import annotations

import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-emptyunit/emptyunit"
FIX = RUN / "lineages/candidate-emptyunit/fixtures"
OUT = RUN / "destroyers/_emptyunit3_scratch"


def run(arg: str | None = "-", text: str | None = None) -> subprocess.CompletedProcess[str]:
    argv = [sys.executable, str(CLI)]
    if arg is not None:
        argv.append(arg)
    return subprocess.run(argv, input=text, capture_output=True, text=True, check=False)


def rows(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        out[name] = rest
    return out


def field(proc: subprocess.CompletedProcess[str], name: str) -> list[str]:
    return rows(proc.stdout).get(name, [])


def show(label: str, proc: subprocess.CompletedProcess[str], keys: list[str]) -> None:
    print(f"\n## {label}")
    print(f"rc={proc.returncode}")
    if proc.stderr.strip():
        print("stderr:", proc.stderr.strip()[:400])
    r = rows(proc.stdout)
    for k in keys:
        print(f"  {k}\t{r.get(k, ['<missing>'])}")


# --- independent replica of flatten + dist regroup + burst (does not import emptyunit) ---
EMPTY = "-"
WATERMARK = 2


def split_scope(nodeid: str, dist: str) -> str:
    if dist == "loadgroup":
        if nodeid.rfind("@") > nodeid.rfind("]"):
            return nodeid.split("@")[-1]
        return nodeid
    if dist == "loadscope":
        return nodeid.rsplit("::", 1)[0]
    raise ValueError(dist)


def flatten(payload: dict) -> OrderedDict[str, bool]:
    flags: OrderedDict[str, bool] = OrderedDict()
    values = list(payload.values())
    nested = all(isinstance(v, dict) for v in values)
    if nested:
        for unit in payload.values():
            for n, done in unit.items():
                flags[n] = bool(done)
        return flags
    for n, done in payload.items():
        flags[n] = bool(done)
    return flags


def replica_inspect(collection: list[str], payload: dict, dist: str) -> dict:
    flags = flatten(payload)
    units: OrderedDict[str, OrderedDict[str, bool]] = OrderedDict()
    for n, done in flags.items():
        units.setdefault(split_scope(n, dist), OrderedDict())[n] = done
    index_of = {n: i for i, n in enumerate(collection)}
    scopes = []
    pending = 0
    missing_index = []
    for scope, items in units.items():
        incomplete = [n for n, d in items.items() if not d]
        indexes = []
        for n, d in items.items():
            if d:
                continue
            pending += 1
            if n not in index_of:
                missing_index.append(n)
                continue
            indexes.append(index_of[n])
        completed_only = bool(items) and not incomplete
        empty_send = len(indexes) == 0
        scopes.append(
            {
                "scope": scope,
                "send": indexes,
                "completed_only": completed_only,
                "empty_send": empty_send,
                "incomplete": incomplete,
            }
        )
    if missing_index:
        return {"error": "index-error"}
    if pending == 0:
        assigned: list[dict] = []
        hang = False
        reschedule = False
        first = None
    else:
        assigned = [scopes[0]]
        reschedule = False
        if assigned[0]["empty_send"]:
            pass
        elif len(assigned[0]["incomplete"]) <= WATERMARK and len(scopes) > 1:
            assigned.append(scopes[1])
            reschedule = True
        hang = any(u["empty_send"] for u in assigned)
        first = assigned[0]
    return {
        "hang_risk": hang,
        "rc": 1 if hang else 0,
        "first_assigned": first["scope"] if first else EMPTY,
        "would_send": first["send"] if first else None,
        "assigned": [u["scope"] for u in assigned],
        "reschedule": reschedule,
        "hang_unit": next((u["scope"] for u in assigned if u["empty_send"]), EMPTY),
        "scopes_n": len(scopes),
        "empty_send_eq_completed_only": all(
            s["empty_send"] == s["completed_only"] for s in scopes
        ),
        "pending": pending,
    }


def first_dict_sticker(payload: dict, collection: list[str]) -> bool:
    """DESTROYER_2 §1 one-liner: pending and first dict empty of False. No dist, no second."""
    pending = 0
    first = None
    values = list(payload.values())
    nested = all(isinstance(v, dict) for v in values)
    units = list(payload.values()) if nested else [payload]
    for unit in units:
        if first is None:
            first = unit
        for n, done in unit.items():
            if not done:
                pending += 1
    assert first is not None
    idxs = [collection.index(n) for n, done in first.items() if not done]
    return bool(pending and not idxs)


KEYS = [
    "hang_risk",
    "first_assigned",
    "would_send",
    "assigned",
    "reschedule",
    "hang_unit",
    "empty_send",
    "completed_only_unit",
    "scopes_n",
    "pending",
    "dist",
]


def main() -> None:
    print("=== A. mutate-3 claims (host CLI) ===")
    owned = run(str(FIX / "063-hang.dump"))
    show("owned 063-hang.dump", owned, KEYS)
    live = run(str(FIX / "unseen-live-first.rec"))
    show("live-first (assign-loop)", live, KEYS)
    p3 = run(str(FIX / "unseen-pending3.rec"))
    show("pending3 then completed-only", p3, KEYS)
    p2 = run(str(FIX / "unseen-pending2.rec"))
    show("pending2 then completed-only", p2, KEYS)
    two = run(str(FIX / "unseen-two-scopes.rec"))
    show("done-first two scopes", two, KEYS)
    wq = run(str(FIX / "063-hang.wq"))
    show("print(workqueue) OrderedDict 063-hang.wq", wq, KEYS)
    rec = run(str(FIX / "063-hang.rec"))
    show("handwritten both-done rec", rec, KEYS)
    hanglog = run(str(FIX / "hang_log.txt"))
    show("hang log", hanglog, KEYS)

    dump = {
        "collection": ["mod.py::a", "mod.py::b"],
        "workqueue": {
            "mod.py::a": {"mod.py::a": True},
            "mod.py::b": {"mod.py::b": False},
        },
    }
    g = run("-", json.dumps({**dump, "dist": "loadgroup"}))
    s = run("-", json.dumps({**dump, "dist": "loadscope"}))
    show("same tests loadgroup no caller regroup", g, KEYS)
    show("same tests loadscope no caller regroup", s, KEYS)

    rec063 = json.loads((FIX / "063-hang.json").read_text())
    rec063["dist"] = "loadscope"
    forced = run("-", json.dumps(rec063))
    show("063 dump forced loadscope", forced, KEYS)

    nodeids = [f"m.py::t{i}" for i in range(257)]
    big = {
        "collection": nodeids,
        "dist": "loadgroup",
        "workqueue": {n: {n: (i == 0)} for i, n in enumerate(nodeids)},
    }
    bigp = run("-", json.dumps(big))
    show("257 loadgroup first-done", bigp, ["hang_risk", "scopes_n", "first_assigned", "would_send", "pending"])

    print("\n=== B. first-dict sticker vs CLI hang_risk ===")
    cases = []

    def add_case(name: str, collection: list[str], payload: dict, dist: str, proc: subprocess.CompletedProcess[str]) -> None:
        sticker = first_dict_sticker(payload, collection)
        cli_hang = field(proc, "hang_risk") == ["yes"]
        cases.append((name, sticker, cli_hang, proc.returncode))
        print(f"  {name}: first_dict_sticker={sticker} cli_hang={cli_hang} rc={proc.returncode} MATCH={sticker==cli_hang}")

    add_case("owned-063", rec063["collection"] if False else json.loads((FIX / "063-hang.json").read_text())["collection"], json.loads((FIX / "063-hang.json").read_text())["workqueue"], "loadgroup", owned)
    live_payload = {"live.py::u": {"live.py::u": False}, "done.py::t": {"done.py::t": True}}
    add_case("live-first", ["done.py::t", "live.py::u"], live_payload, "loadgroup", live)
    add_case("loadgroup-same", dump["collection"], dump["workqueue"], "loadgroup", g)
    add_case("loadscope-same", dump["collection"], dump["workqueue"], "loadscope", s)
    done_first_payload = {"done.py::t": {"done.py::t": True}, "live.py::u": {"live.py::u": False}}
    add_case("done-first", ["done.py::t", "live.py::u"], done_first_payload, "loadgroup", two)

    print("\n=== C. replica vs CLI on mutate claims ===")
    replica_cases = [
        ("owned", ["testing/test_timeout.py::test_1", "testing/test_timeout.py::test_2"], json.loads((FIX / "063-hang.json").read_text())["workqueue"], "loadgroup", owned),
        ("live-first", ["live.py::u", "done.py::t"], live_payload, "loadgroup", live),
        ("loadgroup-same", dump["collection"], dump["workqueue"], "loadgroup", g),
        ("loadscope-same", dump["collection"], dump["workqueue"], "loadscope", s),
        ("forced-loadscope-063", json.loads((FIX / "063-hang.json").read_text())["collection"], json.loads((FIX / "063-hang.json").read_text())["workqueue"], "loadscope", forced),
        ("257", nodeids, big["workqueue"], "loadgroup", bigp),
    ]
    for name, coll, payload, dist, proc in replica_cases:
        r = replica_inspect(coll, payload, dist)
        cli_hang = field(proc, "hang_risk") == ["yes"]
        cli_assigned = field(proc, "assigned")
        cli_first = field(proc, "first_assigned")
        print(
            f"  {name}: replica_hang={r['hang_risk']} cli={cli_hang} "
            f"assigned {r['assigned']} vs {cli_assigned} "
            f"first {r['first_assigned']} vs {cli_first} "
            f"empty==completed {r['empty_send_eq_completed_only']} "
            f"MATCH={r['hang_risk']==cli_hang and r['assigned']==cli_assigned}"
        )

    print("\n=== D. two live then completed-only (while vs one extra) ===")
    text = (
        "collection\tlive1.py::u\tlive2.py::u\tdone.py::t\n"
        "dist\tloadgroup\n"
        "unit\tlive1.py::u\tlive1.py::u\topen\n"
        "unit\tlive2.py::u\tlive2.py::u\topen\n"
        "unit\tdone.py::t\tdone.py::t\tdone\n"
    )
    proc = run("-", text)
    show("two-live-then-done (xdist _reschedule is one extra, not while)", proc, KEYS)

    print("\n=== E. would_send names first even when hang is second ===")
    show("live-first would_send vs hang_unit", live, ["would_send", "hang_unit", "assigned", "hang_risk"])

    print("\n=== F. collection order vs unit/dump FIFO ===")
    text = (
        "collection\tdone.py::t\tlive.py::u\n"
        "dist\tloadgroup\n"
        "unit\tlive.py::u\tlive.py::u\topen\n"
        "unit\tdone.py::t\tdone.py::t\tdone\n"
    )
    proc = run("-", text)
    show("collection done-first, units live-first (FIFO follows units)", proc, KEYS)
    # xdist workqueue is collection-order grouped. collection first-seen scope is done.py::t.

    print("\n=== G. caller module key ignored (dist regroup) ===")
    dump2 = {
        "collection": ["mod.py::a", "mod.py::b"],
        "dist": "loadgroup",
        "workqueue": {"mod.py": {"mod.py::a": True, "mod.py::b": False}},
    }
    proc = run("-", json.dumps(dump2))
    show("caller module key + loadgroup", proc, KEYS)

    print("\n=== H. empty_send vs completed_only on fixtures ===")
    for f in sorted(FIX.glob("*.rec")) + sorted(FIX.glob("*.json")) + sorted(FIX.glob("*.dump")) + sorted(FIX.glob("*.wq")):
        proc = run(str(f))
        if proc.returncode != 0 and not proc.stdout:
            print(f"  {f.name}: no table rc={proc.returncode} stderr={proc.stderr.strip()[:80]}")
            continue
        r = rows(proc.stdout)
        # last empty_send / completed_only_unit may overwrite; collect all pairs from raw
        pairs = []
        es = None
        for line in proc.stdout.splitlines():
            if line.startswith("empty_send\t"):
                es = line.split("\t", 1)[1]
            elif line.startswith("completed_only_unit\t") and es is not None:
                pairs.append((es, line.split("\t", 1)[1]))
                es = None
        same = all(a == b for a, b in pairs)
        print(f"  {f.name}: rc={proc.returncode} hang={r.get('hang_risk')} pairs={pairs} empty==completed={same}")

    print("\n=== I. ingest holes ===")
    proc = run("-", "OrderedDict()")
    show("empty OrderedDict()", proc, KEYS)
    proc = run("-", "{'a.py::t': False}")
    show("flat dict nodeid->bool", proc, KEYS)
    proc = run("-", json.dumps({"collection": ["a.py::t"], "workqueue": {}, "assigned": {"a.py::t": {"a.py::t": True}}}))
    show("empty workqueue uses assigned", proc, KEYS)
    proc = run("-", json.dumps({"collection": ["a.py::t", "b.py::t"], "workqueue": {"a.py::t": {"a.py::t": True}}, "assigned": {"b.py::t": {"b.py::t": False}}}))
    show("nonempty workqueue shadows assigned", proc, KEYS)
    proc = run("-", json.dumps({"collection": [None], "workqueue": {"x.py::t": {"x.py::t": False}}}))
    show("null collection item", proc, KEYS)
    proc = run("-", json.dumps({"collection": ["-", "x"], "workqueue": {"-": {"-": True}, "x": {"x": False}}}))
    show("dash nodeid", proc, KEYS)
    proc = run("-", json.dumps({"collection": ["none"], "workqueue": {"none": {"none": False}}}))
    show("none nodeid", proc, KEYS)
    proc = run("-", json.dumps({"dist": "none", "workqueue": {"a.py::t": {"a.py::t": False}}}))
    show("dist none", proc, KEYS)
    proc = run("-", json.dumps({"dist": "loadfile", "workqueue": {"a.py::t": {"a.py::t": False}}}))
    show("dist loadfile", proc, KEYS)
    proc = run("-", json.dumps({"dist": "each", "workqueue": {"a.py::t": {"a.py::t": False}}}))
    show("dist each", proc, KEYS)
    proc = run("-", '{"a":1}\n{"b":2}\n')
    show("JSONL two objects", proc, KEYS)
    proc = run("-", '{"collection":["a.py::t"],"workqueue":{"a.py::t":{"a.py::t":false}},}')
    show("trailing comma", proc, KEYS)
    proc = run("-", "/*c*/\n{'a.py::t': {'a.py::t': False}}")
    show("c comment", proc, KEYS)
    proc = run("-", "\ufeff" + json.dumps({"workqueue": {"a.py::t": {"a.py::t": False}}}))
    show("UTF-8 BOM JSON", proc, KEYS)
    proc = run("/dev/null")
    show("/dev/null", proc, KEYS)
    proc = run("-", "")
    show("empty stdin", proc, KEYS)
    proc = run("-", "collection\ta.py::t\tb.py::t\nunit\ta.py::t\ta.py::t\topen\n")
    show("TSV tab in... wait two nodeids", proc, KEYS)
    proc = run("-", "collection\tmod.py::a\tmod.py::b\n")
    show("collection only no units", proc, KEYS)

    print("\n=== J. caps ===")
    n8192 = [f"m.py::t{i}" for i in range(8192)]
    cap_ok = {"collection": n8192, "dist": "loadgroup", "workqueue": {n: {n: False} for n in n8192[:2]}}
    # 8192 collection with 2 units — collection cap is on collection list length
    proc = run("-", json.dumps({"collection": n8192, "dist": "loadgroup", "workqueue": {n8192[0]: {n8192[0]: True}, n8192[1]: {n8192[1]: False}}}))
    print("  8192 collection rc", proc.returncode, "stderr", proc.stderr.strip()[:120], "hang", field(proc, "hang_risk"))
    n8193 = [f"m.py::t{i}" for i in range(8193)]
    proc = run("-", json.dumps({"collection": n8193, "dist": "loadgroup", "workqueue": {n8193[0]: {n8193[0]: False}}}))
    print("  8193 collection rc", proc.returncode, "stderr", proc.stderr.strip()[:160])

    print("\n=== K. loadscope :: in params (xdist #1335) ===")
    dump = {
        "collection": ["m.py::test[a::b]", "m.py::test2"],
        "dist": "loadscope",
        "workqueue": {
            "m.py::test[a::b]": {"m.py::test[a::b]": True},
            "m.py::test2": {"m.py::test2": False},
        },
    }
    proc = run("-", json.dumps(dump))
    show("loadscope param contains ::", proc, KEYS)

    print("\n=== L. @ inside parametrize brackets ===")
    dump = {
        "collection": ["m.py::test[a@b]", "m.py::test2"],
        "dist": "loadgroup",
        "workqueue": {
            "m.py::test[a@b]": {"m.py::test[a@b]": True},
            "m.py::test2": {"m.py::test2": False},
        },
    }
    proc = run("-", json.dumps(dump))
    show("loadgroup @ inside []", proc, KEYS)

    print("\n=== M. @ group after ] ===")
    dump = {
        "collection": ["mod.py::a[1]@g1", "mod.py::b[2]@g2"],
        "dist": "loadgroup",
        "workqueue": {
            "mod.py::a[1]@g1": {"mod.py::a[1]@g1": True},
            "mod.py::b[2]@g2": {"mod.py::b[2]@g2": False},
        },
    }
    proc = run("-", json.dumps(dump))
    show("two @ groups done-first", proc, KEYS)

    print("\n=== N. completed nodeid missing from collection ===")
    text = (
        "collection\tlive.py::u\n"
        "dist\tloadgroup\n"
        "unit\tdone.py::t\tdone.py::t\tdone\n"
        "unit\tlive.py::u\tlive.py::u\topen\n"
    )
    proc = run("-", text)
    show("completed missing from collection (not index-error?)", proc, KEYS)

    print("\n=== O. extra collection nodeids not in workqueue ===")
    dump = {
        "collection": ["a.py::t", "ghost.py::t"],
        "workqueue": {"a.py::t": {"a.py::t": False}},
    }
    proc = run("-", json.dumps(dump))
    show("ghost in collection", proc, KEYS)

    print("\n=== P. replacement-one-assign vs burst: live-first JSON ===")
    # xdist later schedule() only _reschedule once on empty assigned -> first unit only.
    print("  CLI hang_risk on live-first:", field(live, "hang_risk"), "assigned", field(live, "assigned"))
    print("  If replacement is one assign: would be hang_risk no, assigned live only.")

    print("\n=== Q. first pending=2 live, second live, third done ===")
    text = (
        "collection\ta.py::t1\ta.py::t2\tb.py::u\tc.py::t\n"
        "dist\tloadscope\n"
        "unit\ta.py\ta.py::t1\topen\n"
        "unit\ta.py\ta.py::t2\topen\n"
        "unit\tb.py\tb.py::u\topen\n"
        "unit\tc.py\tc.py::t\tdone\n"
    )
    proc = run("-", text)
    show("pending2 live then live then done", proc, KEYS)

    print("\n=== R. Python assignment envelope ===")
    text = (
        "collection = ['testing/test_timeout.py::test_1', 'testing/test_timeout.py::test_2']\n"
        "dist = 'loadgroup'\n"
        "workqueue = OrderedDict([('testing/test_timeout.py::test_1', OrderedDict([('testing/test_timeout.py::test_1', True)])), ('testing/test_timeout.py::test_2', OrderedDict([('testing/test_timeout.py::test_2', False)]))])\n"
    )
    proc = run("-", text)
    show("python assignment envelope", proc, KEYS)

    print("\n=== S. collection list + OrderedDict two docs ===")
    wq = OrderedDict(
        [
            ("testing/test_timeout.py::test_1", OrderedDict([("testing/test_timeout.py::test_1", True)])),
            ("testing/test_timeout.py::test_2", OrderedDict([("testing/test_timeout.py::test_2", False)])),
        ]
    )
    text = "['testing/test_timeout.py::test_1', 'testing/test_timeout.py::test_2']\n" + repr(wq)
    proc = run("-", text)
    show("list then OrderedDict two docs", proc, KEYS)

    print("\n=== T. duplicate JSON key collection last-wins ===")
    proc = run("-", '{"collection":["a.py::t"],"collection":["b.py::t"],"workqueue":{"b.py::t":{"b.py::t":false}}}')
    show("dup collection key", proc, KEYS)

    print("\n=== U. nodeid containing TAB in JSON ===")
    proc = run("-", json.dumps({"collection": ["a.py::t\tx"], "workqueue": {"a.py::t\tx": {"a.py::t\tx": False}}}))
    show("tab in nodeid JSON", proc, KEYS)

    print("\n=== V. TSV collection tab-split ===")
    proc = run("-", "collection\ta.py::t\tx\nunit\ta.py::t\tx\ta.py::t\tx\topen\n")
    show("TSV extra tabs", proc, KEYS)

    print("\n=== W. loadscope class rsplit vs function ===")
    dump = {
        "collection": ["m.py::T::a", "m.py::func"],
        "dist": "loadscope",
        "workqueue": {
            "m.py::T::a": {"m.py::T::a": True},
            "m.py::func": {"m.py::func": False},
        },
    }
    proc = run("-", json.dumps(dump))
    show("class done + module func open (two loadscope units)", proc, KEYS)

    print("\n=== X. bool/int completed flags in JSON ===")
    proc = run("-", json.dumps({"workqueue": {"a.py::t": {"a.py::t": 1}}}))
    show("completed flag 1", proc, KEYS)
    proc = run("-", json.dumps({"workqueue": {"a.py::t": {"a.py::t": 2}}}))
    show("completed flag 2", proc, KEYS)
    proc = run("-", json.dumps({"workqueue": {"a.py::t": {"a.py::t": "yes"}}}))
    show("completed flag yes string", proc, KEYS)

    print("\n=== Y. first-dict replica on live-first JSON envelope keys ===")
    # If someone still uses caller keys as units without flatten, live is first -> not hang
    print("  flatten-then-burst is required for live-first hang")

    print("\n=== Z. summary first-dict MATCH rate ===")
    match = sum(1 for n, s, c, rc in cases if s == c)
    print(f"  first_dict_sticker MATCH {match}/{len(cases)}")
    for n, s, c, rc in cases:
        print(f"    {n}: sticker={s} cli={c}")


if __name__ == "__main__":
    main()
