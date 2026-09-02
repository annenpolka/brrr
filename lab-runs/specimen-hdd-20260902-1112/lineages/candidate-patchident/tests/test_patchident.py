#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "patchident"
FIX = ROOT / "fixtures"


def rows(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        k, *rest = line.split("\t")
        out[k] = rest
    return out


def run(lock: str, selector: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), lock, "--selector", selector],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class Owned085(unittest.TestCase):
    def test_object_path_hash(self):
        proc = run(str(FIX / "patcheddeps.object.yaml"), "express@4.18.1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["identity"], ["object"])
        self.assertEqual(r["path"], ["patches/express@4.18.1.patch"])
        self.assertEqual(r["hash"], ["fixture-patch-hash"])
        self.assertEqual(r["legacy_dot_hash"], ["fixture-patch-hash"])

    def test_hash_only_legacy_empty(self):
        proc = run(str(FIX / "patcheddeps.hash.yaml"), "express@4.18.1")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["identity"], ["hash-only"])
        self.assertEqual(r["hash"], ["fixture-patch-hash"])
        self.assertEqual(r["legacy_dot_hash"], ["-"])
        self.assertEqual(r["path"], ["-"])

    def test_empty_string(self):
        proc = run(str(FIX / "patcheddeps.empty.yaml"), "express@4.18.1")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(rows(proc.stdout)["identity"], ["empty"])

    def test_omitted(self):
        proc = run(str(FIX / "patcheddeps.hash.yaml"), "missing-package@1.0.0")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        r = rows(proc.stdout)
        self.assertEqual(r["identity"], ["omitted"])
        self.assertEqual(r["legacy_dot_hash"], ["-"])


class Extra(unittest.TestCase):
    def test_stdin_object(self):
        text = (FIX / "patcheddeps.object.yaml").read_text()
        proc = run("-", "express@4.18.1", stdin=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(rows(proc.stdout)["identity"], ["object"])

    def test_missing_file(self):
        proc = run("/no/such.yaml", "express@4.18.1")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("patchident:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
