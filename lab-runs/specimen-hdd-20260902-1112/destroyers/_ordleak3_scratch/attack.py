#!/usr/bin/env python3
"""Host-executed DESTROYER_ordleak_3 attacks. Writes attack.log + cases/."""

from __future__ import annotations

import os
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
LEAKORDER = Path(
    "/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-leakorder/leakorder"
)

CASES.mkdir(parents=True, exist_ok=True)
LOG = SCRATCH / "attack.log"
lines_out: list[str] = []
HONOR: dict[str, str] = {}
KILL_HITS: list[str] = []


def log(msg: str = "") -> None:
    lines_out.append(msg)
    print(msg, flush=True)


def parse_rows(text: str) -> list[list[str]]:
    return [line.split("\t") for line in text.splitlines() if line]


def rows_kind(rows: list[list[str]], kind: str) -> list[list[str]]:
    return [row for row in rows if row and row[0] == kind]


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


def dual_fail_looks_clean(proc: subprocess.CompletedProcess) -> bool:
    rows = parse_rows(proc.stdout)
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


log("# DESTROYER_ordleak_3 host attacks")
log(f"CLI={CLI}")

# --- owned / unseen specimens ---
proc = run([str(S009), "test_a", "test_b"])
dump("s009", proc)
hunt(proc, "s009")

proc = run([str(S012), "test_a", "test_b"])
dump("s012", proc)
hunt(proc, "s012")
cmp_rc = subprocess.run(["cmp", str(S009), str(S012)], capture_output=True)
log(f"\n===== cmp s009 vs s012 rc={cmp_rc.returncode} =====")

proc = run([str(S060), "test_a", "test_b"])
dump("s060_box_bucket", proc)
hunt(proc, "s060")

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
rows = parse_rows(proc.stdout)
if rows_kind(rows, "leaked") and rows_kind(rows, "leaked")[0][1] not in ("none",):
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
if dual_fail_looks_clean(proc):
    KILL_HITS.append("dual-FAIL-looks-clean:demo_smear")
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

# --- 1. same-process helper smear ---
pid_marker = Path("/tmp/ordleak3-pids.txt")
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
# reverse order is statuses[2] test_b first: must be n=10 not leftover n=11
if any("n=11" in d for d in details):
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
    sys.modules["ordleak3_smear"] = type(sys)("ordleak3_smear")

def test_b():
    assert "ordleak3_smear" not in sys.modules, "smeared"
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("sysmodules_smear", proc)
hunt(proc, "sysmodules")
rows = parse_rows(proc.stdout)
# reverse test_b should PASS if isolated
rev_b = [s for s in rows_kind(rows, "status") if s[1] == "test_b"]
log(f"sysmodules test_b statuses={[s[2] for s in rev_b]}")
if len(rev_b) >= 2 and rev_b[1][2] != "PASS":
    KILL_HITS.append("same-process:sys.modules reverse dirty")

# helper writes next to its own __file__ (copy isolation)
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
from pathlib import Path

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
rows = parse_rows(proc.stdout)
# reverse test_b PASS + named bucket leak expected
statuses = rows_kind(rows, "status")
if statuses and len(statuses) >= 3 and statuses[2][2] != "PASS":
    KILL_HITS.append("same-process:helper __file__ marker reverse dirty")

# --- 3. import-time noise ---
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
if rows_kind(parse_rows(proc.stdout), "leaked")[0][1] != "none" or proc.returncode != 0:
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
if rows_kind(parse_rows(proc.stdout), "leaked")[0][1] != "none":
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
if rows_kind(parse_rows(proc.stdout), "leaked")[0][1] != "none":
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

# --- 4. nested / relative / parent / deeper ---
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
HONOR["nested_pkg"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

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
if no_module_named(proc):
    log("LEFTOVER from ..helper did not load (copy bound / package member)")
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
HONOR["src_layout"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"

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
HONOR["two_up_helper"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"
if "No module named 'helper'" in (proc.stderr or ""):
    KILL_HITS.append("nested-helper-noload:two_up bare No module named")

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
    log("LEFTOVER namespace pkg (no __init__.py) did not load")

d = write_case(
    "hidden_helper",
    {
        ".hidden/helper.py": "bucket = []\n",
        "test_mod.py": """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / ".hidden"))
from helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("hidden_helper", proc)
hunt(proc, "hidden_helper")
HONOR["hidden_helper"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:200]!r}"

# parent too wide (>60 entries) should refuse copy of parent helpers
wide = CASES / "parent_too_wide"
if wide.exists():
    shutil.rmtree(wide)
wide.mkdir(parents=True)
(wide / "helper.py").write_text("bucket = []\n", encoding="utf-8")
sub = wide / "sub"
sub.mkdir()
(sub / "test_mod.py").write_text(
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
for i in range(61):
    (wide / f"pad_{i:02d}.txt").write_text("x\n", encoding="utf-8")
proc = run([str(sub / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("parent_too_wide", proc)
hunt(proc, "parent_too_wide")
HONOR["parent_too_wide"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"
if "No module named 'helper'" in (proc.stderr or ""):
    log("LEFTOVER parent_too_wide still bare No module named")

# --- 5. dual-FAIL smear ---
hard = Path("/tmp/ordleak3-hard.marker")
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
    KILL_HITS.append("dual-FAIL-looks-clean:hard_tmp")
    HONOR["hard_tmp"] = "CLEAN-PAIR LIE"
else:
    HONOR["hard_tmp"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')} leftover={hard.exists()}"
hard.unlink(missing_ok=True)

home_mark = Path.home() / ".ordleak3-home.marker"
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
if dual_fail_looks_clean(proc):
    KILL_HITS.append("dual-FAIL-looks-clean:home_smear")
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
if dual_fail_looks_clean(proc):
    KILL_HITS.append("dual-FAIL-looks-clean:always_fail")

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
    f"exposing={rows_kind(parse_rows(proc.stdout),'exposing_order')} "
    f"leaked={rows_kind(parse_rows(proc.stdout),'leaked')} rc={proc.returncode}"
)

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
hunt(proc, "sibling_marker")

# --- leftovers: custom __eq__, lru_cache, pytest, slots private, property ---
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
HONOR["custom_eq"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

d = write_case(
    "custom_eq_no_fields",
    {
        "test_mod.py": """
class Box:
    def __init__(self):
        object.__setattr__(self, "_hidden", 0)
    def __eq__(self, other):
        return True
    def __repr__(self):
        return "Box()"
    def bump(self):
        object.__setattr__(self, "_hidden", object.__getattribute__(self, "_hidden") + 1)
    def val(self):
        return object.__getattribute__(self, "_hidden")

box = Box()

def test_a():
    box.bump()

def test_b():
    assert box.val() == 0, box.val()
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("custom_eq_no_fields", proc)
hunt(proc, "custom_eq_no_fields")
HONOR["custom_eq_no_fields"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

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
HONOR["lru_cache"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"
if leaked_none_next_to_exposing(proc):
    KILL_HITS.append("lru_cache leaked none beside exposing")

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
HONOR["pytest_fixture"] = f"rc={proc.returncode} status={rows_kind(parse_rows(proc.stdout),'status')}"

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
HONOR["slots_private"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

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
HONOR["property_store"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

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
HONOR["getattr_store"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

# logging / contextvars / decimal / warnings / random — process isolated so reverse PASS, split is unseen or named
d = write_case(
    "logging_mod",
    {
        "test_mod.py": """
import logging

def test_a():
    logging.getLogger("ordleak3").handlers.append(logging.NullHandler())

def test_b():
    assert logging.getLogger("ordleak3").handlers == []
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("logging_mod", proc)
hunt(proc, "logging")

d = write_case(
    "contextvars",
    {
        "test_mod.py": """
from contextvars import ContextVar
v = ContextVar("ordleak3", default=0)

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
hunt(proc, "helper_as_acc")

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
hunt(proc, "instance_bucket")

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
        assert self.acc == [], self.acc
"""
    },
)
proc = run([str(d / "test_mod.py"), "TestOrder.test_a", "TestOrder.test_b"])
dump("unittest_case", proc)
hunt(proc, "unittest_case")

d = write_case(
    "missing_import",
    {
        "test_mod.py": """
import totally_not_a_module_ordleak3

def test_a():
    pass

def test_b():
    pass
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("missing_import", proc)
HONOR["missing_import"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"

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
HONOR["datafile_helper"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"

d = write_case(
    "symlink_helper",
    {
        "outside/helper.py": "bucket = []\n",
        "test_mod.py": """
from helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    },
)
src = CASES / "symlink_helper" / "outside" / "helper.py"
dst = CASES / "symlink_helper" / "helper.py"
try:
    dst.symlink_to(src)
except OSError as exc:
    log(f"symlink failed: {exc}")
proc = run([str(CASES / "symlink_helper" / "test_mod.py"), "test_a", "test_b"], cwd="/tmp")
dump("symlink_helper", proc)
hunt(proc, "symlink_helper")
HONOR["symlink_helper"] = f"rc={proc.returncode} stderr={(proc.stderr or '')[:240]!r}"

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
hunt(proc, "tab_newline")

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
hunt(proc, "systemexit")

d = write_case(
    "stdout_pollute",
    {
        "test_mod.py": """
def test_a():
    print('{"order": ["spoof"]}')

def test_b():
    print("not-json")
    assert True
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("stdout_pollute", proc)
hunt(proc, "stdout_pollute")

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
    "unicode_names",
    {
        "test_mod.py": """
バケツ = []

def 試験甲():
    バケツ.append("a")

def 試験乙():
    assert バケツ == [], バケツ
"""
    },
)
proc = run([str(d / "test_mod.py"), "試験甲", "試験乙"])
dump("unicode_names", proc)
hunt(proc, "unicode_names")

d = write_case(
    "del_create",
    {
        "test_mod.py": """
acc = []

def test_a():
    global acc
    del acc

def test_b():
    acc
"""
    },
)
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("del_create", proc)
hunt(proc, "del_create")

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
HONOR["import_inside_test"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

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
HONOR["thread_local"] = f"rc={proc.returncode} leaked={rows_kind(parse_rows(proc.stdout),'leaked')}"

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
# import-time pid differs across subprocesses; must NOT be a leak
proc = run([str(d / "test_mod.py"), "test_a", "test_b"])
dump("exec_pid_snap", proc)
hunt(proc, "exec_pid_snap")
if rows_kind(parse_rows(proc.stdout), "leaked")[0][1] != "none":
    KILL_HITS.append("pid-import-time-reported-as-leak")

# caller PYTHONPATH pointing at original tree must not smear (worker overwrites)
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

# hunt across all dumped transcripts
log("\n===== HONOR KILL HUNT =====")
for out in sorted(CASES.glob("*.out")):
    text = out.read_text(encoding="utf-8")
    proc_like = subprocess.CompletedProcess(args=[], returncode=0, stdout=text, stderr="")
    if leaked_none_next_to_exposing(proc_like):
        KILL_HITS.append(f"transcript-leaked-none:{out.name}")
        log(f"HIT {out.name}")

log("\n===== HONOR SUMMARY =====")
for k, v in HONOR.items():
    log(f"{k}: {v}")
log(f"KILL_HITS={KILL_HITS!r}")
log(f"KILL_HITS_N={len(KILL_HITS)}")

LOG.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
(SCRATCH / "kill_hits.txt").write_text(repr(KILL_HITS) + "\n", encoding="utf-8")
