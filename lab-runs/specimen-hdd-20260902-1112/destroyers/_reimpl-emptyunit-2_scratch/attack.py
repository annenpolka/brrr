#!/usr/bin/env python3
"""Host attacks on reimpl-emptyunit-2. Does not import either emptyunit CLI."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
RE = RUN / "lineages/reimpl-emptyunit-2"
CA = RUN / "lineages/candidate-emptyunit"
RE_CLI = RE / "emptyunit"
CA_CLI = CA / "emptyunit"
FIX = RE / "fixtures"
CAFIX = CA / "fixtures"
OUT = RUN / "destroyers/_reimpl-emptyunit-2_scratch"


def run(cli: Path, arg: str | None = "-", text: str | None = None) -> subprocess.CompletedProcess[str]:
    argv = [sys.executable, str(cli)]
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
        return "-"
    if not indexes:
        return "()"
    return "(" + ",".join(str(i) for i in indexes) + ")"


def flatten_nested(payload: dict) -> list[tuple[str, bool]]:
    nodes: list[tuple[str, bool]] = []
    for inner in payload.values():
        if not isinstance(inner, dict):
            raise TypeError("not nested")
        for nodeid, flag in inner.items():
            nodes.append((str(nodeid), bool(flag)))
    return nodes


def first_dict_sticker(payload: dict, collection: list[str]) -> bool:
    """DESTROYER_2 §1: pending and first caller dict empty of False. No dist, no second."""
    pending = 0
    first = None
    for inner in payload.values():
        if not isinstance(inner, dict):
            continue
        if first is None:
            first = inner
        for _n, done in inner.items():
            if not done:
                pending += 1
    if first is None:
        return False
    idxs = [collection.index(n) for n, done in first.items() if not done]
    return bool(pending and not idxs)


def two_greps(payload: dict) -> bool:
    """Two-membership leftover: some incomplete exists, and the first bag is all True."""
    bags = [inner for inner in payload.values() if isinstance(inner, dict)]
    if not bags:
        return False
    any_open = any(not flag for inner in bags for flag in inner.values())
    first_all_true = bool(bags[0]) and all(bags[0].values())
    return bool(any_open and first_all_true)


def scope_of(nodeid: str, dist: str) -> str:
    if dist == "loadscope":
        return nodeid.rsplit("::", 1)[0]
    at = nodeid.rfind("@")
    bracket = nodeid.rfind("]")
    if at != -1 and at > bracket:
        return nodeid[at + 1 :]
    return nodeid


def replica_idxpart(collection: list[str], nodes: list[tuple[str, bool]], dist: str) -> dict:
    """Independent leftover formula: collection-index partitions + burst.

    Does not import emptyunit. Matches claimed reimpl-2 style.
    """
    order: list[str] = []
    bags: dict[str, list[tuple[str, bool]]] = {}
    for nodeid, done in nodes:
        scope = scope_of(nodeid, dist)
        if scope not in bags:
            bags[scope] = []
            order.append(scope)
        bags[scope].append((nodeid, done))
    parts = [(scope, bags[scope]) for scope in order]
    pending = sum(1 for _s, items in parts for _n, done in items if not done)
    missing = [
        nodeid
        for _s, items in parts
        for nodeid, done in items
        if not done and nodeid not in collection
    ]
    if missing:
        return {"error": "index-error", "missing": missing}
    if pending == 0 or not parts:
        return {
            "hang_risk": False,
            "rc": 0,
            "first_assigned": "-",
            "would_send": None,
            "assigned": [],
            "reschedule": False,
            "hang_unit": "-",
            "scopes_n": len(parts),
            "pending": pending,
            "empty_send_eq_completed_only": all(
                (not [n for n, d in items if not d]) == (bool(items) and all(d for _n, d in items))
                for _s, items in parts
            ),
        }
    assigned = [parts[0]]
    first_pending = sum(1 for _n, done in parts[0][1] if not done)
    reschedule = False
    if 1 <= first_pending <= 2 and len(parts) > 1:
        assigned.append(parts[1])
        reschedule = True
    hang_risk = False
    hang_unit = "-"
    sends: list[list[int]] = []
    for _scope, items in assigned:
        send = [collection.index(n) for n, done in items if not done]
        sends.append(send)
        if not send and hang_unit == "-":
            hang_risk = True
            hang_unit = _scope
    eq = all(
        (not [n for n, d in items if not d]) == (bool(items) and all(d for _n, d in items))
        for _s, items in parts
    )
    return {
        "hang_risk": hang_risk,
        "rc": 1 if hang_risk else 0,
        "first_assigned": assigned[0][0],
        "would_send": sends[0],
        "assigned": [s for s, _ in assigned],
        "reschedule": reschedule,
        "hang_unit": hang_unit,
        "scopes_n": len(parts),
        "pending": pending,
        "empty_send_eq_completed_only": eq,
    }


def harvest_key(proc: subprocess.CompletedProcess[str]) -> dict:
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


def same_harvest(a: dict, b: dict, *, ignore_err: bool = True) -> bool:
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
    if not ignore_err:
        keys.append("err")
    return all(a.get(k) == b.get(k) for k in keys)


def replica_as_harvest(rep: dict) -> dict:
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
    return {
        "rc": rep["rc"],
        "hang_risk": [yn(rep["hang_risk"])],
        "would_send": [send_tuple(rep["would_send"])],
        "first_assigned": [rep["first_assigned"]],
        "assigned": rep["assigned"] if rep["assigned"] else ["-"],
        "reschedule": [yn(rep["reschedule"])],
        "hang_unit": [rep["hang_unit"]],
        "scopes_n": [str(rep["scopes_n"])],
        "pending": [str(rep["pending"])],
        "err": "",
    }


def show(label: str, proc: subprocess.CompletedProcess[str], keys: list[str]) -> None:
    print(f"\n## {label}")
    print(f"rc={proc.returncode}")
    if proc.stderr.strip():
        print("stderr:", proc.stderr.strip()[:500])
    r = rows(proc.stdout)
    for k in keys:
        print(f"  {k}\t{r.get(k, ['<missing>'])}")


KEYS = [
    "hang_risk",
    "would_send",
    "first_assigned",
    "assigned",
    "reschedule",
    "hang_unit",
    "scopes_n",
    "pending",
    "empty_send",
    "completed_only_unit",
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results: dict = {"cases": []}

    owned = json.loads((FIX / "063-hang.json").read_text())
    live_first = {
        "collection": ["live.py::u", "done.py::t"],
        "workqueue": {
            "live.py::u": {"live.py::u": False},
            "done.py::t": {"done.py::t": True},
        },
    }
    same_tests = {
        "collection": ["mod.py::a", "mod.py::b"],
        "workqueue": {
            "mod.py::a": {"mod.py::a": True},
            "mod.py::b": {"mod.py::b": False},
        },
    }
    done_first = {
        "collection": ["done.py::t", "live.py::u"],
        "workqueue": {
            "done.py::t": {"done.py::t": True},
            "live.py::u": {"live.py::u": False},
        },
    }
    pending3 = {
        "collection": ["a.py::t1", "a.py::t2", "a.py::t3", "b.py::t"],
        "workqueue": {
            "a.py::t1": {"a.py::t1": False},
            "a.py::t2": {"a.py::t2": False},
            "a.py::t3": {"a.py::t3": False},
            "b.py::t": {"b.py::t": True},
        },
    }

    sticker_cases = [
        ("owned 063", owned, "loadgroup"),
        ("live-first", live_first, "loadgroup"),
        ("same tests loadgroup", same_tests, "loadgroup"),
        ("same tests loadscope", same_tests, "loadscope"),
        ("done-first", done_first, "loadgroup"),
        ("owned forced loadscope", {**owned, "dist": "loadscope"}, "loadscope"),
        ("pending3 loadscope-shaped", pending3, "loadscope"),
    ]

    print("=== Honor-KILL 1: first-dict sticker vs CLI hang_risk ===")
    sticker_match = 0
    two_grep_match = 0
    for name, dump, dist in sticker_cases:
        payload = dump["workqueue"]
        collection = dump["collection"]
        sticker = first_dict_sticker(payload, collection)
        greps = two_greps(payload)
        blob = json.dumps({**dump, "dist": dist})
        proc = run(RE_CLI, "-", blob)
        cli_hang = field(proc, "hang_risk") == ["yes"]
        match = sticker == cli_hang
        gmatch = greps == cli_hang
        sticker_match += int(match)
        two_grep_match += int(gmatch)
        print(
            f"{name:28} sticker={sticker!s:5} two_greps={greps!s:5} "
            f"cli_hang={cli_hang!s:5} match={match} grep_match={gmatch} rc={proc.returncode}"
        )
        results["cases"].append(
            {
                "name": name,
                "sticker": sticker,
                "two_greps": greps,
                "cli_hang": cli_hang,
                "match": match,
                "grep_match": gmatch,
                "rc": proc.returncode,
            }
        )
    print(f"sticker MATCH {sticker_match}/{len(sticker_cases)}")
    print(f"two_greps MATCH {two_grep_match}/{len(sticker_cases)}")
    results["sticker_match"] = f"{sticker_match}/{len(sticker_cases)}"
    results["two_greps_match"] = f"{two_grep_match}/{len(sticker_cases)}"

    print("\n=== Honor-KILL 2: reimpl vs candidate harvest fields ===")
    compare_inputs = [
        ("owned dump", str(FIX / "063-hang.dump"), None),
        ("owned json", str(FIX / "063-hang.json"), None),
        ("owned wq", str(FIX / "063-hang.wq"), None),
        ("live-first rec", str(FIX / "unseen-live-first.rec"), None),
        ("two-scopes rec", str(FIX / "unseen-two-scopes.rec"), None),
        ("pending2 rec", str(FIX / "unseen-pending2.rec"), None),
        ("pending3 rec", str(FIX / "unseen-pending3.rec"), None),
        ("mixed rec", str(FIX / "unseen-mixed.rec"), None),
        ("063 rec handwritten", str(FIX / "063-hang.rec"), None),
        ("alldone rec", str(FIX / "loadscope-alldone.rec"), None),
        ("open rec", str(FIX / "loadscope-open.rec"), None),
        ("hang log", str(FIX / "hang_log.txt"), None),
        (
            "same tests loadgroup",
            "-",
            json.dumps({**same_tests, "dist": "loadgroup"}),
        ),
        (
            "same tests loadscope",
            "-",
            json.dumps({**same_tests, "dist": "loadscope"}),
        ),
        (
            "owned forced loadscope",
            "-",
            json.dumps({**owned, "dist": "loadscope"}),
        ),
        (
            "live-first json",
            "-",
            json.dumps({**live_first, "dist": "loadgroup"}),
        ),
        (
            "caller module keys loadgroup",
            "-",
            json.dumps(
                {
                    "collection": ["mod.py::a", "mod.py::b"],
                    "dist": "loadgroup",
                    "workqueue": {"mod.py": {"mod.py::a": True, "mod.py::b": False}},
                }
            ),
        ),
        (
            "class rsplit loadscope",
            "-",
            json.dumps(
                {
                    "collection": ["m.py::T::a", "m.py::T::b"],
                    "dist": "loadscope",
                    "workqueue": {
                        "m.py::T::a": {"m.py::T::a": True},
                        "m.py::T::b": {"m.py::T::b": False},
                    },
                }
            ),
        ),
        (
            "at-group loadgroup",
            "-",
            json.dumps(
                {
                    "collection": ["mod.py::a[1]@g", "mod.py::b[2]@g"],
                    "dist": "loadgroup",
                    "workqueue": {
                        "mod.py::a[1]@g": {"mod.py::a[1]@g": True},
                        "mod.py::b[2]@g": {"mod.py::b[2]@g": False},
                    },
                }
            ),
        ),
        (
            "257 first-done",
            "-",
            json.dumps(
                {
                    "collection": [f"m.py::t{i}" for i in range(257)],
                    "dist": "loadgroup",
                    "workqueue": {
                        n: {n: (i == 0)}
                        for i, n in enumerate([f"m.py::t{i}" for i in range(257)])
                    },
                }
            ),
        ),
        (
            "three live/done/live",
            "-",
            "collection\tlive1.py::u\tdone.py::t\tlive2.py::u\n"
            "dist\tloadgroup\n"
            "unit\tlive1.py::u\tlive1.py::u\topen\n"
            "unit\tdone.py::t\tdone.py::t\tdone\n"
            "unit\tlive2.py::u\tlive2.py::u\topen\n",
        ),
        (
            "two live",
            "-",
            "collection\tlive1.py::u\tlive2.py::u\n"
            "dist\tloadgroup\n"
            "unit\tlive1.py::u\tlive1.py::u\topen\n"
            "unit\tlive2.py::u\tlive2.py::u\topen\n",
        ),
        (
            "missing incomplete",
            "-",
            "collection\tmod.py::a\n"
            "dist\tloadgroup\n"
            "unit\tmod.py::a\tmod.py::a\tdone\n"
            "unit\tmod.py::b\tmod.py::b\topen\n",
        ),
        (
            "dash nodeid",
            "-",
            json.dumps(
                {
                    "collection": ["-", "x"],
                    "workqueue": {"-": {"-": True}, "x": {"x": False}},
                }
            ),
        ),
        (
            "dist none",
            "-",
            json.dumps(
                {
                    "collection": ["a.py::t"],
                    "dist": "none",
                    "workqueue": {"a.py::t": {"a.py::t": False}},
                }
            ),
        ),
        (
            "empty wq assigned",
            "-",
            json.dumps(
                {
                    "collection": [
                        "testing/test_timeout.py::test_1",
                        "testing/test_timeout.py::test_2",
                    ],
                    "workqueue": {},
                    "assigned": owned["workqueue"],
                }
            ),
        ),
        (
            "xdist1335 loadscope",
            "-",
            json.dumps(
                {
                    "collection": ["m.py::test[a::b]", "m.py::test[c]"],
                    "dist": "loadscope",
                    "workqueue": {
                        "m.py::test[a::b]": {"m.py::test[a::b]": True},
                        "m.py::test[c]": {"m.py::test[c]": False},
                    },
                }
            ),
        ),
        (
            "at inside brackets",
            "-",
            json.dumps(
                {
                    "collection": ["m.py::t[a@b]", "n.py::t"],
                    "dist": "loadgroup",
                    "workqueue": {
                        "m.py::t[a@b]": {"m.py::t[a@b]": True},
                        "n.py::t": {"n.py::t": False},
                    },
                }
            ),
        ),
        (
            "fifo dump order not collection",
            "-",
            json.dumps(
                {
                    "collection": ["done.py::t", "live.py::u"],
                    "dist": "loadgroup",
                    "workqueue": {
                        "live.py::u": {"live.py::u": False},
                        "done.py::t": {"done.py::t": True},
                    },
                }
            ),
        ),
        (
            "completed missing from collection",
            "-",
            json.dumps(
                {
                    "collection": ["live.py::u"],
                    "dist": "loadgroup",
                    "workqueue": {
                        "gone.py::t": {"gone.py::t": True},
                        "live.py::u": {"live.py::u": False},
                    },
                }
            ),
        ),
    ]

    harvest_same = 0
    harvest_diff = []
    replica_same = 0
    replica_diff = []
    for name, arg, text in compare_inputs:
        re_p = run(RE_CLI, arg, text)
        ca_p = run(CA_CLI, arg, text)
        re_h = harvest_key(re_p)
        ca_h = harvest_key(ca_p)
        eq = same_harvest(re_h, ca_h)
        harvest_same += int(eq)
        if not eq:
            harvest_diff.append({"name": name, "reimpl": re_h, "candidate": ca_h})
            print(f"DIFF {name}")
            print(f"  reimpl    {re_h}")
            print(f"  candidate {ca_h}")
        else:
            print(f"SAME {name} rc={re_h['rc']} hang={re_h['hang_risk']} send={re_h['would_send']}")

        # replica on JSON dumps only
        if text and text.lstrip().startswith("{"):
            blob = json.loads(text)
            if isinstance(blob.get("workqueue"), dict) and blob.get("collection"):
                try:
                    nodes = flatten_nested(blob["workqueue"] or blob.get("assigned") or {})
                    if not nodes and blob.get("assigned"):
                        nodes = flatten_nested(blob["assigned"])
                    dist = blob.get("dist") or "loadgroup"
                    if dist in {"loadgroup", "loadscope"}:
                        rep = replica_idxpart(blob["collection"], nodes, dist)
                        rh = replica_as_harvest(rep)
                        # compare hang fields only when both parsed
                        if re_p.returncode == 0 or field(re_p, "hang_risk"):
                            req = same_harvest(re_h, rh)
                            replica_same += int(req)
                            if not req:
                                replica_diff.append({"name": name, "reimpl": re_h, "replica": rh})
                                print(f"  REPLICA DIFF {name} {rh}")
                        elif "index-error" in re_p.stderr and rep.get("error") == "index-error":
                            replica_same += 1
                except Exception as exc:
                    replica_diff.append({"name": name, "error": str(exc)})

    print(f"\nreimpl vs candidate harvest SAME {harvest_same}/{len(compare_inputs)}")
    print(f"replica vs reimpl (json subset) SAME {replica_same} diffs {len(replica_diff)}")
    results["harvest_same"] = f"{harvest_same}/{len(compare_inputs)}"
    results["harvest_diff"] = harvest_diff
    results["replica_same"] = replica_same
    results["replica_diff"] = replica_diff

    print("\n=== replica vs CLI on owned + live-first + dist ===")
    replica_cli = []
    for name, dump, dist in sticker_cases:
        nodes = flatten_nested(dump["workqueue"])
        rep = replica_idxpart(dump["collection"], nodes, dist)
        proc = run(RE_CLI, "-", json.dumps({**dump, "dist": dist}))
        rh = replica_as_harvest(rep)
        ch = harvest_key(proc)
        eq = same_harvest(ch, rh)
        replica_cli.append({"name": name, "eq": eq, "replica": rh, "cli": ch})
        print(f"{'EQ' if eq else 'NE'} {name} replica_hang={rh['hang_risk']} cli={ch['hang_risk']}")
    results["replica_cli"] = replica_cli
    print(f"replica MATCH CLI {sum(1 for x in replica_cli if x['eq'])}/{len(replica_cli)}")

    print("\n=== empty_send vs completed_only_unit on fixtures ===")
    for path in sorted(FIX.glob("*")):
        if path.suffix not in {".dump", ".json", ".wq", ".rec"}:
            continue
        proc = run(RE_CLI, str(path))
        if proc.returncode not in (0, 1) or not proc.stdout:
            print(f"{path.name}: no table rc={proc.returncode} err={proc.stderr.strip()[:80]!r}")
            continue
        r = rows(proc.stdout)
        # last empty_send/completed_only_unit are last scope; collect all by scanning
        pairs = []
        cur_es = cur_co = None
        for line in proc.stdout.splitlines():
            if line.startswith("empty_send\t"):
                cur_es = line.split("\t", 1)[1]
            elif line.startswith("completed_only_unit\t"):
                cur_co = line.split("\t", 1)[1]
                pairs.append((cur_es, cur_co))
        eq_all = all(a == b for a, b in pairs)
        print(f"{path.name}: pairs={pairs} empty_send==completed_only_unit={eq_all} hang={r.get('hang_risk')}")

    print("\n=== ingest leftovers ===")
    attacks = []

    def attack(label: str, arg: str, text: str | None = None, cli: Path = RE_CLI) -> None:
        proc = run(cli, arg, text)
        attacks.append(
            {
                "label": label,
                "rc": proc.returncode,
                "stdout": proc.stdout[:200],
                "stderr": proc.stderr.strip()[:240],
            }
        )
        print(f"\n# {label}")
        print(f"rc={proc.returncode}")
        if proc.stderr.strip():
            print("stderr:", proc.stderr.strip()[:240])
        if proc.stdout:
            r = rows(proc.stdout)
            for k in KEYS:
                if k in r:
                    print(f"  {k}\t{r[k]}")

    attack("empty stdin", "-", "")
    attack("/dev/null", "/dev/null")
    attack("missing file", "/no/such/emptyunit.rec")
    attack("jsonl two objects", "-", '{"a":1}\n{"b":2}\n')
    attack("trailing comma", "-", '{"collection":["a.py::t"],"workqueue":{"a.py::t":{"a.py::t":false}},}')
    attack("block comment", "-", '/* x */\n{"collection":["a.py::t"],"workqueue":{"a.py::t":{"a.py::t":false}}}')
    attack("utf8 bom json", "-", "\ufeff" + json.dumps({**same_tests, "dist": "loadgroup"}))
    attack("dist omitted", "-", json.dumps(same_tests))
    attack("dist loadfile", "-", json.dumps({**same_tests, "dist": "loadfile"}))
    attack("nodeid tab json", "-", json.dumps({"collection": ["a.py::t\tx"], "workqueue": {"a.py::t\tx": {"a.py::t\tx": False}}}))
    attack(
        "collection 8193",
        "-",
        json.dumps(
            {
                "collection": [f"m.py::t{i}" for i in range(8193)],
                "workqueue": {"m.py::t0": {"m.py::t0": False}},
            }
        ),
    )
    attack(
        "collection 8192 first open",
        "-",
        json.dumps(
            {
                "collection": [f"m.py::t{i}" for i in range(8192)],
                "workqueue": {"m.py::t0": {"m.py::t0": False}},
            }
        ),
    )
    attack("json array", "-", '["a.py::t"]')
    attack("bare list+dict", "-", "['a.py::t']\n{'a.py::t': {'a.py::t': False}}")
    attack("flat workqueue", "-", json.dumps({"collection": ["a.py::t"], "workqueue": {"a.py::t": False}}))
    attack(
        "tsv workqueue json field",
        "-",
        "collection\ta.py::t\nworkqueue\t" + json.dumps({"a.py::t": {"a.py::t": False}}) + "\n",
    )
    attack("extra argv", "fixtures/063-hang.dump extra")
    attack("none nodeid tsv", "-", "collection\tnone\ndist\tloadgroup\nunit\tnone\tnone\topen\n")
    attack("workers hang log", "-", "workers [gw0]\nreplacing crashed worker gw0\n")
    attack("collecting hang log", "-", "collecting: 2 items\n")
    attack("duplicate json collection last-wins?", "-", '{"collection":["a.py::t"],"collection":["b.py::t"],"workqueue":{"b.py::t":{"b.py::t":false}}}')
    attack(
        "nonempty wq shadows assigned",
        "-",
        json.dumps(
            {
                "collection": ["a.py::t", "b.py::t"],
                "workqueue": {"a.py::t": {"a.py::t": False}},
                "assigned": {
                    "a.py::t": {"a.py::t": True},
                    "b.py::t": {"b.py::t": False},
                },
            }
        ),
    )
    attack(
        "completed-only missing still hang?",
        "-",
        json.dumps(
            {
                "collection": ["live.py::u"],
                "dist": "loadgroup",
                "workqueue": {
                    "gone.py::t": {"gone.py::t": True},
                    "live.py::u": {"live.py::u": False},
                },
            }
        ),
    )
    attack(
        "two live then completed-only",
        "-",
        json.dumps(
            {
                "collection": ["l1.py::u", "l2.py::u", "d.py::t"],
                "dist": "loadgroup",
                "workqueue": {
                    "l1.py::u": {"l1.py::u": False},
                    "l2.py::u": {"l2.py::u": False},
                    "d.py::t": {"d.py::t": True},
                },
            }
        ),
    )
    attack(
        "fifo collection vs dump order",
        "-",
        json.dumps(
            {
                "collection": ["done.py::t", "live.py::u"],
                "dist": "loadgroup",
                "workqueue": {
                    "live.py::u": {"live.py::u": False},
                    "done.py::t": {"done.py::t": True},
                },
            }
        ),
    )
    attack("candidate hang log collecting", "collecting hang log", "collecting: 2 items\n", CA_CLI)
    attack("reimpl hang log collecting", "collecting hang log re", "collecting: 2 items\n")
    attack(
        "eval arithmetic dump?",
        "-",
        "OrderedDict([('a.py::t', OrderedDict([('a.py::t', 1-1)]))])",
    )
    attack(
        "candidate eval arithmetic",
        "-",
        "OrderedDict([('a.py::t', OrderedDict([('a.py::t', 1-1)]))])",
        CA_CLI,
    )
    attack("python print dict only", "-", "{'a.py::t': {'a.py::t': False}}")
    attack("null collection", "-", json.dumps({"collection": [None], "workqueue": {"x.py::t": {"x.py::t": False}}}))
    attack("bool collection", "-", json.dumps({"collection": [True], "workqueue": {"x.py::t": {"x.py::t": False}}}))

    results["attacks"] = [
        {"label": a["label"], "rc": a["rc"], "stderr": a["stderr"], "stdout_head": a["stdout"][:120]}
        for a in attacks
    ]

    print("\n=== stdout byte-identical reimpl vs candidate on owned dump? ===")
    re_owned = run(RE_CLI, str(FIX / "063-hang.dump"))
    ca_owned = run(CA_CLI, str(CAFIX / "063-hang.dump"))
    print("stdout_eq", re_owned.stdout == ca_owned.stdout)
    print("rc_eq", re_owned.returncode == ca_owned.returncode)
    if re_owned.stdout != ca_owned.stdout:
        re_lines = re_owned.stdout.splitlines()
        ca_lines = ca_owned.stdout.splitlines()
        for i, (a, b) in enumerate(zip(re_lines, ca_lines)):
            if a != b:
                print(f"  line {i}: reimpl={a!r} cand={b!r}")
        print("  reimpl extra", re_lines[len(ca_lines) :])
        print("  cand extra", ca_lines[len(re_lines) :])
    results["owned_stdout_eq"] = re_owned.stdout == ca_owned.stdout
    results["owned_rc_eq"] = re_owned.returncode == ca_owned.returncode

    (OUT / "attack.json").write_text(json.dumps(results, indent=2) + "\n")
    print("\nWROTE", OUT / "attack.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
