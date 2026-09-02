#!/usr/bin/env python3
from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "requeue"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("requeue_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


RQ = load_mod()


def rows(text):
    out = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, *rest = line.split("\t")
        out[k] = rest
    return out


class Specimen063Tests(unittest.TestCase):
    def test_requeued_completed_and_open(self):
        text = (FIX / "063-crash.rec").read_text()
        units, order, requeued, assigned = RQ.parse_record(text, source="063")
        result = RQ.inspect(units, order, requeued, assigned)
        self.assertEqual(result["already_done"], ["test_1"])
        self.assertEqual(result["unfinished"], ["test_2"])
        self.assertEqual(result["empty_assign"], [])

    def test_cli(self):
        proc = subprocess.run([sys.executable, str(CLI), str(FIX / "063-crash.rec")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["already_done"], ["test_1"])
        self.assertEqual(r["unfinished"], ["test_2"])

    def test_unseen_all_done_empty_assign(self):
        proc = subprocess.run([sys.executable, str(CLI), str(FIX / "unseen-alldone.rec")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["already_done"], ["a", "b"])
        self.assertEqual(r["unfinished"], ["none"])
        self.assertEqual(r["empty_assign"], ["gw2"])

    def test_missing_unit(self):
        proc = subprocess.run([sys.executable, str(CLI)], input="requeued\tx\n", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
