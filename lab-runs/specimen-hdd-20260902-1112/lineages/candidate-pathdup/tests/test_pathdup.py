#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pathdup"
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


class Owned091(unittest.TestCase):
    def test_dotdot_leftover(self):
        proc = run(str(FIX / "091-dotdot.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_dotdot"], ["yes"])
        self.assertEqual(rows["same_after_collapse"], ["yes"])
        self.assertEqual(rows["true_clash"], ["no"])

    def test_clean_one_spelling(self):
        proc = run(str(FIX / "091-clean.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["lexical_dup"], ["no"])
        self.assertEqual(rows["leftover_dotdot"], ["no"])

    def test_true_clash(self):
        proc = run(str(FIX / "091-clash.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["true_clash"], ["yes"])
        self.assertEqual(rows["leftover_dotdot"], ["no"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("pathdup:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
