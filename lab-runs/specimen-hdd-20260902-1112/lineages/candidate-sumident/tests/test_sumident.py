#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "sumident"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run(sumfile: str, module: str, version: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(CLI), sumfile, "--module", module, "--version", version]
    return subprocess.run(args, input=stdin, capture_output=True, text=True, check=False)


class Owned083(unittest.TestCase):
    def test_download_quote_is_mod_only(self):
        proc = run(str(FIX / "go.sum.download"), "rsc.io/quote", "v1.5.2")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mod"], ["yes"])
        self.assertEqual(rows["zip"], ["no"])
        self.assertEqual(rows["identity"], ["mod-only"])

    def test_tidy_quote_is_both(self):
        proc = run(str(FIX / "go.sum.tidy"), "rsc.io/quote", "v1.5.2")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mod"], ["yes"])
        self.assertEqual(rows["zip"], ["yes"])
        self.assertEqual(rows["identity"], ["both"])

    def test_unseen_sampler_download_mod_only(self):
        proc = run(str(FIX / "go.sum.download"), "rsc.io/sampler", "v1.3.0")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["identity"], ["mod-only"])

    def test_missing_module_is_neither(self):
        proc = run(str(FIX / "go.sum.download"), "example.com/missing", "v0.0.1")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["identity"], ["neither"])
        self.assertEqual(rows["mod"], ["no"])
        self.assertEqual(rows["zip"], ["no"])


class Extra(unittest.TestCase):
    def test_zip_only(self):
        proc = run(str(FIX / "go.sum.zip-only"), "rsc.io/quote", "v1.5.2")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["identity"], ["zip-only"])
        self.assertEqual(rows["zip"], ["yes"])
        self.assertEqual(rows["mod"], ["no"])

    def test_stdin(self):
        text = (FIX / "go.sum.tidy").read_text()
        proc = run("-", "rsc.io/quote", "v1.5.2", stdin=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["identity"], ["both"])

    def test_missing_file(self):
        proc = run("/no/such/go.sum", "rsc.io/quote", "v1.5.2")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("sumident:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
