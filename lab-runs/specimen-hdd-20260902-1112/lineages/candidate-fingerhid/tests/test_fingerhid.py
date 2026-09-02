#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "fingerhid"
FIX = ROOT / "fixtures"


def rows(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, *rest = line.split("\t")
        out[k] = rest
    return out


def run(a: str, b: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), a, b],
        capture_output=True,
        text=True,
        check=False,
    )


class Owned086(unittest.TestCase):
    def test_fc42_vs_fc40_hidden(self):
        proc = run(str(FIX / "086-fc42.rec"), str(FIX / "086-fc40.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["same_path"], ["yes"])
        self.assertEqual(r["same_mtime"], ["yes"])
        self.assertEqual(r["vv_mismatch"], ["yes"])
        self.assertEqual(r["hidden_by_fingerprint"], ["yes"])
        self.assertEqual(r["same_size"], ["no"])
        self.assertEqual(r["same_birth"], ["no"])

    def test_same_vv_not_hidden(self):
        proc = run(str(FIX / "086-fc42.rec"), str(FIX / "unseen-agree.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["hidden_by_fingerprint"], ["no"])
        self.assertEqual(r["vv_mismatch"], ["no"])
        self.assertEqual(r["same_size"], ["-"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/no", str(FIX / "086-fc40.rec"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("fingerhid:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
