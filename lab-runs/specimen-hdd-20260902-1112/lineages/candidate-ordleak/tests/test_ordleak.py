#!/usr/bin/env python3
"""Two orders of a named pair; leak is a test-induced start-of-victim write."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "ordleak"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
FIXTURE = FIXTURES / "test_order.py"
CLASS_ATTR = FIXTURES / "test_class_attr.py"
FNATTR = FIXTURES / "test_fnattr.py"
PRIVATE = FIXTURES / "test_private.py"
HELPER = FIXTURES / "helper" / "test_order.py"
HELPER_IMPORT = FIXTURES / "helper" / "test_import.py"
STAMP = FIXTURES / "test_stamp.py"
ENV = FIXTURES / "test_env.py"
CLASS_METHOD = FIXTURES / "test_class_method.py"
FS = FIXTURES / "test_fs.py"
PKG_FROM = FIXTURES / "pkg" / "test_from_pkg.py"
PKG_RELATIVE = FIXTURES / "pkg" / "test_relative.py"
PARENT_HELPER = FIXTURES / "parent_helper" / "sub" / "test_order.py"
SLOTS = FIXTURES / "test_slots.py"
BINARY = FIXTURES / "test_binary.py"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("ordleak_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


OL = load_mod()


def parse_rows(text: str) -> list[list[str]]:
    return [line.split("\t") for line in text.splitlines() if line]


def rows_kind(rows: list[list[str]], kind: str) -> list[list[str]]:
    return [row for row in rows if row and row[0] == kind]


def run_cli(args, *, file_text=None, file_path=None):
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(CLI)]
        if file_text is not None:
            path = Path(tmp) / "test_mod.py"
            path.write_text(textwrap.dedent(file_text).lstrip(), encoding="utf-8")
        else:
            path = Path(file_path)
        cmd.extend([str(path), *args])
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env=os.environ.copy(),
        )
    return proc


NO_LEAK = """
def test_a():
    assert True


def test_b():
    assert True
"""

HIDDEN = """
acc = []

def test_a():
    acc.append("a")

def test_c():
    pass
"""

MUTABLE_DEFAULT = """
def bag(xs=[]):
    return xs


def test_a():
    bag().append("a")


def test_b():
    assert bag() == [], bag()
"""

CLOSURE = """
def _wrap():
    acc = []

    def test_a():
        acc.append("a")

    def test_b():
        assert acc == [], acc

    return test_a, test_b


test_a, test_b = _wrap()
"""

DATACLASS = """
from dataclasses import dataclass

@dataclass
class S:
    acc: list

state = S(acc=[])

def test_a():
    state.acc.append("a")

def test_b():
    assert state.acc == [], state.acc
"""

DATACLASS_CLEAN = """
from dataclasses import dataclass

@dataclass
class S:
    acc: list

state = S(acc=[])

def test_a():
    pass

def test_b():
    pass
"""

NAN = """
nan = float("nan")

def test_a():
    pass

def test_b():
    pass
"""

TOKEN = """
token = object()

def test_a():
    pass

def test_b():
    pass
"""

SYSTEM_EXIT = """
def test_a():
    raise SystemExit(3)

def test_b():
    pass
"""

GENERATOR_EXIT = """
def test_a():
    raise GeneratorExit()

def test_b():
    pass
"""

ASYNC_TEST = """
async def test_a():
    return 1

def test_b():
    pass
"""

GENERATOR_TEST = """
def test_a():
    yield 1

def test_b():
    pass
"""

ALWAYS_FAIL = """
def test_a():
    pass


def test_b():
    assert False
"""

LRU_CACHE = """
from functools import lru_cache

@lru_cache(maxsize=8)
def cached(x):
    return x


def test_a():
    cached(1)


def test_b():
    assert cached.cache_info().currsize == 0, cached.cache_info()
"""


class SpecimenOrderTests(unittest.TestCase):
    def test_a_then_b_fails_b_then_a_passes(self):
        result = OL.contrast(FIXTURE, "test_a", "test_b")
        ab, ba = result["orders"]
        self.assertEqual(tuple(ab["order"]), ("test_a", "test_b"))
        self.assertEqual([step["status"] for step in ab["steps"]], ["PASS", "FAIL"])
        self.assertEqual(ab["steps"][1]["detail"], "['a']")
        self.assertEqual(tuple(ba["order"]), ("test_b", "test_a"))
        self.assertEqual([step["status"] for step in ba["steps"]], ["PASS", "PASS"])

    def test_names_leaked_acc_and_exposing_order(self):
        result = OL.contrast(FIXTURE, "test_a", "test_b")
        self.assertEqual(result["exposing_orders"], [("test_a", "test_b")])
        self.assertEqual(len(result["leaked"]), 1)
        row = result["leaked"][0]
        self.assertEqual(row["binding"], "acc")
        self.assertEqual(row["into"], "test_b")
        self.assertEqual(row["via"], "test_a")
        self.assertEqual(row["alone"], [])
        self.assertEqual(row["after_other"], ["a"])
        self.assertEqual(result["leak_verdict"], "named")


class CliOrderTests(unittest.TestCase):
    def test_cli_two_orders(self):
        proc = run_cli(["test_a", "test_b"], file_path=FIXTURE)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        orders = rows_kind(rows, "order")
        self.assertEqual(orders[0][1], "test_a test_b")
        self.assertEqual(orders[1][1], "test_b test_a")
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[0][1:], ["test_a", "PASS"])
        self.assertEqual(statuses[1][1:3], ["test_b", "FAIL"])
        self.assertEqual(statuses[1][3], "['a']")
        self.assertEqual(statuses[2][1:], ["test_b", "PASS"])
        self.assertEqual(statuses[3][1:], ["test_a", "PASS"])
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "acc")
        self.assertEqual(leaked[2:4], ["into", "test_b"])
        self.assertEqual(leaked[4:6], ["[]", "['a']"])
        self.assertEqual(leaked[6:8], ["via", "test_a"])

    def test_cli_nodeids(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                f"{FIXTURE}::test_a",
                f"{FIXTURE}::test_b",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "acc")


class ControlTests(unittest.TestCase):
    def test_no_shared_state_is_none(self):
        proc = run_cli(["test_a", "test_b"], file_text=NO_LEAK)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "none")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "none")

    def test_hidden_leak_without_failing_assert(self):
        proc = run_cli(["test_a", "test_c"], file_text=HIDDEN)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "none")
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "acc")
        self.assertEqual(leaked[3], "test_c")
        self.assertEqual(leaked[4:6], ["[]", "['a']"])
        self.assertEqual(leaked[7], "test_a")


class IsolationTests(unittest.TestCase):
    def test_class_attribute_is_named(self):
        proc = run_cli(["test_a", "test_b"], file_path=CLASS_ATTR)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "Box.items")
        self.assertEqual(leaked[2:4], ["into", "test_b"])
        self.assertEqual(leaked[4:6], ["[]", "['a']"])
        self.assertEqual(leaked[6:8], ["via", "test_a"])
        self.assertNotEqual(leaked[1], "none")

    def test_function_attribute_is_named(self):
        proc = run_cli(["test_a", "test_b"], file_path=FNATTR)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "holder.acc")
        self.assertEqual(leaked[4:6], ["[]", "['a']"])

    def test_mutable_default_is_named(self):
        proc = run_cli(["test_a", "test_b"], file_text=MUTABLE_DEFAULT)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "bag.__defaults__[0]")
        self.assertEqual(leaked[4:6], ["[]", "['a']"])

    def test_closure_cell_is_named(self):
        proc = run_cli(["test_a", "test_b"], file_text=CLOSURE)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "acc")
        self.assertEqual(leaked[4:6], ["[]", "['a']"])

    def test_private_global_is_named(self):
        proc = run_cli(["test_a", "test_b"], file_path=PRIVATE)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "_acc")
        self.assertEqual(leaked[4:6], ["[]", "['a']"])
        self.assertNotEqual(leaked[1], "none")


class HelperIsolationTests(unittest.TestCase):
    def test_from_helper_import_bucket(self):
        proc = run_cli(["test_a", "test_b"], file_path=HELPER)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[0][1:], ["test_a", "PASS"])
        self.assertEqual(statuses[1][1:3], ["test_b", "FAIL"])
        self.assertEqual(statuses[2][1:], ["test_b", "PASS"])
        self.assertEqual(statuses[3][1:], ["test_a", "PASS"])
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "bucket")
        self.assertEqual(leaked[2:4], ["into", "test_b"])
        self.assertEqual(leaked[4:6], ["[]", "['a']"])
        self.assertEqual(leaked[6:8], ["via", "test_a"])

    def test_import_helper_module_bucket(self):
        proc = run_cli(["test_a", "test_b"], file_path=HELPER_IMPORT)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "helper.bucket")
        self.assertEqual(leaked[4:6], ["[]", "['a']"])
        self.assertEqual(leaked[7], "test_a")

    def _assert_bucket_pair(self, proc):
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[0][1:], ["test_a", "PASS"])
        self.assertEqual(statuses[1][1:3], ["test_b", "FAIL"])
        self.assertEqual(statuses[2][1:], ["test_b", "PASS"])
        self.assertEqual(statuses[3][1:], ["test_a", "PASS"])
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")
        names = [row[1] for row in leaked]
        self.assertIn("bucket", names)
        row = next(item for item in leaked if item[1] == "bucket")
        self.assertEqual(row[2:4], ["into", "test_b"])
        self.assertEqual(row[4:6], ["[]", "['a']"])
        self.assertEqual(row[6:8], ["via", "test_a"])

    def test_from_pkg_helper_import_bucket(self):
        proc = run_cli(["test_a", "test_b"], file_path=PKG_FROM)
        self._assert_bucket_pair(proc)

    def test_relative_helper_import_bucket(self):
        proc = run_cli(["test_a", "test_b"], file_path=PKG_RELATIVE)
        self._assert_bucket_pair(proc)

    def test_parent_helper_is_copied(self):
        proc = run_cli(["test_a", "test_b"], file_path=PARENT_HELPER)
        self._assert_bucket_pair(proc)


class ImportNoiseTests(unittest.TestCase):
    def test_time_ns_is_not_a_leak(self):
        proc = run_cli(["test_a", "test_b"], file_path=STAMP)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "none")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "none")

    def test_nan_is_not_a_leak(self):
        proc = run_cli(["test_a", "test_b"], file_text=NAN)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "none")

    def test_object_id_is_not_a_leak(self):
        proc = run_cli(["test_a", "test_b"], file_text=TOKEN)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "none")

    def test_dataclass_type_identity_is_not_a_leak(self):
        proc = run_cli(["test_a", "test_b"], file_text=DATACLASS_CLEAN)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "none")

    def test_dataclass_mutation_is_named(self):
        proc = run_cli(["test_a", "test_b"], file_text=DATACLASS)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "state")
        self.assertEqual(leaked[4], "S(acc=[])")
        self.assertEqual(leaked[5], "S(acc=['a'])")
        self.assertEqual(leaked[7], "test_a")


class ClassMethodTests(unittest.TestCase):
    def test_dotted_class_method(self):
        proc = run_cli(["TestOrder.test_a", "TestOrder.test_b"], file_path=CLASS_METHOD)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "TestOrder.test_a TestOrder.test_b")
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "TestOrder.acc")
        self.assertEqual(leaked[4:6], ["[]", "['a']"])
        self.assertEqual(leaked[7], "TestOrder.test_a")

    def test_file_class_method_nodeids(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                f"{CLASS_METHOD}::TestOrder::test_a",
                f"{CLASS_METHOD}::TestOrder::test_b",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        leaked = rows_kind(rows, "leaked")[0]
        self.assertEqual(leaked[1], "TestOrder.acc")
        self.assertEqual(leaked[7], "TestOrder.test_a")


class UnseenAndErrorsTests(unittest.TestCase):
    def test_env_split_is_unseen_not_none(self):
        proc = run_cli(["test_a", "test_b"], file_path=ENV)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")
        self.assertEqual(len(leaked), 1)
        self.assertEqual(leaked[0][1], "<unseen>")
        self.assertNotEqual(leaked[0][1], "none")

    def test_fs_split_is_unseen_not_none(self):
        proc = run_cli(["test_a", "test_b"], file_path=FS)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[2][1:], ["test_b", "PASS"])
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "<unseen>")

    def test_async_is_error_not_pass(self):
        proc = run_cli(["test_a", "test_b"], file_text=ASYNC_TEST)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[0][2], "ERROR")
        self.assertIn("async def", statuses[0][3])
        self.assertNotEqual(statuses[0][2], "PASS")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "<unseen>")

    def test_generator_is_error_not_pass(self):
        proc = run_cli(["test_a", "test_b"], file_text=GENERATOR_TEST)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[0][2], "ERROR")
        self.assertIn("generator", statuses[0][3])
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "<unseen>")

    def test_systemexit_is_error_row(self):
        proc = run_cli(["test_a", "test_b"], file_text=SYSTEM_EXIT)
        self.assertIn(proc.returncode, (0, 1), proc.stderr)
        self.assertTrue(proc.stdout, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[0][1], "test_a")
        self.assertEqual(statuses[0][2], "ERROR")
        self.assertTrue(any("SystemExit" in cell for cell in statuses[0][3:]))

    def test_generatorexit_is_error_row(self):
        proc = run_cli(["test_a", "test_b"], file_text=GENERATOR_EXIT)
        self.assertTrue(proc.stdout, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[0][2], "ERROR")
        self.assertTrue(any("GeneratorExit" in cell for cell in statuses[0][3:]))


class DualFailAndIdentityTests(unittest.TestCase):
    def test_hardcoded_tmp_smear_is_unseen_not_none(self):
        marker = Path("/tmp") / f"ordleak-smear-{uuid.uuid4().hex}.marker"
        self.addCleanup(lambda: marker.unlink(missing_ok=True))
        if marker.exists():
            marker.unlink()
        body = f"""
from pathlib import Path

MARKER = Path({str(marker)!r})

def test_a():
    MARKER.write_text("a", encoding="utf-8")

def test_b():
    assert not MARKER.exists(), MARKER.read_text(encoding="utf-8")
"""
        proc = run_cli(["test_a", "test_b"], file_text=body)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        statuses = rows_kind(rows, "status")
        self.assertEqual(statuses[1][2], "FAIL")
        self.assertEqual(statuses[2][2], "FAIL")
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "none")
        leaked = rows_kind(rows, "leaked")
        self.assertEqual(len(leaked), 1)
        self.assertEqual(leaked[0][1], "<unseen>")
        self.assertNotEqual(leaked[0][1], "none")
        self.assertTrue(marker.exists())

    def test_always_fail_is_unseen_not_green(self):
        proc = run_cli(["test_a", "test_b"], file_text=ALWAYS_FAIL)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "none")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "<unseen>")

    def test_slots_instance_state_is_named(self):
        proc = run_cli(["test_a", "test_b"], file_path=SLOTS)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        leaked = rows_kind(rows, "leaked")
        names = [row[1] for row in leaked]
        self.assertTrue("box.n" in names or "box" in names, leaked)
        if "box.n" in names:
            row = next(item for item in leaked if item[1] == "box.n")
            self.assertEqual(row[4:6], ["0", "1"])
            self.assertEqual(row[7], "test_a")
        else:
            row = next(item for item in leaked if item[1] == "box")
            self.assertIn("0", row[4])
            self.assertIn("1", row[5])
            self.assertEqual(row[7], "test_a")

    def test_lru_cache_currsize_stays_unseen(self):
        proc = run_cli(["test_a", "test_b"], file_text=LRU_CACHE)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "exposing_order")[0][1], "test_a test_b")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "<unseen>")
        self.assertNotEqual(rows_kind(rows, "leaked")[0][1], "none")

    def test_binary_stdout_is_not_a_utf8_crash(self):
        proc = run_cli(["test_a", "test_b"], file_path=BINARY)
        self.assertTrue(proc.stdout, proc.stderr)
        self.assertNotIn("utf-8", proc.stderr.lower())
        self.assertNotIn("codec can't decode", proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows_kind(rows, "status")[0][2], "PASS")
        self.assertEqual(rows_kind(rows, "status")[1][2], "PASS")
        self.assertEqual(rows_kind(rows, "leaked")[0][1], "none")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_outside_tree_import_is_named_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "helper.py").write_text("bucket = []\n", encoding="utf-8")
            nested = root / "mid" / "sub"
            nested.mkdir(parents=True)
            (nested / "test_mod.py").write_text(
                textwrap.dedent(
                    """
                    from helper import bucket

                    def test_a():
                        bucket.append("a")

                    def test_b():
                        assert bucket == [], bucket
                    """
                ).lstrip(),
                encoding="utf-8",
            )
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    str(nested / "test_mod.py"),
                    "test_a",
                    "test_b",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        err = proc.stderr
        self.assertTrue(err.startswith("ordleak:"), err)
        self.assertIn("outside the copied tree", err)
        self.assertNotIn("No module named 'helper'", err)


if __name__ == "__main__":
    unittest.main()

