#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "unusedfp"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class UnusedFpTests(unittest.TestCase):
    def test_owned_idea_nio2(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "076-first.env"), str(FIX / "076-second.env"), "--used", "path"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["used"], ["path"])
        self.assertEqual(rows["changed_unused"], ["idea.io.use.nio2"])
        self.assertEqual(rows["all_same"], ["no"])
        self.assertEqual(rows["used_same"], ["yes"])
        self.assertEqual(rows["invalidate_unused"], ["yes"])

    def test_unseen_org_gradle_project(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                str(FIX / "unseen-first.env"),
                str(FIX / "unseen-second.env"),
                "--used",
                "src",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["changed_unused"], ["ORG_GRADLE_PROJECT_value"])
        self.assertEqual(rows["invalidate_unused"], ["yes"])

    def test_missing_used(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "076-first.env"), str(FIX / "076-second.env")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
