#!/usr/bin/env python3
from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "armtimer"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("armtimer_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


AT = load_mod()


def rows(text):
    out = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, *rest = line.split("\t")
        out[k] = rest
    return out


class Specimen066Tests(unittest.TestCase):
    def test_starting_arms_start_interval(self):
        rec = AT.parse_record((FIX / "066-starting.rec").read_text(), source="066")
        result = AT.inspect(rec)
        self.assertEqual(result["armed"], 30)
        self.assertEqual(result["during"], "starting")
        self.assertTrue(result["late"])
        self.assertEqual(result["expected_after_period"], 2)

    def test_cli(self):
        proc = subprocess.run([sys.executable, str(CLI), str(FIX / "066-starting.rec")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["armed"], ["30"])
        self.assertEqual(r["late"], ["yes"])
        self.assertEqual(r["expected_after_period"], ["2"])

    def test_unseen_after_period(self):
        proc = subprocess.run([sys.executable, str(CLI), str(FIX / "unseen-after.rec")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["armed"], ["2"])
        self.assertEqual(r["late"], ["no"])
        self.assertEqual(r["during"], ["healthy"])

    def test_missing_field(self):
        proc = subprocess.run([sys.executable, str(CLI)], input="status\tstarting\n", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
