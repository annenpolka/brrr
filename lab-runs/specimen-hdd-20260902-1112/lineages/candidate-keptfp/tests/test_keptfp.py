#!/usr/bin/env python3
"""live vs leftover fingerprints against current lockfile hash."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "keptfp"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("keptfp_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


KF = load_mod()


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


class Specimen006Tests(unittest.TestCase):
    def test_owned_record_names_leftover_vs_live(self):
        text = (FIXTURES / "006-cache.rec").read_text(encoding="utf-8")
        current, entries = KF.parse_record(text, source="006")
        result = KF.inspect(current, entries)
        self.assertEqual(result["current"], "f0e1d2c3b4")
        self.assertEqual(result["live_n"], 1)
        self.assertEqual(result["leftover_n"], 2)
        self.assertEqual(result["live"][0].ident, "fm_8e9f0a1b")
        leftover_ids = [e.ident for e in result["leftover"]]
        self.assertEqual(leftover_ids, ["fm_7a1b2c3d", "fm_5c6d7e8f"])
        self.assertEqual(result["leftover_members"], ["project_a", "project_b"])

    def test_cli_matches_owned_record(self):
        proc = run_cli([str(FIXTURES / "006-cache.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["current"][0], ["f0e1d2c3b4"])
        self.assertEqual(rows["live_n"][0], ["1"])
        self.assertEqual(rows["leftover_n"][0], ["2"])
        self.assertEqual(rows["live"][0][0], "fm_8e9f0a1b")
        leftover_ids = [row[0] for row in rows["leftover"]]
        self.assertEqual(leftover_ids, ["fm_7a1b2c3d", "fm_5c6d7e8f"])

    def test_unseen_mixed_members(self):
        proc = run_cli([str(FIXTURES / "unseen-cache.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["live_n"][0], ["2"])
        self.assertEqual(rows["leftover_n"][0], ["3"])
        self.assertEqual(rows["leftover_members"][0], ["crate_x", "crate_y", "crate_z"])

    def test_all_live(self):
        text = "current\tabc\nentry\te1\tm\tabc\t1\n"
        current, entries = KF.parse_record(text)
        result = KF.inspect(current, entries)
        self.assertEqual(result["leftover_n"], 0)
        report = KF.format_report(result)
        self.assertIn("leftover\tnone", report)

    def test_missing_current_is_error(self):
        proc = run_cli(["/dev/stdin"]) if False else subprocess.run(
            [sys.executable, str(CLI)],
            input="entry\te1\tm\th\t1\n",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing current", proc.stderr)

    def test_stdin_roundtrip(self):
        text = (FIXTURES / "006-cache.rec").read_text(encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(CLI)],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_n"][0], ["2"])


if __name__ == "__main__":
    unittest.main()
