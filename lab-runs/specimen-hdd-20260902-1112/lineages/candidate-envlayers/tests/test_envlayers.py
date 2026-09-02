#!/usr/bin/env python3
"""empty assignment vs unset; skip_empty keeps inherited; assign stores empty."""

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
CLI = ROOT / "envlayers"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("envlayers_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


EL = load_mod()


def parse_output(text: str) -> dict[str, str]:
    rows = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        parts = line.split("\t")
        rows[parts[0]] = parts[1]
        if len(parts) > 2:
            rows[parts[0] + "_presence"] = parts[2]
        if len(parts) > 3:
            rows[parts[0] + "_source"] = parts[3]
    return rows


def run_cli(args, *, env=None, file_text=None):
    extra_env = os.environ.copy()
    extra_env.pop("KEY", None)
    extra_env.pop("OTHER", None)
    if env:
        extra_env.update(env)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(CLI)]
        if file_text is not None:
            path = Path(tmp) / "file.env"
            path.write_text(file_text, encoding="utf-8")
            cmd.extend(["--file", str(path)])
        cmd.extend(args)
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            env=extra_env,
        )
    return proc


class EmptyVsUnsetTests(unittest.TestCase):
    def test_empty_file_assignment_is_not_unset(self):
        empty = EL.layers_for_key(
            "KEY",
            inherited={"KEY": "/x"},
            file_text="KEY=\n",
            process_env={},
        )
        missing = EL.layers_for_key(
            "KEY",
            inherited={"KEY": "/x"},
            file_text="OTHER=2\n",
            process_env={},
        )
        self.assertEqual(empty["file"], "")
        self.assertIsNone(missing["file"])
        self.assertNotEqual(empty["file"], missing["file"])
        self.assertEqual(empty["file_presence"], "empty-assignment")
        self.assertEqual(missing["file_presence"], "absent")

    def test_cli_empty_file_assignment_vs_unset(self):
        assigned = run_cli(
            ["--no-process-env", "--inherited", "KEY=/x", "KEY"],
            file_text="KEY=\n",
        )
        absent = run_cli(
            ["--no-process-env", "--inherited", "KEY=/x", "KEY"],
            file_text="OTHER=2\n",
        )
        self.assertEqual(assigned.returncode, 0, assigned.stderr)
        self.assertEqual(absent.returncode, 0, absent.stderr)
        self.assertEqual(parse_output(assigned.stdout)["file"], "''")
        self.assertEqual(parse_output(assigned.stdout)["file_presence"], "empty-assignment")
        self.assertEqual(parse_output(absent.stdout)["file"], "None")
        self.assertEqual(parse_output(absent.stdout)["file_presence"], "absent")


class SkipEmptyTests(unittest.TestCase):
    def test_skip_empty_keeps_inherited(self):
        out = EL.load_skip_empty("KEY=\nOTHER=2\n", {"KEY": "/x", "OTHER": "1"})
        self.assertEqual(out["KEY"], "/x")
        self.assertEqual(out["OTHER"], "2")

    def test_cli_skip_empty_keeps_inherited(self):
        proc = run_cli(
            ["--no-process-env", "--inherited", "KEY=/x", "--inherited", "OTHER=1", "KEY"],
            file_text="KEY=\nOTHER=2\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["inherited"], "'/x'")
        self.assertEqual(rows["skip_empty"], "'/x'")
        self.assertEqual(rows["skip_empty_source"], "inherited")


class AssignEmptyTests(unittest.TestCase):
    def test_assign_stores_empty(self):
        out = EL.load_assign("KEY=\nOTHER=2\n", {"KEY": "/x", "OTHER": "1"})
        self.assertIn("KEY", out)
        self.assertEqual(out["KEY"], "")
        self.assertEqual(out["OTHER"], "2")

    def test_cli_assign_stores_empty(self):
        proc = run_cli(
            ["--no-process-env", "--inherited", "KEY=/x", "KEY"],
            file_text="KEY=\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["assign"], "''")
        self.assertEqual(rows["file"], "''")
        self.assertEqual(rows["assign_source"], "file-empty")


class ProcessLayerTests(unittest.TestCase):
    def test_process_unset_is_none_even_with_inherited_overlay(self):
        proc = run_cli(
            ["--no-process-env", "--inherited", "KEY=/x", "KEY"],
            file_text="KEY=\n",
            env={},
        )
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["inherited"], "'/x'")
        self.assertEqual(rows["process"], "None")
        self.assertEqual(rows["process_presence"], "unset")

    def test_process_empty_string_is_not_unset(self):
        proc = run_cli(
            ["--no-process-env", "KEY"],
            env={"KEY": ""},
        )
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["process"], "''")
        self.assertEqual(rows["inherited"], "None")
        self.assertEqual(rows["process_presence"], "empty")

    def test_default_inherited_is_not_process_copy(self):
        proc = run_cli(["KEY"], env={"KEY": "from-process"})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["process"], "'from-process'")
        self.assertEqual(rows["inherited"], "None")
        self.assertEqual(rows["inherited_presence"], "absent")
        self.assertNotEqual(rows["inherited"], rows["process"])

    def test_from_process_env_copies_into_inherited(self):
        proc = run_cli(["--from-process-env", "KEY"], env={"KEY": "from-process"})
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["inherited"], "'from-process'")
        self.assertEqual(rows["inherited_source"], "process-copy")
        self.assertEqual(rows["process"], "'from-process'")

    def test_injected_process_map(self):
        proc = run_cli(
            ["--process", "KEY=", "KEY"],
            env={"KEY": "live"},
        )
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["process"], "''")
        self.assertEqual(rows["process_presence"], "empty")
        self.assertEqual(rows["process_source"], "injected")


class Specimen010Tests(unittest.TestCase):
    def test_matches_loader_fixture(self):
        result = EL.layers_for_key(
            "KEY",
            inherited={"KEY": "/x", "OTHER": "1"},
            file_text="KEY=\nOTHER=2\n",
            process_env={},
        )
        self.assertEqual(result["inherited"], "/x")
        self.assertEqual(result["file"], "")
        self.assertEqual(result["skip_empty"], "/x")
        self.assertEqual(result["assign"], "")
        self.assertIsNone(result["process"])


class MissingFileTests(unittest.TestCase):
    def test_missing_file_is_clean_error(self):
        missing = "/no/such/envlayers.env"
        proc = run_cli(["--no-process-env", "--file", missing, "KEY"])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("file not found", proc.stderr)
        self.assertIn(missing, proc.stderr)
        self.assertNotIn("Errno", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertFalse(proc.stdout.strip())

    def test_directory_is_clean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_cli(["--no-process-env", "--file", tmp, "KEY"])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("is a directory", proc.stderr)
        self.assertNotIn("Errno", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertFalse(proc.stdout.strip())

    def test_omitted_file_is_not_missing_file(self):
        proc = run_cli(["--no-process-env", "KEY"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "None")
        self.assertEqual(rows["file_presence"], "omitted")

    def test_empty_file_is_absent_not_omitted(self):
        proc = run_cli(["--no-process-env", "KEY"], file_text="")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "None")
        self.assertEqual(rows["file_presence"], "absent")
        self.assertEqual(rows["file_source"], "text")

    def test_invalid_utf8_is_clean_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.env"
            path.write_bytes(b"KEY=\xff\n")
            extra_env = os.environ.copy()
            extra_env.pop("KEY", None)
            proc = subprocess.run(
                [sys.executable, str(CLI), "--no-process-env", "--file", str(path), "KEY"],
                check=False,
                capture_output=True,
                text=True,
                env=extra_env,
            )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("not utf-8", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertNotIn("UnicodeDecodeError", proc.stderr)


class DuplicateKeyTests(unittest.TestCase):
    def test_file_last_assignment_skip_empty_last_nonempty(self):
        text = "KEY=fromfile\nKEY=\n"
        file_map = EL.parse_assignments(text)
        skip = EL.load_skip_empty(text, {"KEY": "/x"})
        assign = EL.load_assign(text, {"KEY": "/x"})
        self.assertEqual(file_map["KEY"], "")
        self.assertEqual(skip["KEY"], "fromfile")
        self.assertEqual(assign["KEY"], "")

    def test_skip_empty_last_nonempty_not_first_and_not_inherited(self):
        text = "KEY=a\nKEY=b\nKEY=\n"
        self.assertEqual(EL.parse_assignments(text)["KEY"], "")
        self.assertEqual(EL.load_skip_empty(text, {"KEY": "/x"})["KEY"], "b")

    def test_cli_duplicate_key_last_assignment_vs_last_nonempty(self):
        proc = run_cli(
            ["--no-process-env", "--inherited", "KEY=/x", "KEY"],
            file_text="KEY=fromfile\nKEY=\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["inherited"], "'/x'")
        self.assertEqual(rows["file"], "''")
        self.assertEqual(rows["skip_empty"], "'fromfile'")
        self.assertEqual(rows["assign"], "''")
        self.assertEqual(rows["skip_empty_source"], "file")
        self.assertEqual(rows["assign_source"], "file-empty")
        self.assertEqual(rows["file_n"], "2")
        self.assertEqual(rows["file_presence"], "empty-assignment")
        self.assertEqual(rows["policies_disagree"], "true")

    def test_layers_for_key_duplicate_empty_does_not_keep_inherited(self):
        result = EL.layers_for_key(
            "KEY",
            inherited={"KEY": "/x"},
            file_text="KEY=fromfile\nKEY=\n",
            process_env={},
        )
        self.assertEqual(result["file"], "")
        self.assertEqual(result["skip_empty"], "fromfile")
        self.assertEqual(result["assign"], "")
        self.assertNotEqual(result["skip_empty"], result["inherited"])
        self.assertEqual(result["skip_empty_source"], "file")
        self.assertEqual(result["file_n"], 2)


class DotenvGrammarTests(unittest.TestCase):
    def test_quoted_empty_is_empty_assignment(self):
        proc = run_cli(
            ["--inherited", "KEY=/x", "KEY"],
            file_text='KEY=""\n',
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "''")
        self.assertEqual(rows["file_presence"], "empty-assignment")
        self.assertEqual(rows["skip_empty"], "'/x'")
        self.assertEqual(rows["skip_empty_source"], "inherited")
        self.assertEqual(rows["assign"], "''")

    def test_single_quoted_empty_is_empty_assignment(self):
        proc = run_cli(
            ["--inherited", "KEY=/x", "KEY"],
            file_text="KEY=''\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "''")
        self.assertEqual(rows["skip_empty"], "'/x'")

    def test_export_prefix_binds_key(self):
        proc = run_cli(
            ["--inherited", "KEY=/x", "KEY"],
            file_text="export KEY=exported\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "'exported'")
        self.assertEqual(rows["file_presence"], "value")
        self.assertEqual(rows["skip_empty"], "'exported'")
        self.assertEqual(rows["assign"], "'exported'")

    def test_comment_is_not_a_key(self):
        proc = run_cli(["KEY"], file_text="# KEY=secret\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "None")
        self.assertEqual(rows["file_presence"], "absent")

    def test_bom_empty_assignment(self):
        proc = run_cli(
            ["--inherited", "KEY=/x", "KEY"],
            file_text="\ufeffKEY=\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "''")
        self.assertEqual(rows["file_presence"], "empty-assignment")

    def test_tab_indented_and_spaced_equals(self):
        proc = run_cli(["KEY"], file_text="\tKEY = value\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_output(proc.stdout)["file"], "'value'")

    def test_whitespace_only_value_is_empty_assignment(self):
        proc = run_cli(
            ["--inherited", "KEY=/x", "KEY"],
            file_text="KEY= \n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertEqual(rows["file"], "''")
        self.assertEqual(rows["skip_empty"], "'/x'")

    def test_export_without_assignment_is_error(self):
        proc = run_cli(["KEY"], file_text="export KEY\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("not an assignment", proc.stderr)
        self.assertFalse(proc.stdout.strip())

    def test_empty_inherited_name_refused(self):
        proc = run_cli(["--inherited", "=", "KEY"])
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("empty key", proc.stderr)

    def test_empty_query_key_refused(self):
        proc = run_cli([""])
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("bad key", proc.stderr)

    def test_query_key_with_equals_refused(self):
        proc = run_cli(["FOO=BAR"])
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("bad key", proc.stderr)

    def test_inherit_alias(self):
        proc = run_cli(
            ["--inherit", "KEY=/x", "KEY"],
            file_text="KEY=\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(parse_output(proc.stdout)["inherited"], "'/x'")

    def test_huge_value_is_capped_in_display(self):
        payload = "H" * 5000
        proc = run_cli(["KEY"], file_text=f"KEY={payload}\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_output(proc.stdout)
        self.assertIn("…", rows["file"])
        self.assertLess(len(proc.stdout), 4000)
        self.assertEqual(rows["file_presence"], "value")


if __name__ == "__main__":
    unittest.main()
