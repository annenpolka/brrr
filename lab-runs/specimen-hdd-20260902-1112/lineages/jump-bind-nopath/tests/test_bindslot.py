#!/usr/bin/env python3
"""leftover vs moved in one module; path is not identity."""

from __future__ import annotations

import ast
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bindslot"

UTIL_LEGACY = "def parse(x):\n    return ('legacy', x)\n"
PARSE_MOVED = "def parse(x):\n    return ('moved', x.strip())\n"
CONCAT = UTIL_LEGACY + "\n" + PARSE_MOVED


def load_mod():
    loader = importlib.machinery.SourceFileLoader("bindslot_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


BS = load_mod()


def parse_output(text: str) -> list[dict]:
    records: list[dict] = []
    current: dict = {}
    for line in text.splitlines():
        if not line.strip():
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition("\t")
        current[key] = value
    if current:
        records.append(current)
    return records


def source_text(repr_value: str) -> str:
    return ast.literal_eval(repr_value)


def run_cli(args, *, stdin=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
    )


def find_specimen() -> Path | None:
    env = os.environ.get("SPECIMEN")
    if env:
        cand = Path(env)
        if (cand / "files" / "pkg_util.py").is_file():
            return cand
    starts = [ROOT, Path.cwd(), Path(__file__).resolve()]
    seen: set[Path] = set()
    for start in starts:
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(start if start.is_dir() else start.parent),
                "rev-parse",
                "--show-toplevel",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            top = Path(proc.stdout.strip())
            if top not in seen:
                seen.add(top)
                cand = top / "lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013"
                if (cand / "files" / "pkg_util.py").is_file():
                    return cand
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(start if start.is_dir() else start.parent),
                "rev-parse",
                "--git-common-dir",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            common = Path(proc.stdout.strip())
            if not common.is_absolute():
                base = start if start.is_dir() else start.parent
                common = (base / common).resolve()
            parent = common.parent if common.name == ".git" else common.parent
            if parent not in seen:
                seen.add(parent)
                cand = parent / "lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013"
                if (cand / "files" / "pkg_util.py").is_file():
                    return cand
    return None


class ConcatLeftoverTests(unittest.TestCase):
    def test_concatenated_defs_are_two_slots(self):
        slots = BS.slots_for_name(CONCAT, "parse")
        self.assertEqual(len(slots), 2)
        self.assertEqual(slots[0].kind, "def")
        self.assertEqual(slots[1].kind, "def")
        self.assertIn("legacy", slots[0].source)
        self.assertIn("moved", slots[1].source)
        self.assertFalse(BS.same_function(slots))

    def test_cli_code_reports_leftover_and_runs(self):
        proc = run_cli(["parse", "--code", CONCAT])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows[0]["name"], "parse")
        self.assertEqual(rows[0]["slots"], "2")
        self.assertEqual(rows[0]["runs_slot"], "1")
        self.assertEqual(rows[0]["same_function"], "False")
        self.assertEqual(rows[1]["slot"], "0")
        self.assertEqual(rows[1]["role"], "leftover")
        self.assertIn("legacy", source_text(rows[1]["source"]))
        self.assertEqual(rows[2]["slot"], "1")
        self.assertEqual(rows[2]["role"], "runs")
        self.assertIn("moved", source_text(rows[2]["source"]))
        self.assertNotIn("file\t", proc.stdout)

    def test_concat_flags_join_files_as_one_module(self):
        with tempfile.TemporaryDirectory() as tmp:
            util = Path(tmp) / "pkg_util.py"
            moved = Path(tmp) / "pkg_parse.py"
            util.write_text(UTIL_LEGACY, encoding="utf-8")
            moved.write_text(PARSE_MOVED, encoding="utf-8")
            proc = run_cli(
                ["parse", "--concat", str(util), "--concat", str(moved)]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["slots"], "2")
            self.assertEqual(rows[1]["role"], "leftover")
            self.assertEqual(rows[2]["role"], "runs")
            self.assertIn("legacy", source_text(rows[1]["source"]))
            self.assertIn("strip", source_text(rows[2]["source"]))


class PathlessLoadTests(unittest.TestCase):
    def test_stdin_has_no_path_identity(self):
        proc = run_cli(["parse"], stdin=CONCAT)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows[0]["slots"], "2")
        self.assertEqual(rows[1]["role"], "leftover")
        self.assertEqual(rows[2]["role"], "runs")
        self.assertNotIn("file\t", proc.stdout)
        self.assertNotIn("pkg_util", proc.stdout)
        self.assertNotIn("pkg_parse", proc.stdout)

    def test_honesty_exec_without_file_binds_last_slot(self):
        mod = types.ModuleType("nopath_blob")
        self.assertFalse(hasattr(mod, "__file__"))
        exec(CONCAT, mod.__dict__)
        self.assertEqual(mod.parse("  z  "), ("moved", "z"))
        self.assertFalse(hasattr(mod, "__file__"))
        slots = BS.slots_for_name(CONCAT, "parse")
        self.assertIn("moved", slots[-1].source)
        self.assertIn("legacy", slots[0].source)

    def test_loader_origin_none_still_answers_leftover(self):
        class SrcLoader:
            def create_module(self, spec):
                return None

            def exec_module(self, module):
                exec(CONCAT, module.__dict__)

            def get_source(self, fullname):
                return CONCAT

        spec = importlib.util.spec_from_loader("blob", SrcLoader(), origin=None)
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.parse("  z  "), ("moved", "z"))
        proc = run_cli(["parse", "--code", spec.loader.get_source("blob")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows[0]["slots"], "2")
        self.assertEqual(rows[1]["role"], "leftover")


class BindingShapeTests(unittest.TestCase):
    def test_single_def_is_one_identity(self):
        proc = run_cli(["parse", "--code", UTIL_LEGACY])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows[0]["slots"], "1")
        self.assertEqual(rows[0]["same_function"], "True")
        self.assertEqual(rows[1]["role"], "runs")

    def test_leftover_def_then_reexport_import(self):
        text = UTIL_LEGACY + "from pkg_parse import parse\n"
        proc = run_cli(["parse", "--code", text])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows[0]["slots"], "2")
        self.assertEqual(rows[1]["kind"], "def")
        self.assertEqual(rows[1]["role"], "leftover")
        self.assertEqual(rows[2]["kind"], "import")
        self.assertEqual(rows[2]["from"], "pkg_parse")
        self.assertEqual(rows[2]["role"], "runs")
        self.assertEqual(rows[0]["same_function"], "False")

    def test_if_body_def_is_a_slot(self):
        text = UTIL_LEGACY + "if True:\n    def parse(x):\n        return ('moved', x.strip())\n"
        slots = BS.slots_for_name(text, "parse")
        self.assertEqual(len(slots), 2)
        self.assertIn("moved", slots[1].source)

    def test_annotation_only_is_not_a_slot(self):
        text = "from typing import Callable\nparse: Callable\n"
        proc = run_cli(["parse", "--code", text])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no slots", proc.stderr)

    def test_does_not_execute_concatenated_sibling(self):
        killer = "import sys\nsys.exit(9)\ndef parse(x):\n    return ('moved', x)\n"
        proc = run_cli(["parse", "--code", UTIL_LEGACY + "\n" + killer])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows[0]["slots"], "2")
        self.assertEqual(rows[2]["role"], "runs")


class ErrorTests(unittest.TestCase):
    def test_missing_name(self):
        proc = run_cli(["nope", "--code", UTIL_LEGACY])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no slots", proc.stderr)

    def test_syntax_error_is_visible(self):
        proc = run_cli(["parse", "--code", "def parse(x)\n    return 1\n"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("syntax error", proc.stderr)

    def test_non_utf8_is_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "blob.py"
            path.write_bytes(b"def parse(x):\n    return '\xff'\n")
            proc = run_cli(["parse", "-s", str(path)])
            self.assertEqual(proc.returncode, 1)
            self.assertIn("not utf-8", proc.stderr)

    def test_missing_file(self):
        proc = run_cli(["parse", "-s", "/no/such/bindslot-source.py"])
        self.assertEqual(proc.returncode, 1)

    def test_conflicting_source_flags(self):
        proc = run_cli(["parse", "--code", CONCAT, "-s", "-"])
        self.assertEqual(proc.returncode, 2)


class Specimen013ConcatTests(unittest.TestCase):
    def test_owned_files_concatenated(self):
        specimen = find_specimen()
        if specimen is None:
            self.skipTest("specimen-013 not found")
        util = specimen / "files" / "pkg_util.py"
        moved = specimen / "files" / "pkg_parse.py"
        proc = run_cli(["parse", "--concat", str(util), "--concat", str(moved)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows[0]["slots"], "2")
        self.assertEqual(rows[0]["same_function"], "False")
        self.assertIn("legacy", source_text(rows[1]["source"]))
        self.assertIn("moved", source_text(rows[2]["source"]))
        self.assertIn("strip", source_text(rows[2]["source"]))


if __name__ == "__main__":
    unittest.main()
