#!/usr/bin/env python3
"""Host-executed DESTROYER_ordleak_4 attacks. Writes attack.log + cases/."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
CASES = SCRATCH / "cases"
CLI = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak"
)
ROOT = CLI.parent
S009 = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009/files/test_order.py"
)
S012 = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-012/files/test_order.py"
)
S060 = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-060/files/test_class_leak.py"
)
RUN_ORDERS = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009/files/run_orders.py"
)
HELPER = ROOT / "tests/fixtures/helper/test_order.py"
HELPER_IMPORT = ROOT / "tests/fixtures/helper/test_import.py"
PKG_FROM = ROOT / "tests/fixtures/pkg/test_from_pkg.py"
PKG_REL = ROOT / "tests/fixtures/pkg/test_relative.py"
PARENT_HELPER = ROOT / "tests/fixtures/parent_helper/sub/test_order.py"
STAMP = ROOT / "tests/fixtures/test_stamp.py"
ENV = ROOT / "tests/fixtures/test_env.py"
SLOTS = ROOT / "tests/fixtures/test_slots.py"
BINARY = ROOT / "tests/fixtures/test_binary.py"
SMEAR = ROOT / "tests/fixtures/test_smear.py"
CLASS_METHOD = ROOT / "tests/fixtures/test_class_method.py"
PRIVATE = ROOT / "tests/fixtures/test_private.py"
FS = ROOT / "tests/fixtures/test_fs.py"
CLASS_ATTR = ROOT / "tests/fixtures/test_class_attr.py"
LEAKORDER = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder"
)

CASES.mkdir(parents=True, exist_ok=True)
LOG = SCRATCH / "attack.log"
lines_out: list[str] = []
HONOR: dict[str, str] = {}
KILL_HITS: list[str] = []
LEFTOVER: dict[str, str] = {}


def log(msg: str = "") -> None:
    lines_out.append(msg)
    print(msg, flush=True)


def parse_rows(text: str) -> list[list[str]]:
    return [line.split("\t") for line in text.splitlines() if line]


def rows_kind(rows: list[list[str]], kind: str) -> list[list[str]]:
    return [row for row in rows if row and row[0] == kind]


def leaked_names(proc: subprocess.CompletedProcess) -> list[str]:
    return [row[1] for row in rows_kind(parse_rows(proc.stdout or ""), "leaked") if len(row) > 1]


def exposing_val(proc: subprocess.CompletedProcess) -> str:
    rows = rows_kind(parse_rows(proc.stdout or ""), "exposing_order")
    if not rows or len(rows[0]) < 2:
        return ""
    return rows[0][1]


def run(
    args: list[str],
    *,
    cwd: str | None = None,
    env: dict | None = None,
    timeout: int = 25,
) -> subprocess.CompletedProcess:
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
    rows = parse_rows(proc.stdout or "")
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


def dual_fail_looks_clean(proc: subprocess.CompletedProcess) -> bool:
    rows = parse_rows(proc.stdout or "")
    statuses = rows_kind(rows, "status")
    leaked = rows_kind(rows, "leaked")
    failish = [s for s in statuses if len(s) > 2 and s[2] in ("FAIL", "ERROR")]
    if not failish:
        return False
    if proc.returncode == 0:
        return True
    if leaked and leaked[0][1] == "none":
        return True
    return False


def no_module_named(proc: subprocess.CompletedProcess) -> bool:
    blob = (proc.stderr or "") + (proc.stdout or "")
    return "No module named" in blob or "relative import" in blob.lower()


def hunt(proc: subprocess.CompletedProcess, name: str) -> None:
    if leaked_none_next_to_exposing(proc):
        KILL_HITS.append(f"leaked-none-beside-exposing:{name}")
        log(f"HONOR-KILL HIT leaked none next to exposing_order ≠ none [{name}]")
    if dual_fail_looks_clean(proc):
        KILL_HITS.append(f"dual-FAIL-looks-clean:{name}")
        log(f"HONOR-KILL HIT dual-FAIL looks clean [{name}]")


log("# DESTROYER_ordleak_4 host attacks")
log(f"CLI={CLI}")

# --- owned / unseen ---
proc = run([str(S009), "test_a", "test_b"])
dump("s009", proc)
hunt(proc, "s009")
HONOR["s009"] = f"rc={proc.returncode} exposing={exposing_val(proc)} leaked={leaked_names(proc)}"

proc = run([str(S012), "test_a", "test_b"])
dump("s012", proc)
hunt(proc, "s012")
cmp_rc = subprocess.run(["cmp", str(S009), str(S012)], capture_output=True)
log(f"\n===== cmp s009 vs s012 rc={cmp_rc.returncode} =====")

proc = run([str(S060), "test_a", "test_b"])
dump("s060_box_bucket", proc)
hunt(proc, "s060")
HONOR["s060"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

proc = run([str(HELPER), "test_a", "test_b"])
dump("helper_from_import", proc)
hunt(proc, "helper_from_import")

proc = run([str(HELPER_IMPORT), "test_a", "test_b"])
dump("helper_import_module", proc)
hunt(proc, "helper_import_module")

proc = run([str(PKG_FROM), "test_a", "test_b"], cwd="/tmp")
dump("pkg_from_cwd_tmp", proc)
hunt(proc, "pkg_from")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:pkg_from")
HONOR["pkg_from"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

proc = run([str(PKG_REL), "test_a", "test_b"], cwd="/tmp")
dump("pkg_relative_cwd_tmp", proc)
hunt(proc, "pkg_rel")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:pkg_rel")

proc = run([str(PARENT_HELPER), "test_a", "test_b"], cwd="/tmp")
dump("parent_helper_cwd_tmp", proc)
hunt(proc, "parent_helper")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:parent_helper")

proc = run([str(STAMP), "test_a", "test_b"])
dump("stamp_time_ns", proc)
hunt(proc, "stamp")
if leaked_names(proc) != ["none"] or proc.returncode != 0:
    KILL_HITS.append("time_ns-reported-as-leak")

proc = run([str(ENV), "test_a", "test_b"])
dump("env_unseen", proc)
hunt(proc, "env")

proc = run([str(SLOTS), "test_a", "test_b"])
dump("slots_fixture", proc)
hunt(proc, "slots_fixture")

proc = run([str(BINARY), "test_a", "test_b"])
dump("binary_stdout", proc)
hunt(proc, "binary")
if "codec can't decode" in (proc.stderr or ""):
    log("LEFTOVER binary stdout still utf-8 crash")

proc = run([str(SMEAR), "test_a", "test_b"])
dump("demo_smear", proc)
hunt(proc, "demo_smear")
Path("/tmp/ordleak-demo-smear.marker").unlink(missing_ok=True)

proc = run([str(CLASS_METHOD), "TestOrder.test_a", "TestOrder.test_b"])
dump("class_method", proc)
hunt(proc, "class_method")

proc = run([str(PRIVATE), "test_a", "test_b"])
dump("private_acc", proc)
hunt(proc, "private")

proc = run([str(FS), "test_a", "test_b"])
dump("fs_sibling", proc)
hunt(proc, "fs")

proc = run([str(CLASS_ATTR), "test_a", "test_b"])
dump("class_attr", proc)
hunt(proc, "class_attr")

# leakorder is leftover-after, not this object
if LEAKORDER.is_file():
    lo = subprocess.run(
        [sys.executable, str(LEAKORDER), str(S009), "test_a", "test_b"],
        check=False,
        capture_output=True,
        text=True,
        timeout=25,
    )
    log("\n===== leakorder s009 rc=%s =====" % lo.returncode)
    log((lo.stdout or "")[:800])
    (CASES / "leakorder_s009.out").write_text(lo.stdout or "", encoding="utf-8")
    (CASES / "leakorder_s009.err").write_text(lo.stderr or "", encoding="utf-8")
    (CASES / "leakorder_s009.rc").write_text(str(lo.returncode), encoding="utf-8")

# --- Honor KILL 1: same-process helper smear ---
pid_marker = Path("/tmp/ordleak4-pids.txt")
pid_marker.unlink(missing_ok=True)
d = write_case(
    "pid_isolation",
    {
        "test_mod.py": f"""
import os
from pathlib import Path

PIDFILE = Path({str(pid_marker)!r})

def _w(tag):
    prev = PIDFILE.read_text() if PIDFILE.exists() else ""
    PIDFILE.write_text(prev + f"{{tag}} {{os.getpid()}}\\n")

def test_a():
    _w("a")

def test_b():
    _w("b")
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
iso = "YES" if len(unique_pids) >= 2 else "NO SAME-PROCESS"
log(f"subprocess_isolation={iso}")
HONOR["subprocess_isolation"] = iso
if iso != "YES":
    KILL_HITS.append("same-process:pidfile")
pid_marker.unlink(missing_ok=True)

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
hunt(proc, "helper_counter")
rows = parse_rows(proc.stdout)
statuses = rows_kind(rows, "status")
details = [s[3] if len(s) > 3 else "" for s in statuses]
log(f"helper_counter details={details}")
if any("n=11" in x for x in details):
    KILL_HITS.append("same-process-helper-smear:n=11")
    HONOR["helper_smear"] = "DIRTY n=11"
else:
    HONOR["helper_smear"] = "clean reverse n=10 (no leftover 11)"

d = write_case(
    "sysmodules_smear",
    {
        "test_mod.py": """
import sys

def test_a():
    sys.modules["ordleak4_smear"] = type(sys)("ordleak4_smear")

def test_b():
    assert "ordleak4_smear" not in sys.modules, "smeared"
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("sysmodules_smear", proc)
hunt(proc, "sysmodules")
rev_b = [s for s in rows_kind(parse_rows(proc.stdout), "status") if s[1] == "test_b"]
log(f"sysmodules test_b statuses={[s[2] for s in rev_b]}")
if len(rev_b) >= 2 and rev_b[1][2] != "PASS":
    KILL_HITS.append("same-process:sys.modules reverse dirty")

d = write_case(
    "helper_file_marker",
    {
        "helper.py": """
from pathlib import Path
MARKER = Path(__file__).resolve().with_name("side.marker")
bucket = []
""",
        "test_mod.py": """
import helper

def test_a():
    helper.MARKER.write_text("a", encoding="utf-8")
    helper.bucket.append("a")

def test_b():
    assert not helper.MARKER.exists(), "marker smeared"
    assert helper.bucket == [], helper.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("helper_file_marker", proc)
hunt(proc, "helper_file_marker")
statuses = rows_kind(parse_rows(proc.stdout), "status")
if statuses and len(statuses) >= 3 and statuses[2][2] != "PASS":
    KILL_HITS.append("same-process:helper __file__ marker reverse dirty")

# caller PYTHONPATH pointing at original tree must not smear
d = write_case(
    "pythonpath_original",
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
env = os.environ.copy()
env["PYTHONPATH"] = str(d) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], env=env)
dump("pythonpath_original", proc)
hunt(proc, "pythonpath_original")
details = [s[3] if len(s) > 3 else "" for s in rows_kind(parse_rows(proc.stdout), "status")]
if any("n=11" in x for x in details):
    KILL_HITS.append("same-process-helper-smear:pythonpath n=11")

# --- Honor KILL 3: import-time noise ---
d = write_case(
    "object_id",
    {
        "test_mod.py": """
token = object()

def test_a():
    pass

def test_b():
    pass
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("object_id", proc)
hunt(proc, "object_id")
if leaked_names(proc) != ["none"] or proc.returncode != 0:
    KILL_HITS.append("object()-reported-as-leak")

d = write_case(
    "nan_clean",
    {
        "test_mod.py": """
nan = float("nan")

def test_a():
    pass

def test_b():
    pass
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("nan_clean", proc)
hunt(proc, "nan_clean")
if leaked_names(proc) != ["none"]:
    KILL_HITS.append("nan-reported-as-leak")

d = write_case(
    "dataclass_identity",
    {
        "test_mod.py": """
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
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("dataclass_identity", proc)
hunt(proc, "dataclass_identity")
if leaked_names(proc) != ["none"]:
    KILL_HITS.append("dataclass-type-identity-reported-as-leak")

d = write_case(
    "dataclass_mut",
    {
        "test_mod.py": """
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
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("dataclass_mut", proc)
hunt(proc, "dataclass_mut")

d = write_case(
    "nan_mutate",
    {
        "test_mod.py": """
box = {"n": float("nan")}

def test_a():
    box["n"] = 1.0

def test_b():
    import math
    assert math.isnan(box["n"]), box["n"]
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("nan_mutate", proc)
hunt(proc, "nan_mutate")

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
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("exec_pid_snap", proc)
hunt(proc, "exec_pid_snap")
if leaked_names(proc) != ["none"]:
    KILL_HITS.append("pid-import-time-reported-as-leak")

# --- Honor KILL 4: nested / relative / parent ---
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
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("nested_pkg", proc)
hunt(proc, "nested_pkg")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:nested_pkg")
HONOR["nested_pkg"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

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
proc = run([str(d / "pkg/test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("relative_import", proc)
hunt(proc, "relative_import")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:relative")

d = write_case(
    "relative_parent",
    {
        "pkg/__init__.py": "",
        "pkg/helper.py": "bucket = []\n",
        "pkg/sub/__init__.py": "",
        "pkg/sub/test_mod.py": """
from ..helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "pkg/sub/test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("relative_parent", proc)
hunt(proc, "relative_parent")
if "No module named" in (proc.stderr or ""):
    KILL_HITS.append("nested-helper-noload:relative_parent bare")
HONOR["relative_parent"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:200]!r}"

d = write_case(
    "helper_package",
    {
        "helper/__init__.py": "bucket = []\n",
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
dump("helper_package", proc)
hunt(proc, "helper_package")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:helper_package")

d = write_case(
    "namespace_pkg",
    {
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
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("namespace_pkg", proc)
hunt(proc, "namespace_pkg")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:namespace_pkg")

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
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/")
dump("cwd_elsewhere", proc)
hunt(proc, "cwd_elsewhere")
if no_module_named(proc):
    KILL_HITS.append("nested-helper-noload:cwd_elsewhere")

d = write_case(
    "src_layout",
    {
        "src/pkg/__init__.py": "",
        "src/pkg/helper.py": "bucket = []\n",
        "tests/test_mod.py": """
from pkg.helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "tests/test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("src_layout", proc)
hunt(proc, "src_layout")
if "No module named" in (proc.stderr or ""):
    KILL_HITS.append("nested-helper-noload:src_layout bare")
LEFTOVER["src_layout"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"

d = write_case(
    "two_up_helper",
    {
        "helper.py": "bucket = []\n",
        "mid/sub/test_mod.py": """
from helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "mid/sub/test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("two_up_helper", proc)
hunt(proc, "two_up_helper")
if "No module named 'helper'" in (proc.stderr or ""):
    KILL_HITS.append("nested-helper-noload:two_up bare No module named")
LEFTOVER["two_up_helper"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"

# --- Honor KILL 5: dual-FAIL smear ---
hard = Path("/tmp/ordleak4-hard.marker")
hard.unlink(missing_ok=True)
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
hunt(proc, "hard_tmp")
if dual_fail_looks_clean(proc):
    HONOR["hard_tmp"] = "CLEAN-PAIR LIE"
else:
    HONOR["hard_tmp"] = (
        f"rc={proc.returncode} leaked={leaked_names(proc)} leftover={hard.exists()}"
    )
hard.unlink(missing_ok=True)

home_mark = Path.home() / ".ordleak4-home.marker"
home_mark.unlink(missing_ok=True)
d = write_case(
    "home_smear",
    {
        "test_mod.py": f"""
from pathlib import Path
MARKER = Path({str(home_mark)!r})

def test_a():
    MARKER.write_text("a", encoding="utf-8")

def test_b():
    assert not MARKER.exists(), MARKER.read_text(encoding="utf-8")
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("home_smear", proc)
hunt(proc, "home_smear")
home_mark.unlink(missing_ok=True)

d = write_case(
    "always_fail",
    {
        "test_mod.py": """
def test_a():
    pass

def test_b():
    assert False
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("always_fail", proc)
hunt(proc, "always_fail")

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
hunt(proc, "always_fail_leak")
HONOR["always_fail_leak"] = (
    f"exposing={exposing_val(proc)} leaked={leaked_names(proc)} rc={proc.returncode}"
)

# --- Honor KILL 6: THIN_WRAPPER of two greps ---
ro = subprocess.run(
    [sys.executable, str(RUN_ORDERS)],
    check=False,
    capture_output=True,
    text=True,
    timeout=10,
)
(CASES / "run_orders.out").write_text(ro.stdout or "", encoding="utf-8")
log("\n===== run_orders.py =====")
log((ro.stdout or "").rstrip("\n"))
grep_fail = subprocess.run(
    ["grep", "-nE", "FAIL|PASS|acc_after"],
    input=ro.stdout or "",
    capture_output=True,
    text=True,
    check=False,
)
(CASES / "two_greps_run_orders.out").write_text(grep_fail.stdout or "", encoding="utf-8")
log("\n===== two greps of run_orders.py =====")
log((grep_fail.stdout or "").rstrip("\n"))
s009_out = (CASES / "s009.out").read_text(encoding="utf-8")
has_join = (
    "leaked\tacc\tinto\ttest_b\t[]\t['a']\tvia\ttest_a" in s009_out
    or "leaked\tacc\tinto\ttest_b" in s009_out
)
s060_out = (CASES / "s060_box_bucket.out").read_text(encoding="utf-8")
helper_out = (CASES / "helper_from_import.out").read_text(encoding="utf-8")
pkg_out = (CASES / "pkg_from_cwd_tmp.out").read_text(encoding="utf-8")
join_beyond_grep = (
    "Box.bucket" in s060_out
    and "bucket" in helper_out
    and "bucket" in pkg_out
    and "into" in s009_out
    and "via" in s009_out
)
# replica: two greps cannot name Box.bucket or start-of-victim [] vs ['a']
replica_names_box = "Box.bucket" in (grep_fail.stdout or "")
replica_names_into_via = "into" in (grep_fail.stdout or "") and "via" in (grep_fail.stdout or "")
HONOR["thin_wrapper"] = (
    f"run_orders_has_acc_after={'acc_after' in (ro.stdout or '')} "
    f"grep_names_Box.bucket={replica_names_box} "
    f"grep_has_into_via={replica_names_into_via} "
    f"ordleak_join={has_join} beyond_grep={join_beyond_grep}"
)
if replica_names_box and replica_names_into_via and not join_beyond_grep:
    KILL_HITS.append("THIN_WRAPPER of two greps")
if not has_join or not join_beyond_grep:
    KILL_HITS.append("THIN_WRAPPER: join missing")
log(f"THIN_WRAPPER honor={HONOR['thin_wrapper']}")

# naive two-order grep replica on a helper pair: caller already knows FAIL/PASS
naive = subprocess.run(
    ["grep", "-nE", "FAIL|PASS|leaked|exposing"],
    input=(CASES / "helper_from_import.out").read_text(encoding="utf-8"),
    capture_output=True,
    text=True,
    check=False,
)
(CASES / "two_greps_helper.out").write_text(naive.stdout or "", encoding="utf-8")
# The grep is of ordleak output, not a replica of the object. Object is the join
# that produced that output. Two greps of FAIL/PASS on the source file:
src_grep = subprocess.run(
    ["grep", "-nE", "acc|bucket|append|assert", str(HELPER), str(HELPER.parent / "helper.py")],
    capture_output=True,
    text=True,
    check=False,
)
(CASES / "two_greps_helper_src.out").write_text(src_grep.stdout or "", encoding="utf-8")
log("\n===== two greps of helper source =====")
log((src_grep.stdout or "").rstrip("\n"))
if "into" not in (src_grep.stdout or "") and "[]" not in "".join(leaked_names(run([str(HELPER), "test_a", "test_b"]))):
    pass  # join lives in CLI output, not in source greps

# --- leftover-identity probes (DESTROYER_2 ceilings + copy-tree leftovers) ---
d = write_case(
    "slots_private",
    {
        "test_mod.py": """
class Box:
    __slots__ = ("_n",)
    def __init__(self):
        self._n = 0

box = Box()

def test_a():
    box._n += 1

def test_b():
    assert box._n == 0, box._n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("slots_private", proc)
hunt(proc, "slots_private")
LEFTOVER["slots_private"] = (
    f"rc={proc.returncode} exposing={exposing_val(proc)} leaked={leaked_names(proc)}"
)

d = write_case(
    "dataclass_private",
    {
        "test_mod.py": """
from dataclasses import dataclass

@dataclass
class S:
    _n: int = 0

state = S()

def test_a():
    state._n += 1

def test_b():
    assert state._n == 0, state._n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("dataclass_private", proc)
hunt(proc, "dataclass_private")
LEFTOVER["dataclass_private"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "instance_private_dict",
    {
        "test_mod.py": """
class Box:
    def __init__(self):
        self._n = 0

box = Box()

def test_a():
    box._n += 1

def test_b():
    assert box._n == 0, box._n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("instance_private_dict", proc)
hunt(proc, "instance_private_dict")
LEFTOVER["instance_private_dict"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "import_pkg_attr",
    {
        "pkg/__init__.py": "",
        "pkg/helper.py": "bucket = []\n",
        "test_mod.py": """
import pkg.helper

def test_a():
    pkg.helper.bucket.append("a")

def test_b():
    assert pkg.helper.bucket == [], pkg.helper.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("import_pkg_attr", proc)
hunt(proc, "import_pkg_attr")
LEFTOVER["import_pkg_attr"] = (
    f"rc={proc.returncode} exposing={exposing_val(proc)} leaked={leaked_names(proc)}"
)

d = write_case(
    "import_pkg_then_helper",
    {
        "pkg/__init__.py": "",
        "pkg/helper.py": "bucket = []\n",
        "test_mod.py": """
import pkg

def test_a():
    pkg.helper.bucket.append("a")

def test_b():
    assert pkg.helper.bucket == [], pkg.helper.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("import_pkg_then_helper", proc)
hunt(proc, "import_pkg_then_helper")
LEFTOVER["import_pkg_then_helper"] = (
    f"rc={proc.returncode} exposing={exposing_val(proc)} leaked={leaked_names(proc)}"
)

d = write_case(
    "helper_class_attr",
    {
        "helper.py": """
class Box:
    bucket = []
""",
        "test_mod.py": """
import helper

def test_a():
    helper.Box.bucket.append("a")

def test_b():
    assert helper.Box.bucket == [], helper.Box.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("helper_class_attr", proc)
hunt(proc, "helper_class_attr")
LEFTOVER["helper_class_attr"] = (
    f"rc={proc.returncode} exposing={exposing_val(proc)} leaked={leaked_names(proc)}"
)

d = write_case(
    "helper_private_global",
    {
        "helper.py": "_acc = []\n",
        "test_mod.py": """
import helper

def test_a():
    helper._acc.append("a")

def test_b():
    assert helper._acc == [], helper._acc
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("helper_private_global", proc)
hunt(proc, "helper_private_global")
LEFTOVER["helper_private_global"] = (
    f"rc={proc.returncode} exposing={exposing_val(proc)} leaked={leaked_names(proc)}"
)

d = write_case(
    "star_import",
    {
        "helper.py": "bucket = []\n_hidden = []\n",
        "test_mod.py": """
from helper import *

def test_a():
    bucket.append("a")
    _hidden.append("x")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("star_import", proc)
hunt(proc, "star_import")
LEFTOVER["star_import"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "property_store",
    {
        "test_mod.py": """
class Box:
    def __init__(self):
        self._n = 0
    @property
    def n(self):
        return self._n
    @n.setter
    def n(self, v):
        self._n = v

box = Box()

def test_a():
    box.n += 1

def test_b():
    assert box.n == 0, box.n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("property_store", proc)
hunt(proc, "property_store")
LEFTOVER["property_store"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "getattr_store",
    {
        "test_mod.py": """
class Box:
    def __init__(self):
        object.__setattr__(self, "_store", {"n": 0})
    def __getattr__(self, name):
        return object.__getattribute__(self, "_store")[name]
    def __setattr__(self, name, value):
        object.__getattribute__(self, "_store")[name] = value

box = Box()

def test_a():
    box.n = 1

def test_b():
    assert box.n == 0, box.n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("getattr_store", proc)
hunt(proc, "getattr_store")
LEFTOVER["getattr_store"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

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
hunt(proc, "custom_eq")
LEFTOVER["custom_eq"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "lru_cache",
    {
        "test_mod.py": """
from functools import lru_cache

@lru_cache(maxsize=8)
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
hunt(proc, "lru_cache")
LEFTOVER["lru_cache"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "import_inside_test",
    {
        "helper.py": "bucket = []\n",
        "test_mod.py": """
def test_a():
    from helper import bucket
    bucket.append("a")

def test_b():
    from helper import bucket
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("import_inside_test", proc)
hunt(proc, "import_inside_test")
LEFTOVER["import_inside_test"] = (
    f"rc={proc.returncode} exposing={exposing_val(proc)} leaked={leaked_names(proc)}"
)

d = write_case(
    "thread_local",
    {
        "test_mod.py": """
import threading
tls = threading.local()

def test_a():
    tls.n = 1

def test_b():
    assert getattr(tls, "n", 0) == 0, getattr(tls, "n", None)
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("thread_local", proc)
hunt(proc, "thread_local")
LEFTOVER["thread_local"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "simple_namespace",
    {
        "test_mod.py": """
from types import SimpleNamespace
box = SimpleNamespace(n=0)

def test_a():
    box.n += 1

def test_b():
    assert box.n == 0, box.n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("simple_namespace", proc)
hunt(proc, "simple_namespace")
LEFTOVER["simple_namespace"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "namedtuple_mut",
    {
        "test_mod.py": """
from collections import namedtuple
Box = namedtuple("Box", "acc")
state = Box(acc=[])

def test_a():
    state.acc.append("a")

def test_b():
    assert state.acc == [], state.acc
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("namedtuple_mut", proc)
hunt(proc, "namedtuple_mut")
LEFTOVER["namedtuple_mut"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "deque_mut",
    {
        "test_mod.py": """
from collections import deque
acc = deque()

def test_a():
    acc.append("a")

def test_b():
    assert list(acc) == [], list(acc)
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("deque_mut", proc)
hunt(proc, "deque_mut")
LEFTOVER["deque_mut"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "module_getattr",
    {
        "helper.py": """
_store = {"n": 0}

def __getattr__(name):
    return _store[name]
""",
        "test_mod.py": """
import helper

def test_a():
    helper._store["n"] = 1

def test_b():
    assert helper.n == 0, helper.n
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("module_getattr", proc)
hunt(proc, "module_getattr")
LEFTOVER["module_getattr"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "missing_import",
    {
        "test_mod.py": """
import totally_not_a_module_ordleak4

def test_a():
    pass

def test_b():
    pass
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("missing_import", proc)
LEFTOVER["missing_import"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"
if "No module named" in (proc.stderr or "") and "outside the copied tree" not in (proc.stderr or ""):
    KILL_HITS.append("nested-helper-noload:missing_import bare")

d = write_case(
    "datafile_helper",
    {
        "helper.py": """
from pathlib import Path
DATA = (Path(__file__).resolve().parent / "payload.txt").read_text(encoding="utf-8")
bucket = []
""",
        "payload.txt": "secret\n",
        "test_mod.py": """
import helper

def test_a():
    helper.bucket.append(helper.DATA)

def test_b():
    assert helper.bucket == [], helper.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("datafile_helper", proc)
hunt(proc, "datafile_helper")
LEFTOVER["datafile_helper"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"

d = write_case(
    "pytest_fixture",
    {
        "test_mod.py": """
def test_a(ready):
    ready.append("a")

def test_b(ready):
    assert ready == []
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("pytest_fixture", proc)
hunt(proc, "pytest_fixture")
LEFTOVER["pytest_fixture"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "two_bindings",
    {
        "test_mod.py": """
acc = []
other = set()

def test_a():
    acc.append("a")
    other.add("x")

def test_b():
    assert acc == [] and other == set(), (acc, other)
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("two_bindings", proc)
hunt(proc, "two_bindings")

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
hunt(proc, "hidden_pass")
HONOR["hidden_pass"] = f"rc={proc.returncode} leaked={leaked_names(proc)} exposing={exposing_val(proc)}"

d = write_case(
    "contextvars",
    {
        "test_mod.py": """
from contextvars import ContextVar
v = ContextVar("ordleak4", default=0)

def test_a():
    v.set(1)

def test_b():
    assert v.get() == 0, v.get()
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("contextvars", proc)
hunt(proc, "contextvars")
LEFTOVER["contextvars"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "logging_mod",
    {
        "test_mod.py": """
import logging

def test_a():
    logging.getLogger("ordleak4").handlers.append(logging.NullHandler())

def test_b():
    assert logging.getLogger("ordleak4").handlers == []
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("logging_mod", proc)
hunt(proc, "logging")
LEFTOVER["logging"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "warnings_filter",
    {
        "test_mod.py": """
import warnings

def test_a():
    warnings.filterwarnings("ignore", category=UserWarning)

def test_b():
    assert warnings.filters[0][0] != "ignore"
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("warnings_filter", proc)
hunt(proc, "warnings")
LEFTOVER["warnings"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "decimal_ctx",
    {
        "test_mod.py": """
from decimal import getcontext

def test_a():
    getcontext().prec = 10

def test_b():
    assert getcontext().prec != 10, getcontext().prec
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("decimal_ctx", proc)
hunt(proc, "decimal")
LEFTOVER["decimal"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

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
hunt(proc, "helper_alias")
HONOR["helper_alias"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "from_pkg_import_helper",
    {
        "pkg/__init__.py": "",
        "pkg/helper.py": "bucket = []\n",
        "test_mod.py": """
from pkg import helper

def test_a():
    helper.bucket.append("a")

def test_b():
    assert helper.bucket == [], helper.bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("from_pkg_import_helper", proc)
hunt(proc, "from_pkg_import_helper")
LEFTOVER["from_pkg_import_helper"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "slots_and_dict",
    {
        "test_mod.py": """
class Box:
    __slots__ = ("n", "__dict__")
    def __init__(self):
        self.n = 0
        self.extra = 0

box = Box()

def test_a():
    box.n += 1
    box.extra += 1

def test_b():
    assert box.n == 0 and box.extra == 0, (box.n, box.extra)
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("slots_and_dict", proc)
hunt(proc, "slots_and_dict")
LEFTOVER["slots_and_dict"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "enum_mut",
    {
        "test_mod.py": """
from enum import Enum
class Color(Enum):
    RED = []
def test_a():
    Color.RED.value.append("a")
def test_b():
    assert Color.RED.value == [], Color.RED.value
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("enum_mut", proc)
hunt(proc, "enum_mut")
LEFTOVER["enum_mut"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

d = write_case(
    "weakref_proxy",
    {
        "test_mod.py": """
import weakref
class Box:
    def __init__(self):
        self.n = 0
box = Box()
proxy = weakref.proxy(box)

def test_a():
    proxy.n += 1

def test_b():
    assert box.n == 0, box.n
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("weakref_proxy", proc)
hunt(proc, "weakref_proxy")
LEFTOVER["weakref_proxy"] = f"rc={proc.returncode} leaked={leaked_names(proc)}"

# hunt across all dumped transcripts
log("\n===== HONOR KILL HUNT =====")
none_beside = []
for out in sorted(CASES.glob("*.out")):
    text = out.read_text(encoding="utf-8")
    proc_like = subprocess.CompletedProcess(args=[], returncode=0, stdout=text, stderr="")
    if leaked_none_next_to_exposing(proc_like):
        KILL_HITS.append(f"transcript-leaked-none:{out.name}")
        none_beside.append(out.name)
        log(f"HIT {out.name}")
log(f"leaked-none-beside-exposing transcripts={none_beside}")

# dual-fail hunt on transcripts that have FAIL in both orders
dual_clean = []
for out in sorted(CASES.glob("*.out")):
    text = out.read_text(encoding="utf-8")
    rc_path = out.with_suffix(".rc")
    rc = int(rc_path.read_text()) if rc_path.exists() else 0
    proc_like = subprocess.CompletedProcess(args=[], returncode=rc, stdout=text, stderr="")
    if dual_fail_looks_clean(proc_like) and out.name not in ("run_orders.out",):
        # skip greps of source
        if out.name.startswith("two_greps"):
            continue
        dual_clean.append(out.name)
        KILL_HITS.append(f"transcript-dual-fail-clean:{out.name}")
        log(f"DUAL-CLEAN HIT {out.name}")
log(f"dual-fail-clean transcripts={dual_clean}")

log("\n===== HONOR SUMMARY =====")
for k, v in HONOR.items():
    log(f"{k}: {v}")
log("\n===== LEFTOVER IDENTITY =====")
for k, v in LEFTOVER.items():
    log(f"{k}: {v}")
log(f"KILL_HITS={KILL_HITS!r}")
log(f"KILL_HITS_N={len(KILL_HITS)}")

LOG.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
(SCRATCH / "kill_hits.txt").write_text(repr(KILL_HITS) + "\n", encoding="utf-8")
(SCRATCH / "honor.txt").write_text(
    "\n".join(f"{k}: {v}" for k, v in HONOR.items()) + "\n", encoding="utf-8"
)
(SCRATCH / "leftover.txt").write_text(
    "\n".join(f"{k}: {v}" for k, v in LEFTOVER.items()) + "\n", encoding="utf-8"
)
