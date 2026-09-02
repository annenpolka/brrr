#!/usr/bin/env python3
"""Host attacks for DESTROYER_leakorder_3. Archive CLI only. No merge."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = ROOT / "lineages/candidate-leakorder/leakorder"
ORD = ROOT / "lineages/candidate-ordleak/ordleak"
S009 = ROOT / "specimens/specimen-009/files/test_order.py"
S012 = ROOT / "specimens/specimen-012/files/test_order.py"
S060 = ROOT / "specimens/specimen-060/files/test_class_leak.py"
FIX = ROOT / "lineages/candidate-leakorder/fixtures"
SCRATCH = ROOT / "destroyers/_leakorder3_scratch"
CASES = SCRATCH / "cases"
LOG = SCRATCH / "attack.log"

CASES.mkdir(parents=True, exist_ok=True)
lines: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    lines.append(msg)


def run(cmd, *, cwd=None, env=None, timeout=40) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        env=env,
        timeout=timeout,
    )


def write_case(name: str, text: str) -> Path:
    path = CASES / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    path.write_text(text, encoding="utf-8")
    return path


def field(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def order_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if ln.startswith("order ")]


def leakorder(path: Path, extra: list[str] | None = None, cwd=None, env=None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(CLI), str(path)]
    if extra:
        cmd[2:2] = extra  # flags before FILE
        # argparse: flags can be anywhere; keep FILE last
        cmd = [sys.executable, str(CLI), *extra, str(path)]
    return run(cmd, cwd=cwd, env=env)


def ordleak(path: Path, left: str, right: str, cwd=None) -> subprocess.CompletedProcess:
    return run([sys.executable, str(ORD), str(path), left, right], cwd=cwd)


def dump(tag: str, proc: subprocess.CompletedProcess) -> None:
    (SCRATCH / f"{tag}.out").write_text(proc.stdout, encoding="utf-8")
    (SCRATCH / f"{tag}.err").write_text(proc.stderr, encoding="utf-8")
    (SCRATCH / f"{tag}.rc").write_text(str(proc.returncode), encoding="utf-8")
    log(f"--- {tag} rc={proc.returncode} ---")
    if proc.stdout:
        log(proc.stdout.rstrip())
    if proc.stderr:
        log("STDERR: " + proc.stderr.rstrip()[:800])


# ---------------------------------------------------------------------------
log("## identity")
log(f"CLI={CLI}")
log(f"ORD={ORD}")
log(f"python={sys.version.split()[0]}")

# ---------------------------------------------------------------------------
log("\n## owned specimens vs sibling")
for tag, path in (("s009", S009), ("s012", S012), ("s060", S060)):
    p = leakorder(path)
    dump(tag, p)
    o = ordleak(path, "test_a", "test_b")
    dump(f"ord_{tag}", o)

p = leakorder(FIX / "helper_pair" / "test_helper.py")
dump("helper_bucket", p)
p = leakorder(FIX / "helper_pair" / "test_helper_n.py")
dump("helper_n", p)
p = leakorder(FIX / "test_private.py")
dump("private", p)
o = ordleak(FIX / "test_private.py", "test_a", "test_b")
dump("ord_private", o)

# ---------------------------------------------------------------------------
log("\n## Honor KILL 1: leaked= on order lines")
hunt_leaked = 0
hunt_none_split = 0
none_split_hits: list[str] = []

# ---------------------------------------------------------------------------
log("\n## Honor KILL 2: isolation pids + helper smear")
pid_py = write_case(
    "pid_probe.py",
    """import os
from pathlib import Path
LOG = Path(__file__).resolve().parent / "pids.txt"
acc = []

def test_a():
    LOG.write_text(LOG.read_text() + f"a {os.getpid()}\\n" if LOG.exists() else f"a {os.getpid()}\\n")
    acc.append("a")

def test_b():
    LOG.write_text(LOG.read_text() + f"b {os.getpid()}\\n" if LOG.exists() else f"b {os.getpid()}\\n")
    assert acc == [], acc
""",
)
(CASES / "pids.txt").unlink(missing_ok=True)
p = leakorder(pid_py)
dump("pid_probe", p)
pids_txt = (CASES / "pids.txt").read_text(encoding="utf-8") if (CASES / "pids.txt").exists() else ""
log("pids.txt:\n" + pids_txt)
pids = re.findall(r"\b(\d+)\b", pids_txt)
uniq = sorted(set(pids))
log(f"unique_pids={uniq} subprocess_isolation={'YES' if len(uniq) >= 2 else 'NO'}")

# helper n smear already dumped as helper_n

# ---------------------------------------------------------------------------
log("\n## leftover-after JOIN vs start-of-victim (Honor KILL 5)")

restore = write_case(
    "restore.py",
    """acc = []

def test_a():
    acc.append("a")

def test_b():
    try:
        assert acc == [], acc
    finally:
        acc.clear()
""",
)
p = leakorder(restore)
dump("restore", p)
o = ordleak(restore, "test_a", "test_b")
dump("ord_restore", o)

leftover_only = write_case(
    "leftover_only.py",
    """acc = []

def test_a():
    acc.append("a")

def test_b():
    acc.append("b")
""",
)
p = leakorder(leftover_only)
dump("leftover_only", p)
o = ordleak(leftover_only, "test_a", "test_b")
dump("ord_leftover_only", o)

same_twice = write_case(
    "same_twice.py",
    """acc = []

def test_a():
    acc.append("a")
""",
)
p = leakorder(same_twice, extra=["--order", "test_a", "--order", "test_a"])
dump("same_twice", p)

hidden = write_case(
    "hidden.py",
    """acc = []

def test_a():
    acc.append("a")

def test_b():
    pass
""",
)
p = leakorder(hidden)
dump("hidden", p)
o = ordleak(hidden, "test_a", "test_b")
dump("ord_hidden", o)

cleanup_victim = write_case(
    "cleanup_pass.py",
    """acc = []

def test_a():
    acc.append("a")

def test_b():
    acc.clear()
""",
)
p = leakorder(cleanup_victim)
dump("cleanup_pass", p)
o = ordleak(cleanup_victim, "test_a", "test_b")
dump("ord_cleanup_pass", o)

# leftover of a binding that is not a start-of-victim of the *other* test:
# test_a mutates extra; test_b never reads extra; start of extra for test_b differs
extra_bind = write_case(
    "extra_bind.py",
    """acc = []
noise = []

def test_a():
    acc.append("a")
    noise.append("n")

def test_b():
    assert acc == [], acc
""",
)
p = leakorder(extra_bind)
dump("extra_bind", p)
o = ordleak(extra_bind, "test_a", "test_b")
dump("ord_extra_bind", o)

# ---------------------------------------------------------------------------
log("\n## Honor KILL 3 hunt cases: unnamed splits must be unknown not none")

env = write_case(
    "envmark.py",
    """import os

def test_a():
    os.environ["LEAKORDER3_MARK"] = "1"

def test_b():
    assert "LEAKORDER3_MARK" not in os.environ
""",
)
p = leakorder(env)
dump("envmark", p)

fs_smear = write_case(
    "fs_smear.py",
    """from pathlib import Path
MARK = Path(__file__).resolve().parent / "MARKER_SMEAR"

def test_a():
    MARK.write_text("a", encoding="utf-8")

def test_b():
    assert not MARK.exists()
""",
)
(CASES / "MARKER_SMEAR").unlink(missing_ok=True)
p = leakorder(fs_smear)
dump("fs_smear", p)
log(f"MARKER_SMEAR exists={ (CASES / 'MARKER_SMEAR').exists() }")

fs_split = write_case(
    "fs_split.py",
    """from pathlib import Path
MARK = Path(__file__).resolve().parent / "MARKER_SPLIT"

def test_a():
    MARK.write_text("a", encoding="utf-8")

def test_b():
    try:
        assert not MARK.exists()
    finally:
        if MARK.exists():
            MARK.unlink()
""",
)
(CASES / "MARKER_SPLIT").unlink(missing_ok=True)
p = leakorder(fs_split)
dump("fs_split", p)

ctx = write_case(
    "ctx.py",
    """from contextvars import ContextVar
v = ContextVar("v", default=0)

def test_a():
    v.set(1)

def test_b():
    assert v.get() == 0
""",
)
p = leakorder(ctx)
dump("ctx", p)

sysmod = write_case(
    "sysmod.py",
    """import sys

def test_a():
    sys.modules["leakorder3_mod"] = object()

def test_b():
    assert "leakorder3_mod" not in sys.modules
""",
)
p = leakorder(sysmod)
dump("sysmod", p)

chdir = write_case(
    "chdir.py",
    """import os
from pathlib import Path
HERE = Path(__file__).resolve().parent

def test_a():
    os.chdir("/tmp")

def test_b():
    assert Path.cwd() == HERE
""",
)
p = leakorder(chdir)
dump("chdir", p)

ident = write_case(
    "ident.py",
    """sentinel = object()
box = {"s": sentinel}

def test_a():
    box["s"] = object()

def test_b():
    assert box["s"] is sentinel
""",
)
p = leakorder(ident)
dump("ident", p)

# ---------------------------------------------------------------------------
log("\n## DESTROYER_2 leftover re-hits")

rel = CASES / "relpkg"
rel.mkdir(exist_ok=True)
(rel / "__init__.py").write_text("", encoding="utf-8")
(rel / "helper.py").write_text("bucket = []\n", encoding="utf-8")
(rel / "test_rel.py").write_text(
    """from .helper import bucket

def test_a():
    bucket.append("a")

def test_b():
    assert bucket == [], bucket
""",
    encoding="utf-8",
)
p = leakorder(rel / "test_rel.py")
dump("relpkg", p)

ut = write_case(
    "ut.py",
    """class TestOrder:
    bucket = []
    def test_a(self):
        self.bucket.append("a")
    def test_b(self):
        assert self.bucket == [], self.bucket
""",
)
p = leakorder(ut)
dump("ut_default", p)
p = leakorder(ut, extra=["--order", "TestOrder.test_a,TestOrder.test_b", "--order", "TestOrder.test_b,TestOrder.test_a"])
dump("ut_order", p)

three = write_case(
    "three.py",
    """acc = []

def test_a():
    acc.append("a")

def test_b():
    pass

def test_c():
    assert acc == [], acc
""",
)
p = leakorder(three)
dump("three", p)
p = leakorder(three, extra=["--order", "test_a,test_c", "--order", "test_c,test_a"])
dump("three_pair", p)

evil = write_case(
    "evil.py",
    """class Boom:
    def __repr__(self):
        raise RuntimeError("boom")

box = Boom()

def test_a():
    pass

def test_b():
    pass
""",
)
p = leakorder(evil)
dump("evil", p)

stamp = write_case(
    "stamp.py",
    """import time
stamp = time.time_ns()

def test_a():
    pass

def test_b():
    pass
""",
)
p = leakorder(stamp)
dump("stamp", p)

nan = write_case(
    "nan.py",
    """nan = float("nan")
sentinel = object()

def test_a():
    pass

def test_b():
    pass
""",
)
p = leakorder(nan)
dump("nan", p)

always = write_case(
    "always.py",
    """acc = []

def test_a():
    acc.append("a")

def test_b():
    assert False
""",
)
p = leakorder(always)
dump("always", p)

empty = write_case("empty.py", "# comments only\n")
p = leakorder(empty)
dump("empty", p)

p = leakorder(FIX / "unseen_bucket.py")
dump("unseen", p)

p = leakorder(FIX / "test_async.py")
dump("asyncf", p)
p = leakorder(FIX / "test_gen.py")
dump("gen", p)
p = leakorder(FIX / "test_sysexit.py")
dump("sysexit", p)

missing = leakorder(CASES / "no-such.py")
dump("missing", missing)

noargs = run([sys.executable, str(CLI)])
dump("noargs", noargs)

nul = CASES / "nul.py"
nul.write_bytes(b"acc = []\n\x00\ndef test_a():\n    pass\n")
p = leakorder(nul)
dump("nul", p)

space = CASES / "file with space.py"
space.write_text(
    """acc = []
def test_a():
    acc.append("a")
def test_b():
    assert acc == [], acc
""",
    encoding="utf-8",
)
p = leakorder(space)
dump("space", p)

# class attrs extra hiding places
for name, body in [
    (
        "fnattr.py",
        """def holder():
    pass
holder.acc = []
def test_a():
    holder.acc.append("a")
def test_b():
    assert holder.acc == [], holder.acc
""",
    ),
    (
        "defaults.py",
        """def bag(xs=[]):
    return xs
def test_a():
    bag().append("a")
def test_b():
    assert bag() == [], bag()
""",
    ),
    (
        "closure.py",
        """def make():
    acc = []
    def test_a():
        acc.append("a")
    def test_b():
        assert acc == [], acc
    return test_a, test_b
test_a, test_b = make()
""",
    ),
    (
        "lru.py",
        """from functools import lru_cache
@lru_cache
def f(x):
    return x
def test_a():
    f(1)
def test_b():
    assert f.cache_info().currsize == 0
""",
    ),
    (
        "slots.py",
        """class Box:
    __slots__ = ("n",)
    def __init__(self):
        self.n = 0
box = Box()
def test_a():
    box.n += 1
def test_b():
    assert box.n == 0
""",
    ),
    (
        "custeq.py",
        """class Box:
    def __init__(self):
        self.n = 0
    def __eq__(self, other):
        return True
box = Box()
def test_a():
    box.n += 1
def test_b():
    assert box.n == 0
""",
    ),
]:
    path = write_case(name, body)
    p = leakorder(path)
    dump(name.replace(".py", ""), p)

# ---------------------------------------------------------------------------
log("\n## THIN_WRAPPER replica of run_orders.py (owned 009 only)")
# run_orders already prints acc_after. Compare whether leakorder leftover+rc
# is just that printer plus a name.

ro = run([sys.executable, str(S009.parent / "run_orders.py")])
dump("run_orders_009", ro)

# ---------------------------------------------------------------------------
log("\n## hunt leaked= / none-next-to-split across this pass")
for out in sorted(SCRATCH.glob("*.out")):
    text = out.read_text(encoding="utf-8")
    for ln in order_lines(text):
        if "leaked=" in ln:
            hunt_leaked += 1
            log(f"LEAKED_TOKEN {out.name}: {ln}")
    leaked = field(text, "leaked_names")
    sufficient = field(text, "sufficient_exposing_order")
    if leaked == "none" and sufficient and sufficient != "none":
        hunt_none_split += 1
        none_split_hits.append(f"{out.name}: leaked_names={leaked} sufficient={sufficient}")
        log(f"NONE_NEXT_TO_SPLIT {out.name}: leaked_names={leaked} sufficient={sufficient}")

log(f"hunt_leaked_eq_on_order_lines={hunt_leaked}")
log(f"hunt_none_next_to_split={hunt_none_split}")
for h in none_split_hits:
    log("  " + h)

# leftover vs leaked_names divergence
log("\n## leftover vs leaked_names divergence")
for tag in (
    "s009",
    "restore",
    "leftover_only",
    "same_twice",
    "hidden",
    "cleanup_pass",
    "extra_bind",
    "fs_smear",
    "fs_split",
    "envmark",
    "always",
    "empty",
    "stamp",
    "nan",
):
    outp = SCRATCH / f"{tag}.out"
    if not outp.exists():
        continue
    text = outp.read_text(encoding="utf-8")
    leftover_vals = []
    for ln in order_lines(text):
        m = re.search(r"leftover=(\{.*\})$", ln)
        leftover_vals.append(m.group(1) if m else "?")
    log(
        f"{tag}: leftover={leftover_vals} leaked_names={field(text, 'leaked_names')} "
        f"sufficient={field(text, 'sufficient_exposing_order')} rc={(SCRATCH / f'{tag}.rc').read_text().strip()}"
    )

LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
log(f"\nwrote {LOG}")
