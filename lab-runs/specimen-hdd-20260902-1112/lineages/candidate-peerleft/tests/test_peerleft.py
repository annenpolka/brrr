#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "peerleft"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class PeerLeftTests(unittest.TestCase):
    def test_owned_leftover_packages_identity(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                str(FIX / "082-never.rec"),
                str(FIX / "082-after-remove.rec"),
                "--name",
                "no-deps",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["packages_a"], ["no"])
        self.assertEqual(rows["packages_b"], ["yes"])
        self.assertEqual(rows["mentioned_a"], ["yes"])
        self.assertEqual(rows["mentioned_b"], ["yes"])
        self.assertEqual(rows["leftover_identity"], ["yes"])

    def test_unseen_widget(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                str(FIX / "unseen-never.rec"),
                str(FIX / "unseen-after.rec"),
                "--name",
                "widget",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_identity"], ["yes"])

    def test_same_never_is_not_leftover(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                str(FIX / "082-never.rec"),
                str(FIX / "082-never.rec"),
                "--name",
                "no-deps",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_identity"], ["no"])


if __name__ == "__main__":
    unittest.main()
