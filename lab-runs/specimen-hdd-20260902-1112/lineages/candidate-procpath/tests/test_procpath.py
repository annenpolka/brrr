#!/usr/bin/env python3
from __future__ import annotations
import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "procpath"
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

class Owned096(unittest.TestCase):
    def test_case_b_fail(self):
        proc = run(str(FIX / "096-reactor.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["omitted_fail"], ["yes"])
    def test_case_a_local(self):
        proc = run(str(FIX / "096-local.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["omitted_fail"], ["no"])
    def test_case_c_missing(self):
        proc = run(str(FIX / "096-missing.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["reactor_present"], ["no"])

class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("procpath:", proc.stderr)

if __name__ == "__main__":
    unittest.main()
