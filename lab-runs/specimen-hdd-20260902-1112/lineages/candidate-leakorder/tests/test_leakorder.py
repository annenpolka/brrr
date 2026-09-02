#!/usr/bin/env python3
"""Order-dependent start is leaked; leftover is leftover; orders are isolated."""

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
FIXTURES = ROOT / "fixtures"
FIXTURE_009 = FIXTURES / "specimen009.py"
CLASS_ATTR = FIXTURES / "test_class_attr.py"
HELPER = FIXTURES / "helper_pair" / "test_helper.py"
HELPER_N = FIXTURES / "helper_pair" / "test_helper_n.py"
PRIVATE = FIXTURES / "test_private.py"
FNATTR = FIXTURES / "test_fnattr.py"
ENVMARK = FIXTURES / "test_envmark.py"
ALWAYS = FIXTURES / "test_always_fail.py"
NAN = FIXTURES / "test_nan.py"
ASYNC_F = FIXTURES / "test_async.py"
GEN = FIXTURES / "test_gen.py"
SYSEXIT = FIXTURES / "test_sysexit.py"
CLASS_M = FIXTURES / "test_class_method.py"
CUSTEQ = FIXTURES / "test_custeq.py"
EMPTY = FIXTURES / "empty.py"
DEFAULTS = FIXTURES / "test_defaults.py"
CLOSURE = FIXTURES / "test_closure.py"
UNSEEN = FIXTURES / "unseen_bucket.py"


def find_cli() -> Path:
    for name in ("leakorder", "leakorder.py"):
        cand = ROOT / name
        if cand.is_file():
            return cand
    raise FileNotFoundError(f"no leakorder CLI under {ROOT}")


CLI = find_cli()


def load_mod():
    loader = importlib.machinery.SourceFileLoader("leakorder_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


LO = load_mod()


def run_cli(path: Path, extra: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(CLI), str(path)]
    if extra:
        cmd.extend(extra)
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=os.environ.copy(),
    )


def field(text: str, prefix: str) -> str:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    raise AssertionError(f"missing {prefix!r} in:\n{text}")


class ModuleGlobalTests(unittest.TestCase):
    def test_snapshot_sees_acc(self):
        snap = LO.snapshot(LO.load_fresh(FIXTURE_009))
        self.assertEqual(LO.display(snap["acc"]), [])
        self.assertNotIn("test_a", snap)

    def test_cli_names_acc_and_exposing_order(self):
        proc = run_cli(FIXTURE_009)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        out = proc.stdout
        self.assertIn("test_a=PASS test_b=FAIL ['a']", out)
        self.assertIn("test_b=PASS test_a=PASS", out)
        self.assertIn("leftover={'acc': ['a']}", out)
        self.assertEqual(field(out, "leaked_names"), "acc")
        self.assertEqual(field(out, "sufficient_exposing_order"), "test_a,test_b")
        self.assertIn("fail=['test_a,test_b']", out)
        self.assertIn("pass=['test_b,test_a']", out)
        self.assertNotIn("leaked=acc", out)
        self.assertNotIn("leaked=none", out)

    def test_pass_order_leftover_is_not_leaked_column(self):
        proc = run_cli(FIXTURE_009)
        lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("order test_b,test_a")]
        self.assertTrue(lines)
        self.assertIn("leftover={'acc': ['a']}", lines[0])
        self.assertNotIn("leaked=", lines[0])


class ClassAttrTests(unittest.TestCase):
    def test_snapshot_sees_box_bucket(self):
        snap = LO.snapshot(LO.load_fresh(CLASS_ATTR))
        self.assertEqual(LO.display(snap["Box.bucket"]), [])
        self.assertNotIn("Box", snap)
        self.assertNotIn("bucket", snap)

    def test_cli_names_box_bucket_not_none(self):
        proc = run_cli(CLASS_ATTR)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        out = proc.stdout
        self.assertIn("test_a=PASS test_b=FAIL ['a']", out)
        self.assertIn("leftover={'Box.bucket': ['a']}", out)
        self.assertEqual(field(out, "leaked_names"), "Box.bucket")
        self.assertEqual(field(out, "sufficient_exposing_order"), "test_a,test_b")
        self.assertNotEqual(field(out, "leaked_names"), "none")
        self.assertNotIn("leaked_names  none", out)

    def test_inline_class_attr_is_named(self):
        text = (
            "class Box:\n"
            "    bucket = []\n"
            "\n"
            "def test_a():\n"
            "    Box.bucket.append('a')\n"
            "\n"
            "def test_b():\n"
            "    assert Box.bucket == [], Box.bucket\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test_class_leak.py"
            path.write_text(text, encoding="utf-8")
            proc = run_cli(path)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "Box.bucket")


class IsolationTests(unittest.TestCase):
    def test_helper_bucket_reverse_passes(self):
        proc = run_cli(HELPER)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        out = proc.stdout
        self.assertEqual(field(out, "leaked_names"), "bucket")
        self.assertEqual(field(out, "sufficient_exposing_order"), "test_a,test_b")
        self.assertIn("fail=['test_a,test_b']", out)
        self.assertIn("pass=['test_b,test_a']", out)
        self.assertIn("leftover={'bucket': ['a']}", out)

    def test_helper_n_is_not_smeared_to_21(self):
        proc = run_cli(HELPER_N)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        out = proc.stdout
        self.assertIn("n=11", out)
        self.assertIn("n=10", out)
        self.assertNotIn("n=21", out)
        self.assertEqual(field(out, "sufficient_exposing_order"), "none")
        self.assertEqual(field(out, "leaked_names"), "helper.n")

    def test_env_split_is_unknown_not_none(self):
        proc = run_cli(ENVMARK)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        out = proc.stdout
        self.assertEqual(field(out, "sufficient_exposing_order"), "test_a,test_b")
        self.assertEqual(field(out, "leaked_names"), "unknown")
        self.assertNotEqual(field(out, "leaked_names"), "none")


class SnapshotShapeTests(unittest.TestCase):
    def test_private_global_is_named(self):
        proc = run_cli(PRIVATE)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "_acc")
        self.assertNotEqual(field(proc.stdout, "leaked_names"), "none")

    def test_function_attr_is_named(self):
        proc = run_cli(FNATTR)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "holder.acc")

    def test_mutable_default_is_named(self):
        proc = run_cli(DEFAULTS)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "bag.__defaults__[0]")

    def test_closure_cell_is_named(self):
        proc = run_cli(CLOSURE)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "acc")

    def test_custom_eq_does_not_hide_box_n(self):
        proc = run_cli(CUSTEQ)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "box.n")
        self.assertNotEqual(field(proc.stdout, "leaked_names"), "none")


class SufficientSplitTests(unittest.TestCase):
    def test_always_fail_both_is_none(self):
        proc = run_cli(ALWAYS)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "sufficient_exposing_order"), "none")
        self.assertEqual(field(proc.stdout, "leaked_names"), "acc")
        self.assertIn("fail=['test_a,test_b', 'test_b,test_a']", proc.stdout)

    def test_empty_file_does_not_invent_order(self):
        proc = run_cli(EMPTY)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "none")
        self.assertEqual(field(proc.stdout, "sufficient_exposing_order"), "none")
        self.assertNotIn("order test_a,test_b", proc.stdout)

    def test_unseen_bucket_discovered_without_order_flag(self):
        proc = run_cli(UNSEEN)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "bucket")
        self.assertEqual(field(proc.stdout, "sufficient_exposing_order"), "test_write,test_empty")

    def test_nan_and_object_are_not_leaks(self):
        proc = run_cli(NAN)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "none")
        self.assertEqual(field(proc.stdout, "sufficient_exposing_order"), "none")
        self.assertNotIn("leaked_names  nan", proc.stdout)


class InvokeTests(unittest.TestCase):
    def test_async_is_error_not_pass(self):
        proc = run_cli(ASYNC_F)
        self.assertIn("test_a=ERROR async callable", proc.stdout)
        self.assertNotIn("test_a=PASS", proc.stdout)
        self.assertEqual(field(proc.stdout, "sufficient_exposing_order"), "none")

    def test_generator_is_error_not_pass(self):
        proc = run_cli(GEN)
        self.assertIn("test_a=ERROR generator callable", proc.stdout)
        self.assertNotIn("test_a=PASS", proc.stdout)

    def test_systemexit_is_error_not_cli_rc(self):
        proc = run_cli(SYSEXIT)
        self.assertNotEqual(proc.returncode, 3)
        self.assertIn("test_a=ERROR SystemExit: 3", proc.stdout)
        self.assertTrue(proc.stdout.startswith("file  "), proc.stderr)

    def test_class_method_instantiates(self):
        proc = run_cli(
            CLASS_M,
            extra=["--order", "TestOrder.test_a,TestOrder.test_b", "--order", "TestOrder.test_b,TestOrder.test_a"],
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(field(proc.stdout, "leaked_names"), "TestOrder.bucket")
        self.assertEqual(
            field(proc.stdout, "sufficient_exposing_order"),
            "TestOrder.test_a,TestOrder.test_b",
        )


class UsageTests(unittest.TestCase):
    def test_missing_file_rc_2(self):
        proc = run_cli(ROOT / "no-such-file.py")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("leakorder: file not found", proc.stderr)

    def test_no_args_rc_2(self):
        proc = subprocess.run(
            [sys.executable, str(CLI)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
