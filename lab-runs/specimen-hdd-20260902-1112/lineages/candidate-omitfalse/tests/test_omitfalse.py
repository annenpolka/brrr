#!/usr/bin/env python3
from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "omitfalse"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("omitfalse_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


OF = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class OmitFalseTests(unittest.TestCase):
    def test_owned_a_omits_false(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "a.json"), str(FIX / "b.json"), "--key", "flag"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["a_has"], ["no"])
        self.assertEqual(rows["b_has"], ["yes"])
        self.assertEqual(rows["b_value"], ["false"])
        self.assertEqual(rows["omitted"], ["a"])
        self.assertEqual(rows["downstream_missing"], ["true"])
        self.assertEqual(rows["disagree"], ["yes"])

    def test_unseen_debug_key(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), str(FIX / "unseen-a.json"), str(FIX / "unseen-b.json"), "--key", "debug"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["omitted"], ["a"])
        self.assertEqual(rows["b_value"], ["false"])

    def test_bad_json(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), "/dev/null", str(FIX / "b.json")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
