#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "fingerid"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


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
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["same_path"], ["yes"])
        self.assertEqual(rows["same_mtime"], ["yes"])
        self.assertEqual(rows["same_vv"], ["no"])
        self.assertEqual(rows["fingerprint_same"], ["yes"])
        self.assertEqual(rows["hidden_by_fingerprint"], ["yes"])

    def test_same_file_not_hidden(self):
        proc = run(str(FIX / "086-fc42.rec"), str(FIX / "086-fc42.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["hidden_by_fingerprint"], ["no"])


class Unseen(unittest.TestCase):
    def test_size_does_not_break_fingerprint(self):
        proc = run(str(FIX / "086-fc42.rec"), str(FIX / "unseen-size.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["same_size"], ["no"])
        self.assertEqual(rows["fingerprint_same"], ["yes"])
        self.assertEqual(rows["hidden_by_fingerprint"], ["yes"])

    def test_missing(self):
        proc = run("/nope", str(FIX / "086-fc40.rec"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("fingerid:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
