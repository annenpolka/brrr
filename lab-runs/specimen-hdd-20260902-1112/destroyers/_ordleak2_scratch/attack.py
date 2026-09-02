#!/usr/bin/env python3
"""Host-executed DESTROYER_ordleak_2 attacks. Writes attack.log + cases/."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
CASES = SCRATCH / "cases"
CLI = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak"
)
S009 = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009/files/test_order.py"
)
S012 = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files/test_order.py"
)
S060 = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-060/files/test_class_leak.py"
)
HELPER = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/tests/fixtures/helper/test_order.py"
)
HELPER_IMPORT = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/tests/fixtures/helper/test_import.py"
)
STAMP = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/tests/fixtures/test_stamp.py"
)
ENV = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/tests/fixtures/test_env.py"
)
PRIVATE = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/tests/fixtures/test_private.py"
)
CLASS_ATTR = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/tests/fixtures/test_class_attr.py"
)

CASES.mkdir(parents=True, exist_ok=True)
LOG = SCRATCH / "attack.log"
lines_out: list[str] = []


def log(msg: str = "") -> None:
    lines_out.append(msg)
    print(msg, flush=True)


def parse_rows(text: str) -> list[list[str]]:
    return [line.split("\t") for line in text.splitlines() if line]


def rows_kind(rows: list[list[str]], kind: str) -> list[list[str]]:
    return [row for row in rows if row and row[0] == kind]


def run(args: list[str], *, cwd: str | None = None, env: dict | None = None, timeout: int = 25) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(CLI), *args]
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env or os.environ.copy(),
        timeout=timeout,
    )


def write_case(name: str, files: dict[str, str]) -> Path:
    d = CASES / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for rel, body in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return d


def dump(name: str, proc: subprocess.CompletedProcess) -> None:
    log(f"\n===== {name} rc={proc.returncode} =====")
    if proc.stdout:
        log(proc.stdout.rstrip("\n"))
    if proc.stderr:
        log("-- stderr --")
        log(proc.stderr.rstrip("\n"))
    (CASES / f"{name}.out").write_text(proc.stdout or "", encoding="utf-8")
    (CASES / f"{name}.err").write_text(proc.stderr or "", encoding="utf-8")
    (CASES / f"{name}.rc").write_text(str(proc.returncode), encoding="utf-8")


def leaked_none_next_to_exposing(proc: subprocess.CompletedProcess) -> bool:
    rows = parse_rows(proc.stdout)
    exposing = rows_kind(rows, "exposing_order")
    leaked = rows_kind(rows, "leaked")
    if not exposing:
        return False
    exp = exposing[0][1] if len(exposing[0]) > 1 else ""
    if exp == "none":
        return False
    if not leaked:
        return True
    return leaked[0][1] == "none"


# --- required host cases ---
log("# DESTROYER_ordleak_2 host attacks")
log(f"CLI={CLI}")

proc = run([str(S009), "test_a", "test_b"])
dump("s009", proc)

proc = run([str(HELPER), "test_a", "test_b"])
dump("helper_from_import", proc)

proc = run([str(HELPER_IMPORT), "test_a", "test_b"])
dump("helper_import_module", proc)

proc = run([str(S060), "test_a", "test_b"])
dump("s060_box_bucket", proc)

proc = run([str(STAMP), "test_a", "test_b"])
dump("stamp_time_ns", proc)

proc = run([str(ENV), "test_a", "test_b"])
dump("env_unseen", proc)

proc = run([str(PRIVATE), "test_a", "test_b"])
dump("private_acc", proc)

proc = run([str(CLASS_ATTR), "test_a", "test_b"])
dump("class_attr_items", proc)

# specimen-012 identity
cmp_rc = subprocess.run(["cmp", str(S009), str(S012)], capture_output=True)
log(f"\n===== cmp s009 vs s012 rc={cmp_rc.returncode} =====")

# --- PID isolation: two orders must be different processes ---
pid_marker = Path("/tmp/ordleak2-pids.txt")
if pid_marker.exists():
    pid_marker.unlink()
d = write_case(
    "pid_isolation",
    {
        "test_mod.py": f"""
import os
from pathlib import Path

PIDFILE = Path({str(pid_marker)!r})

def test_a():
    PIDFILE.write_text(PIDFILE.read_text() + f"a {{os.getpid()}}\\n" if PIDFILE.exists() else f"a {{os.getpid()}}\\n")

def test_b():
    PIDFILE.write_text(PIDFILE.read_text() + f"b {{os.getpid()}}\\n" if PIDFILE.exists() else f"b {{os.getpid()}}\\n")
    assert True
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("pid_isolation", proc)
pid_text = pid_marker.read_text() if pid_marker.exists() else ""
log(f"-- pidfile --\n{pid_text.rstrip()}")
pids = []
for line in pid_text.splitlines():
    parts = line.split()
    if len(parts) == 2:
        pids.append(int(parts[1]))
unique_pids = sorted(set(pids))
log(f"unique_pids={unique_pids} n_lines={len(pids)}")
log(f"subprocess_isolation={'YES' if len(unique_pids) >= 2 else 'NO SAME-PROCESS'}")

# --- sys.modules smear detector (same-process would fail reverse test_b) ---
d = write_case(
    "sysmodules_smear",
    {
        "test_mod.py": """
import sys

def test_a():
    sys.modules["ordleak2_smear"] = type(sys)("ordleak2_smear")

def test_b():
    assert "ordleak2_smear" not in sys.modules, "smeared"
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("sysmodules_smear", proc)
log(f"sysmodules leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")

# --- helper n+=1 / n+=10 classic smear ---
d = write_case(
    "helper_counter",
    {
        "helper.py": "n = 0\n",
        "test_mod.py": """
import helper

def test_a():
    helper.n += 1

def test_b():
    helper.n += 10
    raise AssertionError(f"n={helper.n}")
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("helper_counter", proc)

# --- nested package helper ---
d = write_case(
    "nested_pkg",
    {
        "pkg/__init__.py": "",
        "pkg/helper.py": "bucket = []\n",
        "test_mod.py": """
from pkg.helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("nested_pkg", proc)

# nested with PYTHONPATH to original
proc = run(
    [str(d / "test_mod.py"), "test_a", "test_b"],
    env={**os.environ, "PYTHONPATH": str(d) + (os.pathsep + os.environ["PYTHONPATH"] if os.environ.get("PYTHONPATH") else "")},
)
dump("nested_pkg_pythonpath", proc)

# --- hardcoded /tmp marker smear ---
hard = Path("/tmp/ordleak2-hard.marker")
if hard.exists():
    hard.unlink()
d = write_case(
    "hard_tmp",
    {
        "test_mod.py": f"""
from pathlib import Path
MARKER = Path({str(hard)!r})

def test_a():
    MARKER.write_text("a", encoding="utf-8")

def test_b():
    assert not MARKER.exists(), MARKER.read_text(encoding="utf-8")
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("hard_tmp", proc)
log(f"hard_tmp leftover exists={hard.exists()} leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")
if hard.exists():
    hard.unlink()

# --- sibling marker (should isolate) ---
d = write_case(
    "sibling_marker",
    {
        "test_mod.py": """
from pathlib import Path
MARKER = Path(__file__).resolve().parent / "ordleak.marker"

def test_a():
    MARKER.write_text("a", encoding="utf-8")

def test_b():
    assert not MARKER.exists(), MARKER.read_text(encoding="utf-8")
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("sibling_marker", proc)

# --- lru_cache ---
d = write_case(
    "lru_cache",
    {
        "test_mod.py": """
from functools import lru_cache

@lru_cache
def cached(x):
    return x

def test_a():
    cached(1)

def test_b():
    assert cached.cache_info().currsize == 0, cached.cache_info()
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("lru_cache", proc)
log(f"lru leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")

# --- custom __eq__ always true ---
d = write_case(
    "custom_eq",
    {
        "test_mod.py": """
class Box:
    def __init__(self):
        self.n = 0
    def __eq__(self, other):
        return True
    def __repr__(self):
        return "Box()"

box = Box()

def test_a():
    box.n += 1

def test_b():
    assert box.n == 0, box.n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("custom_eq", proc)

# --- slots ---
d = write_case(
    "slots",
    {
        "test_mod.py": """
class Box:
    __slots__ = ("n",)
    def __init__(self):
        self.n = 0

box = Box()

def test_a():
    box.n += 1

def test_b():
    assert box.n == 0, box.n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("slots", proc)

# --- always-fail plus leak ---
d = write_case(
    "always_fail_leak",
    {
        "test_mod.py": """
acc = []

def test_a():
    acc.append("a")

def test_b():
    assert acc == [], acc
    assert False
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("always_fail_leak", proc)

# --- random module state ---
d = write_case(
    "random_state",
    {
        "test_mod.py": """
import random

def test_a():
    random.seed(1)
    random.random()

def test_b():
    random.seed(1)
    assert random.random() == random.Random(1).random()
"""
    },
)
# better: test_b fails if RNG advanced
d = write_case(
    "random_state",
    {
        "test_mod.py": """
import random

def test_a():
    random.random()

def test_b():
    random.seed(0)
    expected = random.Random(0).random()
    # after test_a, global RNG is not freshly seeded 0 unless we seed here
    # instead: fail if getstate differs from a fresh seed(0)
    random.seed(0)
    x = random.random()
    y = random.Random(0).random()
    assert x == y
"""
    },
)
# This always passes. Use:
d = write_case(
    "random_state",
    {
        "test_mod.py": """
import random

def test_a():
    random.seed(123)
    random.random()

def test_b():
    # depends on prior consumption of the global RNG if seed not reset
    v = random.random()
    assert v == 0.0, v
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("random_state", proc)
log(f"random leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")

# --- logging module ---
d = write_case(
    "logging_mod",
    {
        "test_mod.py": """
import logging

def test_a():
    logging.getLogger("ordleak2").handlers.append(logging.NullHandler())

def test_b():
    assert logging.getLogger("ordleak2").handlers == []
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("logging_mod", proc)
log(f"logging leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")

# --- contextvars ---
d = write_case(
    "contextvars",
    {
        "test_mod.py": """
from contextvars import ContextVar
v = ContextVar("ordleak2", default=0)

def test_a():
    v.set(1)

def test_b():
    assert v.get() == 0, v.get()
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("contextvars", proc)
log(f"contextvars leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")

# --- import helper as alias ---
d = write_case(
    "helper_alias",
    {
        "helper.py": "bucket = []\n",
        "test_mod.py": """
import helper as h

def test_a():
    h.bucket.append("a")

def test_b():
    assert h.bucket == [], h.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("helper_alias", proc)

# --- from helper import bucket as acc ---
d = write_case(
    "helper_as_acc",
    {
        "helper.py": "bucket = []\n",
        "test_mod.py": """
from helper import bucket as acc

def test_a():
    acc.append("a")

def test_b():
    assert acc == [], acc
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("helper_as_acc", proc)

# --- relative import ---
d = write_case(
    "relative_import",
    {
        "pkg/__init__.py": "",
        "pkg/helper.py": "bucket = []\n",
        "pkg/test_mod.py": """
from .helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "pkg/test_mod.py"), "test_a", "test_b"])
dump("relative_import", proc)

# --- unittest.TestCase ---
d = write_case(
    "unittest_case",
    {
        "test_mod.py": """
import unittest

class TestOrder(unittest.TestCase):
    acc = []

    def test_a(self):
        self.acc.append("a")

    def test_b(self):
        self.assertEqual(self.acc, [])
"""
    },
)
proc = run([str(d / "test_mod.py"), "TestOrder.test_a", "TestOrder.test_b"])
dump("unittest_case", proc)

# --- fixture-parameterized ---
d = write_case(
    "fixture_params",
    {
        "test_mod.py": """
def test_a(ready):
    return ready

def test_b():
    pass
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("fixture_params", proc)

# --- stdout pollution ---
d = write_case(
    "stdout_pollute",
    {
        "test_mod.py": """
acc = []

def test_a():
    print("hello from test")
    acc.append("a")

def test_b():
    print('{"order": "fake"}')
    assert acc == [], acc
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("stdout_pollute", proc)

# --- binary stdout ---
d = write_case(
    "binary_stdout",
    {
        "test_mod.py": """
import sys
acc = []

def test_a():
    sys.stdout.buffer.write(b"\\xff\\xfe")
    acc.append("a")

def test_b():
    assert acc == [], acc
"""
    },
)
try:
    proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
    dump("binary_stdout", proc)
except Exception as exc:
    log(f"\n===== binary_stdout EXCEPTION {type(exc).__name__}: {exc} =====")

# --- two bindings ---
d = write_case(
    "two_bindings",
    {
        "test_mod.py": """
acc = []
other = []

def test_a():
    acc.append("a")
    other.append("o")

def test_b():
    assert acc == [] and other == [], (acc, other)
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("two_bindings", proc)

# --- unicode names ---
d = write_case(
    "unicode_names",
    {
        "test_mod.py": """
箱 = []

def 試験甲():
    箱.append("a")

def 試験乙():
    assert 箱 == [], 箱
"""
    },
)
proc = run([str(d / "test_mod.py"), "試験甲", "試験乙"])
dump("unicode_names", proc)

# --- tab/newline in assertion ---
d = write_case(
    "tab_newline",
    {
        "test_mod.py": """
acc = []

def test_a():
    acc.append("a")

def test_b():
    raise AssertionError("tab\\there\\nand newline " + str(acc))
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("tab_newline", proc)

# --- SystemExit ---
d = write_case(
    "systemexit",
    {
        "test_mod.py": """
def test_a():
    raise SystemExit(3)

def test_b():
    pass
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("systemexit", proc)

# --- dataclass clean vs mutate already in tests; threading.Lock ---
d = write_case(
    "thread_lock",
    {
        "test_mod.py": """
import threading
lock = threading.Lock()

def test_a():
    lock.acquire()

def test_b():
    assert not lock.locked(), "locked"
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("thread_lock", proc)

# --- property / skipped ---
d = write_case(
    "property_store",
    {
        "test_mod.py": """
class Store:
    _acc = []
    @property
    def acc(self):
        return self._acc

store = Store()

def test_a():
    Store._acc.append("a")

def test_b():
    assert Store._acc == [], Store._acc
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("property_store", proc)

# --- metaclass / class factory ---
d = write_case(
    "class_rebind",
    {
        "test_mod.py": """
class Box:
    bucket = []

def test_a():
    Box.bucket.append("a")

def test_b():
    assert Box.bucket == [], Box.bucket
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("class_rebind_box_bucket", proc)

# --- importlib import of helper under two names ---
d = write_case(
    "importlib_two_names",
    {
        "helper.py": "bucket = []\n",
        "test_mod.py": """
import importlib
h1 = importlib.import_module("helper")

def test_a():
    h1.bucket.append("a")

def test_b():
    import helper as h2
    assert h2.bucket == [], h2.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("importlib_two_names", proc)

# --- delete/create binding ---
d = write_case(
    "del_create",
    {
        "test_mod.py": """
acc = []

def test_a():
    global acc
    del acc

def test_b():
    global acc
    assert "acc" in globals()
    acc = ["reborn"]
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("del_create", proc)

# --- hidden leak PASS ---
d = write_case(
    "hidden_pass",
    {
        "test_mod.py": """
acc = []

def test_a():
    acc.append("a")

def test_c():
    pass
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_c"])
dump("hidden_pass", proc)

# --- nan mutate vs nan import ---
d = write_case(
    "nan_mutate",
    {
        "test_mod.py": """
box = {"n": float("nan")}

def test_a():
    box["n"] = 1.0

def test_b():
    import math
    assert math.isnan(box["n"]), box
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("nan_mutate", proc)

# --- parent PYTHONPATH pointing at original helper (smear if same process) ---
d = write_case(
    "pythonpath_original",
    {
        "helper.py": "bucket = []\n",
        "test_mod.py": """
from helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run(
    [str(d / "test_mod.py"), "test_a", "test_b"],
    env={**os.environ, "PYTHONPATH": str(d)},
)
dump("pythonpath_original", proc)

# --- helper in parent dir (not sibling) ---
d = write_case(
    "parent_helper",
    {
        "helper.py": "bucket = []\n",
        "sub/test_mod.py": """
from helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "sub/test_mod.py"), "test_a", "test_b"])
dump("parent_helper", proc)

# --- cwd vs FILE dir: run from elsewhere without PYTHONPATH ---
d = write_case(
    "cwd_elsewhere",
    {
        "helper.py": "bucket = []\n",
        "test_mod.py": """
from helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("cwd_elsewhere", proc)

# --- warnings filter ---
d = write_case(
    "warnings_filter",
    {
        "test_mod.py": """
import warnings

def test_a():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

def test_b():
    assert warnings.filters == [] or not any(f[2] is DeprecationWarning for f in warnings.filters)
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("warnings_filter", proc)
log(f"warnings leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")

# --- decimal context ---
d = write_case(
    "decimal_ctx",
    {
        "test_mod.py": """
from decimal import getcontext, Decimal

def test_a():
    getcontext().prec = 10

def test_b():
    assert getcontext().prec != 10 or True
    # fail if prec was changed
    from decimal import DefaultContext
    # actually check current prec equals default 28
    assert getcontext().prec == 28, getcontext().prec
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("decimal_ctx", proc)
log(f"decimal leaked_none_next_to_exposing={leaked_none_next_to_exposing(proc)}")

# --- mutable default already tested; closure already tested ---
# instance vs class: Box() instance with own list
d = write_case(
    "instance_bucket",
    {
        "test_mod.py": """
class Box:
    def __init__(self):
        self.bucket = []

box = Box()

def test_a():
    box.bucket.append("a")

def test_b():
    assert box.bucket == [], box.bucket
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("instance_bucket", proc)

# --- via both mutate ---
d = write_case(
    "both_write",
    {
        "test_mod.py": """
acc = []

def test_a():
    acc.append("a")

def test_b():
    acc.append("b")
    assert acc == ["b"], acc
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("both_write", proc)

# --- nodeid Class::method ---
d = write_case(
    "nodeid_class",
    {
        "test_mod.py": """
class Box:
    bucket = []

class TestOrder:
    def test_a(self):
        Box.bucket.append("a")
    def test_b(self):
        assert Box.bucket == [], Box.bucket
"""
    },
)
p = d / "test_mod.py"
proc = run([f"{p}::TestOrder::test_a", f"{p}::TestOrder::test_b"])
dump("nodeid_class", proc)

# --- missing helper without PYTHONPATH (cwd is helper dir) ---
# already have helper_from_import

# --- exec-order JSON pid in snapshot ---
d = write_case(
    "exec_pid_snap",
    {
        "test_mod.py": """
import os
pid = os.getpid()

def test_a():
    pass

def test_b():
    pass
"""
    },
)
proc1 = subprocess.run(
    [sys.executable, str(CLI), "--exec-order", str(d / "test_mod.py"), "test_a", "test_b"],
    capture_output=True,
    text=True,
    cwd=str(d),
)
proc2 = subprocess.run(
    [sys.executable, str(CLI), "--exec-order", str(d / "test_mod.py"), "test_b", "test_a"],
    capture_output=True,
    text=True,
    cwd=str(d),
)
import json

def pid_from(stdout: str):
    line = [ln for ln in stdout.splitlines() if ln.strip()][-1]
    rec = json.loads(line)
    return rec["steps"][0]["before"].get("pid")

p1 = pid_from(proc1.stdout)
p2 = pid_from(proc2.stdout)
log(f"\n===== exec_pid_snap p1={p1} p2={p2} differ={p1 != p2} =====")
(CASES / "exec_pid_snap.out").write_text(
    f"p1={p1}\np2={p2}\ndiffer={p1 != p2}\n---1---\n{proc1.stdout}\n---2---\n{proc2.stdout}\n",
    encoding="utf-8",
)

# --- leakorder sibling should not be this CLI ---
leakorder = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder"
)
if leakorder.exists():
    cmp2 = subprocess.run(["cmp", str(CLI), str(leakorder)], capture_output=True)
    log(f"\n===== cmp ordleak vs leakorder rc={cmp2.returncode} (1 means different) =====")

# --- hunt leaked none next to exposing across recorded cases ---
log("\n===== HUNT leaked none next to exposing_order =====")
hits = []
for out in sorted(CASES.glob("*.out")):
    text = out.read_text(encoding="utf-8")
    rows = parse_rows(text)
    exposing = rows_kind(rows, "exposing_order")
    leaked = rows_kind(rows, "leaked")
    if not exposing:
        continue
    exp = exposing[0][1] if len(exposing[0]) > 1 else ""
    leakv = leaked[0][1] if leaked and len(leaked[0]) > 1 else "<missing>"
    if exp != "none" and leakv == "none":
        hits.append(f"{out.name}: exposing={exp} leaked={leakv}")
        log(f"HIT {out.name}: exposing={exp} leaked={leakv}")
    elif exp != "none":
        log(f"ok  {out.name}: exposing={exp} leaked={leakv}")
    else:
        log(f"--  {out.name}: exposing=none leaked={leakv}")
if not hits:
    log("NO HITS: leaked none never sat next to exposing_order in these cases")

# --- deepcopy absence in process: import CLI module and check ---
log("\n===== import CLI; copy.deepcopy in source =====")
src = CLI.read_text(encoding="utf-8")
log(f"has deepcopy={('deepcopy' in src)}")
log(f"has subprocess.run={('subprocess.run' in src)}")
log(f"has --exec-order={('--exec-order' in src)}")
log(f"has copy.deepcopy call={('copy.deepcopy' in src)}")

LOG.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
log(f"\nWrote {LOG}")
