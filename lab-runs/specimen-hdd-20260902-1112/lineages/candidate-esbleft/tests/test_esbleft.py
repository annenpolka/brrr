#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "esbleft"
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


class Owned093(unittest.TestCase):
    def test_case_b_leftover(self):
        proc = run(str(FIX / "093-leftover.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_uniquekey"], ["yes"])

    def test_case_a_fresh(self):
        proc = run(str(FIX / "093-fresh.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_uniquekey"], ["no"])

    def test_case_d_long(self):
        proc = run(str(FIX / "093-long.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_uniquekey"], ["yes"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("esbleft:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
