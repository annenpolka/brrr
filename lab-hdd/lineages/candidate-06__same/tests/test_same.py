#!/usr/bin/env python3
"""Drive the shipped `same` CLI. No imported implementation."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAME = ROOT / "same"
FIX = ROOT / "fixtures"
EMPTY_SHA = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def run(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SAME), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


class SameCLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        src = FIX / "hardlink" / "a"
        dst = FIX / "hardlink" / "b"
        if dst.exists() or dst.is_symlink():
            dst.unlink()
        os.link(src, dst)
        link = FIX / "symlink" / "link"
        if not link.is_symlink():
            if link.exists():
                link.unlink()
            os.symlink("file", link)

    def test_omit_kind_exits_1_and_lists_kinds(self) -> None:
        proc = run(str(FIX / "empty" / "a"), str(FIX / "empty" / "b"))
        self.assertEqual(proc.returncode, 1)
        combined = proc.stdout + proc.stderr
        self.assertIn("available kinds:", combined)
        self.assertIn("inode", combined)
        self.assertIn("bytes", combined)
        self.assertIn("json", combined)

    def test_two_kinds_exits_1_and_lists_kinds(self) -> None:
        proc = run("--inode", "--bytes", str(FIX / "empty" / "a"), str(FIX / "empty" / "b"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("available kinds:", proc.stdout + proc.stderr)

    def test_inode_hardlink_identical(self) -> None:
        a = FIX / "hardlink" / "a"
        b = FIX / "hardlink" / "b"
        st_a = os.lstat(a)
        st_b = os.lstat(b)
        self.assertEqual((st_a.st_dev, st_a.st_ino), (st_b.st_dev, st_b.st_ino))
        proc = run("--inode", str(a), str(b))
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.startswith("IDENTICAL inode "))
        self.assertIn(f"{st_a.st_dev}:{st_a.st_ino}", proc.stdout)

    def test_inode_two_empties_distinct(self) -> None:
        a = FIX / "empty" / "a"
        b = FIX / "empty" / "b"
        st_a = os.lstat(a)
        st_b = os.lstat(b)
        self.assertNotEqual((st_a.st_dev, st_a.st_ino), (st_b.st_dev, st_b.st_ino))
        proc = run("--inode", str(a), str(b))
        self.assertEqual(proc.returncode, 2)
        self.assertTrue(proc.stdout.startswith("DISTINCT inode "))
        self.assertIn(f"{st_a.st_dev}:{st_a.st_ino}", proc.stdout)
        self.assertIn(f"{st_b.st_dev}:{st_b.st_ino}", proc.stdout)

    def test_bytes_two_empties_identical(self) -> None:
        proc = run("--bytes", str(FIX / "empty" / "a"), str(FIX / "empty" / "b"))
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, f"IDENTICAL bytes {EMPTY_SHA}\n")

    def test_json_key_order_identical(self) -> None:
        proc = run(
            "--json",
            str(FIX / "json" / "order-ba.json"),
            str(FIX / "json" / "order-ab.json"),
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, 'IDENTICAL json {"a":2,"b":1}\n')

    def test_bytes_json_key_order_distinct(self) -> None:
        proc = run(
            "--bytes",
            str(FIX / "json" / "order-ba.json"),
            str(FIX / "json" / "order-ab.json"),
        )
        self.assertEqual(proc.returncode, 2)
        self.assertTrue(proc.stdout.startswith("DISTINCT bytes sha256:"))

    def test_bytes_symlink_follows(self) -> None:
        proc = run(
            "--bytes",
            str(FIX / "symlink" / "file"),
            str(FIX / "symlink" / "link"),
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.startswith("IDENTICAL bytes sha256:"))

    def test_inode_symlink_vs_file_distinct(self) -> None:
        file_path = FIX / "symlink" / "file"
        link_path = FIX / "symlink" / "link"
        self.assertTrue(link_path.is_symlink())
        proc = run("--inode", str(file_path), str(link_path))
        self.assertEqual(proc.returncode, 2)
        self.assertTrue(proc.stdout.startswith("DISTINCT inode "))

    def test_json_distinct_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "left.json"
            right = Path(tmp) / "right.json"
            left.write_text('{"a": 1}', encoding="utf-8")
            right.write_text('{"a": 2}', encoding="utf-8")
            proc = run("--json", str(left), str(right))
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout, 'DISTINCT json {"a":1} {"a":2}\n')

    def test_json_parse_error_exit_1(self) -> None:
        path = str(FIX / "symlink" / "file")
        proc = run("--json", path, str(FIX / "json" / "order-ab.json"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn(f"same: {path}: not JSON", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_missing_file_exit_1_no_traceback(self) -> None:
        missing = str(FIX / "no-such")
        proc = run("--bytes", str(FIX / "empty" / "a"), missing)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, f"same: {missing}: No such file or directory\n")
        self.assertNotIn("Traceback", proc.stderr + proc.stdout)

    def test_binary_vs_json_exit_1_no_traceback(self) -> None:
        blob = FIX / "binary.bin"
        proc = run("--json", str(blob), str(FIX / "json" / "order-ab.json"))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr, f"same: {blob}: not JSON (not UTF-8 text)\n")
        self.assertNotIn("Traceback", proc.stderr + proc.stdout)


if __name__ == "__main__":
    unittest.main()
