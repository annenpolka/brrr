#!/usr/bin/env python3
"""Two-pass queue: completed-only requeue sends () and is hang_risk."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "emptyunit"
FIX = ROOT / "fixtures"


def load_cli():
    loader = importlib.machinery.SourceFileLoader("emptyunit2_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


MOD = load_cli()


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def last_fields(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        key, *rest = line.split("\t")
        rows[key] = rest
    return rows


class QueueTwoPassTests(unittest.TestCase):
    def test_requeue_then_drain_sends_empty_on_completed_only(self):
        q = MOD.LoadScopeQueue()
        q.collection = [
            "testing/test_timeout.py::test_1",
            "testing/test_timeout.py::test_2",
        ]
        q.assigned = {
            "testing/test_timeout.py": {
                "testing/test_timeout.py::test_1": True,
                "testing/test_timeout.py::test_2": True,
            }
        }
        self.assertEqual(len(q._fifo), 0)
        q.requeue()
        self.assertEqual(len(q._fifo), 1)
        q.drain()
        self.assertEqual(len(q._fifo), 0)
        snap = q.snapshot()
        self.assertTrue(snap["hang_risk"])
        self.assertEqual(snap["completed_only"], ["testing/test_timeout.py"])
        self.assertEqual(snap["sends"][0].indexes, [])
        self.assertTrue(snap["sends"][0].empty_send)
        ops = [ev["op"] for ev in q.trace]
        self.assertEqual(ops, ["update", "send_runtest_some"])
        self.assertEqual(q.trace[1]["indexes"], [])

    def test_mixed_pending_indexes_are_collection_positions(self):
        q = MOD.LoadScopeQueue()
        q.run(
            [
                {"op": "collect", "nodeid": "mod.py::test_a"},
                {"op": "collect", "nodeid": "mod.py::test_b"},
                {"op": "collect", "nodeid": "mod.py::test_c"},
                {
                    "op": "mark",
                    "scope": "mod.py",
                    "nodeid": "mod.py::test_a",
                    "completed": True,
                },
                {
                    "op": "mark",
                    "scope": "mod.py",
                    "nodeid": "mod.py::test_b",
                    "completed": False,
                },
                {
                    "op": "mark",
                    "scope": "mod.py",
                    "nodeid": "mod.py::test_c",
                    "completed": False,
                },
                {"op": "crash"},
            ]
        )
        snap = q.snapshot()
        self.assertFalse(snap["hang_risk"])
        self.assertEqual(snap["sends"][0].indexes, [1, 2])
        self.assertEqual(snap["completed_only"], [])


class FixtureCliTests(unittest.TestCase):
    def test_owned_hang_tsv(self):
        proc = run_cli(str(FIX / "063-hang.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = last_fields(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["completed_only"], ["testing/test_timeout.py"])
        self.assertEqual(rows["send"], ["()"])
        self.assertEqual(rows["empty_send"], ["yes"])

    def test_unseen_mixed_is_not_hang_risk(self):
        proc = run_cli(str(FIX / "unseen-mixed.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = last_fields(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["send"], ["(1,2)"])
        self.assertEqual(rows["empty_send"], ["no"])
        self.assertEqual(rows["completed_only"], ["none"])

    def test_two_scopes_completed_only_still_hangs(self):
        proc = run_cli(str(FIX / "unseen-two-scopes.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = last_fields(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["completed_only"], ["done.py"])
        self.assertEqual(rows["incomplete_scopes"], ["live.py"])

    def test_jsonl_hang_matches_tsv(self):
        tsv = run_cli(str(FIX / "063-hang.rec"))
        jsonl = run_cli(str(FIX / "063-hang.jsonl"))
        self.assertEqual(tsv.returncode, 0, tsv.stderr)
        self.assertEqual(jsonl.returncode, 0, jsonl.stderr)
        self.assertEqual(tsv.stdout, jsonl.stdout)
        rows = last_fields(jsonl.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["completed_only"], ["testing/test_timeout.py"])
        self.assertEqual(rows["send"], ["()"])

    def test_jsonl_mixed_hang_risk_no(self):
        proc = run_cli(str(FIX / "unseen-mixed.jsonl"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = last_fields(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["send"], ["(1,2)"])

    def test_json_array_is_accepted(self):
        payload = json.dumps(
            [
                {"op": "collect", "nodeid": "a::t"},
                {"op": "mark", "scope": "a", "nodeid": "a::t", "completed": True},
                {"op": "crash"},
            ]
        )
        proc = run_cli("-", stdin=payload)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("hang_risk\tyes", proc.stdout)
        self.assertIn("completed_only\ta", proc.stdout)
        self.assertIn("send\t()", proc.stdout)

    def test_stdin_tsv_and_missing_file(self):
        proc = run_cli("-", stdin=(FIX / "063-hang.rec").read_text())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("hang_risk\tyes", proc.stdout)
        missing = run_cli("/no/such/emptyunit.rec")
        self.assertEqual(missing.returncode, 1)

    def test_pending_but_absent_from_collection_is_empty_send(self):
        events = [
            {"op": "collect", "nodeid": "kept::one"},
            {
                "op": "mark",
                "scope": "gone.py",
                "nodeid": "gone.py::t",
                "completed": False,
            },
            {"op": "crash"},
        ]
        q = MOD.LoadScopeQueue()
        q.run(events)
        snap = q.snapshot()
        self.assertTrue(snap["hang_risk"])
        self.assertEqual(snap["completed_only"], [])
        self.assertEqual(snap["sends"][0].missing, ["gone.py::t"])
        self.assertEqual(snap["sends"][0].indexes, [])


if __name__ == "__main__":
    unittest.main()
