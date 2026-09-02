#!/usr/bin/env python3
"""|| echo swallows a nonzero; && success does not."""

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
CLI = ROOT / "swallowecho"
HIDE = ROOT / "hidestatus"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("swallowecho_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


SE = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        key, *rest = line.split("\t")
        rows[key] = rest
    return rows


def run_cli(args, *, file_text=None, exe=None):
    cmd = [sys.executable, str(exe or CLI)]
    with tempfile.TemporaryDirectory() as tmp:
        if file_text is not None:
            path = Path(tmp) / "snippet.sh"
            path.write_text(file_text, encoding="utf-8")
            cmd.extend(["--file", str(path)])
        cmd.extend(args)
        return subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            env=os.environ.copy(),
        )


class FalseOrEchoTests(unittest.TestCase):
    def test_false_or_echo_ok_swallows_false_step_0(self):
        proc = run_cli(["false || echo ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["yes"])
        self.assertEqual(rows["step_status"], ["0"])
        self.assertEqual(rows["swallowed"], ["false"])
        self.assertEqual(rows["swallowed_status"], ["1"])
        self.assertEqual(rows["hid_by"], ["echo ok"])
        self.assertEqual(rows["hid_status"], ["0"])
        self.assertEqual(rows["operator"], ["||"])

    def test_module_false_or_echo(self):
        result = SE.analyze(SE.parse_snippet("false || echo ok"))
        self.assertTrue(result.swallow)
        self.assertEqual(result.step_status, 0)
        self.assertEqual(result.swallows[-1].command, "false")
        self.assertEqual(result.swallows[-1].status, 1)
        self.assertEqual(result.swallows[-1].hid_by, "echo ok")


class TrueAndEchoTests(unittest.TestCase):
    def test_true_and_echo_ok_no_swallow(self):
        proc = run_cli(["true && echo ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["0"])
        self.assertNotIn("swallowed", rows)

    def test_module_true_and_echo(self):
        result = SE.analyze(SE.parse_snippet("true && echo ok"))
        self.assertFalse(result.swallow)
        self.assertEqual(result.step_status, 0)


class ArgvListTests(unittest.TestCase):
    def test_argv_false_or_echo(self):
        proc = run_cli(["--", "false", "||", "echo", "ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["yes"])
        self.assertEqual(rows["swallowed"], ["false"])
        self.assertEqual(rows["step_status"], ["0"])

    def test_argv_true_and_echo(self):
        proc = run_cli(["--", "true", "&&", "echo", "ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["0"])


class NeighboringCasesTests(unittest.TestCase):
    def test_false_and_echo_skips_right_no_swallow(self):
        proc = run_cli(["false && echo ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["1"])
        self.assertEqual(rows["skip"], ["echo ok", "left_failed"])

    def test_true_or_echo_skips_right_no_swallow(self):
        proc = run_cli(["true || echo ok"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["0"])
        self.assertEqual(rows["skip"], ["echo ok", "left_succeeded"])

    def test_false_or_false_later_did_not_succeed(self):
        proc = run_cli(["false || false"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["1"])

    def test_semicolon_last_status_is_not_or_swallow(self):
        proc = run_cli(["false; echo ok"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["0"])

    def test_set_e_false_or_echo_still_swallows(self):
        proc = run_cli(["set -e; false || echo ok"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["yes"])
        self.assertEqual(rows["step_status"], ["0"])
        self.assertEqual(rows["swallowed"], ["false"])

    def test_set_e_false_semicolon_aborts_before_echo(self):
        proc = run_cli(["set -e; false; echo ok"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["1"])
        self.assertNotIn("skip", rows)
        ran = [line.split("\t") for line in proc.stdout.splitlines() if line.startswith("ran\t")]
        commands = [row[1] for row in ran]
        self.assertIn("false", commands)
        self.assertNotIn("echo ok", commands)


class RecordedStatusTests(unittest.TestCase):
    def test_recorded_failing_left_of_echo(self):
        proc = run_cli(
            [
                "--status",
                "1",
                "bazel test //... || echo Please run ./regenerate_stale_files.sh",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["yes"])
        self.assertEqual(rows["step_status"], ["0"])
        self.assertEqual(rows["swallowed"], ["bazel test //..."])
        self.assertEqual(rows["swallowed_status"], ["1"])
        self.assertTrue(rows["hid_by"][0].startswith("echo "))
        self.assertEqual(rows["recorded"], ["bazel test //...", "1"])

    def test_missing_status_is_clean_error(self):
        proc = run_cli(["bazel test //... || echo please"])
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("no status for: bazel test //...", proc.stderr)
        self.assertIn("--status", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertFalse(proc.stdout.strip())


class FileAndErrorTests(unittest.TestCase):
    def test_file_snippet(self):
        proc = run_cli([], file_text="false || echo ok\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["swallow"], ["yes"])

    def test_missing_file(self):
        proc = run_cli(["--file", "/no/such/swallowecho.sh"])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("file not found", proc.stderr)
        self.assertNotIn("Errno", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_empty_snippet(self):
        proc = run_cli(["   "])
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("empty command", proc.stderr)


SPECIMEN_043_BASH = (
    "set -ex; if [[ -z $COMMIT_TRIGGERED_RUN || -z $MAIN_RUN ]]; then "
    "bazel query 'attr(tags, \"staleness_test\", //...)' | "
    "xargs bazel test $BAZEL_FLAGS || "
    "echo \"Please run ./regenerate_stale_files.sh to regenerate stale files\"; "
    "else bazel query 'attr(tags, \"staleness_test\", //...)'; fi"
)


class BracketOrIsNotCommandSwallowTests(unittest.TestCase):
    def test_double_bracket_or_is_not_swallow(self):
        proc = run_cli(
            [
                "--no-process-env",
                "[[ -z $COMMIT_TRIGGERED_RUN || -z $MAIN_RUN ]]",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["0"])
        self.assertNotIn("swallowed", rows)

    def test_bracket_false_when_both_set(self):
        proc = run_cli(
            [
                "--no-process-env",
                "--env",
                "COMMIT_TRIGGERED_RUN=1",
                "--env",
                "MAIN_RUN=1",
                "[[ -z $COMMIT_TRIGGERED_RUN || -z $MAIN_RUN ]]",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["1"])


class Specimen043Tests(unittest.TestCase):
    def test_full_workflow_bash_swallows_bazel_pipeline(self):
        proc = run_cli(
            [
                "--no-process-env",
                "--unset",
                "COMMIT_TRIGGERED_RUN",
                "--unset",
                "MAIN_RUN",
                "--status",
                "1",
                SPECIMEN_043_BASH,
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["yes"])
        self.assertEqual(rows["step_status"], ["0"])
        self.assertIn("xargs bazel test", rows["swallowed"][0])
        self.assertIn("regenerate_stale_files.sh", rows["hid_by"][0])
        self.assertNotIn("-z $MAIN_RUN", rows.get("swallowed", [""])[0])

    def test_commit_on_main_else_branch_no_swallow(self):
        proc = run_cli(
            [
                "--no-process-env",
                "--env",
                "COMMIT_TRIGGERED_RUN=1",
                "--env",
                "MAIN_RUN=1",
                "--status",
                "0",
                SPECIMEN_043_BASH,
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["no"])
        self.assertEqual(rows["step_status"], ["0"])

    def test_v1_misparse_needed_a_second_status_before_grouping(self):
        # After [[ grouping, one --status is enough for the bazel pipeline.
        proc = run_cli(["--no-process-env", "--status", "1", SPECIMEN_043_BASH])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["swallow"], ["yes"])


class UnseenOrTrueTests(unittest.TestCase):
    def test_make_or_true_swallows_make(self):
        proc = run_cli(["--status", "1", "make test || true"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["yes"])
        self.assertEqual(rows["swallowed"], ["make test"])
        self.assertEqual(rows["hid_by"], ["true"])
        self.assertEqual(rows["step_status"], ["0"])


class HideStatusAliasTests(unittest.TestCase):
    def test_hidestatus_alias_same_swallow(self):
        if not HIDE.exists():
            self.skipTest("hidestatus symlink not created yet")
        proc = run_cli(["false || echo ok"], exe=HIDE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["swallow"], ["yes"])
        self.assertEqual(rows["swallowed"], ["false"])
        self.assertEqual(rows["step_status"], ["0"])


if __name__ == "__main__":
    unittest.main()
