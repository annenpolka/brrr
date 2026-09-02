#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "patchid"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run(path: str, selector: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(CLI), path, "--selector", selector]
    return subprocess.run(args, input=stdin, capture_output=True, text=True, check=False)


class Owned085(unittest.TestCase):
    def test_object_is_path_hash(self):
        proc = run(str(FIX / "patcheddeps.object.yaml"), "express@4.18.1")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["kind"], ["object"])
        self.assertEqual(rows["has_path"], ["yes"])
        self.assertEqual(rows["has_hash"], ["yes"])
        self.assertEqual(rows["hash"], ["fixture-patch-hash"])

    def test_hash_only(self):
        proc = run(str(FIX / "patcheddeps.hash.yaml"), "express@4.18.1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["kind"], ["hash-only"])
        self.assertEqual(rows["has_path"], ["no"])
        self.assertEqual(rows["hash"], ["fixture-patch-hash"])

    def test_omitted(self):
        proc = run(str(FIX / "patcheddeps.hash.yaml"), "missing@1.0.0")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["kind"], ["omitted"])


class Unseen(unittest.TestCase):
    def test_empty_string(self):
        proc = run("-", "express@4.18.1", stdin='patchedDependencies:\n  express@4.18.1: ""\n')
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["kind"], ["empty"])

    def test_missing_file(self):
        proc = run("/no/such.yaml", "express@4.18.1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("patchid:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
