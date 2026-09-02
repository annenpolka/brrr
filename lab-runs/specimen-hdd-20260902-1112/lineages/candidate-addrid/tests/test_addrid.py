#!/usr/bin/env python3
"""pointer address in a done-set can name a different lock node later."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "addrid"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("addrid_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


AD = load_mod()


def parse_rows(text: str) -> dict[str, list[list[str]]]:
    rows: dict[str, list[list[str]]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows.setdefault(name, []).append(rest)
    return rows


class Specimen070Tests(unittest.TestCase):
    def test_reused_address_skips_new_name(self):
        text = (FIX / "070-reuse.rec").read_text()
        inserts, workers, fetched = AD.parse_record(text, source="070")
        result = AD.inspect(inserts, workers, fetched)
        self.assertEqual(len(result["reused"]), 1)
        self.assertEqual(result["reused"][0]["addr"], "0xa")
        self.assertEqual(result["reused"][0]["was"], "flake-utils")
        self.assertEqual(result["reused"][0]["now"], "naersk")
        self.assertIn("naersk", result["skipped"])
        self.assertNotIn("flake-utils", result["skipped"])

    def test_cli_owned(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "070-reuse.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        reused = rows["reused"][0]
        self.assertEqual(reused[0], "0xa")
        self.assertEqual(reused[2], "flake-utils")
        self.assertEqual(reused[4], "naersk")
        self.assertIn("naersk", rows["skipped"][0])

    def test_unseen_stable_no_reuse(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "unseen-stable.rec")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["reused"][0], ["none"])
        self.assertEqual(rows["skipped"][0], ["none"])

    def test_missing_insert_errors(self):
        proc = subprocess.run(
            [sys.executable, str(CLI)],
            input="fetched\ta\n",
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing insert", proc.stderr)


if __name__ == "__main__":
    unittest.main()
