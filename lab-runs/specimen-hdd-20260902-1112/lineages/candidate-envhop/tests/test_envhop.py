#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "envhop"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class EnvHopTests(unittest.TestCase):
    def test_owned_hyphen_dropped(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "068-before.env"), str(FIX / "068-after.env")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["invalid_posix"], ["TEST-VAR"])
        self.assertEqual(rows["dropped"], ["TEST-VAR"])
        self.assertEqual(rows["dropped_invalid"], ["TEST-VAR"])
        self.assertEqual(rows["survived_invalid"], ["none"])
        self.assertEqual(rows["kept"], ["PATH", "HOME"])

    def test_unseen_survived_invalid(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "unseen-before.env"), str(FIX / "unseen-after.env")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["invalid_posix"], ["INPUT-FOO"])
        self.assertEqual(rows["dropped_invalid"], ["none"])
        self.assertEqual(rows["survived_invalid"], ["INPUT-FOO"])

    def test_missing_file(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), "/no/env", str(FIX / "068-after.env")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
