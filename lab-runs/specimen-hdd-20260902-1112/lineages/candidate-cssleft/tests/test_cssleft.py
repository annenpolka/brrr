#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "cssleft"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run(path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), path],
        capture_output=True,
        text=True,
        check=False,
    )


class Owned090(unittest.TestCase):
    def test_case_c_leftover_url_and_css_hash(self):
        proc = run(str(FIX / "090-leftover.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_url"], ["yes"])
        self.assertEqual(rows["leftover_css_hash"], ["yes"])
        self.assertEqual(rows["leftover"], ["yes"])

    def test_case_a_fresh(self):
        proc = run(str(FIX / "090-fresh.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_url"], ["no"])
        self.assertEqual(rows["leftover"], ["no"])

    def test_case_b_css_moved_url_ok(self):
        proc = run(str(FIX / "090-css-only.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_url"], ["no"])
        self.assertEqual(rows["leftover_css_hash"], ["no"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("cssleft:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
