#!/usr/bin/env python3
"""silent-success add vs remaining file/dir collision; scan-cursor dependence."""

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
CLI = ROOT / "silentadd"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("silentadd_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


SA = load_mod()


def parse_rows(text: str) -> list[list[str]]:
    return [line.split("\t") for line in text.splitlines() if line]


def row_map(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    remains: list[list[str]] = []
    for row in parse_rows(text):
        if not row:
            continue
        if row[0] == "remain":
            remains.append(row)
        else:
            out[row[0]] = row[1:]
    out["_remain"] = remains  # type: ignore[assignment]
    return out


def run_cli(args, *, file_text=None, stdin_text=None):
    extra_env = os.environ.copy()
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(CLI)]
        if file_text is not None:
            path = Path(tmp) / "index.txt"
            path.write_text(file_text, encoding="utf-8")
            cmd.extend(["--file", str(path)])
        cmd.extend(args)
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            env=extra_env,
            input=stdin_text,
        )
    return proc


class Specimen014Tests(unittest.TestCase):
    def test_sibling_hides_dir_when_scan_starts_at_0(self):
        result = SA.inspect(["aaa", "blobtree/", "zzz"], "blobtree", scan="0")
        self.assertEqual(result["insert_pos"], 1)
        self.assertEqual(result["scan_start"], 0)
        self.assertEqual(result["add"], "ok")
        self.assertEqual(result["collision"], "present")
        self.assertEqual(result["remain"], [("blobtree/", "dir")])
        self.assertEqual(result["hide"], "aaa")
        self.assertEqual(result["scan0"], "miss")
        self.assertEqual(result["scan_pos"], "hit")
        self.assertEqual(result["ordered"], "yes")
        self.assertEqual(result["silent"], "yes")

    def test_scan_from_pos_finds_dir(self):
        result = SA.inspect(["aaa", "blobtree/", "zzz"], "blobtree", scan="pos")
        self.assertEqual(result["scan_start"], 1)
        self.assertEqual(result["add"], "fail")
        self.assertEqual(result["collision"], "present")
        self.assertIsNone(result["hide"])
        self.assertEqual(result["scan0"], "miss")
        self.assertEqual(result["scan_pos"], "hit")
        self.assertEqual(result["silent"], "no")

    def test_only_dir_entry_found_from_0(self):
        result = SA.inspect(["blobtree/"], "blobtree", scan="0")
        self.assertEqual(result["insert_pos"], 0)
        self.assertEqual(result["add"], "fail")
        self.assertEqual(result["silent"], "no")

    def test_cli_014_siblings(self):
        proc = run_cli(["blobtree"], file_text="aaa\nblobtree/\nzzz\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["insert_pos"], ["1"])
        self.assertEqual(rows["scan_start"], ["0"])
        self.assertEqual(rows["add"], ["ok"])
        self.assertEqual(rows["collision"], ["present"])
        self.assertEqual(rows["silent"], ["yes"])
        self.assertEqual(rows["hide"], ["aaa"])
        self.assertEqual(rows["scan0"], ["miss"])
        self.assertEqual(rows["scan_pos"], ["hit"])
        self.assertEqual(rows["ordered"], ["yes"])
        self.assertEqual(rows["_remain"], [["remain", "blobtree/", "dir"]])

    def test_cli_scan_pos(self):
        proc = run_cli(["--scan", "pos", "blobtree", "aaa", "blobtree/", "zzz"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["scan_start"], ["1"])
        self.assertEqual(rows["add"], ["fail"])
        self.assertEqual(rows["silent"], ["no"])


class UnseenAnd017Tests(unittest.TestCase):
    def test_unseen_pkg_dir_hidden_by_leading_sibling(self):
        entries = Path(FIXTURES / "unseen-pkg.txt").read_text(encoding="utf-8")
        proc = run_cli(["pkg"], file_text=entries)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["add"], ["ok"])
        self.assertEqual(rows["silent"], ["yes"])
        self.assertEqual(rows["_remain"][0][1], "pkg/__init__.py")
        self.assertNotEqual(rows["insert_pos"], ["0"])

    def test_017_extra_name_is_not_a_path_collision(self):
        result = SA.inspect(["B"], "B", scan="0")
        self.assertEqual(result["add"], "ok")
        self.assertEqual(result["collision"], "absent")
        self.assertEqual(result["remain"], [])
        self.assertEqual(result["silent"], "no")

    def test_cli_017_extra_name(self):
        proc = run_cli(["B", "B"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = row_map(proc.stdout)
        self.assertEqual(rows["collision"], ["absent"])
        self.assertEqual(rows["_remain"], [["remain", "none"]])
        self.assertEqual(rows["silent"], ["no"])


class CollisionKindTests(unittest.TestCase):
    def test_parent_file_blocks_nested_add(self):
        result = SA.inspect(["aaa", "pkg", "zzz"], "pkg/mod.py", scan="0")
        self.assertEqual(result["add"], "fail")
        self.assertEqual(result["remain"], [("pkg", "file")])
        self.assertEqual(result["silent"], "no")

    def test_no_collision(self):
        result = SA.inspect(["aaa", "zzz"], "blobtree", scan="0")
        self.assertEqual(result["add"], "ok")
        self.assertEqual(result["collision"], "absent")
        self.assertEqual(result["silent"], "no")

    def test_unsorted_is_named(self):
        result = SA.inspect(["zzz", "blobtree/", "aaa"], "blobtree", scan="0")
        self.assertEqual(result["ordered"], "no")
        self.assertEqual(result["collision"], "present")


class ErrorTests(unittest.TestCase):
    def test_missing_file(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), "--file", "/no/such/index", "blobtree"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("silentadd:", proc.stderr)

    def test_bad_scan(self):
        proc = run_cli(["--scan", "nope", "blobtree", "aaa"])
        self.assertEqual(proc.returncode, 2)
        self.assertIn("scan start", proc.stderr)

    def test_file_and_args(self):
        proc = run_cli(["--file", str(FIXTURES / "014-siblings.txt"), "blobtree", "aaa"])
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
