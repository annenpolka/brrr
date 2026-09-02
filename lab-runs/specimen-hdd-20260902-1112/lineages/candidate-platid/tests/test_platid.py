#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "platid"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class PlatidTests(unittest.TestCase):
    def test_owned_ruby_vs_linux(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "074-installed.rec"), str(FIX / "074-lookup.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["installed"], ["nokogiri-1.18.10"])
        self.assertEqual(rows["lookup"], ["nokogiri-1.18.10-x86_64-linux"])
        self.assertEqual(rows["same_name"], ["yes"])
        self.assertEqual(rows["same_version"], ["yes"])
        self.assertEqual(rows["same_platform"], ["no"])
        self.assertEqual(rows["mismatch"], ["yes"])
        self.assertEqual(rows["hidden_by_exit0"], ["yes"])

    def test_unseen_darwin_vs_ruby(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "unseen-installed.rec"), str(FIX / "unseen-lookup.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["installed"], ["ffi-1.17.0-arm64-darwin"])
        self.assertEqual(rows["lookup"], ["ffi-1.17.0"])
        self.assertEqual(rows["mismatch"], ["yes"])
        self.assertEqual(rows["hidden_by_exit0"], ["yes"])

    def test_missing(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), "/nope", str(FIX / "074-lookup.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
