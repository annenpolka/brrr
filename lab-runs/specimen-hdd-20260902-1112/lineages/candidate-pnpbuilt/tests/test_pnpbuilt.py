#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "pnpbuilt"
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


class Owned089(unittest.TestCase):
    def test_leftover_after_unplug_delete(self):
        proc = run(str(FIX / "089-leftover.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_built"], ["yes"])
        self.assertEqual(rows["identity"], ["leftover-built"])

    def test_intact_built(self):
        proc = run(str(FIX / "089-built.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_built"], ["no"])

    def test_never_built(self):
        proc = run(str(FIX / "089-never.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["identity"], ["never-built"])


class Extra(unittest.TestCase):
    def test_missing(self):
        proc = run("/nope")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("pnpbuilt:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
