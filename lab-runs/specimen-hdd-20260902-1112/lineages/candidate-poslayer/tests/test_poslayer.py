#!/usr/bin/env python3
"""file expands {posargs}; CLI override keeps it literal; leftover unused."""

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
CLI = ROOT / "poslayer"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("poslayer_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


PL = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run_cli(args, *, file_text=None):
    extra_env = os.environ.copy()
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(CLI)]
        if file_text is not None:
            path = Path(tmp) / "template.txt"
            path.write_text(file_text, encoding="utf-8")
            cmd.extend(["--file", str(path)])
        cmd.extend(args)
        return subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            env=extra_env,
        )


class Specimen019Tests(unittest.TestCase):
    def test_file_expands_override_literal_leftover_missed(self):
        result = PL.inspect(
            "pytest {posargs}",
            "pytest {posargs}",
            ["tests", "src"],
        )
        self.assertEqual(result["file"], "expanded")
        self.assertEqual(result["file_argv"], ["pytest", "tests", "src"])
        self.assertEqual(result["override"], "literal")
        self.assertEqual(result["override_argv"], ["pytest", "{posargs}"])
        self.assertEqual(result["missed"], ["tests", "src"])
        self.assertEqual(result["entered"], ["file"])
        self.assertEqual(result["in_override"], [])
        self.assertEqual(result["ran_against"], "{posargs}")
        self.assertEqual(result["exit"], 0)
        self.assertEqual(result["silent"], "yes")

    def test_cli_matches_owned_fixture_argv(self):
        proc = run_cli(
            ["--file-template", "pytest {posargs}", "--", "tests", "src"]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["file"][0], "expanded")
        self.assertEqual(rows["file"][1:], ["pytest", "tests", "src"])
        self.assertEqual(rows["override"][0], "literal")
        self.assertEqual(rows["override"][1:], ["pytest", "{posargs}"])
        self.assertEqual(rows["leftover"], ["tests", "src"])
        self.assertEqual(rows["missed"], ["tests", "src"])
        self.assertEqual(rows["entered"], ["file"])
        self.assertEqual(rows["in_override"], ["-"])
        self.assertEqual(rows["ran_against"], ["{posargs}"])
        self.assertEqual(rows["exit"], ["0"])
        self.assertEqual(rows["silent"], ["yes"])

    def test_fixture_script_still_prints_literal_override(self):
        proc = subprocess.run(
            [sys.executable, str(FIXTURES / "override_subst.py")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("['pytest', 'tests', 'src']", proc.stdout)
        self.assertIn("['pytest', '{posargs}']", proc.stdout)
        self.assertIn("cli_leftover ['tests', 'src']", proc.stdout)
        self.assertIn("override_ran_against {posargs}", proc.stdout)


class FilePathTests(unittest.TestCase):
    def test_file_path_same_as_string(self):
        proc = run_cli(["--", "tests", "src"], file_text="pytest {posargs}\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["file"][0], "expanded")
        self.assertEqual(rows["override"][0], "literal")

    def test_missing_file_is_clean_error(self):
        missing = "/no/such/poslayer.tmpl"
        proc = run_cli(["--file", missing, "--", "tests"])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("file not found", proc.stderr)
        self.assertIn(missing, proc.stderr)
        self.assertNotIn("Errno", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertFalse(proc.stdout.strip())

    def test_directory_is_clean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_cli(["--file", tmp, "--", "tests"])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("is a directory", proc.stderr)
        self.assertNotIn("Errno", proc.stderr)


class UnseenTokenTests(unittest.TestCase):
    def test_packages_token_same_split(self):
        result = PL.inspect(
            "pytest {packages}",
            "pytest {packages}",
            ["pkg"],
            token="{packages}",
        )
        self.assertEqual(result["file"], "expanded")
        self.assertEqual(result["file_argv"], ["pytest", "pkg"])
        self.assertEqual(result["override"], "literal")
        self.assertEqual(result["override_argv"], ["pytest", "{packages}"])
        self.assertEqual(result["missed"], ["pkg"])
        self.assertEqual(result["ran_against"], "{packages}")

    def test_cli_unseen_token(self):
        proc = run_cli(
            [
                "--file-template",
                "pytest {packages}",
                "--token",
                "{packages}",
                "--",
                "pkg",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["file"][0], "expanded")
        self.assertEqual(rows["override"][0], "literal")
        self.assertEqual(rows["missed"], ["pkg"])


class MembershipLieTests(unittest.TestCase):
    def test_coincidental_tests_in_override_is_not_entry(self):
        """leftover 'tests' can appear as an override word without subst."""
        result = PL.inspect(
            "pytest {posargs}",
            "pytest tests {posargs}",
            ["tests", "src"],
        )
        self.assertEqual(result["override"], "literal")
        self.assertEqual(result["in_override"], ["tests"])
        self.assertEqual(result["missed"], ["tests", "src"])
        self.assertEqual(result["entered"], ["file"])
        self.assertEqual(result["silent"], "yes")

    def test_cli_coincidental_word_still_missed(self):
        proc = run_cli(
            [
                "--file-template",
                "pytest {posargs}",
                "--override",
                "pytest tests {posargs}",
                "--",
                "tests",
                "src",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["in_override"], ["tests"])
        self.assertEqual(rows["missed"], ["tests", "src"])
        self.assertEqual(rows["entered"], ["file"])
        self.assertEqual(rows["silent"], ["yes"])


class SubstOverrideTests(unittest.TestCase):
    def test_subst_override_enters_leftover(self):
        result = PL.inspect(
            "pytest {posargs}",
            "pytest {posargs}",
            ["tests", "src"],
            subst_override=True,
        )
        self.assertEqual(result["file"], "expanded")
        self.assertEqual(result["override"], "expanded")
        self.assertEqual(result["override_argv"], ["pytest", "tests", "src"])
        self.assertEqual(result["entered"], ["file", "override"])
        self.assertEqual(result["missed"], [])
        self.assertEqual(result["in_override"], ["tests", "src"])
        self.assertEqual(result["ran_against"], "src")
        self.assertEqual(result["silent"], "no")

    def test_cli_subst_override(self):
        proc = run_cli(
            [
                "--file-template",
                "pytest {posargs}",
                "--subst-override",
                "--",
                "tests",
                "src",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["override"][0], "expanded")
        self.assertEqual(rows["entered"], ["file", "override"])
        self.assertEqual(rows["missed"], ["-"])
        self.assertEqual(rows["silent"], ["no"])
        self.assertEqual(rows["ran_against"], ["src"])

    def test_override_without_token_still_misses_leftover(self):
        result = PL.inspect(
            "pytest {posargs}",
            "pytest",
            ["tests", "src"],
            subst_override=True,
        )
        self.assertEqual(result["override"], "absent")
        self.assertEqual(result["entered"], ["file"])
        self.assertEqual(result["missed"], ["tests", "src"])
        self.assertEqual(result["silent"], "no")


if __name__ == "__main__":
    unittest.main()
