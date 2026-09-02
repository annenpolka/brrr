#!/usr/bin/env python3
"""Sorted-keys vs insertion-order labels on owned {1: 0, 0: 0} prints."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "keyorder"
FIXTURES = ROOT / "fixtures"
TWO_PRINTS = FIXTURES / "two_prints.py"


def load_mod(path: Path, name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


KO = load_mod(CLI, "keyorder_cli")
FX = load_mod(TWO_PRINTS, "two_prints_fixture")


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    displays: list[list[str]] = []
    for line in text.splitlines():
        if not line:
            continue
        kind, *rest = line.split("\t")
        if kind == "display":
            displays.append(rest)
        else:
            rows[kind] = rest
    rows["_display"] = displays  # type: ignore[assignment]
    return rows


def display_map(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) >= 4 and parts[0] == "display":
            out[parts[1]] = parts[2:]
    return out


def run_cli(args, *, stdin_text=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=os.environ.copy(),
        input=stdin_text,
    )


class OwnedFixtureTests(unittest.TestCase):
    def test_fixture_prints_disagree(self):
        self.assertEqual(FX.OBJ, {1: 0, 0: 0})
        self.assertEqual(list(FX.OBJ), [1, 0])
        sorted_print = FX.print_sorted(FX.OBJ)
        insertion_print = FX.print_insertion(FX.OBJ)
        self.assertEqual(sorted_print, "{0: 0, 1: 0}")
        self.assertEqual(insertion_print, "{1: 0, 0: 0}")
        self.assertNotEqual(sorted_print, insertion_print)

    def test_inspect_labels_sorted_vs_insertion(self):
        obj = {1: 0, 0: 0}
        pretty = KO.parse_mapping(FX.print_sorted(obj))
        stored = KO.parse_mapping(FX.print_insertion(obj))
        result = KO.inspect([("pretty", pretty), ("repr", stored)], obj=obj)
        text = KO.format_rows(result)
        shown = display_map(text)
        self.assertEqual(shown["pretty"], ["{0: 0, 1: 0}", "sorted-keys"])
        self.assertEqual(shown["repr"], ["{1: 0, 0: 0}", "insertion-order"])
        rows = parse_rows(text)
        self.assertEqual(rows["disagree"], ["yes"])
        self.assertEqual(rows["same_items"], ["yes"])
        self.assertEqual(rows["reordered"], ["pretty"])
        self.assertEqual(rows["faithful"], ["repr"])
        self.assertEqual(rows["obj_keys"], ["1", "0"])
        self.assertEqual(rows["sorted_keys"], ["0", "1"])

    def test_cli_fixture_flag(self):
        proc = run_cli(["--fixture"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["pretty"][1], "sorted-keys")
        self.assertEqual(shown["repr"][1], "insertion-order")
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["disagree"], ["yes"])
        self.assertEqual(rows["reordered"], ["pretty"])
        self.assertEqual(rows["faithful"], ["repr"])

    def test_cli_file_owned_prints(self):
        proc = run_cli(
            ["--obj", "{1: 0, 0: 0}", "--file", str(FIXTURES / "two_prints.txt")]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["pretty"], ["{0: 0, 1: 0}", "sorted-keys"])
        self.assertEqual(shown["repr"], ["{1: 0, 0: 0}", "insertion-order"])

    def test_cli_file_with_obj_row(self):
        proc = run_cli(["--file", str(FIXTURES / "two_prints_obj.txt")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["obj"], ["{1: 0, 0: 0}"])
        self.assertEqual(rows["reordered"], ["pretty"])

    def test_cli_positional_two_prints(self):
        proc = run_cli(["--obj", "{1: 0, 0: 0}", "{0: 0, 1: 0}", "{1: 0, 0: 0}"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["0"][1], "sorted-keys")
        self.assertEqual(shown["1"][1], "insertion-order")


class AgreeAndUnseenTests(unittest.TestCase):
    def test_already_sorted_obj_does_not_disagree(self):
        proc = run_cli(
            ["--obj", "{0: 0, 1: 0}", "--file", str(FIXTURES / "agree.txt")]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["disagree"], ["no"])
        self.assertEqual(rows["reordered"], ["none"])
        self.assertEqual(rows["faithful"], ["pretty", "repr"])
        shown = display_map(proc.stdout)
        self.assertEqual(shown["pretty"][1], "sorted-keys")
        self.assertEqual(shown["repr"][1], "sorted-keys")

    def test_infer_insertion_without_obj(self):
        proc = run_cli(["{0: 0, 1: 0}", "{1: 0, 0: 0}"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["0"][1], "sorted-keys")
        self.assertEqual(shown["1"][1], "insertion-order")
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["disagree"], ["yes"])
        self.assertEqual(rows["reordered"], ["0"])
        self.assertEqual(rows["faithful"], ["1"])

    def test_spacing_does_not_change_order(self):
        proc = run_cli(["--obj", "{1:0,0:0}", "{0:0,1:0}", "{1:0,0:0}"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["0"][1], "sorted-keys")
        self.assertEqual(shown["1"][1], "insertion-order")

    def test_different_items_are_not_a_reorder(self):
        proc = run_cli(["--obj", "{1: 0, 0: 0}", "{0: 1, 1: 1}"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["same_items"], ["no"])
        self.assertNotIn("reordered", rows)

    def test_parse_error(self):
        proc = run_cli(["not-a-dict"])
        self.assertEqual(proc.returncode, 2)
        self.assertIn("not a mapping literal", proc.stderr)

    def test_missing_file(self):
        proc = run_cli(["--file", str(FIXTURES / "missing.txt")])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("file not found", proc.stderr)

    def test_prefixed_three_views_of_owned_dict(self):
        proc = run_cli(["--file", str(FIXTURES / "three_views.txt")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["pytest"], ["{0: 0, 1: 0}", "sorted-keys"])
        self.assertEqual(shown["note"], ["{1: 0, 0: 0}", "insertion-order"])
        self.assertEqual(shown["falsifying"], ["{0: 0, 1: 0}", "sorted-keys"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["disagree"], ["yes"])
        self.assertEqual(rows["reordered"], ["pytest", "falsifying"])
        self.assertEqual(rows["faithful"], ["note"])

    def test_cli_positional_prefixes(self):
        proc = run_cli(
            ["--obj", "{1: 0, 0: 0}", "d = {0: 0, 1: 0}", "d={1: 0, 0: 0}"]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["0"][1], "sorted-keys")
        self.assertEqual(shown["1"][1], "insertion-order")

    def test_fixture_script_output_roundtrip(self):
        produced = subprocess.run(
            [sys.executable, str(TWO_PRINTS)],
            check=True,
            capture_output=True,
            text=True,
        )
        lines = [line for line in produced.stdout.splitlines() if line]
        self.assertEqual(lines, ["{0: 0, 1: 0}", "{1: 0, 0: 0}"])
        proc = run_cli(["--obj", "{1: 0, 0: 0}", *lines])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        shown = display_map(proc.stdout)
        self.assertEqual(shown["0"][1], "sorted-keys")
        self.assertEqual(shown["1"][1], "insertion-order")


if __name__ == "__main__":
    unittest.main()
