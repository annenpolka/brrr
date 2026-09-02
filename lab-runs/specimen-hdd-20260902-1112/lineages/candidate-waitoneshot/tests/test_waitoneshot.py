#!/usr/bin/env python3
"""timeout 0 visit vs wait-for-creation abort; harvest flag table."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "waitoneshot"
PY = ROOT / "waitoneshot.py"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("waitoneshot_cli", str(PY))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


WO = load_mod()


def parse_fields(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition("  ")
        if not sep:
            continue
        out[key] = value
    return out


def run_cli(args):
    return subprocess.run(
        [str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=os.environ.copy(),
    )


def find_specimen_056() -> Path | None:
    env = os.environ.get("SPECIMEN")
    if env:
        cand = Path(env)
        if (cand / "files" / "flags.txt").is_file():
            return cand
    here = ROOT
    for parent in [here, *here.parents]:
        cand = parent / "lab-runs/specimen-hdd-20260902-1112/specimens/specimen-056"
        if (cand / "files" / "flags.txt").is_file():
            return cand
    return None


class DecideTableTests(unittest.TestCase):
    def test_timeout0_wait_for_creation_true_aborts_before_visit(self):
        rec = WO.decide(0, True, "jsonpath", True)
        self.assertEqual(rec["visited"], "false")
        self.assertEqual(rec["oneshot"], "false")
        self.assertEqual(rec["abort"], "wait-for-creation-requires-timeout")
        self.assertIn("aborts before lookup", rec["reason"])

    def test_timeout0_wait_for_creation_false_oneshot_visit(self):
        rec = WO.decide(0, False, "jsonpath", True)
        self.assertEqual(rec["visited"], "true")
        self.assertEqual(rec["oneshot"], "true")
        self.assertEqual(rec["abort"], "none")
        self.assertEqual(rec["reason"], "one-shot check")

    def test_timeout0_for_delete_oneshot(self):
        rec = WO.decide(0, True, "delete", True)
        self.assertEqual(rec["visited"], "true")
        self.assertEqual(rec["oneshot"], "true")
        self.assertEqual(rec["abort"], "none")
        self.assertEqual(rec["reason"], "one-shot check")

    def test_missing_object_still_aborts_when_timeout0_creation_wait(self):
        rec = WO.decide(0, True, "jsonpath", False)
        self.assertEqual(rec["visited"], "false")
        self.assertEqual(rec["abort"], "wait-for-creation-requires-timeout")

    def test_positive_timeout_missing_is_wait_path_not_oneshot(self):
        rec = WO.decide(5, True, "jsonpath", False)
        self.assertEqual(rec["visited"], "false")
        self.assertEqual(rec["oneshot"], "false")
        self.assertEqual(rec["abort"], "none")
        self.assertEqual(rec["reason"], "would wait for creation (not executed here)")

    def test_timeout0_missing_without_creation_wait_is_oneshot_not_visited(self):
        rec = WO.decide(0, False, "jsonpath", False)
        self.assertEqual(rec["visited"], "false")
        self.assertEqual(rec["oneshot"], "true")
        self.assertEqual(rec["abort"], "none")

    def test_delete_oneshot_even_if_object_missing(self):
        rec = WO.decide(0, True, "delete", False)
        self.assertEqual(rec["visited"], "true")
        self.assertEqual(rec["oneshot"], "true")
        self.assertEqual(rec["abort"], "none")


class CliTests(unittest.TestCase):
    def test_cli_abort_before_visit(self):
        proc = run_cli(
            [
                "--timeout",
                "0",
                "--wait-for-creation",
                "true",
                "--for",
                "jsonpath",
                "--object-exists",
                "true",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["visited"], "false")
        self.assertEqual(rows["oneshot"], "false")
        self.assertEqual(rows["abort"], "wait-for-creation-requires-timeout")

    def test_cli_oneshot_when_creation_wait_disabled(self):
        proc = run_cli(
            [
                "--timeout",
                "0",
                "--wait-for-creation",
                "false",
                "--for",
                "jsonpath",
                "--object-exists",
                "true",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["visited"], "true")
        self.assertEqual(rows["oneshot"], "true")
        self.assertEqual(rows["abort"], "none")
        self.assertEqual(rows["reason"], "one-shot check")

    def test_cli_for_delete_oneshot(self):
        proc = run_cli(
            [
                "--timeout",
                "0",
                "--wait-for-creation",
                "true",
                "--for",
                "delete",
                "--object-exists",
                "true",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["visited"], "true")
        self.assertEqual(rows["oneshot"], "true")
        self.assertEqual(rows["abort"], "none")

    def test_cli_python_module_matches_launcher(self):
        args = ["--timeout", "0", "--wait-for-creation", "true"]
        via_py = subprocess.run(
            [sys.executable, str(PY), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        via_sh = run_cli(args)
        self.assertEqual(via_py.returncode, 0, via_py.stderr)
        self.assertEqual(via_sh.returncode, 0, via_sh.stderr)
        self.assertEqual(via_py.stdout, via_sh.stdout)

    def test_cli_default_wait_for_creation_is_true(self):
        proc = run_cli(["--timeout", "0"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["wait_for_creation"], "true")
        self.assertEqual(rows["abort"], "wait-for-creation-requires-timeout")

    def test_timeout_required(self):
        proc = run_cli([])
        self.assertNotEqual(proc.returncode, 0)


class Specimen056Tests(unittest.TestCase):
    def test_local_flags_fixture_matches_abort_row(self):
        text = (FIXTURES / "flags.txt").read_text(encoding="utf-8")
        self.assertIn("timeout=0", text)
        self.assertIn("wait_for_creation=true", text)
        rec = WO.decide(0, True, "jsonpath", True)
        self.assertEqual(rec["abort"], "wait-for-creation-requires-timeout")
        self.assertEqual(rec["visited"], "false")

    def test_owned_specimen_flags_txt_if_present(self):
        specimen = find_specimen_056()
        if specimen is None:
            self.skipTest("specimen-056 not found")
        text = (specimen / "files" / "flags.txt").read_text(encoding="utf-8")
        self.assertEqual(text.strip(), "timeout=0 wait_for_creation=true for=jsonpath exists=true")
        rec = WO.decide(0, True, "jsonpath", True)
        self.assertEqual(rec["visited"], "false")
        self.assertEqual(rec["abort"], "wait-for-creation-requires-timeout")


if __name__ == "__main__":
    unittest.main()
