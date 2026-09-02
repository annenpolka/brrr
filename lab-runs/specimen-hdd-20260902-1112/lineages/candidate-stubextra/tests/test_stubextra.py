#!/usr/bin/env python3
from __future__ import annotations
import importlib.machinery, importlib.util, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "stubextra"
FIX = ROOT / "fixtures"

def load_mod():
    loader = importlib.machinery.SourceFileLoader("stubextra_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod

ST = load_mod()

def rows(text):
    out = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, *rest = line.split("\t")
        out[k] = rest
    return out

class StubextraTests(unittest.TestCase):
    def test_owned(self):
        p = subprocess.run([sys.executable, str(CLI), str(FIX/"071-first.rec"), str(FIX/"071-second.rec")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = rows(p.stdout)
        self.assertEqual(r["leftover_stub"], ["yes"])
        self.assertEqual(r["produced_for_request"], ["no"])
        self.assertEqual(r["extra_outside_identity"], ["yes"])
        self.assertEqual(r["requested_outside"], ["out.sbom"])
        self.assertEqual(r["same_key"], ["yes"])

    def test_unseen(self):
        p = subprocess.run([sys.executable, str(CLI), str(FIX/"unseen-first.rec"), str(FIX/"unseen-second.rec")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = rows(p.stdout)
        self.assertEqual(r["leftover_stub"], ["yes"])
        self.assertEqual(r["requested_outside"], ["out.cyclonedx"])

    def test_produced(self):
        p = subprocess.run([sys.executable, str(CLI), str(FIX/"071-first.rec"), str(FIX/"produced-second.rec")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = rows(p.stdout)
        self.assertEqual(r["same_key"], ["no"])
        self.assertEqual(r["leftover_stub"], ["no"])
        self.assertEqual(r["produced_for_request"], ["yes"])

    def test_missing(self):
        p = subprocess.run([sys.executable, str(CLI), "/no/a", str(FIX/"071-second.rec")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)

if __name__ == "__main__":
    unittest.main()
