#!/usr/bin/env python3
"""Host attacks for DESTROYER_leakorder_4. Archive CLI only. No merge. No worktree edit."""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = ROOT / "lineages/candidate-leakorder/leakorder"
ORD = ROOT / "lineages/candidate-ordleak/ordleak"
S009 = ROOT / "specimens/specimen-009/files/test_order.py"
S012 = ROOT / "specimens/specimen-012/files/test_order.py"
S060 = ROOT / "specimens/specimen-060/files/test_class_leak.py"
FIX = ROOT / "lineages/candidate-leakorder/fixtures"
SCRATCH = ROOT / "destroyers/_leakorder4_scratch"
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


def leftover_vals(text: str) -> list[str]:
    out = []
    for ln in order_lines(text):
        m = re.search(r"leftover=(\{.*\})$", ln)
        out.append(m.group(1) if m else "?")
    return out


def leakorder(path: Path, extra: list[str] | None = None, cwd=None, env=None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(CLI), str(path)]
    if extra:
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


def ast_mutated_names(path: Path) -> list[str]:
    """AST-static leftover-identity replica: names that look mutated in source."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()

    def add(node) -> None:
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                names.add(f"{node.value.id}.{node.attr}")
            else:
                names.add(node.attr)

    class V(ast.NodeVisitor):
        def visit_Assign(self, node):
            for t in node.targets:
                add(t)
            self.generic_visit(node)

        def visit_AugAssign(self, node):
            add(node.target)
            self.generic_visit(node)

        def visit_AnnAssign(self, node):
            if node.value is not None:
                add(node.target)
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "append",
                "extend",
                "clear",
                "add",
                "update",
                "pop",
                "remove",
                "discard",
            }:
                add(node.func.value)
            self.generic_visit(node)

        def visit_Delete(self, node):
            for t in node.targets:
                add(t)
            self.generic_visit(node)

    V().visit(tree)
    return sorted(n for n in names if not n.startswith("test_"))


def two_greps(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    tests = re.findall(r"^def (test_\w+)\(", src, re.M)
    assigns = re.findall(r"^([A-Za-z_][\w]*)\s*=", src, re.M)
    return {"tests": tests, "assigns": [a for a in assigns if not a.startswith("test_")]}


# ---------------------------------------------------------------------------
log("## identity")
log(f"CLI={CLI}")
log(f"ORD={ORD}")
log(f"python={sys.version.split()[0]}")
log(f"archive exists={CLI.is_file()} bytes={CLI.stat().st_size}")

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

# class-attr leftover restore (leftover-after identity of Box.bucket)
restore_cls = write_case(
    "restore_cls.py",
    """class Box:
    bucket = []

def test_a():
    Box.bucket.append("a")

def test_b():
    try:
        assert Box.bucket == [], Box.bucket
    finally:
        Box.bucket.clear()
""",
)
p = leakorder(restore_cls)
dump("restore_cls", p)
o = ordleak(restore_cls, "test_a", "test_b")
dump("ord_restore_cls", o)

# ---------------------------------------------------------------------------
log("\n## leftover-after IDENTITY (4th pass object)")

# 1. rebind to empty (value restore via new list, not in-place clear)
rebind_empty = write_case(
    "rebind_empty.py",
    """acc = []

def test_a():
    acc.append("a")

def test_b():
    global acc
    try:
        assert acc == [], acc
    finally:
        acc = []
""",
)
p = leakorder(rebind_empty)
dump("rebind_empty", p)
o = ordleak(rebind_empty, "test_a", "test_b")
dump("ord_rebind_empty", o)

# 2. leftover of rebind-to-same-value vs mutate (acc = ["a"] vs append)
rebind_same = write_case(
    "rebind_same.py",
    """acc = []

def test_a():
    global acc
    acc = ["a"]

def test_b():
    assert acc == [], acc
""",
)
p = leakorder(rebind_same)
dump("rebind_same", p)

# 3. identity-only rebind of equal empty list: leftover should be {} (value leftover)
id_rebind = write_case(
    "id_rebind.py",
    """acc = []

def test_a():
    global acc
    acc = []

def test_b():
    global acc
    acc = []
""",
)
p = leakorder(id_rebind)
dump("id_rebind", p)

# 4. alias: two names, one list
alias = write_case(
    "alias.py",
    """acc = []
alias = acc

def test_a():
    alias.append("a")

def test_b():
    assert acc == [], acc
""",
)
p = leakorder(alias)
dump("alias", p)
o = ordleak(alias, "test_a", "test_b")
dump("ord_alias", o)

# 5. leftover of nested dict value identity
nested = write_case(
    "nested.py",
    """box = {"n": 0}

def test_a():
    box["n"] = 1

def test_b():
    assert box["n"] == 0, box
""",
)
p = leakorder(nested)
dump("nested", p)

# 6. leftover after mutate-then-restore-same-value in the SAME test
roundtrip = write_case(
    "roundtrip.py",
    """acc = []

def test_a():
    acc.append("a")
    acc.clear()

def test_b():
    assert acc == [], acc
""",
)
p = leakorder(roundtrip)
dump("roundtrip", p)

# 7. leftover of del name
del_acc = write_case(
    "del_acc.py",
    """acc = []

def test_a():
    global acc
    acc.append("a")
    del acc

def test_b():
    assert "acc" not in globals() or acc == []
""",
)
p = leakorder(del_acc)
dump("del_acc", p)

# 8. leftover identity of object() swap inside a dict (address-stripped structured)
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

# 9. leftover of equal structured NEW list after mutation (acc = list(acc) after append)
copy_list = write_case(
    "copy_list.py",
    """acc = []

def test_a():
    global acc
    acc.append("a")
    acc = list(acc)

def test_b():
    assert acc == [], acc
""",
)
p = leakorder(copy_list)
dump("copy_list", p)

# 10. leftover identity: both orders leave the SAME leftover value, no start split
same_leftover = write_case(
    "same_leftover.py",
    """acc = []

def test_a():
    if not acc:
        acc.append("a")

def test_b():
    if not acc:
        acc.append("a")
""",
)
p = leakorder(same_leftover)
dump("same_leftover", p)

# 11. leftover of class attr via instance write
inst_cls = write_case(
    "inst_cls.py",
    """class Box:
    bucket = []

def test_a():
    Box().bucket.append("a")

def test_b():
    assert Box.bucket == [], Box.bucket
""",
)
p = leakorder(inst_cls)
dump("inst_cls", p)

# 12. leftover of slots instance
slots = write_case(
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
)
p = leakorder(slots)
dump("slots", p)

# 13. leftover identity of custom __eq__ hiding box.n
custeq = write_case(
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
)
p = leakorder(custeq)
dump("custeq", p)

# 14. leftover of private _acc
private_case = write_case(
    "underscore.py",
    """_acc = []

def test_a():
    _acc.append("a")

def test_b():
    assert _acc == [], _acc
""",
)
p = leakorder(private_case)
dump("underscore", p)
o = ordleak(private_case, "test_a", "test_b")
dump("ord_underscore", o)

# ---------------------------------------------------------------------------
log("\n## AST-static leftover-identity replica vs runtime leftover")
ast_targets = [
    ("s009", S009),
    ("s060", S060),
    ("restore", restore),
    ("leftover_only", leftover_only),
    ("same_twice", same_twice),
    ("cleanup_pass", cleanup_victim),
    ("rebind_empty", rebind_empty),
    ("roundtrip", roundtrip),
    ("same_leftover", same_leftover),
    ("restore_cls", restore_cls),
    ("hidden", hidden),
    ("id_rebind", id_rebind),
    ("alias", alias),
]
for tag, path in ast_targets:
    outp = SCRATCH / f"{tag}.out"
    if not outp.exists():
        continue
    text = outp.read_text(encoding="utf-8")
    leftover = leftover_vals(text)
    ast_names = ast_mutated_names(path)
    greps = two_greps(path)
    leaked = field(text, "leaked_names")
    suff = field(text, "sufficient_exposing_order")
    rc = (SCRATCH / f"{tag}.rc").read_text(encoding="utf-8").strip()
    leftover_keys = []
    for lv in leftover:
        try:
            leftover_keys.append(str(sorted(eval(lv, {"__builtins__": {}}, {}).keys())))
        except Exception as exc:
            leftover_keys.append(f"parse_err:{exc}")
    log(
        f"AST {tag}: ast_mutated={ast_names} two_greps={greps} leftover={leftover} "
        f"leftover_keys={leftover_keys} leaked_names={leaked} sufficient={suff} rc={rc}"
    )
    # Discriminator: AST names include a leftover name that leftover keys omit on some order
    ast_set = set(ast_names)
    omitted = []
    for lv in leftover:
        try:
            keys = set(eval(lv, {"__builtins__": {}}, {}).keys())
        except Exception:
            continue
        if ast_set - keys:
            omitted.append(sorted(ast_set - keys))
    if any(omitted) and any(k == "{}" or k == "{}" for k in leftover):
        log(f"  AST_OVER_RUNTIME {tag}: AST names persist where leftover empty omitted={omitted}")

# ---------------------------------------------------------------------------
log("\n## THIN_WRAPPER: two greps / run_orders.py vs leftover join")
ro = run([sys.executable, str(S009.parent / "run_orders.py")])
dump("run_orders_009", ro)
log("run_orders.py names acc_after for a known name; does not name Box.bucket")
p = leakorder(S060)
log(f"leakorder S060 leftover={leftover_vals(p.stdout)} leaked_names={field(p.stdout, 'leaked_names')}")

# two-grep replica cannot produce leftover VALUES or restore-empty leftover
s009_greps = two_greps(S009)
restore_greps = two_greps(restore)
log(f"two_greps S009={s009_greps}")
log(f"two_greps restore={restore_greps}")
log("two_greps restore still names acc=; leakorder leftover on exposing order is {}")

# ---------------------------------------------------------------------------
log("\n## Honor KILL 3 hunt cases: unnamed splits must be unknown not none")

env = write_case(
    "envmark.py",
    """import os

def test_a():
    os.environ["LEAKORDER4_MARK"] = "1"

def test_b():
    assert "LEAKORDER4_MARK" not in os.environ
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
log(f"MARKER_SMEAR exists={(CASES / 'MARKER_SMEAR').exists()}")

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
    sys.modules["leakorder4_mod"] = object()

def test_b():
    assert "leakorder4_mod" not in sys.modules
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

# DESTROYER_2 leftovers re-hit
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
p = leakorder(
    ut,
    extra=[
        "--order",
        "TestOrder.test_a,TestOrder.test_b",
        "--order",
        "TestOrder.test_b,TestOrder.test_a",
    ],
)
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
]:
    path = write_case(name, body)
    p = leakorder(path)
    dump(name.replace(".py", ""), p)

# ---------------------------------------------------------------------------
log("\n## hunt leaked= / none-next-to-split across this pass")
hunt_leaked = 0
hunt_none_split = 0
none_split_hits: list[str] = []
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

# ---------------------------------------------------------------------------
log("\n## leftover vs leaked_names divergence (leftover-after join)")
for tag in (
    "s009",
    "s060",
    "restore",
    "restore_cls",
    "leftover_only",
    "same_twice",
    "hidden",
    "cleanup_pass",
    "extra_bind",
    "rebind_empty",
    "rebind_same",
    "id_rebind",
    "alias",
    "nested",
    "roundtrip",
    "del_acc",
    "ident",
    "copy_list",
    "same_leftover",
    "inst_cls",
    "slots",
    "custeq",
    "underscore",
    "fs_smear",
    "fs_split",
    "envmark",
    "always",
    "empty",
    "stamp",
    "nan",
    "helper_n",
    "helper_bucket",
    "pid_probe",
):
    outp = SCRATCH / f"{tag}.out"
    if not outp.exists():
        continue
    text = outp.read_text(encoding="utf-8")
    log(
        f"{tag}: leftover={leftover_vals(text)} leaked_names={field(text, 'leaked_names')} "
        f"sufficient={field(text, 'sufficient_exposing_order')} rc={(SCRATCH / f'{tag}.rc').read_text().strip()}"
    )

# Can leftover be reconstructed from ordleak into/via?
log("\n## leftover reconstruct from ordleak into/via?")
for tag in ("s009", "restore", "leftover_only", "cleanup_pass", "same_twice", "restore_cls", "hidden"):
    lo = SCRATCH / f"{tag}.out"
    oo = SCRATCH / f"ord_{tag}.out" if tag != "same_twice" else None
    if not lo.exists():
        continue
    lt = lo.read_text(encoding="utf-8")
    log(f"JOIN {tag} leakorder leftover={leftover_vals(lt)} leaked_names={field(lt, 'leaked_names')}")
    if oo and oo.exists():
        ot = oo.read_text(encoding="utf-8")
        leaked_row = [ln for ln in ot.splitlines() if ln.startswith("leaked") or ln.startswith("exposing")]
        log(f"JOIN {tag} ordleak rows={leaked_row}")

LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
log(f"\nwrote {LOG}")
