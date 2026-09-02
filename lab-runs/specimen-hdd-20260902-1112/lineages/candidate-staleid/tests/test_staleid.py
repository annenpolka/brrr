#!/usr/bin/env python3
import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CLI, FIX = ROOT/"staleid", ROOT/"fixtures"

def rows(text):
    out={}
    for line in text.splitlines():
        if "\t" not in line: continue
        k,*r=line.split("\t"); out[k]=r
    return out

class T(unittest.TestCase):
    def test_owned(self):
        p=subprocess.run([sys.executable,str(CLI),str(FIX/"075-first.rec"),str(FIX/"075-second.rec")],capture_output=True,text=True)
        self.assertEqual(p.returncode,1,p.stderr)
        r=rows(p.stdout)
        self.assertEqual(r["stale_binary"],["yes"])
        self.assertEqual(r["key_includes_buildid"],["no"])
        self.assertEqual(r["same_key"],["yes"])
    def test_includes(self):
        p=subprocess.run([sys.executable,str(CLI),str(FIX/"075-first.rec"),str(FIX/"includes-second.rec")],capture_output=True,text=True)
        r=rows(p.stdout)
        self.assertEqual(r["same_key"],["no"])
        self.assertEqual(r["key_includes_buildid"],["yes"])
        self.assertEqual(r["stale_binary"],["no"])
        self.assertEqual(p.returncode,0)
    def test_missing(self):
        p=subprocess.run([sys.executable,str(CLI),"/no",str(FIX/"075-second.rec")],capture_output=True,text=True)
        self.assertEqual(p.returncode,1)
if __name__=="__main__":
    unittest.main()
