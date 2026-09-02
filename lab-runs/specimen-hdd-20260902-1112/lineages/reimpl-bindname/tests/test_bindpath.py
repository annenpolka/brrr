#!/usr/bin/env python3
"""bindpath: leftover helper vs moved body, plus reexport and nested-def bounds."""

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
CLI = ROOT / "bindpath"

PKG_UTIL = "def parse(x):\n    return ('legacy', x)\n"
PKG_PARSE = "def parse(x):\n    return ('moved', x.strip())\n"
TEST_PARSE = (
    'import pkg_util, pkg_parse\n'
    'a = pkg_util.parse("  z  ")\n'
    'b = pkg_parse.parse("  z  ")\n'
    'print("util", a)\n'
    'print("parse", b)\n'
    'print("same_function", pkg_util.parse is pkg_parse.parse)\n'
    'print("stale_test_would_see", a[0])\n'
)


def load_mod(path: Path, name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


BP = load_mod(CLI, "bindpath_cli")


def run_cli(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=os.environ.copy(),
    )


def records(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            if current:
                rows.append(current)
                current = {}
            continue
        key, sep, value = line.partition("\t")
        if not sep:
            continue
        if key in current:
            rows.append(current)
            current = {}
        current[key] = value
    if current:
        rows.append(current)
    return rows


def write_leftover(dirpath: Path) -> None:
    (dirpath / "pkg_util.py").write_text(PKG_UTIL, encoding="utf-8")
    (dirpath / "pkg_parse.py").write_text(PKG_PARSE, encoding="utf-8")
    (dirpath / "test_parse_identity.py").write_text(TEST_PARSE, encoding="utf-8")


class LeftoverMoveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        write_leftover(self.dir)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_list_mode_two_defs_not_same(self) -> None:
        proc = run_cli(self.dir, ["-C", str(self.dir), "parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = records(proc.stdout)
        header = rows[0]
        self.assertEqual(header["name"], "parse")
        self.assertEqual(header["count"], "2")
        self.assertEqual(header["same_function"], "False")
        binds = [row for row in rows if "bind" in row]
        self.assertEqual([row["bind"] for row in binds], ["pkg_parse.parse", "pkg_util.parse"])
        by_bind = {row["bind"]: row for row in binds}
        self.assertIn("('legacy', x)", by_bind["pkg_util.parse"]["source"])
        self.assertIn("('moved', x.strip())", by_bind["pkg_parse.parse"]["source"])
        self.assertEqual(by_bind["pkg_util.parse"]["kind"], "def")
        self.assertEqual(by_bind["pkg_parse.parse"]["kind"], "def")
        self.assertEqual(by_bind["pkg_util.parse"]["runs"], "pkg_util.parse")
        self.assertEqual(by_bind["pkg_parse.parse"]["runs"], "pkg_parse.parse")

    def test_from_util_binds_legacy_body(self) -> None:
        proc = run_cli(self.dir, ["-C", str(self.dir), "--from", "pkg_util", "parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        row = records(proc.stdout)[0]
        self.assertEqual(row["query"], "from pkg_util import parse")
        self.assertEqual(row["bind"], "pkg_util.parse")
        self.assertEqual(row["runs"], "pkg_util.parse")
        self.assertEqual(row["kind"], "def")
        self.assertEqual(row["file"], "pkg_util.py")
        self.assertIn("('legacy', x)", row["source"])
        self.assertEqual(row["also"], "pkg_parse.parse")
        self.assertEqual(row["same_function"], "False")

    def test_import_parse_binds_moved_body(self) -> None:
        proc = run_cli(
            self.dir,
            ["-C", str(self.dir), "--import", "from pkg_parse import parse"],
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        row = records(proc.stdout)[0]
        self.assertEqual(row["query"], "from pkg_parse import parse")
        self.assertEqual(row["bind"], "pkg_parse.parse")
        self.assertEqual(row["runs"], "pkg_parse.parse")
        self.assertEqual(row["kind"], "def")
        self.assertEqual(row["file"], "pkg_parse.py")
        self.assertIn("('moved', x.strip())", row["source"])
        self.assertEqual(row["also"], "pkg_util.parse")
        self.assertEqual(row["same_function"], "False")

    def test_file_mode_uses_in_appearance_order(self) -> None:
        test_path = self.dir / "test_parse_identity.py"
        proc = run_cli(
            self.dir,
            ["-C", str(self.dir), "--file", str(test_path), "parse"],
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = records(proc.stdout)
        self.assertEqual(rows[0]["count"], "2")
        self.assertEqual(rows[0]["same_function"], "False")
        binds = [row for row in rows if "bind" in row]
        self.assertEqual([row["bind"] for row in binds], ["pkg_util.parse", "pkg_parse.parse"])
        self.assertIn("('legacy', x)", binds[0]["source"])
        self.assertIn("('moved', x.strip())", binds[1]["source"])

    def test_qualified_name_query(self) -> None:
        proc = run_cli(self.dir, ["-C", str(self.dir), "pkg_util.parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        row = records(proc.stdout)[0]
        self.assertEqual(row["bind"], "pkg_util.parse")
        self.assertIn("('legacy', x)", row["source"])
        self.assertEqual(row["same_function"], "False")

    def test_does_not_call_the_function(self) -> None:
        (self.dir / "pkg_util.py").write_text(
            "def parse(x):\n    raise RuntimeError('executed')\n    return ('legacy', x)\n",
            encoding="utf-8",
        )
        proc = run_cli(self.dir, ["-C", str(self.dir), "--from", "pkg_util", "parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("executed", proc.stderr)
        self.assertIn("RuntimeError('executed')", proc.stdout)


class ReexportNestedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_reexport_runs_defining_module(self) -> None:
        (self.dir / "pkg_parse.py").write_text(PKG_PARSE, encoding="utf-8")
        (self.dir / "pkg_util.py").write_text(
            "from pkg_parse import parse\n", encoding="utf-8"
        )
        proc = run_cli(self.dir, ["-C", str(self.dir), "--from", "pkg_util", "parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        row = records(proc.stdout)[0]
        self.assertEqual(row["kind"], "reexport")
        self.assertEqual(row["bind"], "pkg_util.parse")
        self.assertEqual(row["runs"], "pkg_parse.parse")
        self.assertEqual(row["file"], "pkg_parse.py")
        self.assertIn("('moved', x.strip())", row["source"])
        self.assertEqual(row["same_function"], "True")
        self.assertNotIn("also", row)

        listed = run_cli(self.dir, ["-C", str(self.dir), "parse"])
        self.assertEqual(listed.returncode, 0, listed.stderr)
        header = records(listed.stdout)[0]
        self.assertEqual(header["count"], "2")
        self.assertEqual(header["same_function"], "True")

    def test_nested_def_is_not_an_import_binding(self) -> None:
        (self.dir / "nested.py").write_text(
            "def outer():\n    def parse(x):\n        return x\n    return parse\n",
            encoding="utf-8",
        )
        (self.dir / "pkg_parse.py").write_text(PKG_PARSE, encoding="utf-8")
        proc = run_cli(self.dir, ["-C", str(self.dir), "parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        header = records(proc.stdout)[0]
        self.assertEqual(header["count"], "1")
        binds = [row for row in records(proc.stdout) if "bind" in row]
        self.assertEqual([row["bind"] for row in binds], ["pkg_parse.parse"])

    def test_assignment_alias_is_reexport(self) -> None:
        (self.dir / "pkg_parse.py").write_text(PKG_PARSE, encoding="utf-8")
        (self.dir / "pkg_util.py").write_text(
            "import pkg_parse\nparse = pkg_parse.parse\n", encoding="utf-8"
        )
        proc = run_cli(self.dir, ["-C", str(self.dir), "--from", "pkg_util", "parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        row = records(proc.stdout)[0]
        self.assertEqual(row["kind"], "reexport")
        self.assertEqual(row["runs"], "pkg_parse.parse")
        self.assertEqual(row["same_function"], "True")


class AstUnitTests(unittest.TestCase):
    def test_module_level_binds_def_and_from_import(self) -> None:
        tree = BP.ast.parse("def parse(x):\n    return x\n")
        self.assertTrue(BP.module_level_binds(tree, "parse"))
        tree = BP.ast.parse("from pkg_parse import parse\n")
        self.assertTrue(BP.module_level_binds(tree, "parse"))
        tree = BP.ast.parse("def outer():\n    def parse(x):\n        return x\n")
        self.assertFalse(BP.module_level_binds(tree, "parse"))

    def test_file_uses_attribute_and_from_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.py"
            path.write_text(
                "import pkg_util, pkg_parse\n"
                "pkg_util.parse(1)\n"
                "pkg_parse.parse(2)\n",
                encoding="utf-8",
            )
            self.assertEqual(BP.uses_in_file(str(path), "parse"), ["pkg_util", "pkg_parse"])
            path.write_text("from leftover import parse\n", encoding="utf-8")
            self.assertEqual(BP.uses_in_file(str(path), "parse"), ["leftover"])


if __name__ == "__main__":
    unittest.main()
