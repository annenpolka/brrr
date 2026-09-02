#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "narleftover"
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


class Owned092(unittest.TestCase):
    def test_poison_leftover(self):
        proc = run(str(FIX / "092-poison.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_stale_nar"], ["yes"])

    def test_fresh_consistent(self):
        proc = run(str(FIX / "092-fresh.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_stale_nar"], ["no"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("narleftover:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
