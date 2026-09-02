#!/usr/bin/env python3
from __future__ import annotations
import importlib.machinery, importlib.util, json, subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "falseomit"
FIX = ROOT / "fixtures"

def load_mod():
    loader = importlib.machinery.SourceFileLoader("falseomit_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod

FO = load_mod()

def rows(text):
    out = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, *rest = line.split("\t")
        out[k] = rest
    return out

class FalseomitTests(unittest.TestCase):
    def test_owned(self):
        a = json.loads((FIX/"a.json").read_text())
        b = json.loads((FIX/"b.json").read_text())
        r = FO.inspect(a, b)
        self.assertEqual(r["dropped_false"], ["flag"])
        self.assertEqual(r["missing_in_a"], ["flag"])
        self.assertFalse(r["a_has"]["flag"])
        self.assertTrue(r["b_has"]["flag"])

    def test_cli_owned(self):
        p = subprocess.run([sys.executable, str(CLI), str(FIX/"a.json"), str(FIX/"b.json")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = rows(p.stdout)
        self.assertEqual(r["dropped_false"], ["flag"])
        self.assertEqual(r["missing_decoded_as"], ["true"])
        self.assertIn("flag", r["a_has"])

    def test_unseen(self):
        p = subprocess.run([sys.executable, str(CLI), str(FIX/"unseen-a.json"), str(FIX/"unseen-b.json")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = rows(p.stdout)
        self.assertEqual(r["dropped_false"], ["enabled"])

    def test_same(self):
        p = subprocess.run([sys.executable, str(CLI), str(FIX/"b.json"), str(FIX/"b.json")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        r = rows(p.stdout)
        self.assertEqual(r["dropped_false"], ["none"])

    def test_missing(self):
        p = subprocess.run([sys.executable, str(CLI), "/no/a.json", str(FIX/"b.json")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)

    def test_not_object(self):
        p = subprocess.run([sys.executable, str(CLI), str(FIX/"a.json"), str(FIX/"a.json")], input=None, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)

if __name__ == "__main__":
    unittest.main()
