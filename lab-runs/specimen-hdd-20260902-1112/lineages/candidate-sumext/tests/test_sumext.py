#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "sumext"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run(payload: str, module: str, version: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(CLI), payload, "--module", module, "--version", version]
    return subprocess.run(args, input=stdin, capture_output=True, text=True, check=False)


class Owned084(unittest.TestCase):
    def test_leftover_bad_is_extension_only(self):
        proc = run(str(FIX / "084-leftover.rec"), "golang.org/x/bad", "v1.0.0")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["in_record"], ["no"])
        self.assertEqual(rows["in_extension"], ["yes"])
        self.assertEqual(rows["leftover_identity"], ["yes"])

    def test_good_in_record_is_not_leftover(self):
        proc = run(str(FIX / "084-leftover.rec"), "golang.org/x/good", "v1.0.0")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["in_record"], ["yes"])
        self.assertEqual(rows["in_extension"], ["no"])
        self.assertEqual(rows["leftover_identity"], ["no"])

    def test_honest_sampler_in_record(self):
        proc = run(str(FIX / "084-honest.rec"), "rsc.io/sampler", "v1.3.0")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["in_record"], ["yes"])
        self.assertEqual(rows["leftover_identity"], ["no"])


class Unseen(unittest.TestCase):
    def test_both_regions_not_leftover(self):
        proc = run(str(FIX / "unseen-both.rec"), "example.com/m", "v0.1.0")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_identity"], ["no"])

    def test_missing_is_not_leftover(self):
        proc = run(str(FIX / "084-leftover.rec"), "example.com/missing", "v0.0.1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["leftover_identity"], ["no"])
        self.assertEqual(rows["in_record"], ["no"])
        self.assertEqual(rows["in_extension"], ["no"])

    def test_stdin(self):
        text = (FIX / "084-leftover.rec").read_text()
        proc = run("-", "golang.org/x/bad", "v1.0.0", stdin=text)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["leftover_identity"], ["yes"])

    def test_missing_file(self):
        proc = run("/no/such.rec", "golang.org/x/bad", "v1.0.0")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("sumext:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
