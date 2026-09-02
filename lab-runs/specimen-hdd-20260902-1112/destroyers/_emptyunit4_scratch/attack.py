#!/usr/bin/env python3
"""emptyunit FOURTH pass. Does not import emptyunit. No pytest-xdist."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-emptyunit/emptyunit"
FIX = RUN / "lineages/candidate-emptyunit/fixtures"
OUT = RUN / "destroyers/_emptyunit4_scratch"
WATERMARK = 2
EMPTY = "-"


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


def yn(flag: bool) -> str:
    return "yes" if flag else "no"


def send_tuple(indexes: list[int] | None) -> str:
    if indexes is None:
        return EMPTY
    if not indexes:
        return "()"
    return "(" + ",".join(str(i) for i in indexes) + ")"


def show(label: str, proc: subprocess.CompletedProcess[str], keys: list[str]) -> None:
    print(f"\n## {label}")
    print(f"rc={proc.returncode}")
    if proc.stderr.strip():
        print("stderr:", proc.stderr.strip()[:400])
    r = rows(proc.stdout)
    for k in keys:
        print(f"  {k}\t{r.get(k, ['<missing>'])}")


def flatten(payload: dict) -> OrderedDict[str, bool]:
    flags: OrderedDict[str, bool] = OrderedDict()
    values = list(payload.values())
    nested = all(isinstance(v, dict) for v in values)
    if nested:
        for unit in payload.values():
            for n, done in unit.items():
                flags[str(n)] = bool(done)
        return flags
    for n, done in payload.items():
        flags[str(n)] = bool(done)
    return flags


def split_scope(nodeid: str, dist: str) -> str:
    if dist == "loadgroup":
        if nodeid.rfind("@") > nodeid.rfind("]"):
            return nodeid.split("@")[-1]
        return nodeid
    if dist == "loadscope":
        return nodeid.rsplit("::", 1)[0]
    raise ValueError(dist)


def first_dict_sticker(payload: dict, collection: list[str]) -> bool:
    """DESTROYER_2 §1: pending and first caller dict empty of False. No dist, no second."""
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
    if first is None:
        return False
    idxs = [collection.index(n) for n, done in first.items() if not done]
    return bool(pending and not idxs)


def two_greps(payload: dict) -> bool:
    """Two-membership leftover: some incomplete exists, and the first bag is all True."""
    values = list(payload.values())
    nested = all(isinstance(v, dict) for v in values)
    bags = list(payload.values()) if nested else [payload]
    if not bags:
        return False
    any_open = any(not flag for inner in bags for flag in inner.values())
    first_all_true = bool(bags[0]) and all(bags[0].values())
    return bool(any_open and first_all_true)


def leftover_inspect(collection: list[str], payload: dict, dist: str) -> dict:
    """Leftover empty-unit identity: hang if assigned send is ().

    Flatten inner nodeids, dist regroup, FIFO first, plus one more if that
    unit's pending is 1 or 2. Does not import emptyunit.
    """
    flags = flatten(payload)
    units: OrderedDict[str, OrderedDict[str, bool]] = OrderedDict()
    for n, done in flags.items():
        units.setdefault(split_scope(n, dist), OrderedDict())[n] = done
    index_of = {n: i for i, n in enumerate(collection)}
    scopes = []
    pending = 0
    missing_index: list[str] = []
    for scope, items in units.items():
        incomplete = [n for n, d in items.items() if not d]
        indexes: list[int] = []
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
        return {"error": "index-error", "missing": missing_index}
    any_empty = any(s["empty_send"] for s in scopes)
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
    assigned_empty = any(u["empty_send"] for u in assigned) if assigned else False
    return {
        "hang_risk": hang,
        "rc": 1 if hang else 0,
        "first_assigned": first["scope"] if first else EMPTY,
        "would_send": first["send"] if first else None,
        "assigned": [u["scope"] for u in assigned],
        "reschedule": reschedule,
        "hang_unit": next((u["scope"] for u in assigned if u["empty_send"]), EMPTY),
        "scopes_n": len(scopes),
        "pending": pending,
        "any_empty_send": any_empty,
        "assigned_empty_send": assigned_empty,
        "empty_send_eq_completed_only": all(
            s["empty_send"] == s["completed_only"] for s in scopes
        ),
        "hang_is_assigned_empty": hang == assigned_empty if pending > 0 else (not hang),
    }


def any_empty_send_hang(collection: list[str], payload: dict, dist: str) -> bool:
    """Honor-KILL 3: hang_risk is any empty send list, no leftover identity."""
    flags = flatten(payload)
    units: OrderedDict[str, OrderedDict[str, bool]] = OrderedDict()
    for n, done in flags.items():
        units.setdefault(split_scope(n, dist), OrderedDict())[n] = done
    pending = sum(1 for items in units.values() for d in items.values() if not d)
    if pending == 0:
        return False
    for items in units.values():
        incomplete = [n for n, d in items.items() if not d]
        if not incomplete:
            return True
    return False


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


def harvest(proc: subprocess.CompletedProcess[str]) -> dict:
    r = rows(proc.stdout)
    return {
        "rc": proc.returncode,
        "hang_risk": r.get("hang_risk", []),
        "would_send": r.get("would_send", []),
        "first_assigned": r.get("first_assigned", []),
        "assigned": r.get("assigned", []),
        "reschedule": r.get("reschedule", []),
        "hang_unit": r.get("hang_unit", []),
        "scopes_n": r.get("scopes_n", []),
        "pending": r.get("pending", []),
        "err": proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "",
    }


def leftover_as_harvest(rep: dict) -> dict:
    if rep.get("error"):
        return {
            "rc": 1,
            "hang_risk": [],
            "would_send": [],
            "first_assigned": [],
            "assigned": [],
            "reschedule": [],
            "hang_unit": [],
            "scopes_n": [],
            "pending": [],
            "err": "index-error",
        }
    assigned = rep["assigned"] if rep["assigned"] else ["-"]
    return {
        "rc": rep["rc"],
        "hang_risk": [yn(rep["hang_risk"])],
        "would_send": [send_tuple(rep["would_send"])],
        "first_assigned": [rep["first_assigned"]],
        "assigned": assigned,
        "reschedule": [yn(rep["reschedule"])],
        "hang_unit": [rep["hang_unit"]],
        "scopes_n": [str(rep["scopes_n"])],
        "pending": [str(rep["pending"])],
        "err": "",
    }


def same_harvest(a: dict, b: dict) -> bool:
    keys = [
        "rc",
        "hang_risk",
        "would_send",
        "first_assigned",
        "assigned",
        "reschedule",
        "hang_unit",
        "scopes_n",
        "pending",
    ]
    return all(a.get(k) == b.get(k) for k in keys)


def cli_ast_hang_formula() -> dict:
    src = CLI.read_text(encoding="utf-8")
    tree = ast.parse(src)
    facts: dict[str, object] = {
        "imports": [],
        "empty_send_assign": None,
        "completed_only_assign": None,
        "hang_assign": None,
        "burst_fn": None,
        "pytest_xdist_import": False,
    }
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            facts["imports"].extend(a.name for a in n.names)
            if any("xdist" in a.name or a.name == "pytest" for a in n.names):
                facts["pytest_xdist_import"] = True
        elif isinstance(n, ast.ImportFrom):
            facts["imports"].append(n.module or "")
            if (n.module or "").startswith(("pytest", "xdist")):
                facts["pytest_xdist_import"] = True
        elif isinstance(n, ast.FunctionDef) and n.name == "replacement_burst":
            facts["burst_fn"] = ast.unparse(n)
        elif isinstance(n, ast.Assign):
            if len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                name = n.targets[0].id
                if name == "empty_send" and facts["empty_send_assign"] is None:
                    facts["empty_send_assign"] = ast.unparse(n)
                if name == "completed_only" and facts["completed_only_assign"] is None:
                    facts["completed_only_assign"] = ast.unparse(n)
                if name == "hang" and facts["hang_assign"] is None:
                    facts["hang_assign"] = ast.unparse(n)
    facts["imports"] = sorted(set(facts["imports"]))
    return facts


def main() -> None:
    rec063 = json.loads((FIX / "063-hang.json").read_text())
    owned_payload = rec063["workqueue"]
    owned_coll = rec063["collection"]
    dump_same = {
        "collection": ["mod.py::a", "mod.py::b"],
        "workqueue": {
            "mod.py::a": {"mod.py::a": True},
            "mod.py::b": {"mod.py::b": False},
        },
    }
    live_payload = {
        "live.py::u": {"live.py::u": False},
        "done.py::t": {"done.py::t": True},
    }
    done_first_payload = {
        "done.py::t": {"done.py::t": True},
        "live.py::u": {"live.py::u": False},
    }
    pending3_payload = {
        "a.py::t1": {"a.py::t1": False},
        "a.py::t2": {"a.py::t2": False},
        "a.py::t3": {"a.py::t3": False},
        "b.py::t": {"b.py::t": True},
    }
    pending3_coll = ["a.py::t1", "a.py::t2", "a.py::t3", "b.py::t"]
    two_live_done_payload = {
        "live1.py::u": {"live1.py::u": False},
        "live2.py::u": {"live2.py::u": False},
        "done.py::t": {"done.py::t": True},
    }
    two_live_done_coll = ["live1.py::u", "live2.py::u", "done.py::t"]

    print("=== A. mutate-3 KEEP harvest (host CLI, archive only) ===")
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
    g = run("-", json.dumps({**dump_same, "dist": "loadgroup"}))
    s = run("-", json.dumps({**dump_same, "dist": "loadscope"}))
    show("same tests loadgroup no caller regroup", g, KEYS)
    show("same tests loadscope no caller regroup", s, KEYS)
    rec063_ls = dict(rec063)
    rec063_ls["dist"] = "loadscope"
    forced = run("-", json.dumps(rec063_ls))
    show("063 dump forced loadscope", forced, KEYS)
    alldone = run(str(FIX / "loadscope-alldone.rec"))
    show("loadscope both done", alldone, KEYS)
    two_live = run(
        "-",
        "collection\tlive1.py::u\tlive2.py::u\tdone.py::t\n"
        "dist\tloadgroup\n"
        "unit\tlive1.py::u\tlive1.py::u\topen\n"
        "unit\tlive2.py::u\tlive2.py::u\topen\n"
        "unit\tdone.py::t\tdone.py::t\tdone\n",
    )
    show("two-live-then-done", two_live, KEYS)

    print("\n=== B. Honor-KILL 1+2: first-dict sticker / two greps vs CLI ===")
    sticker_cases = []

    def add_sticker(
        name: str,
        collection: list[str],
        payload: dict,
        dist: str,
        proc: subprocess.CompletedProcess[str],
    ) -> None:
        sticker = first_dict_sticker(payload, collection)
        greps = two_greps(payload)
        cli_hang = field(proc, "hang_risk") == ["yes"]
        leftover = leftover_inspect(collection, payload, dist)
        any_empty = any_empty_send_hang(collection, payload, dist)
        sticker_cases.append(
            {
                "name": name,
                "sticker": sticker,
                "two_greps": greps,
                "any_empty": any_empty,
                "leftover": leftover["hang_risk"] if not leftover.get("error") else "error",
                "cli": cli_hang,
                "rc": proc.returncode,
            }
        )
        print(
            f"  {name:22} sticker={sticker!s:5} two_greps={greps!s:5} "
            f"any_empty={any_empty!s:5} leftover={leftover.get('hang_risk')} "
            f"cli={cli_hang!s:5} rc={proc.returncode} "
            f"stickerMATCH={sticker == cli_hang} grepsMATCH={greps == cli_hang} "
            f"anyMATCH={any_empty == cli_hang} leftoverMATCH={leftover.get('hang_risk') == cli_hang}"
        )

    add_sticker("owned-063", owned_coll, owned_payload, "loadgroup", owned)
    add_sticker("live-first", ["done.py::t", "live.py::u"], live_payload, "loadgroup", live)
    add_sticker("loadgroup-same", dump_same["collection"], dump_same["workqueue"], "loadgroup", g)
    add_sticker("loadscope-same", dump_same["collection"], dump_same["workqueue"], "loadscope", s)
    add_sticker("done-first", ["done.py::t", "live.py::u"], done_first_payload, "loadgroup", two)
    add_sticker("owned-forced-ls", owned_coll, owned_payload, "loadscope", forced)
    add_sticker("pending3", pending3_coll, pending3_payload, "loadscope", p3)
    add_sticker("two-live-done", two_live_done_coll, two_live_done_payload, "loadgroup", two_live)

    sm = sum(1 for c in sticker_cases if c["sticker"] == c["cli"])
    gm = sum(1 for c in sticker_cases if c["two_greps"] == c["cli"])
    am = sum(1 for c in sticker_cases if c["any_empty"] == c["cli"])
    lm = sum(1 for c in sticker_cases if c["leftover"] == c["cli"])
    print(f"  first_dict_sticker MATCH {sm}/{len(sticker_cases)}")
    print(f"  two_greps MATCH {gm}/{len(sticker_cases)}")
    print(f"  any_empty_send MATCH {am}/{len(sticker_cases)}")
    print(f"  leftover assigned-send-() MATCH {lm}/{len(sticker_cases)}")

    print("\n=== C. leftover replica vs CLI harvest fields ===")
    replica_cases = [
        ("owned", owned_coll, owned_payload, "loadgroup", owned),
        ("live-first", ["done.py::t", "live.py::u"], live_payload, "loadgroup", live),
        ("loadgroup-same", dump_same["collection"], dump_same["workqueue"], "loadgroup", g),
        ("loadscope-same", dump_same["collection"], dump_same["workqueue"], "loadscope", s),
        ("forced-loadscope-063", owned_coll, owned_payload, "loadscope", forced),
        ("done-first", ["done.py::t", "live.py::u"], done_first_payload, "loadgroup", two),
        ("pending3", pending3_coll, pending3_payload, "loadscope", p3),
        ("two-live-done", two_live_done_coll, two_live_done_payload, "loadgroup", two_live),
    ]
    nodeids = [f"m.py::t{i}" for i in range(257)]
    big = {
        "collection": nodeids,
        "dist": "loadgroup",
        "workqueue": {n: {n: (i == 0)} for i, n in enumerate(nodeids)},
    }
    bigp = run("-", json.dumps(big))
    replica_cases.append(("257-first-done", nodeids, big["workqueue"], "loadgroup", bigp))
    replica_ok = 0
    for name, coll, payload, dist, proc in replica_cases:
        r = leftover_inspect(coll, payload, dist)
        h = leftover_as_harvest(r)
        c = harvest(proc)
        ok = same_harvest(h, c)
        replica_ok += int(ok)
        print(
            f"  {name:22} leftover_hang={r.get('hang_risk')} cli={field(proc, 'hang_risk')} "
            f"assigned {r.get('assigned')} vs {field(proc, 'assigned')} "
            f"empty==completed {r.get('empty_send_eq_completed_only')} "
            f"hang_is_assigned_empty {r.get('hang_is_assigned_empty')} MATCH={ok}"
        )
    print(f"  leftover replica MATCH {replica_ok}/{len(replica_cases)}")

    print("\n=== D. Honor-KILL 3: any empty send vs leftover assigned-send-() ===")
    print("  pending3: CLI hang", field(p3, "hang_risk"), "empty_send", field(p3, "empty_send"), "hang_unit", field(p3, "hang_unit"))
    print("  two-live-done: CLI hang", field(two_live, "hang_risk"), "assigned", field(two_live, "assigned"), "empty_send last", field(two_live, "empty_send"))
    print("  alldone: CLI hang", field(alldone, "hang_risk"), "pending", field(alldone, "pending"), "empty_send", field(alldone, "empty_send"))
    print("  live-first: CLI hang", field(live, "hang_risk"), "assigned", field(live, "assigned"), "hang_unit", field(live, "hang_unit"), "would_send", field(live, "would_send"))
    print(
        "  Honor-KILL 3 fires only if CLI hang_risk tracks any_empty_send, not assigned-send-()."
    )
    print(f"  any_empty MATCH {am}/{len(sticker_cases)}; leftover MATCH {lm}/{len(sticker_cases)}")

    print("\n=== E. CLI AST hang formula (static, no import) ===")
    facts = cli_ast_hang_formula()
    print("  imports", facts["imports"])
    print("  pytest_xdist_import", facts["pytest_xdist_import"])
    print("  empty_send_assign", facts["empty_send_assign"])
    print("  completed_only_assign", facts["completed_only_assign"])
    print("  hang_assign", facts["hang_assign"])
    burst = str(facts["burst_fn"] or "")
    print("  burst_has_empty_send_shortcircuit", "empty_send" in burst)
    print("  burst_has_watermark", "RESCHEDULE_WATERMARK" in burst)
    print("  burst_len", len(burst.splitlines()))

    print("\n=== F. leftover-identity lie hunt (AST-static ingest vs leftover replica) ===")
    ast_cases = []

    def add_ast(name: str, text: str, collection: list[str], payload: dict, dist: str) -> None:
        proc = run("-", text)
        cli_hang = field(proc, "hang_risk") == ["yes"] if proc.stdout else None
        leftover = leftover_inspect(collection, payload, dist)
        match = (leftover.get("hang_risk") == cli_hang) if cli_hang is not None else leftover.get("error") == "index-error" and "index-error" in proc.stderr
        if leftover.get("error") and "index-error" in proc.stderr:
            match = True
        ast_cases.append((name, leftover.get("hang_risk"), cli_hang, proc.returncode, match, proc.stderr.strip()[:80]))
        print(
            f"  {name:28} leftover={leftover.get('hang_risk')} cli={cli_hang} rc={proc.returncode} MATCH={match} err={proc.stderr.strip()[:60]!r}"
        )

    add_ast(
        "py-Name-True",
        "{'collection': ['a.py::t', 'b.py::t'], 'dist': 'loadgroup', "
        "'workqueue': {'a.py::t': {'a.py::t': True}, 'b.py::t': {'b.py::t': False}}}",
        ["a.py::t", "b.py::t"],
        {"a.py::t": {"a.py::t": True}, "b.py::t": {"b.py::t": False}},
        "loadgroup",
    )
    add_ast(
        "py-Constant-true-json",
        json.dumps(
            {
                "collection": ["a.py::t", "b.py::t"],
                "dist": "loadgroup",
                "workqueue": {"a.py::t": {"a.py::t": True}, "b.py::t": {"b.py::t": False}},
            }
        ),
        ["a.py::t", "b.py::t"],
        {"a.py::t": {"a.py::t": True}, "b.py::t": {"b.py::t": False}},
        "loadgroup",
    )
    add_ast(
        "py-int-1-completed",
        "{'workqueue': {'a.py::t': {'a.py::t': 1}, 'b.py::t': {'b.py::t': 0}}}",
        ["a.py::t", "b.py::t"],
        {"a.py::t": {"a.py::t": True}, "b.py::t": {"b.py::t": False}},
        "loadgroup",
    )
    proc_binop = run("-", "{'workqueue': {'a.py::t': {'a.py::t': 1-1}, 'b.py::t': {'b.py::t': False}}}")
    print(
        f"  {'py-BinOp-1-1':28} leftover=n/a cli_stdout={bool(proc_binop.stdout)} rc={proc_binop.returncode} "
        f"err={proc_binop.stderr.strip()[:80]!r}"
    )
    ast_cases.append(("py-BinOp-1-1", "n/a", None, proc_binop.returncode, proc_binop.returncode == 1 and not proc_binop.stdout, proc_binop.stderr.strip()[:80]))
    add_ast(
        "caller-module-key-lg",
        json.dumps(
            {
                "collection": ["mod.py::a", "mod.py::b"],
                "dist": "loadgroup",
                "workqueue": {"mod.py": {"mod.py::a": True, "mod.py::b": False}},
            }
        ),
        ["mod.py::a", "mod.py::b"],
        {"mod.py": {"mod.py::a": True, "mod.py::b": False}},
        "loadgroup",
    )
    add_ast(
        "xdist-1335-loadscope",
        json.dumps(
            {
                "collection": ["m.py::test[a::b]", "m.py::test2"],
                "dist": "loadscope",
                "workqueue": {
                    "m.py::test[a::b]": {"m.py::test[a::b]": True},
                    "m.py::test2": {"m.py::test2": False},
                },
            }
        ),
        ["m.py::test[a::b]", "m.py::test2"],
        {
            "m.py::test[a::b]": {"m.py::test[a::b]": True},
            "m.py::test2": {"m.py::test2": False},
        },
        "loadscope",
    )
    add_ast(
        "at-inside-brackets",
        json.dumps(
            {
                "collection": ["m.py::test[a@b]", "m.py::test2"],
                "dist": "loadgroup",
                "workqueue": {
                    "m.py::test[a@b]": {"m.py::test[a@b]": True},
                    "m.py::test2": {"m.py::test2": False},
                },
            }
        ),
        ["m.py::test[a@b]", "m.py::test2"],
        {
            "m.py::test[a@b]": {"m.py::test[a@b]": True},
            "m.py::test2": {"m.py::test2": False},
        },
        "loadgroup",
    )
    coll_order = run(
        "-",
        "collection\tdone.py::t\tlive.py::u\n"
        "dist\tloadgroup\n"
        "unit\tlive.py::u\tlive.py::u\topen\n"
        "unit\tdone.py::t\tdone.py::t\tdone\n",
    )
    leftover_dump_fifo = leftover_inspect(
        ["done.py::t", "live.py::u"],
        {"live.py::u": {"live.py::u": False}, "done.py::t": {"done.py::t": True}},
        "loadgroup",
    )
    leftover_coll_fifo = leftover_inspect(
        ["done.py::t", "live.py::u"],
        {"done.py::t": {"done.py::t": True}, "live.py::u": {"live.py::u": False}},
        "loadgroup",
    )
    print(
        f"  {'collection-done units-live':28} CLI first={field(coll_order, 'first_assigned')} "
        f"hang={field(coll_order, 'hang_risk')} dump_fifo={leftover_dump_fifo['first_assigned']}/"
        f"{leftover_dump_fifo['hang_risk']} coll_fifo={leftover_coll_fifo['first_assigned']}/"
        f"{leftover_coll_fifo['hang_risk']}"
    )
    print(
        "  FIFO follows dump/unit insertion, not collection. leftover replica uses dump order. not a lie."
    )

    print("\n=== G. empty_send vs completed_only on fixtures (coincidence, not a cut) ===")
    for f in sorted(FIX.glob("*.rec")) + sorted(FIX.glob("*.json")) + sorted(FIX.glob("*.dump")) + sorted(FIX.glob("*.wq")):
        proc = run(str(f))
        if proc.returncode != 0 and not proc.stdout:
            print(f"  {f.name}: no table rc={proc.returncode} stderr={proc.stderr.strip()[:80]}")
            continue
        pairs = []
        es = None
        for line in proc.stdout.splitlines():
            if line.startswith("empty_send\t"):
                es = line.split("\t", 1)[1]
            elif line.startswith("completed_only_unit\t") and es is not None:
                pairs.append((es, line.split("\t", 1)[1]))
                es = None
        same = all(a == b for a, b in pairs)
        print(f"  {f.name}: rc={proc.returncode} hang={rows(proc.stdout).get('hang_risk')} pairs={pairs} empty==completed={same}")

    print("\n=== H. ceilings re-hit (not leftover-identity lies) ===")
    n8193 = [f"m.py::t{i}" for i in range(8193)]
    cap = run(
        "-",
        json.dumps(
            {
                "collection": n8193,
                "dist": "loadgroup",
                "workqueue": {n8193[0]: {n8193[0]: False}},
            }
        ),
    )
    print("  8193 collection rc", cap.returncode, cap.stderr.strip()[:160])
    tab = run("-", json.dumps({"collection": ["a.py::t\tx"], "workqueue": {"a.py::t\tx": {"a.py::t\tx": False}}}))
    print("  tab in nodeid first_assigned", field(tab, "first_assigned"), "rc", tab.returncode)
    loadfile = run("-", json.dumps({"dist": "loadfile", "workqueue": {"a.py::t": {"a.py::t": False}}}))
    print("  dist loadfile", loadfile.returncode, loadfile.stderr.strip()[:80])
    missing = run(
        "-",
        "collection\tmod.py::a\n"
        "dist\tloadgroup\n"
        "unit\tmod.py::a\tmod.py::a\tdone\n"
        "unit\tmod.py::b\tmod.py::b\topen\n",
    )
    print("  missing incomplete", missing.returncode, missing.stderr.strip()[:80], "stdout", bool(missing.stdout))
    completed_missing = run(
        "-",
        "collection\tlive.py::u\n"
        "dist\tloadgroup\n"
        "unit\tdone.py::t\tdone.py::t\tdone\n"
        "unit\tlive.py::u\tlive.py::u\topen\n",
    )
    show("completed missing from collection", completed_missing, KEYS)

    print("\n=== I. summary ===")
    print(json.dumps(
        {
            "sticker_match": f"{sm}/{len(sticker_cases)}",
            "two_greps_match": f"{gm}/{len(sticker_cases)}",
            "any_empty_match": f"{am}/{len(sticker_cases)}",
            "leftover_match": f"{lm}/{len(sticker_cases)}",
            "replica_match": f"{replica_ok}/{len(replica_cases)}",
            "sticker_cases": sticker_cases,
            "pytest_xdist_import": facts["pytest_xdist_import"],
            "empty_send_assign": facts["empty_send_assign"],
            "hang_assign": facts["hang_assign"],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
