#!/usr/bin/env python3
import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "platident"
FIX = ROOT / "fixtures"

def rows(text):
    out = {}
    for line in text.splitlines():
        if "\t" not in line: continue
        k,*r = line.split("\t"); out[k]=r
    return out

class T(unittest.TestCase):
    def test_owned(self):
        p=subprocess.run([sys.executable,str(CLI),str(FIX/"074-nokogiri.rec")],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        r=rows(p.stdout)
        self.assertEqual(r["hidden_by_exit0"],["yes"])
        self.assertEqual(r["identity_mismatch"],["yes"])
        self.assertEqual(r["same_name_version"],["yes"])
        self.assertEqual(r["install_platform"],["ruby"])
        self.assertEqual(r["lookup_platform"],["x86_64-linux"])
    def test_agree(self):
        p=subprocess.run([sys.executable,str(CLI),str(FIX/"agree.rec")],capture_output=True,text=True)
        r=rows(p.stdout)
        self.assertEqual(r["hidden_by_exit0"],["no"])
        self.assertEqual(r["identity_mismatch"],["no"])
    def test_missing(self):
        p=subprocess.run([sys.executable,str(CLI),"/no"],capture_output=True,text=True)
        self.assertEqual(p.returncode,1)
if __name__=="__main__":
    unittest.main()
