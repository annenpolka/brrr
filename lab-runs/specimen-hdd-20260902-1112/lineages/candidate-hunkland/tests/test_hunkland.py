#!/usr/bin/env python3
"""Insert land vs hunk-header named line; apply exit 0 can still mismatch."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "hunkland"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("hunkland_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


HL = load_mod()


def row_map(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        kind, *rest = line.split("\t")
        out[kind] = rest
    return out


def run_cli(args, *, orig_text=None, result_text=None):
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(CLI)]
        tmp_path = Path(tmp)
        if orig_text is not None:
            orig = tmp_path / "orig.txt"
            orig.write_text(orig_text, encoding="utf-8")
            cmd.append(str(orig))
        if result_text is not None:
            result = tmp_path / "result.txt"
            result.write_text(result_text, encoding="utf-8")
            cmd.append(str(result))
        cmd.extend(args)
        return subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )


class Specimen020Tests(unittest.TestCase):
    def test_owned_insert_lands_before_header(self):
        orig = (FIXTURES / "020-orig.txt").read_text(encoding="utf-8")
        result = (FIXTURES / "020-result.txt").read_text(encoding="utf-8")
        report = HL.inspect(orig, result, "@@ -2,0 +3 @@", apply_exit=0)
        self.assertEqual(report["header"], 3)
        self.assertEqual(report["land"], 2)
        self.assertEqual(report["header_line"], "second")
        self.assertEqual(report["land_line"], "inserted")
        self.assertEqual(report["apply_exit"], 0)
        self.assertFalse(report["match"])
        self.assertEqual(report["verdict"], "mis-indexed")

    def test_cli_020_mismatch_with_exit_0(self):
        proc = run_cli(
            ["--hunk", "@@ -2,0 +3 @@", "--apply-exit", "0"],
            orig_text="first\nsecond\nthird\n",
            result_text="first\ninserted\nsecond\nthird\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["header"], ["3"])
        self.assertEqual(rows["land"], ["2"])
        self.assertEqual(rows["header_line"], ["second"])
        self.assertEqual(rows["land_line"], ["inserted"])
        self.assertEqual(rows["apply_exit"], ["0"])
        self.assertEqual(rows["match"], ["no"])
        self.assertEqual(rows["verdict"], ["mis-indexed"])

    def test_aligned_insert_matches_header(self):
        orig = (FIXTURES / "020-orig.txt").read_text(encoding="utf-8")
        result = (FIXTURES / "020-aligned.txt").read_text(encoding="utf-8")
        report = HL.inspect(orig, result, "@@ -2,0 +3 @@")
        self.assertEqual(report["header"], 3)
        self.assertEqual(report["land"], 3)
        self.assertEqual(report["header_line"], "inserted")
        self.assertEqual(report["land_line"], "inserted")
        self.assertTrue(report["match"])
        self.assertEqual(report["verdict"], "aligned")


class UnseenTests(unittest.TestCase):
    def test_empty_range_on_line_3_lands_early(self):
        orig = (FIXTURES / "unseen-orig.txt").read_text(encoding="utf-8")
        result = (FIXTURES / "unseen-result.txt").read_text(encoding="utf-8")
        report = HL.inspect(orig, result, "@@ -3,0 +4 @@", apply_exit=0)
        self.assertEqual(report["header"], 4)
        self.assertEqual(report["land"], 3)
        self.assertEqual(report["header_line"], "gamma")
        self.assertEqual(report["land_line"], "mid")
        self.assertFalse(report["match"])
        self.assertEqual(report["apply_exit"], 0)
        self.assertEqual(report["verdict"], "mis-indexed")

    def test_cli_unseen(self):
        proc = run_cli(
            ["--hunk", "@@ -3,0 +4 @@"],
            orig_text="alpha\nbeta\ngamma\ndelta\n",
            result_text="alpha\nbeta\nmid\ngamma\ndelta\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["header"], ["4"])
        self.assertEqual(rows["land"], ["3"])
        self.assertEqual(rows["match"], ["no"])


class ParseAndErrorTests(unittest.TestCase):
    def test_hunk_with_counts_and_plus_line(self):
        old_start, old_count, header, new_count = HL.parse_hunk(
            "@@ -2,0 +3,1 @@ +inserted"
        )
        self.assertEqual((old_start, old_count, header, new_count), (2, 0, 3, 1))

    def test_missing_result(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                str(FIXTURES / "020-orig.txt"),
                "/no/such/result",
                "--hunk",
                "@@ -2,0 +3 @@",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("hunkland:", proc.stderr)

    def test_bad_hunk(self):
        proc = run_cli(
            ["--hunk", "not a hunk"],
            orig_text="a\n",
            result_text="b\n",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("hunk header", proc.stderr)

    def test_no_insert(self):
        report = HL.inspect("a\nb\n", "a\nb\n", "@@ -2,0 +3 @@")
        self.assertIsNone(report["land"])
        self.assertFalse(report["match"])
        self.assertEqual(report["verdict"], "no-insert")
        self.assertEqual(report["land_line"], "none")


class ApplierTests(unittest.TestCase):
    def test_owned_applier_lands_before_header(self):
        proc = run_cli(
            [
                "--applier",
                str(FIXTURES / "patch_insert.py"),
                "--hunk",
                "@@ -2,0 +3 @@",
                "--insert",
                "inserted",
            ],
            orig_text="first\nsecond\nthird\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["header"], ["3"])
        self.assertEqual(rows["land"], ["2"])
        self.assertEqual(rows["header_line"], ["second"])
        self.assertEqual(rows["land_line"], ["inserted"])
        self.assertEqual(rows["apply_exit"], ["0"])
        self.assertEqual(rows["verdict"], ["mis-indexed"])

    def test_zero_start_empty_range_inserts_before_last(self):
        proc = run_cli(
            [
                "--applier",
                str(FIXTURES / "patch_insert.py"),
                "--hunk",
                "@@ -0,0 +1 @@",
            ],
            orig_text="first\nsecond\nthird\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        # apply_hunk uses idx = old_start - 1; insert(-1) is before the last line.
        self.assertEqual(rows["header"], ["1"])
        self.assertEqual(rows["land"], ["3"])
        self.assertEqual(rows["header_line"], ["first"])
        self.assertEqual(rows["land_line"], ["inserted"])
        self.assertEqual(rows["match"], ["no"])
        self.assertEqual(rows["verdict"], ["mis-indexed"])

    def test_unseen_applier_line_3(self):
        proc = run_cli(
            [
                "--applier",
                str(FIXTURES / "patch_insert.py"),
                "--hunk",
                "@@ -3,0 +4 @@",
                "--insert",
                "mid",
            ],
            orig_text="alpha\nbeta\ngamma\ndelta\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["header"], ["4"])
        self.assertEqual(rows["land"], ["3"])
        self.assertEqual(rows["verdict"], ["mis-indexed"])

    def test_result_and_applier_rejected(self):
        proc = run_cli(
            [
                "--applier",
                str(FIXTURES / "patch_insert.py"),
                "--hunk",
                "@@ -2,0 +3 @@",
            ],
            orig_text="first\nsecond\nthird\n",
            result_text="first\ninserted\nsecond\nthird\n",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("RESULT or --applier", proc.stderr)

    def test_missing_applier(self):
        proc = run_cli(
            ["--applier", "/no/such/apply.py", "--hunk", "@@ -2,0 +3 @@"],
            orig_text="first\nsecond\nthird\n",
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("hunkland:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
