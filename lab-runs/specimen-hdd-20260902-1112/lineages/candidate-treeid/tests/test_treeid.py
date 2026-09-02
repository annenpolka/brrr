#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "treeid"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run(path: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), path],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class Owned088(unittest.TestCase):
    def test_filetree_omits_names_and_loads(self):
        proc = run(str(FIX / "088-filetree.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["omitted_names"], ["yes"])
        self.assertEqual(rows["load_after_add"], ["yes"])
        self.assertEqual(rows["hidden_by_omitted_names"], ["yes"])

    def test_named_collection_not_hidden(self):
        proc = run(str(FIX / "088-named.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["omitted_names"], ["no"])
        self.assertEqual(rows["hidden_by_omitted_names"], ["no"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("treeid:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
