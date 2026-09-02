#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "catleft"
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


class Owned100(unittest.TestCase):
    def test_case_b_leftover(self):
        proc = run(str(FIX / "100-leftover.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_detach"], ["yes"])

    def test_case_a_joined(self):
        proc = run(str(FIX / "100-joined.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_detach"], ["no"])

    def test_both_moved(self):
        proc = run(str(FIX / "100-moved.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_detach"], ["no"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("catleft:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
