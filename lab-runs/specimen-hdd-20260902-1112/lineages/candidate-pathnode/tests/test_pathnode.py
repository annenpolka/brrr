#!/usr/bin/env python3
"""same path can be two collection nodes; fixtures bind to node identity."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pathnode"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("pathnode_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


PN = load_mod()


def parse_rows(text: str) -> dict[str, list[list[str]]]:
    rows: dict[str, list[list[str]]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows.setdefault(name, []).append(rest)
    return rows


def run_cli(args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
    )


class Specimen003Tests(unittest.TestCase):
    def test_same_path_two_nodes_fixture_miss(self):
        text = (FIXTURES / "003-collect.rec").read_text(encoding="utf-8")
        collects, registers, lookups = PN.parse_record(text, source="003")
        result = PN.inspect(collects, registers, lookups)
        self.assertEqual(result["paths"], ["dir1", "dir2", "dir1"])
        self.assertEqual(len(result["dups"]), 1)
        self.assertEqual(result["dups"][0]["path"], "dir1")
        self.assertEqual(result["dups"][0]["nodes"], ["n1", "n3"])
        self.assertFalse(result["dups"][0]["same_node"])
        self.assertEqual(len(result["misses"]), 1)
        self.assertEqual(result["misses"][0]["fixture"], "shared_fixture")
        self.assertEqual(result["misses"][0]["lookup"], "n3")
        self.assertEqual(result["misses"][0]["bound_to"], ["n1"])

    def test_cli_matches_owned_events(self):
        proc = run_cli([str(FIXTURES / "003-collect.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["paths"][0], ["dir1", "dir2", "dir1"])
        dup = rows["dup_path"][0]
        self.assertEqual(dup[0], "dir1")
        self.assertIn("n1", dup)
        self.assertIn("n3", dup)
        self.assertEqual(dup[-1], "no")
        miss = rows["miss"][0]
        self.assertEqual(miss[0], "shared_fixture")
        self.assertEqual(miss[2], "n3")
        self.assertEqual(miss[4], "n1")
        self.assertEqual(miss[miss.index("found") + 1], "no")
        self.assertEqual(rows["shared_node"][0], ["none"])

    def test_unseen_same_node_twice_is_same_object(self):
        proc = run_cli([str(FIXTURES / "unseen-collect.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        dup = rows["dup_path"][0]
        self.assertEqual(dup[0], "pkg/tests")
        self.assertEqual(dup[-1], "yes")
        self.assertEqual(rows["miss"][0], ["none"])

    def test_single_path_no_dup(self):
        text = "collect\tonly\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n"
        collects, registers, lookups = PN.parse_record(text)
        result = PN.inspect(collects, registers, lookups)
        self.assertEqual(result["dups"], [])
        self.assertEqual(result["misses"], [])
        report = PN.format_report(result)
        self.assertIn("dup_path\tnone", report)
        self.assertIn("miss\tnone", report)

    def test_found_lookup_unbound_is_miss(self):
        text = "collect\td\tn1\nlookup\tfx\tn1\tfound\n"
        collects, registers, lookups = PN.parse_record(text)
        result = PN.inspect(collects, registers, lookups)
        self.assertEqual(len(result["misses"]), 1)
        self.assertTrue(result["misses"][0]["found"])
        self.assertTrue(result["misses"][0]["unbound"])
        report = PN.format_report(result)
        self.assertIn("found\tyes", report)
        self.assertIn("unbound\tyes", report)

    def test_two_paths_one_node_is_shared(self):
        text = "collect\ta\tn1\ncollect\tb\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n"
        collects, registers, lookups = PN.parse_record(text)
        result = PN.inspect(collects, registers, lookups)
        self.assertEqual(result["dups"], [])
        self.assertEqual(result["misses"], [])
        self.assertEqual(result["shared"][0]["node"], "n1")
        self.assertEqual(result["shared"][0]["paths"], ["a", "b"])
        proc = subprocess.run(
            [sys.executable, str(CLI)],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["shared_node"][0][0], "n1")
        self.assertIn("a", rows["shared_node"][0])
        self.assertIn("b", rows["shared_node"][0])

    def test_missing_collect_is_error(self):
        proc = subprocess.run(
            [sys.executable, str(CLI)],
            input="register\tfx\tn1\n",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing collect", proc.stderr)


if __name__ == "__main__":
    unittest.main()
