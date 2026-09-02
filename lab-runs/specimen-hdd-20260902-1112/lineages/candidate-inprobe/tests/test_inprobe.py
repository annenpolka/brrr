#!/usr/bin/env python3
from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "inprobe"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("inprobe_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


IP = load_mod()


def rows(text):
    out = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, *rest = line.split("\t")
        out[k] = rest
    return out


class Specimen065Tests(unittest.TestCase):
    def test_cgroupv2_mismatch(self):
        rec = IP.parse_record((FIX / "065-cgroupv2.rec").read_text(), source="065")
        result = IP.inspect(rec)
        self.assertFalse(result["cgroup_docker"])
        self.assertTrue(result["mountinfo_docker"])
        self.assertTrue(result["mismatch"])
        self.assertTrue(result["container"].startswith("c33988ec"))
        self.assertEqual(result["path_used"], "/workspace")

    def test_cli(self):
        proc = subprocess.run([sys.executable, str(CLI), str(FIX / "065-cgroupv2.rec")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["cgroup_docker"], ["no"])
        self.assertEqual(r["mismatch"], ["yes"])
        self.assertEqual(r["path_used"], ["/workspace"])

    def test_unseen_v1_no_mismatch(self):
        proc = subprocess.run([sys.executable, str(CLI), str(FIX / "unseen-v1.rec")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["cgroup_docker"], ["yes"])
        self.assertEqual(r["mismatch"], ["no"])
        self.assertEqual(r["container"], ["none"])

    def test_missing_cgroup(self):
        proc = subprocess.run([sys.executable, str(CLI)], input="path_used\t/x\n", capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
