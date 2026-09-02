#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "refkey"
FIX = ROOT / "fixtures"

def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows

def run(path: str):
    return subprocess.run([sys.executable, str(CLI), path], capture_output=True, text=True, check=False)

class Owned097(unittest.TestCase):
    def test_case_b_leftover(self):
        proc = run(str(FIX / "097-leftover.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_ref"], ["yes"])
    def test_case_a_nokeep(self):
        proc = run(str(FIX / "097-nokeep.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_ref"], ["no"])
    def test_case_d_split(self):
        proc = run(str(FIX / "097-split.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_ref"], ["no"])

class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refkey:", proc.stderr)

if __name__ == "__main__":
    unittest.main()
