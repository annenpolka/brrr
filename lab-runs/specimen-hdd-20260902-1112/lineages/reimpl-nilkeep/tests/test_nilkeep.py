#!/usr/bin/env python3
"""Two-pass coalesce tables: empty-map drops user-null; null chart keeps it."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "nilkeep"
FIX = ROOT / "fixtures"


def load_cli():
    loader = importlib.machinery.SourceFileLoader("nilkeep2_cli", str(CLI))
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


def rows_of(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class TwoPassTablesTests(unittest.TestCase):
    def test_copy_nils_then_delete_drops_baz(self):
        engine = MOD.CoalesceTables()
        dst = {"foo": "bar", "baz": None}
        src = {}
        marked = engine.copy_nils(dst, src, path="data")
        self.assertEqual(marked, {"baz": None})
        self.assertEqual(src, {})
        out = engine.apply_src(dst, marked, path="data")
        self.assertEqual(out, {"foo": "bar"})
        ops = [ev["op"] for ev in engine.trace]
        self.assertEqual(ops, ["copy_nil", "delete"])
        self.assertEqual(engine.trace[0]["key"], "baz")
        self.assertEqual(engine.trace[1]["key"], "baz")

    def test_skipping_copy_nils_keeps_user_null(self):
        engine = MOD.CoalesceTables()
        dst = {"foo": "bar", "baz": None}
        out = engine.apply_src(dst, {}, path="data")
        self.assertEqual(out, {"foo": "bar", "baz": None})
        self.assertEqual(engine.trace, [])

    def test_null_chart_value_skips_table_walk(self):
        engine = MOD.CoalesceTables()
        dest = engine.coalesce_values(
            {"data": {"foo": "bar", "baz": None}},
            {"data": None},
        )
        self.assertEqual(dest["data"]["baz"], None)
        self.assertIn("baz", dest["data"])
        ops = [ev["op"] for ev in engine.trace]
        self.assertEqual(ops, ["skip_table"])
        self.assertTrue(engine.trace[0]["src_null"])

    def test_empty_chart_table_enters_two_pass(self):
        engine = MOD.CoalesceTables()
        dest = engine.coalesce_values(
            {"data": {"foo": "bar", "baz": None}},
            {"data": {}},
        )
        self.assertEqual(dest, {"data": {"foo": "bar"}})
        ops = [ev["op"] for ev in engine.trace]
        self.assertEqual(ops, ["copy_nil", "delete"])


class FixtureCliTests(unittest.TestCase):
    def test_empty_map_drops_baz(self):
        proc = run_cli(str(FIX / "079-empty-map.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["default"], ["empty-map"])
        self.assertEqual(rows["dropped"], ["baz"])
        self.assertEqual(rows["kept"], ["foo"])
        self.assertEqual(rows["user_nulls"], ["baz"])
        self.assertEqual(rows["quoted"], ["map[foo:bar]"])

    def test_null_default_keeps_baz(self):
        proc = run_cli(str(FIX / "079-null-default.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["dropped"], ["-"])
        self.assertIn("baz", rows["kept"])
        self.assertIn("foo", rows["kept"])
        self.assertEqual(rows["quoted"], ["map[baz:<nil> foo:bar]"])

    def test_unseen(self):
        proc = run_cli(str(FIX / "unseen.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["dropped"], ["gone"])
        self.assertEqual(rows["kept"], ["keep"])

    def test_json_empty_map_matches_tsv(self):
        tsv = run_cli(str(FIX / "079-empty-map.rec"))
        js = run_cli(str(FIX / "079-empty-map.json"))
        self.assertEqual(tsv.returncode, 1, tsv.stderr)
        self.assertEqual(js.returncode, 1, js.stderr)
        self.assertEqual(tsv.stdout, js.stdout)
        rows = rows_of(js.stdout)
        self.assertEqual(rows["dropped"], ["baz"])
        self.assertEqual(rows["kept"], ["foo"])

    def test_json_null_default_matches_tsv(self):
        tsv = run_cli(str(FIX / "079-null-default.rec"))
        js = run_cli(str(FIX / "079-null-default.json"))
        self.assertEqual(tsv.returncode, 0, tsv.stderr)
        self.assertEqual(js.returncode, 0, js.stderr)
        self.assertEqual(tsv.stdout, js.stdout)
        rows = rows_of(js.stdout)
        self.assertEqual(rows["dropped"], ["-"])
        self.assertIn("baz", rows["kept"])
        self.assertIn("foo", rows["kept"])

    def test_json_shorthand_default_user(self):
        payload = json.dumps({"default": {}, "user": {"foo": "bar", "baz": None}})
        proc = run_cli("-", stdin=payload)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["dropped"], ["baz"])
        self.assertEqual(rows["kept"], ["foo"])

    def test_stdin_tsv_and_missing_file(self):
        proc = run_cli("-", stdin=(FIX / "079-empty-map.rec").read_text())
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("dropped\tbaz", proc.stdout)
        missing = run_cli("/no/such/nilkeep.rec")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("nilkeep:", missing.stderr)

    def test_json_array_is_accepted(self):
        payload = json.dumps(
            [{"chart": {"data": {}}, "user": {"data": {"keep": 1, "gone": None}}}]
        )
        proc = run_cli("-", stdin=payload)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("dropped\tgone", proc.stdout)
        self.assertIn("kept\tkeep", proc.stdout)


if __name__ == "__main__":
    unittest.main()
