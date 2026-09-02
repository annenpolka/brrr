#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "nilkeep"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class NilKeepTests(unittest.TestCase):
    def test_empty_map_drops_baz(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "079-empty-map.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["default"], ["empty-map"])
        self.assertEqual(rows["dropped"], ["baz"])
        self.assertEqual(rows["kept"], ["foo"])

    def test_null_default_keeps_baz(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "079-null-default.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["dropped"], ["-"])
        self.assertIn("baz", rows["kept"])
        self.assertIn("foo", rows["kept"])

    def test_unseen(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "unseen.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["dropped"], ["gone"])
        self.assertEqual(rows["kept"], ["keep"])


if __name__ == "__main__":
    unittest.main()
