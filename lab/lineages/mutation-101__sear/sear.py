#!/usr/bin/env python3
"""sear — lockset clearance at visa-birth, following dest-file slot identity.

A sear is brand's joint after --follow of the visa *slot* across dest-file
identity (git R records, not git log --follow). Same-commit lockset
clearance still required. A dest-only rename is not a birth. Copy is not
a follow. Skip is not a lock. SPREAD is not a mint. Not a fourth cinch.

mint names OPEN/SPEC → BOUND of a production world. Tests are not
its object. File rename of a BOUND world looks like ABSENT→BOUND when
path is in the slot key — that is mint's hole. sear follows the slot.

gage names LOCKED-and-BOUND vs LOCKED-and-OPEN on a current splice.
A skip is not a lock.

brand is the joint occupancy. sear is the joint plus dest identity:
rename of a visa-bearing test still brands the birth commit, not the rename.
Leftover names are not a machine. sitbone/kizu first-parent births=0
is mint's gold — sear must not invent them.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import hatchlib
import visalib

VERSION = "0.2.0"

TEXTBOOK_TAILS = {
    "user",
    "foo",
    "bar",
    "baz",
    "ubuntu",
    "nobody",
    "testuser",
    "john",
    "jane",
    "john doe",
    "jane doe",
}

HARD_SKIP_AXES = ("platform", "HOME", "USER", "CI")
SOURCE_EXTS = {".py", ".rs", ".js", ".ts", ".tsx", ".jsx", ".go", ".swift"}
SELF_EXCLUDE = ["hatchlib.py", "visalib.py", "sear.py", "brand.py"]
KIND_ORDER = ("OPEN→BOUND", "SPEC→BOUND", "ABSENT→BOUND", "RETARGET", "SPREAD")

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "node_modules",
    "target",
    "dist",
    "build",
    ".build",
    "DerivedData",
    ".idea",
    ".vscode",
    "lab",
}

TEST_DIR_NAMES = {
    "test",
    "tests",
    "spec",
    "specs",
    "testing",
    "__tests__",
}

FIXTURE_DIR_NAMES = {
    "fixtures",
    "golden",
    "testdata",
    "test_data",
    "snapshots",
    "__snapshots__",
    "expected",
}

TEST_FILE_RE = re.compile(
    r"""(
        ^test_.*\.py$
      | ^test\.py$
      | ^tests\.py$
      | .*_test\.py$
      | .*_test\.go$
      | .*_test\.rs$
      | .*\.test\.(js|jsx|ts|tsx|mjs|cjs)$
      | .*\.spec\.(js|jsx|ts|tsx|mjs|cjs)$
      | ^conftest\.py$
    )""",
    re.VERBOSE | re.IGNORECASE,
)

PATH_RE = re.compile(
    r"(?:"
    r"/Users/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|/home/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|[A-Za-z]:\\(?:[^\\\s'\"`]+\\)+[^\\\s'\"`]+"
    r")"
)


# ---------------------------------------------------------------------------
# Visa-birth occupancy (mint's object — do not lie about sitbone/kizu)
# ---------------------------------------------------------------------------


@dataclass
class Clearance:
    report: hatchlib.Report
    fixture: hatchlib.Fixture
    visa: visalib.Visa
    recovered: str = ""

    @property
    def require(self) -> dict[str, str]:
        return {k: v for k, v in self.visa.require.items() if k in HARD_SKIP_AXES}


@dataclass
class WorldBirth:
    child: Clearance
    kind: str
    was_status: str
    was: Optional[Clearance] = None


@dataclass
class Birth:
    commit: str
    parent: str
    subject: str
    machine: dict[str, str]
    kind: str
    worlds: list[WorldBirth] = field(default_factory=list)


def eprint(*a: object) -> None:
    print(*a, file=sys.stderr)


def strip_canon(val: object) -> str:
    raw = str(val) if val is not None else ""
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def world_oracle_text(args: dict) -> str:
    chunks: list[str] = []
    for name, a in args.items():
        if not isinstance(a, dict):
            continue
        val = a.get("value")
        if val is None:
            continue
        inner = strip_canon(val)
        chunks.append(f"{name}={inner}")
        chunks.append(inner)
    return ("\n".join(chunks) + "\n") if chunks else ""


def _tail(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def require_is_textbook(require: dict[str, str]) -> bool:
    home = require.get("HOME", "")
    user = require.get("USER", "")
    tails: list[str] = []
    if home:
        tails.append(_tail(home))
    if user:
        tails.append(user)
    if not tails:
        return False
    for t in tails:
        if " " in t or "'" in t:
            continue
        if t.lower() in TEXTBOOK_TAILS:
            continue
        return False
    return True


def recover_call(root: Path | None, site: str) -> str:
    if not site or ":" not in site:
        return ""
    path_s, lineno_s = site.rsplit(":", 1)
    try:
        lineno = int(lineno_s)
    except ValueError:
        return ""
    path = Path(path_s)
    if not path.is_file() and root is not None:
        path = Path(root) / path_s
    if not path.is_file():
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    lines = text.splitlines(keepends=True)
    if lineno < 1 or lineno > len(lines):
        return ""
    start = sum(len(ln) for ln in lines[: lineno - 1])
    return _take_call(text, start)


def _take_call(text: str, start: int) -> str:
    n = len(text)
    i = start
    while i < n and text[i] in " \t":
        i += 1
    for prefix in ("return ", "_ = ", "let _ = "):
        if text.startswith(prefix, i):
            i += len(prefix)
            while i < n and text[i] in " \t":
                i += 1
    name_start = i
    paren = text.find("(", i)
    if paren < 0 or paren > i + 240:
        return ""
    j = paren
    depth = 0
    in_str: str | None = None
    triple = False
    escape = False
    while j < n:
        c = text[j]
        if in_str:
            if escape:
                escape = False
            elif c == "\\" and not triple:
                escape = True
            elif triple and text.startswith(in_str * 3, j):
                j += 3
                in_str = None
                triple = False
                continue
            elif not triple and c == in_str:
                in_str = None
            j += 1
            continue
        if c in "\"'`":
            if text.startswith(c * 3, j):
                in_str = c
                triple = True
                j += 3
                continue
            in_str = c
            j += 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            j += 1
            if depth == 0:
                return text[name_start:j].strip()
            continue
        j += 1
    return ""


def visa_of_world(args: dict, recovered: str = "") -> visalib.Visa:
    text = recovered if recovered else world_oracle_text(args)
    v = visalib.infer(text, "production.world.snap")
    if v.status == "BOUND" and require_is_textbook(v.require):
        return visalib.Visa(
            path=v.path,
            status="SPEC",
            require={},
            soft=dict(v.soft),
            witnesses=list(v.witnesses),
            contradictions=list(v.contradictions),
        )
    return v


def args_truncated(args: dict) -> bool:
    for a in args.values():
        if isinstance(a, dict) and "..." in str(a.get("value") or ""):
            return True
    return False


def qualify_call(fn: hatchlib.FuncDef, call: str) -> str:
    if not call:
        return ""
    recv = fn.recv
    if recv and not call.startswith(recv + ".") and not call.startswith(recv + "("):
        return f"{recv}.{call}"
    return call


def emit_call(c: Clearance) -> str:
    if c.recovered and c.fixture.kind != "member":
        return qualify_call(c.report.fn, c.recovered)
    return hatchlib._emit_call(c.report.fn, c.fixture.args)


def drop_member_world_dupes(cs: list[Clearance]) -> list[Clearance]:
    members: set[str] = set()
    for c in cs:
        if c.fixture.kind != "member":
            continue
        for a in c.fixture.args.values():
            if isinstance(a, dict) and a.get("value") is not None:
                members.add(strip_canon(a["value"]))
    if not members:
        return cs
    out: list[Clearance] = []
    for c in cs:
        if c.fixture.kind == "world":
            vals = [
                strip_canon(a["value"])
                for a in c.fixture.args.values()
                if isinstance(a, dict) and a.get("value") is not None
            ]
            if vals and all(v in members for v in vals):
                continue
        out.append(c)
    return out


def clear(reports: list[hatchlib.Report], root: Path | None = None) -> list[Clearance]:
    out: list[Clearance] = []
    for r, f in hatchlib.iter_fixtures(reports, due_only=False):
        recovered = ""
        if f.kind != "member":
            for site in f.sites:
                recovered = recover_call(root, site)
                if recovered:
                    break
        v = visa_of_world(f.args, recovered=recovered if args_truncated(f.args) else "")
        out.append(Clearance(report=r, fixture=f, visa=v, recovered=recovered))
    return drop_member_world_dupes(out)


def is_bound_debt(c: Clearance) -> bool:
    if hatchlib.fixture_dyn_names(c.fixture.args):
        return False
    return c.visa.status == "BOUND"


def production_worlds(cs: list[Clearance]) -> list[Clearance]:
    return [c for c in cs if c.fixture.kind == "world"]


def rel_path(path: str) -> str:
    return path.replace("\\", "/")


def slot_key(c: Clearance, dest_to_src: Optional[dict[str, str]] = None) -> tuple:
    """Occupancy identity. Dest-file path follows R records when dest_to_src is set."""
    fn = c.report.fn
    params = tuple(p.name for p in fn.params)
    path = rel_path(fn.path)
    if dest_to_src:
        path = dest_to_src.get(path, path)
    return (fn.name, path, params)


def world_key(c: Clearance, dest_to_src: Optional[dict[str, str]] = None) -> tuple:
    args: list[tuple[str, str, str]] = []
    for name, a in sorted(c.fixture.args.items()):
        if not isinstance(a, dict):
            continue
        kind = str(a.get("kind") or "")
        if kind == "dyn":
            args.append((name, "dyn", "*"))
            continue
        val = strip_canon(a.get("value")).rstrip("/")
        args.append((name, kind, val))
    return slot_key(c, dest_to_src) + (tuple(args),)


def machine_key(c: Clearance) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((k, v.rstrip("/")) for k, v in c.require.items()))


def machine_key_from_dict(machine: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((k, str(v).rstrip("/")) for k, v in machine.items() if k in HARD_SKIP_AXES))


def scan_tree(root: Path) -> list[Clearance]:
    _defs, _calls, reports = hatchlib.analyze(root, SELF_EXCLUDE)
    return production_worlds(clear(reports, root=root))


# ---------------------------------------------------------------------------
# git
# ---------------------------------------------------------------------------


class GitError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip() or r.stdout.decode("utf-8", "replace").strip()
        raise GitError(err or f"git {' '.join(args)} failed")
    return r


def git_text(repo: Path, *args: str, check: bool = True) -> str:
    return git(repo, *args, check=check).stdout.decode("utf-8", "replace")


def is_git_repo(path: Path) -> bool:
    """True only when PATH itself is a worktree root (mint's lesson)."""
    r = git(path, "rev-parse", "--show-toplevel", check=False)
    if r.returncode != 0:
        return False
    top = Path(r.stdout.decode().strip())
    try:
        return top.resolve() == path.resolve()
    except OSError:
        return False


def short_sha(repo: Path, rev: str) -> str:
    return git_text(repo, "rev-parse", "--short", rev).strip()


def full_sha(repo: Path, rev: str) -> str:
    return git_text(repo, "rev-parse", rev).strip()


def commit_subject(repo: Path, rev: str) -> str:
    return git_text(repo, "log", "-1", "--format=%s", rev).strip()


def first_parent(repo: Path, rev: str) -> Optional[str]:
    r = git(repo, "rev-parse", f"{rev}^", check=False)
    if r.returncode != 0:
        return None
    return r.stdout.decode().strip()


def source_touched(repo: Path, parent: Optional[str], commit: str) -> bool:
    if parent is None:
        names = git_text(repo, "ls-tree", "-r", "--name-only", commit)
    else:
        names = git_text(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit)
    for line in names.splitlines():
        if Path(line).suffix.lower() in SOURCE_EXTS:
            return True
    return False


def tests_touched(repo: Path, parent: Optional[str], commit: str) -> bool:
    if parent is None:
        names = git_text(repo, "ls-tree", "-r", "--name-only", commit)
    else:
        names = git_text(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", parent, commit)
    return any(is_test_path(line) for line in names.splitlines())


def dest_renames(repo: Path, parent: Optional[str], commit: str) -> dict[str, str]:
    """child dest path → parent path for git R records.

    Dest-file identity is R records (berth/ditto), not `git log --follow`.
    Copy has no R; a copy is not a follow. SPREAD of a visa into a new
    function is not a dest rename.
    """
    if parent is None:
        return {}
    raw = git_text(
        repo,
        "diff-tree",
        "-r",
        "-M",
        "-z",
        "--name-status",
        "--diff-filter=R",
        "--no-commit-id",
        parent,
        commit,
        check=False,
    )
    out: dict[str, str] = {}
    parts = [p for p in raw.split("\0") if p]
    i = 0
    while i < len(parts):
        status = parts[i]
        if not status.startswith("R"):
            i += 1
            continue
        if i + 2 >= len(parts):
            break
        src, dst = parts[i + 1], parts[i + 2]
        out[rel_path(dst)] = rel_path(src)
        i += 3
    return out


def slot_identity_map(
    parent_cs: list[Clearance],
    child_cs: list[Clearance],
    dest_to_src: dict[str, str],
) -> dict[str, str]:
    """child dest path → parent path.

    R records first. A pin that also `git mv`s the dest file is often D+A
    (content changed), so unique (fn, params) whose parent dest died and
    whose child dest was born is the same slot. Copy is not a follow: the
    parent dest still lives. Two births of the same sig stay unmatched.
    """
    out = dict(dest_to_src)
    parent_by_sig: dict[tuple, list[str]] = {}
    child_by_sig: dict[tuple, list[str]] = {}
    parent_paths: set[str] = set()
    child_paths: set[str] = set()
    for c in parent_cs:
        path = rel_path(c.report.fn.path)
        parent_paths.add(path)
        sig = (c.report.fn.name, tuple(p.name for p in c.report.fn.params))
        parent_by_sig.setdefault(sig, []).append(path)
    for c in child_cs:
        path = rel_path(c.report.fn.path)
        child_paths.add(path)
        sig = (c.report.fn.name, tuple(p.name for p in c.report.fn.params))
        child_by_sig.setdefault(sig, []).append(path)
    already_src = set(out.values())
    already_dst = set(out)
    for sig, c_paths in child_by_sig.items():
        p_paths = parent_by_sig.get(sig, [])
        new_c = [p for p in dict.fromkeys(c_paths) if p not in parent_paths and p not in already_dst]
        dead_p = [p for p in dict.fromkeys(p_paths) if p not in child_paths and p not in already_src]
        if len(new_c) == 1 and len(dead_p) == 1:
            out[new_c[0]] = dead_p[0]
            already_dst.add(new_c[0])
            already_src.add(dead_p[0])
    return out


def materialize(repo: Path, rev: str, dest: Path) -> None:
    """Extract tracked source files only. Skip symlinks (kizu AGENTS.md)."""
    dest.mkdir(parents=True, exist_ok=True)
    dest_r = dest.resolve()
    r = git(repo, "archive", "--format=tar", rev)
    buf = io.BytesIO(r.stdout)
    with tarfile.open(fileobj=buf, mode="r:") as tf:
        for m in tf.getmembers():
            if m.issym() or m.islnk() or not m.isfile():
                continue
            name = m.name.lstrip("./")
            if not name or name.startswith("/") or ".." in Path(name).parts:
                continue
            if Path(name).suffix.lower() not in SOURCE_EXTS:
                continue
            target = (dest / name).resolve()
            try:
                target.relative_to(dest_r)
            except ValueError:
                continue
            src = tf.extractfile(m)
            if src is None:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with src, target.open("wb") as out:
                out.write(src.read())


def resolve_commits(repo: Path, spec: str, walk: bool, max_commits: int) -> list[str]:
    spec = spec.strip() or "HEAD"
    if ".." in spec:
        out = git_text(repo, "rev-list", "--first-parent", "--reverse", spec).split()
        if max_commits > 0:
            out = out[-max_commits:]
        return out
    sha = full_sha(repo, spec)
    if not walk:
        return [sha]
    out = git_text(
        repo, "rev-list", "--first-parent", "--reverse", f"--max-count={max_commits}", sha
    ).split()
    return out


def _index(cs: list[Clearance]) -> tuple[dict, dict[tuple, list[Clearance]], set]:
    by_world = {world_key(c): c for c in cs}
    by_slot: dict[tuple, list[Clearance]] = {}
    machines: set[tuple] = set()
    for c in cs:
        by_slot.setdefault(slot_key(c), []).append(c)
        if is_bound_debt(c):
            machines.add(machine_key(c))
    return by_world, by_slot, machines


def _was_status(parent_slot: list[Clearance]) -> tuple[str, Optional[Clearance]]:
    if not parent_slot:
        return "ABSENT", None
    bound = [p for p in parent_slot if is_bound_debt(p)]
    if bound:
        return "BOUND", bound[0]
    openish = [p for p in parent_slot if p.visa.status in {"OPEN", "SPEC", "FIXTURE"}]
    if openish:
        return openish[0].visa.status, openish[0]
    return parent_slot[0].visa.status or "OPEN", parent_slot[0]


def pair_births(
    parent_cs: list[Clearance],
    child_cs: list[Clearance],
    commit: str,
    parent: str,
    subject: str,
    *,
    follow: bool = True,
    dest_to_src: Optional[dict[str, str]] = None,
) -> list[Birth]:
    remap = dest_to_src if follow else None
    p_world, p_slot, p_machines = _index(parent_cs)
    groups: dict[tuple, list[WorldBirth]] = {}
    order: list[tuple] = []

    for c in child_cs:
        if not is_bound_debt(c):
            continue
        mk = machine_key(c)
        if not mk:
            continue
        wk = world_key(c, remap)
        sk = slot_key(c, remap)
        if wk in p_world and is_bound_debt(p_world[wk]) and machine_key(p_world[wk]) == mk:
            continue
        machine_new = mk not in p_machines
        parent_slot = p_slot.get(sk, [])
        was_st, was_c = _was_status(parent_slot)
        child_path = rel_path(c.report.fn.path)
        renamed_from = (dest_to_src or {}).get(child_path)
        if not machine_new:
            # Same machine at a new dest path: copy/spread vs dest-file rename.
            if (not follow) and renamed_from and was_st == "ABSENT":
                # mint's hole: path is in the slot key, so a rename looks
                # like ABSENT→BOUND. SPREAD is reserved for a new function.
                kind = "ABSENT→BOUND"
            else:
                kind = "SPREAD"
        elif was_st == "ABSENT":
            kind = "ABSENT→BOUND"
        elif was_st == "BOUND":
            kind = "RETARGET"
        elif was_st == "SPEC":
            kind = "SPEC→BOUND"
        else:
            kind = "OPEN→BOUND"
        wb = WorldBirth(child=c, kind=kind, was_status=was_st, was=was_c)
        if mk not in groups:
            groups[mk] = []
            order.append(mk)
        groups[mk].append(wb)

    births: list[Birth] = []
    for mk in order:
        worlds = groups[mk]
        kinds = {w.kind for w in worlds}
        kind = next(k for k in KIND_ORDER if k in kinds)
        births.append(
            Birth(
                commit=commit,
                parent=parent,
                subject=subject,
                machine=dict(mk),
                kind=kind,
                worlds=worlds,
            )
        )
    return births


def minted_for_check(births: list[Birth]) -> list[Birth]:
    return [b for b in births if b.kind != "SPREAD"]


# ---------------------------------------------------------------------------
# Lock occupancy (gage's object — skip is not a lock; not a cinch)
# ---------------------------------------------------------------------------


def is_test_path(path: str) -> bool:
    posix = path.replace("\\", "/")
    parts = [p.lower() for p in Path(posix).parts]
    if any(p in TEST_DIR_NAMES or p in FIXTURE_DIR_NAMES for p in parts):
        return True
    return bool(TEST_FILE_RE.match(Path(posix).name))


def is_source_path(path: str) -> bool:
    return Path(path.replace("\\", "/")).suffix.lower() in SOURCE_EXTS


def path_role(path: str) -> str:
    if is_test_path(path):
        return "test"
    if is_source_path(path):
        return "production"
    return "other"


def infer_world_text(text: str) -> tuple[str, dict[str, str]]:
    if re.search(r"GitHub\s*-|github\.com/", text):
        return "OPEN", {}
    require: dict[str, str] = {}
    for m in PATH_RE.finditer(text):
        derived = visalib.derive_from_path(m.group(0))
        for axis in HARD_SKIP_AXES:
            if axis in derived and axis not in require:
                require[axis] = derived[axis]
    if require and require_is_textbook(require):
        return "SPEC", {}
    if require:
        return "BOUND", {k: v for k, v in require.items() if k in HARD_SKIP_AXES}
    return "OPEN", {}


def match_require(require: dict[str, str]) -> list[dict[str, str]]:
    live = visalib.live_axes()
    misses: list[dict[str, str]] = []
    for axis, want in require.items():
        have = live.get(axis, "")
        if axis == "HOME":
            if have.rstrip("/\\") != str(want).rstrip("/\\"):
                misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
        elif have != want:
            misses.append({"axis": axis, "want": want, "have": have or "(unset)"})
    return misses


def match_label(require: dict[str, str]) -> str:
    if not require:
        return "MATCH"
    return "MISS" if match_require(require) else "MATCH"


def tests_assume_machine(tree: Path, machine: dict[str, str]) -> tuple[bool, list[str], dict[str, str]]:
    """Whether child tests encode the born machine (not leftover names)."""
    if not machine:
        return False, [], {}
    homes = [v for k, v in machine.items() if k == "HOME" and v]
    users = [v for k, v in machine.items() if k == "USER" and v]
    hits: list[str] = []
    require: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(tree).as_posix()
            if path_role(rel) != "test":
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            visa, req = infer_world_text(text)
            assumed = False
            if visa == "BOUND" and req:
                if any(req.get(k) == v for k, v in machine.items() if k in req):
                    assumed = True
                    require.update(req)
            for h in homes:
                if h in text:
                    assumed = True
                    require.setdefault("HOME", h)
            for u in users:
                if re.search(rf"(?:/Users|/home)/{re.escape(u)}\b", text) or f"USER={u}" in text:
                    assumed = True
                    require.setdefault("USER", u)
            if assumed:
                hits.append(rel)
    return bool(hits), hits, require


@dataclass
class RunResult:
    exit_code: int
    output: str
    seconds: float
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


def run_cmd(cmd: list[str], cwd: Path, timeout: float) -> RunResult:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout
        )
        seconds = time.monotonic() - t0
        output = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
        return RunResult(proc.returncode, output, seconds, False)
    except FileNotFoundError as e:
        return RunResult(127, str(e), time.monotonic() - t0, False)
    except subprocess.TimeoutExpired as e:
        out = ""
        if e.stdout:
            out += e.stdout if isinstance(e.stdout, str) else e.stdout.decode("utf-8", "replace")
        if e.stderr:
            out += "\n" + (e.stderr if isinstance(e.stderr, str) else e.stderr.decode("utf-8", "replace"))
        return RunResult(124, out + f"\n[sear: timed out after {timeout}s]", time.monotonic() - t0, True)


def count_skips(output: str) -> int:
    m = re.search(r"skipped[= ](\d+)", output, re.I)
    if m:
        return int(m.group(1))
    m = re.search(r"\bskipped=(\d+)\b", output)
    if m:
        return int(m.group(1))
    return len(re.findall(r"\bSKIP(?:PED)?\b", output))


def count_ran(output: str) -> int:
    m = re.search(r"\bran=(\d+)\b", output)
    if m:
        return int(m.group(1))
    m = re.search(r"Ran (\d+) tests?", output)
    if m:
        return int(m.group(1))
    return -1


SUITE_RUNNER = r'''
import importlib.util
import os
import sys
import traceback
import unittest
from pathlib import Path

root = Path(".").resolve()
sys.path.insert(0, str(root))
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "lab", "target", "dist", "build"}
TEST_DIRS = {"test", "tests", "spec", "specs", "__tests__"}

ran = failed = skipped = errors = 0
lines = []

def load_mod(path: Path):
    name = "sear_" + "_".join(path.relative_to(root).with_suffix("").parts)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

def test_files():
    found = []
    # test.py at repo root is a test (gage's lesson), not production.
    root_script = root / "test.py"
    if root_script.is_file():
        found.append(root_script)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        in_tests = any(p.lower() in TEST_DIRS for p in Path(rel_dir).parts) if rel_dir != "." else False
        for name in filenames:
            if not name.endswith(".py"):
                continue
            p = Path(dirpath) / name
            if p.resolve() == root_script.resolve():
                continue
            low = name.lower()
            if in_tests or low.startswith("test_") or low.endswith("_test.py") or low == "conftest.py":
                found.append(p)
    return found

files = test_files()
if not files:
    print("sear-suite ran=0 failed=0 skipped=0 errors=0")
    print("NO TESTS RAN")
    raise SystemExit(5)

class _R(unittest.TextTestResult):
    def addSkip(self, test, reason):
        super().addSkip(test, reason)

for path in files:
    # Bare assert-script (lockset test.py): run as a program.
    text = path.read_text(encoding="utf-8", errors="replace")
    has_case = "unittest" in text or "TestCase" in text
    has_fn = bool(__import__("re").search(r"^def test_", text, __import__("re").M))
    rel = path.relative_to(root).as_posix()
    if path.name == "test.py" and path.parent == root and not has_case and not has_fn:
        import runpy
        try:
            ran += 1
            runpy.run_path(str(path), run_name="__main__")
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
            if code not in (0, None):
                failed += 1
                lines.append(f"FAIL-FILE: {rel}")
                lines.append(f"FAIL: {path.name} exit {code}")
        except Exception:
            failed += 1
            lines.append(f"FAIL-FILE: {rel}")
            lines.append(f"FAIL: {path.name}")
            lines.append(traceback.format_exc().splitlines()[-1])
        continue
    try:
        mod = load_mod(path)
    except Exception as e:
        errors += 1
        lines.append(f"FAIL-FILE: {rel}")
        lines.append(f"ERROR: load {path}: {e}")
        continue
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    # pytest-style functions unittest would miss
    extra = []
    for name, obj in list(vars(mod).items()):
        if name.startswith("test_") and callable(obj) and not isinstance(obj, type):
            extra.append((name, obj))
    stream = __import__("io").StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=0, resultclass=_R)
    if suite.countTestCases():
        result = runner.run(suite)
        ran += result.testsRun
        failed += len(result.failures) + len(result.unexpectedSuccesses)
        errors += len(result.errors)
        skipped += len(result.skipped)
        if result.failures or result.errors:
            lines.append(f"FAIL-FILE: {rel}")
        for t, tb in result.failures + result.errors:
            lines.append(f"FAIL: {t}")
            if tb:
                lines.append(tb.strip().splitlines()[-1][:240])
        out = stream.getvalue()
        if "skipped=" in out:
            pass
    for name, fn in extra:
        try:
            ran += 1
            fn()
        except unittest.SkipTest as e:
            skipped += 1
            ran -= 0
        except Exception:
            failed += 1
            lines.append(f"FAIL-FILE: {rel}")
            lines.append(f"FAIL: {path.name}::{name}")
            lines.append(traceback.format_exc().splitlines()[-1][:240])

print(f"sear-suite ran={ran} failed={failed} skipped={skipped} errors={errors}")
for ln in lines[:20]:
    print(ln)
if ran == 0 and skipped == 0 and failed == 0 and errors == 0:
    print("NO TESTS RAN")
    raise SystemExit(5)
raise SystemExit(1 if failed or errors else 0)
'''


def run_suite(tree: Path, timeout: float) -> RunResult:
    return run_cmd([sys.executable, "-c", SUITE_RUNNER], tree, timeout)


def classify_suite(new_run: RunResult, sp_run: RunResult | None) -> str:
    new_skip = count_skips(new_run.output)
    new_ran = count_ran(new_run.output)
    if new_run.exit_code == 5 or "NO TESTS RAN" in new_run.output:
        return "NONE"
    if new_run.ok and new_skip and (new_ran == 0 or (new_ran > 0 and new_ran == new_skip)):
        return "SKIP"
    if not new_run.ok:
        return "BROKEN"
    if sp_run is None:
        return "NONE"
    if not sp_run.ok:
        if sp_run.exit_code == 5 or "NO TESTS RAN" in sp_run.output:
            return "NONE"
        return "LOCKED"
    sp_skip = count_skips(sp_run.output)
    sp_ran = count_ran(sp_run.output)
    if sp_skip and (sp_ran == 0 or (sp_ran > 0 and sp_ran == sp_skip)):
        return "SKIP"
    return "LOOSE"


def fail_files_of(run: RunResult | None) -> list[str]:
    if run is None:
        return []
    found: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(r"^FAIL-FILE:\s+(\S+)", run.output, re.M):
        name = m.group(1).strip()
        if name and name not in seen:
            seen.add(name)
            found.append(name)
    return found


def suite_tail(run: RunResult | None, n: int = 6) -> str:
    if run is None or not run.output:
        return ""
    lines = [ln for ln in run.output.splitlines() if ln.strip()]
    return " | ".join(lines[-n:])[:400]


@dataclass
class SuiteOcc:
    lock: str  # LOCKED LOOSE SKIP BROKEN NONE
    new: RunResult | None = None
    splice: RunResult | None = None
    test_files: list[str] = field(default_factory=list)
    fail_files: list[str] = field(default_factory=list)
    tail: str = ""


def list_test_files(tree: Path) -> list[str]:
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(tree):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(tree).as_posix()
            if path_role(rel) == "test":
                out.append(rel)
    return out


def occupy_suite(child_tree: Path, splice_tree: Path, timeout: float) -> SuiteOcc:
    tests = list_test_files(child_tree)
    if not tests:
        return SuiteOcc(lock="NONE", test_files=[])
    new_run = run_suite(child_tree, timeout)
    if new_run.exit_code == 5 or "NO TESTS RAN" in new_run.output:
        return SuiteOcc(lock="NONE", new=new_run, test_files=tests, tail=suite_tail(new_run))
    new_skip = count_skips(new_run.output)
    new_ran = count_ran(new_run.output)
    if new_run.ok and new_skip and (new_ran == 0 or new_ran == new_skip):
        return SuiteOcc(lock="SKIP", new=new_run, test_files=tests, tail=suite_tail(new_run))
    if not new_run.ok:
        return SuiteOcc(
            lock="BROKEN",
            new=new_run,
            test_files=tests,
            fail_files=fail_files_of(new_run),
            tail=suite_tail(new_run),
        )
    sp_run = run_suite(splice_tree, timeout)
    lock = classify_suite(new_run, sp_run)
    fails = fail_files_of(sp_run) if lock == "LOCKED" else fail_files_of(new_run)
    tail = suite_tail(sp_run if lock == "LOCKED" else new_run)
    return SuiteOcc(
        lock=lock, new=new_run, splice=sp_run, test_files=tests, fail_files=fails, tail=tail
    )


def overlay_splice(
    parent_tree: Path | None,
    child_tree: Path,
    dest: Path,
    dest_to_src: Optional[dict[str, str]] = None,
) -> None:
    """tests@child, production@parent. Whole files, not hunks.

    When dest_to_src is set, parent production at the old path is laid onto
    the child's dest path so a visa-bearing test that moved with the dest
    file still splices against old production. Copy is not a follow.
    """
    shutil.copytree(child_tree, dest, dirs_exist_ok=True)
    dest_to_src = dest_to_src or {}
    src_to_dest = {src: dst for dst, src in dest_to_src.items()}
    child_prod = []
    for dirpath, dirnames, filenames in os.walk(dest):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(dest).as_posix()
            if path_role(rel) == "production":
                child_prod.append(rel)
    if parent_tree is None:
        for rel in child_prod:
            (dest / rel).unlink(missing_ok=True)
        return
    parent_prod: set[str] = set()
    child_dest_keep: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(parent_tree):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(parent_tree).as_posix()
            if path_role(rel) != "production":
                continue
            parent_prod.add(rel)
            dest_rel = src_to_dest.get(rel, rel)
            child_dest_keep.add(dest_rel)
            target = dest / dest_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
    for rel in child_prod:
        if rel not in child_dest_keep:
            (dest / rel).unlink(missing_ok=True)
    for src, dst in src_to_dest.items():
        if src != dst and src not in child_dest_keep:
            (dest / src).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Join: LOCKED-and-BOUND-at-birth
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """One joint (or one-sided) occupancy at one commit."""

    tag: str  # BRAND | MINT | GAGE | SKIP | OPEN | BROKEN
    commit: str
    parent: str
    subject: str
    machine: dict[str, str]
    birth_kind: str
    lock: str
    visa: str
    match: str
    tests: list[str] = field(default_factory=list)
    worlds: list[WorldBirth] = field(default_factory=list)
    note: str = ""

    @property
    def is_brand(self) -> bool:
        return self.tag == "BRAND"

    @property
    def verdict(self) -> str:
        if self.tag == "BRAND":
            return "LOCKED-and-BOUND-at-birth"
        if self.tag == "SKIP":
            return "SKIP-and-BOUND-at-birth"
        if self.tag == "MINT":
            return f"{self.birth_kind}-unlocked"
        if self.tag == "GAGE":
            return "LOCKED-and-BOUND"
        if self.tag == "OPEN":
            return "LOCKED-and-OPEN"
        return self.tag


def lock_tests(occ: SuiteOcc, hits: list[str], assumed: bool) -> list[str]:
    """Name the tests that veto or assume the born machine, not the whole suite.

    v0.1 listed every test file at the child (dummy `assert True` next to
    an OPEN test.py lock). The lockset is the fail witnesses, else the
    tests that encode the visa.
    """
    if assumed and hits:
        return list(dict.fromkeys(hits))
    if occ.fail_files:
        return list(dict.fromkeys(occ.fail_files))
    return list(occ.test_files)


def join_birth_lock(
    birth: Birth, occ: SuiteOcc, hits: list[str], assumed: bool
) -> Event:
    match = match_label(birth.machine)
    tests = lock_tests(occ, hits, assumed)
    if occ.lock == "BROKEN":
        note = "suite already red on the child tree"
        if occ.tail:
            note += f" ({occ.tail})"
        return Event(
            tag="BROKEN",
            commit=birth.commit,
            parent=birth.parent,
            subject=birth.subject,
            machine=birth.machine,
            birth_kind=birth.kind,
            lock="BROKEN",
            visa="BOUND",
            match=match,
            tests=tests or occ.fail_files or occ.test_files,
            worlds=birth.worlds,
            note=note,
        )
    if occ.lock == "SKIP":
        return Event(
            tag="SKIP",
            commit=birth.commit,
            parent=birth.parent,
            subject=birth.subject,
            machine=birth.machine,
            birth_kind=birth.kind,
            lock="SKIP",
            visa="BOUND",
            match=match,
            tests=hits or occ.test_files,
            worlds=birth.worlds,
            note="skip is not a lock",
        )
    if occ.lock == "LOCKED" and assumed:
        return Event(
            tag="BRAND",
            commit=birth.commit,
            parent=birth.parent,
            subject=birth.subject,
            machine=birth.machine,
            birth_kind=birth.kind,
            lock="LOCKED",
            visa="BOUND",
            match=match,
            tests=tests,
            worlds=birth.worlds,
        )
    if occ.lock == "LOCKED" and not assumed:
        return Event(
            tag="OPEN",
            commit=birth.commit,
            parent=birth.parent,
            subject=birth.subject,
            machine=birth.machine,
            birth_kind=birth.kind,
            lock="LOCKED",
            visa="OPEN",
            match=match,
            tests=tests,
            worlds=birth.worlds,
            note="lock is OPEN — birth is mint-only; OPEN lock is a clearance",
        )
    return Event(
        tag="MINT",
        commit=birth.commit,
        parent=birth.parent,
        subject=birth.subject,
        machine=birth.machine,
        birth_kind=birth.kind,
        lock=occ.lock,
        visa="BOUND",
        match=match,
        tests=hits or occ.test_files,
        worlds=birth.worlds,
        note="visa-birth without a lock",
    )


def collect_events(
    repo: Path,
    commits: list[str],
    *,
    include_spread: bool,
    want_locks: bool,
    timeout: float,
    follow: bool = True,
) -> tuple[list[Event], int, int, int]:
    """Return (events, scanned, skipped, broken)."""
    events: list[Event] = []
    scanned = 0
    skipped = 0
    broken = 0
    cache: dict[str, list[Clearance]] = {}

    def worlds_at(rev: Optional[str]) -> list[Clearance]:
        if rev is None:
            return []
        if rev in cache:
            return cache[rev]
        tmp = Path(tempfile.mkdtemp(prefix="sear-tree-"))
        try:
            materialize(repo, rev, tmp)
            cs = scan_tree(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        cache[rev] = cs
        return cs

    suite_cache: dict[str, SuiteOcc] = {}

    def suite_at(
        parent: Optional[str], sha: str, dest_to_src: Optional[dict[str, str]] = None
    ) -> SuiteOcc:
        key = f"{parent or '∅'}..{sha}..{'F' if dest_to_src else '-'}"
        if key in suite_cache:
            return suite_cache[key]
        child_tmp = Path(tempfile.mkdtemp(prefix="sear-child-"))
        parent_tmp = Path(tempfile.mkdtemp(prefix="sear-parent-"))
        splice_tmp = Path(tempfile.mkdtemp(prefix="sear-splice-"))
        try:
            materialize(repo, sha, child_tmp)
            # Occupancy always follows dest identity. Import-fail of a
            # renamed dest is not a visa veto (v0.1 hole). --no-follow
            # only path-keys slot pairing.
            if parent:
                materialize(repo, parent, parent_tmp)
                overlay_splice(parent_tmp, child_tmp, splice_tmp, dest_to_src=dest_to_src)
            else:
                overlay_splice(None, child_tmp, splice_tmp, dest_to_src=dest_to_src)
            occ = occupy_suite(child_tmp, splice_tmp, timeout)
        finally:
            shutil.rmtree(child_tmp, ignore_errors=True)
            shutil.rmtree(parent_tmp, ignore_errors=True)
            shutil.rmtree(splice_tmp, ignore_errors=True)
        suite_cache[key] = occ
        return occ

    def assume_at(sha: str, machine: dict[str, str]) -> tuple[bool, list[str], dict[str, str]]:
        tmp = Path(tempfile.mkdtemp(prefix="sear-assume-"))
        try:
            materialize(repo, sha, tmp)
            return tests_assume_machine(tmp, machine)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    for sha in commits:
        parent = first_parent(repo, sha)
        if not source_touched(repo, parent, sha):
            skipped += 1
            continue
        scanned += 1
        rmap = slot_identity_map(
            worlds_at(parent) if parent else [],
            worlds_at(sha),
            dest_renames(repo, parent, sha),
        )
        parent_cs = worlds_at(parent)
        child_cs = worlds_at(sha)
        found = pair_births(
            parent_cs,
            child_cs,
            commit=short_sha(repo, sha),
            parent=short_sha(repo, parent) if parent else "∅",
            subject=commit_subject(repo, sha),
            follow=follow,
            dest_to_src=rmap,
        )
        minted = minted_for_check(found) if not include_spread else found
        need_suite = bool(minted) or (want_locks and tests_touched(repo, parent, sha))
        occ: SuiteOcc | None = None
        if need_suite:
            occ = suite_at(parent, sha, dest_to_src=rmap)
            if occ.lock == "BROKEN":
                broken += 1

        for b in found:
            if b.kind == "SPREAD" and not include_spread:
                continue
            assumed, hits, req = assume_at(sha, b.machine)
            if occ is None:
                # birth without suite run: treat as mint-only
                events.append(
                    Event(
                        tag="MINT",
                        commit=b.commit,
                        parent=b.parent,
                        subject=b.subject,
                        machine=b.machine,
                        birth_kind=b.kind,
                        lock="NONE",
                        visa="BOUND",
                        match=match_label(b.machine),
                        tests=[],
                        worlds=b.worlds,
                        note="visa-birth without a lock",
                    )
                )
                continue
            ev = join_birth_lock(b, occ, hits, assumed or bool(hits))
            events.append(ev)

        if want_locks and occ is not None and occ.lock == "LOCKED":
            # A LOCKED-and-BOUND whose machine the parent already held is gage-now.
            already = {machine_key(c) for c in parent_cs if is_bound_debt(c)}
            child_bound = [c for c in child_cs if is_bound_debt(c)]
            birth_keys = {machine_key_from_dict(b.machine) for b in minted}
            seen_gages: set[tuple] = set()
            for c in child_bound:
                mk = machine_key(c)
                if not mk or mk in birth_keys or mk not in already:
                    continue
                assumed, hits, req = assume_at(sha, dict(mk))
                if not assumed:
                    continue
                if mk in seen_gages:
                    continue
                seen_gages.add(mk)
                events.append(
                    Event(
                        tag="GAGE",
                        commit=short_sha(repo, sha),
                        parent=short_sha(repo, parent) if parent else "∅",
                        subject=commit_subject(repo, sha),
                        machine=dict(mk),
                        birth_kind="-",
                        lock="LOCKED",
                        visa="BOUND",
                        match=match_label(dict(mk)),
                        tests=hits or occ.test_files,
                        note="lock of a visa the parent already held",
                    )
                )

    return events, scanned, skipped, broken


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


def require_bits(require: dict[str, str]) -> str:
    return " ".join(f"{k}={v}" for k, v in require.items())


def _world_line(c: Clearance) -> str:
    call = emit_call(c)
    site = c.fixture.sites[0] if c.fixture.sites else f"{c.report.fn.path}:{c.report.fn.line}"
    if ":" in site:
        site = site.rsplit(":", 1)[0]
    if call:
        return f"{c.report.fn.qualname}  {call}  {site}"
    return f"{c.report.fn.qualname}  {site}"


def brands_only(events: list[Event]) -> list[Event]:
    return [e for e in events if e.is_brand]


def render_debt(events: list[Event]) -> str:
    """Default CI stdout: BRAND only. Empty when no lock was born."""
    brands = brands_only(events)
    if not brands:
        return ""
    n_worlds = sum(len(e.worlds) for e in brands)
    commits: list[str] = []
    seen: set[str] = set()
    for e in brands:
        if e.commit not in seen:
            seen.add(e.commit)
            commits.append(e.commit)
    lines: list[str] = []
    if len(commits) == 1:
        e0 = brands[0]
        lines.append(
            f"sear  brands={len(brands)}  worlds={n_worlds}  "
            f"commit={e0.commit}  parent={e0.parent}"
        )
        if e0.subject:
            lines.append(f"  {e0.subject}")
    else:
        lines.append(f"sear  brands={len(brands)}  worlds={n_worlds}  commits={len(commits)}")
    last = None
    for e in brands:
        if len(commits) > 1 and e.commit != last:
            last = e.commit
            subj = f"  {e.subject}" if e.subject else ""
            lines.append(f"  {e.commit}  parent={e.parent}{subj}")
        req = require_bits(e.machine)
        head = f"  BRAND  LOCKED-and-BOUND-at-birth  {e.birth_kind}"
        if req:
            head += f"  {req}"
        head += f"  match={e.match}"
        lines.append(head)
        for w in e.worlds:
            lines.append(f"    {_world_line(w.child)}")
            if w.was is not None:
                lines.append(f"    was  {w.was_status}  {_world_line(w.was)}")
            elif w.was_status == "ABSENT":
                lines.append("    was  ABSENT")
        for t in e.tests[:8]:
            lines.append(f"    lock  {t}")
    return "\n".join(lines) + "\n"


def render_report(events: list[Event], scanned: int, skipped: int, n_commits: int) -> str:
    n_brand = sum(1 for e in events if e.tag == "BRAND")
    n_mint = sum(1 for e in events if e.tag == "MINT")
    n_gage = sum(1 for e in events if e.tag == "GAGE")
    n_skip = sum(1 for e in events if e.tag == "SKIP")
    n_open = sum(1 for e in events if e.tag == "OPEN")
    lines = [
        f"sear  commits={n_commits}  scanned={scanned}  skipped={skipped}  "
        f"brands={n_brand}  mint-only={n_mint}  gage-only={n_gage}  "
        f"skip-at-birth={n_skip}  open-lock={n_open}",
        "joint = lock in the same commit as the visa-birth. "
        "mint-only is a visa without a lock. "
        "gage-only is a lock of a visa the parent already held. skip is not a lock.",
    ]
    last = None
    for e in events:
        if e.commit != last:
            last = e.commit
            subj = f"  {e.subject}" if e.subject else ""
            lines.append(f"  {e.commit}  parent={e.parent}{subj}")
        req = require_bits(e.machine)
        extra = f"  {req}" if req else ""
        lines.append(
            f"    {e.tag:6s}  {e.verdict}  birth={e.birth_kind}  lock={e.lock}  "
            f"visa={e.visa}  match={e.match}{extra}"
        )
        for w in e.worlds[:4]:
            lines.append(f"      {_world_line(w.child)}")
        for t in e.tests[:6]:
            lines.append(f"      lock  {t}")
        if e.note:
            lines.append(f"      note: {e.note}")
    return "\n".join(lines) + "\n"


def render_porcelain(events: list[Event]) -> str:
    lines = []
    for e in events:
        req = ",".join(f"{k}={v}" for k, v in e.machine.items())
        tests = ",".join(e.tests[:6])
        fn = e.worlds[0].child.report.fn.qualname if e.worlds else "-"
        call = emit_call(e.worlds[0].child) if e.worlds else "-"
        lines.append(
            "\t".join(
                [
                    "sear",
                    e.tag,
                    e.commit,
                    e.parent,
                    e.birth_kind,
                    e.lock,
                    e.visa,
                    e.match,
                    req,
                    fn,
                    call.replace("\t", " ").replace("\n", " "),
                    tests,
                    e.verdict,
                ]
            )
        )
    return ("\n".join(lines) + "\n") if lines else ""


def event_record(e: Event) -> dict:
    return {
        "tag": e.tag,
        "verdict": e.verdict,
        "commit": e.commit,
        "parent": e.parent,
        "subject": e.subject,
        "birth": e.birth_kind,
        "lock": e.lock,
        "visa": e.visa,
        "match": e.match,
        "machine": e.machine,
        "tests": e.tests,
        "note": e.note,
        "worlds": [
            {
                "kind": w.kind,
                "was": w.was_status,
                "fn": w.child.report.fn.qualname,
                "call": emit_call(w.child),
                "path": rel_path(w.child.report.fn.path),
            }
            for w in e.worlds
        ],
    }


def render_json(events: list[Event], extra: dict | None = None) -> str:
    payload = {
        "tool": "sear",
        "version": VERSION,
        "events": [event_record(e) for e in events],
        "brands": [event_record(e) for e in events if e.is_brand],
        "follow": extra.get("follow") if extra else None,
    }
    if extra:
        payload.update(extra)
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# self-test fixtures
# ---------------------------------------------------------------------------


def _git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "sear@lab"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "sear"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=path, check=True, capture_output=True)


def _commit(path: Path, msg: str) -> str:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "sear")
    env.setdefault("GIT_AUTHOR_EMAIL", "sear@lab")
    env.setdefault("GIT_COMMITTER_NAME", "sear")
    env.setdefault("GIT_COMMITTER_EMAIL", "sear@lab")
    subprocess.run(["git", "commit", "-m", msg], cwd=path, check=True, capture_output=True, env=env)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _open_profile(root: Path) -> None:
    _write(
        root / "src" / "profile.py",
        "import os\n"
        "def load_profile(home):\n"
        "    return home == '/tmp/cache' or os.path.isdir(home)\n"
        "def who(home):\n"
        "    return home == '/tmp/cache'\n"
        "def start():\n"
        "    load_profile('/tmp/cache')\n"
        "    who('/tmp/cache')\n",
    )
    _write(
        root / "tests" / "test_profile.py",
        "from src.profile import load_profile\n"
        "def test_tmp():\n"
        "    load_profile('/tmp')\n",
    )
    _write(
        root / "src" / "App.swift",
        "// when the macOS PollWatcher fallback is active.\n"
        "public enum WindowTitleParser {\n"
        '    private static let browsers: Set<String> = ["Chrome", "Safari", "Brave Browser"]\n'
        "    public static func isBrowser(_ appName: String) -> Bool {\n"
        "        browsers.contains(appName)\n"
        "    }\n"
        "}\n"
        "public func loadHome(_ path: String) -> Bool { true }\n"
        "public func boot() {\n"
        '    _ = loadHome("/tmp/sitbone")\n'
        '    _ = WindowTitleParser.isBrowser("Brave Browser")\n'
        "}\n",
    )
    _write(
        root / "src" / "quote.py",
        "def quote(path):\n"
        "    return path\n"
        "def examples():\n"
        "    quote('/home/user/project')\n",
    )
    _write(
        root / "src" / "nick.py",
        "def nick(name):\n"
        "    return name\n"
        "def go():\n"
        "    nick('desktop')\n",
    )
    _write(
        root / "src" / "add.py",
        "def add(a, b):\n"
        "    return 0\n",
    )
    _write(
        root / "add.py",
        "def add(a, b):\n"
        "    return 0\n",
    )


def _pin_alice(root: Path) -> None:
    _write(
        root / "src" / "profile.py",
        "import os\n"
        "def load_profile(home):\n"
        "    return home == '/Users/alice' or os.path.isdir(home)\n"
        "def who(home):\n"
        "    return home == '/Users/alice'\n"
        "def start():\n"
        "    load_profile('/Users/alice')\n"
        "    who('/Users/alice')\n",
    )


def _lock_alice_tests(root: Path) -> None:
    _write(
        root / "tests" / "test_profile.py",
        "from src.profile import who\n"
        "def test_alice():\n"
        "    assert who('/Users/alice')\n",
    )


def _skip_alice_tests(root: Path) -> None:
    _write(
        root / "tests" / "test_profile.py",
        "import os\n"
        "import unittest\n"
        "from src.profile import who\n"
        "\n"
        "@unittest.skipUnless(os.path.expanduser('~') == '/Users/alice', 'alice only')\n"
        "class TestAlice(unittest.TestCase):\n"
        "    def test_alice(self):\n"
        "        self.assertTrue(who('/Users/alice'))\n",
    )


def _open_lock_add(root: Path) -> None:
    _write(
        root / "add.py",
        "def add(a, b):\n"
        "    print('debug')\n"
        "    return a + b\n",
    )
    _write(
        root / "test.py",
        "from add import add\n"
        "assert add(2, 3) == 5\n",
    )


def self_test() -> int:
    failures: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        if cond:
            print(f"  ok  {msg}")
        else:
            failures.append(msg)
            print(f"  FAIL  {msg}", file=sys.stderr)

    def run_cli(argv: list[str]) -> tuple[int, str, str]:
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = main(argv)
        return rc, buf.getvalue(), err.getvalue()

    tmp = Path(tempfile.mkdtemp(prefix="sear-self-"))

    # --- history A: mint then later gage (split across commits) ---
    a = tmp / "split"
    _git_init(a)
    _open_profile(a)
    c_open = _commit(a, "open portable worlds")
    _pin_alice(a)
    c_mint = _commit(a, "pin Alice home")
    _write(
        a / "src" / "App.swift",
        (a / "src" / "App.swift").read_text(encoding="utf-8").replace(
            'loadHome("/tmp/sitbone")', 'loadHome("/Users/alice/Library/sitbone")'
        ),
    )
    c_spread = _commit(a, "spread Alice into Swift")
    _lock_alice_tests(a)
    c_gage = _commit(a, "lock Alice after the birth")
    _write(
        a / "src" / "titles.py",
        "def extract_title(title):\n"
        "    return title.split(' - ', 1)[0]\n"
        "def crawl():\n"
        "    extract_title('GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome')\n",
    )
    c_title = _commit(a, "add GitHub titles")

    rc, out, _err = run_cli(["-C", str(a), c_mint])
    ok(rc == 0, f"split mint-only commit is not a brand rc={rc} {out}")
    ok(out == "", f"split mint-only default empty {out!r}")

    rc, rep, _err = run_cli(["-C", str(a), "--report", c_mint])
    ok("MINT" in rep or "unlocked" in rep, f"split --report names mint-only {rep}")
    ok("BRAND" not in rep.split("brands=")[0] or "brands=0" in rep, f"split report brands=0 {rep}")

    rc, out, _err = run_cli(["-C", str(a), c_gage])
    ok(rc == 0, f"split gage-only (lock after birth) is not a brand rc={rc} {out}")
    ok(out == "", f"split gage-only default empty {out!r}")

    rc, out, _err = run_cli(["-C", str(a), f"{c_open[:10]}..{c_gage[:10]}"])
    # Range spanning mint-then-lock: concatenation of mint|gage would fire;
    # brand stays empty because they did not co-occur.
    ok(rc == 0, f"split range mint-then-lock is not a brand rc={rc} {out}")
    ok(out == "", f"split range default empty {out!r}")

    rc, out, _err = run_cli(["-C", str(a), c_spread])
    ok(rc == 0 and out == "", f"SPREAD is not a brand rc={rc} {out!r}")

    rc, out, _err = run_cli(["-C", str(a), c_title])
    ok(rc == 0 and out == "", f"GitHub titles not a brand {out!r}")
    ok("annenpolka" not in out, "USER not minted from a title")

    rc, out, _err = run_cli(["-C", str(a), "--walk", "--max", "8", c_title])
    ok(rc == 0, f"split walk has no same-commit brand rc={rc} {out}")
    ok(out == "", f"split walk default empty {out!r}")

    # --- history B: same commit pin + lock (the object) ---
    b = tmp / "joint"
    _git_init(b)
    _open_profile(b)
    _commit(b, "open portable worlds")
    _pin_alice(b)
    _lock_alice_tests(b)
    c_brand = _commit(b, "pin Alice home and lock it")

    rc, out, _err = run_cli(["-C", str(b), c_brand])
    ok(rc == 1, f"joint birth+lock is a brand rc={rc}")
    ok("BRAND" in out and "LOCKED-and-BOUND-at-birth" in out, f"joint names the verdict {out}")
    ok("/Users/alice" in out, f"joint names Alice {out}")
    ok("SPEC→BOUND" in out or "OPEN→BOUND" in out or "ABSENT→BOUND" in out, f"joint names birth kind {out}")
    ok("test_profile" in out or "lock" in out, f"joint names the locking tests {out}")
    ok("import pytest" not in out and "XCTest" not in out, "joint is not a test file")
    ok("Brave" not in out, f"OPEN Brave is not a brand {out}")
    ok("erst" not in out.lower() and "\tt1\t" not in out, "not leftover names")

    rc, out, _err = run_cli(["-q", "-C", str(b), c_brand])
    ok(rc == 1 and out == "", f"quiet is exit only rc={rc} {out!r}")

    rc, out, _err = run_cli(["-C", str(b), "--json", c_brand])
    ok('"tool": "sear"' in out, "json names sear")
    ok('"tool": "brand"' not in out and '"tool": "gage"' not in out and '"tool": "mint"' not in out, "json is not a parent")
    ok("LOCKED-and-BOUND-at-birth" in out, "json verdict")

    rc, out, _err = run_cli(["-C", str(b), "--porcelain", c_brand])
    ok(out.startswith("sear\t") or "\nsear\t" in "\n" + out, f"porcelain tag {out}")
    ok("BRAND" in out, f"porcelain BRAND {out}")

    # --- history C: skip-at-birth (gage empty, mint would fire) ---
    c = tmp / "skip"
    _git_init(c)
    _open_profile(c)
    _commit(c, "open portable worlds")
    _pin_alice(c)
    _skip_alice_tests(c)
    c_skip = _commit(c, "pin Alice with skipif lock")

    rc, out, _err = run_cli(["-C", str(c), c_skip])
    ok(rc == 0, f"skip-at-birth is not a brand rc={rc} {out}")
    ok(out == "", f"skip-at-birth default empty {out!r}")
    rc, _out, _err = run_cli(["-C", str(c), "--due", "-q", c_skip])
    ok(rc == 1, f"--due recovers skip-at-birth rc={rc}")
    rc, rep, _err = run_cli(["-C", str(c), "--report", c_skip])
    ok("SKIP" in rep, f"skip-at-birth --report names SKIP {rep}")

    # --- history D: OPEN lock coinciding with a birth ---
    d = tmp / "openlock"
    _git_init(d)
    _open_profile(d)
    _commit(d, "open portable worlds")
    _pin_alice(d)
    _open_lock_add(d)
    _write(d / "tests" / "test_profile.py", "def test_ok():\n    assert True\n")
    c_openlock = _commit(d, "pin Alice and lock add()")

    rc, out, _err = run_cli(["-C", str(d), c_openlock])
    ok(rc == 0, f"OPEN lock at a birth is not a brand rc={rc} {out}")
    ok(out == "", f"OPEN lock default empty {out!r}")
    rc, rep, _err = run_cli(["-C", str(d), "--report", c_openlock])
    ok("OPEN" in rep or "MINT" in rep, f"OPEN lock at birth is clearance/mint-only {rep}")
    ok("lock  test.py" in rep, f"OPEN lock witness is test.py {rep}")
    ok("lock  tests/test_profile.py" not in rep, f"dummy assert-True is not the OPEN lock {rep}")
    ok("LOCKED-and-BOUND-at-birth" not in render_debt(
        # just confirm default stayed empty
        []
    ), "sanity")

    # --- history E: live HOME brand (MATCH still a brand) ---
    home = str(Path.home())
    e = tmp / "live"
    _git_init(e)
    _write(
        e / "app.py",
        "def who(home):\n"
        "    return home == '/tmp/nobody'\n"
        "def boot():\n"
        "    who('/tmp/nobody')\n",
    )
    _write(
        e / "tests" / "test_who.py",
        "from app import who\n"
        "def test_old():\n"
        "    assert who('/tmp/nobody')\n",
    )
    _commit(e, "old who")
    _write(
        e / "app.py",
        f"def who(home):\n"
        f"    return home == {home!r}\n"
        f"def boot():\n"
        f"    who({home!r})\n",
    )
    _write(
        e / "tests" / "test_who.py",
        "from app import who\n"
        f"def test_live():\n"
        f"    assert who({home!r})\n",
    )
    c_live = _commit(e, "pin live HOME and lock it")
    rc, out, _err = run_cli(["-C", str(e), c_live])
    ok(rc == 1, f"live HOME same-commit lock is a brand rc={rc} {out}")
    ok(home in out, f"live brand names HOME {out}")
    ok("match=MATCH" in out, f"MATCH is still a brand {out}")

    # --- -C must be a repo root ---
    nested = a / "src"
    rc, _out, err = run_cli(["-C", str(nested)])
    ok(rc == 2, f"nested -C is not a repo root rc={rc}")
    ok("not a git repository" in err, f"nested error {err}")

    # --- abs symlink walk must not crash (kizu trap) ---
    linked = tmp / "link"
    _git_init(linked)
    _open_profile(linked)
    (linked / "AGENTS.md").symlink_to("/Users/someone/CLAUDE.md")
    _commit(linked, "open with abs link")
    _pin_alice(linked)
    _lock_alice_tests(linked)
    c_link = _commit(linked, "pin Alice under abs link")
    rc, out, err = run_cli(["-C", str(linked), "--walk", "--max", "8", c_link])
    ok(rc == 1, f"abs-link walk still brands Alice rc={rc} err={err}")
    ok("AbsoluteLinkError" not in err and "Traceback" not in err, f"abs-link must not crash {err}")
    ok("BRAND" in out, f"abs-link brand {out}")

    # --- history F: rename of a visa-bearing test still brands the birth ---
    f = tmp / "test-rename"
    _git_init(f)
    _open_profile(f)
    _commit(f, "open portable worlds")
    _pin_alice(f)
    _lock_alice_tests(f)
    c_birth = _commit(f, "pin Alice home and lock it")
    subprocess.run(
        ["git", "mv", "tests/test_profile.py", "tests/test_who.py"],
        cwd=f,
        check=True,
        capture_output=True,
    )
    c_ren = _commit(f, "rename visa-bearing test")
    rc, out, _err = run_cli(["-C", str(f), c_ren])
    ok(rc == 0 and out == "", f"test rename is not a brand rc={rc} {out!r}")
    rc, out, _err = run_cli(["-C", str(f), "--walk", "--max", "8", c_ren])
    ok(rc == 1, f"walk after test rename still brands rc={rc} {out}")
    birth_s = short_sha(f, c_birth)
    ren_s = short_sha(f, c_ren)
    ok("BRAND" in out and f"commit={birth_s}" in out, f"walk brands the birth commit {out}")
    ok(f"commit={ren_s}" not in out, f"walk commit is not the rename {out}")
    rc, out, _err = run_cli(["-C", str(f), "--no-follow", c_ren])
    ok(rc == 0 and out == "", f"--no-follow test rename is not a brand {out!r}")

    # --- history G: dest-file rename of production (mint's hole) ---
    g = tmp / "dest-rename"
    _git_init(g)
    _open_profile(g)
    _commit(g, "open portable worlds")
    _pin_alice(g)
    _lock_alice_tests(g)
    c_gb = _commit(g, "pin Alice home and lock it")
    subprocess.run(
        ["git", "mv", "src/profile.py", "src/user.py"],
        cwd=g,
        check=True,
        capture_output=True,
    )
    _write(
        g / "tests" / "test_profile.py",
        "from src.user import who\n"
        "def test_alice():\n"
        "    assert who('/Users/alice')\n",
    )
    c_gr = _commit(g, "rename dest profile.py → user.py")
    rc, out, _err = run_cli(["-C", str(g), c_gr])
    ok(rc == 0 and out == "", f"dest rename --follow is not a brand rc={rc} {out!r}")
    rc, walk, _err = run_cli(["-C", str(g), "--walk", "--max", "8", c_gr])
    ok(rc == 1, f"walk after dest rename still brands rc={rc} {walk}")
    gb_s = short_sha(g, c_gb)
    gr_s = short_sha(g, c_gr)
    ok(f"commit={gb_s}" in walk, f"dest-rename walk brands birth {walk}")
    ok(f"commit={gr_s}" not in walk, f"dest-rename walk is not the rename {walk}")
    rc, nfo_out, _err = run_cli(["-C", str(g), "--no-follow", c_gr])
    ok(rc == 0 and nfo_out == "", f"--no-follow dest rename default empty (lock did not newly fire) rc={rc} {nfo_out!r}")
    rc, rep, _err = run_cli(["-C", str(g), "--no-follow", "--report", c_gr])
    ok("ABSENT→BOUND" in rep, f"--no-follow dest rename looks like ABSENT→BOUND {rep}")
    ok("MINT" in rep, f"--no-follow dest rename is mint-hole not a brand {rep}")
    ok("brands=0" in rep, f"--no-follow dest rename report brands=0 {rep}")

    # --- history I: same-commit pin + dest rename + lock ---
    i = tmp / "same-ren"
    _git_init(i)
    _open_profile(i)
    _commit(i, "open portable worlds")
    _pin_alice(i)
    subprocess.run(
        ["git", "mv", "src/profile.py", "src/user.py"],
        cwd=i,
        check=True,
        capture_output=True,
    )
    _write(
        i / "tests" / "test_profile.py",
        "from src.user import who\n"
        "def test_alice():\n"
        "    assert who('/Users/alice')\n",
    )
    c_sr = _commit(i, "pin Alice, mv dest, and lock it")
    rc, out, _err = run_cli(["-C", str(i), c_sr])
    ok(rc == 1, f"same-commit pin+mv+lock is a brand rc={rc} {out}")
    ok("BRAND" in out, f"same-commit names BRAND {out}")
    ok("SPEC→BOUND" in out or "OPEN→BOUND" in out, f"follow same-commit is not ABSENT→BOUND {out}")
    ok("ABSENT→BOUND" not in out, f"follow does not name ABSENT for a dest-moved birth {out}")
    rc, nfo, _err = run_cli(["-C", str(i), "--no-follow", c_sr])
    ok(rc == 1, f"--no-follow same-commit still brands (lock is real) rc={rc} {nfo}")
    ok("ABSENT→BOUND" in nfo, f"--no-follow same-commit kind is the hole {nfo}")

    # --- history H: copy is not follow ---
    h = tmp / "copy"
    _git_init(h)
    _open_profile(h)
    _commit(h, "open")
    _pin_alice(h)
    _lock_alice_tests(h)
    _commit(h, "pin Alice home and lock it")
    shutil.copy(h / "src" / "profile.py", h / "src" / "copy.py")
    c_cp = _commit(h, "copy profile.py to copy.py")
    rc, out, _err = run_cli(["-C", str(h), c_cp])
    ok(rc == 0 and out == "", f"copy is not a brand rc={rc} {out!r}")
    rc, nfo, _err = run_cli(["-C", str(h), "--no-follow", c_cp])
    ok(rc == 0 and nfo == "", f"copy --no-follow is not a brand {nfo!r}")

    # --- textbook / Brave are not births ---
    t1 = Path(tempfile.mkdtemp(prefix="sear-scan-"))
    materialize(a, c_open, t1)
    w1 = scan_tree(t1)
    ok(not any(is_bound_debt(x) for x in w1), f"open tree has no BOUND {[(x.report.fn.name, x.visa.status) for x in w1]}")
    shutil.rmtree(t1, ignore_errors=True)

    # --- HEAD of split (titles) empty ---
    rc, out, _err = run_cli(["-C", str(a)])
    ok(rc == 0 and out == "", f"HEAD titles empty rc={rc} {out!r}")

    shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("SELF-TEST FAILURES:")
        for f in failures:
            print("  FAIL", f)
        return 1
    print("self-test ok")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sear",
        description=(
            "Lockset clearance at visa-birth, following dest-file slot identity. "
            "Default: empty stdout unless this range newly locked production in "
            "the same commit that first bound a machine visa. A dest-only rename "
            "is not a birth. Copy is not a follow. Skip is not a lock. SPREAD is "
            "not a mint. Not a fourth cinch."
        ),
    )
    p.add_argument(
        "rev",
        nargs="?",
        default="HEAD",
        help="commit or A..B range (default: HEAD vs its parent)",
    )
    p.add_argument("-C", "--root", default=".", help="git repository root")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--porcelain",
        action="store_true",
        help="sear\\ttag\\tcommit\\tparent\\tbirth\\tlock\\tvisa\\tmatch\\trequire\\tfn\\tcall\\ttests\\tverdict",
    )
    p.add_argument("--report", "--human", action="store_true", help="all sides: BRAND / MINT / GAGE / SKIP / OPEN")
    p.add_argument(
        "--locks",
        action="store_true",
        help="also occupy suite locks of a visa the parent already held (gage-now)",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if this range branded a lock (already the default)",
    )
    p.add_argument(
        "--due",
        action="store_true",
        help="fail on SKIP-and-BOUND-at-birth too (stained tests that did not occupy)",
    )
    p.add_argument(
        "--spread",
        action="store_true",
        help="also join SPREAD births (default hides them; SPREAD is not a mint)",
    )
    p.add_argument(
        "--follow",
        action="store_true",
        default=True,
        help="follow visa slot identity across dest-file R records (default)",
    )
    p.add_argument(
        "--no-follow",
        action="store_false",
        dest="follow",
        help="path-keyed slots (mint's hole: dest rename looks like ABSENT→BOUND)",
    )
    p.add_argument("--walk", action="store_true", help="walk first-parent history of REV")
    p.add_argument(
        "--max",
        type=int,
        default=0,
        help="max commits to walk (default: 1 for a single rev, unlimited for a range)",
    )
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--version", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    p = build_parser()
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2
    if args.version:
        print(VERSION)
        return 0
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve()
    if not root.exists():
        eprint(f"sear: no such path: {root}")
        return 2
    if not is_git_repo(root):
        eprint(f"sear: not a git repository: {root}")
        return 2
    walk = args.walk or (".." in args.rev)
    if args.max > 0:
        max_commits = args.max
    elif walk:
        max_commits = 10_000
    else:
        max_commits = 1
    try:
        commits = resolve_commits(root, args.rev, walk=walk, max_commits=max_commits)
    except GitError as e:
        eprint(f"sear: {e}")
        return 2
    if not commits:
        eprint(f"sear: no commits in {args.rev}")
        return 2
    if not walk:
        commits = commits[-1:]
    try:
        events, scanned, skipped, broken = collect_events(
            root,
            commits,
            include_spread=args.spread,
            want_locks=args.locks,
            timeout=args.timeout,
            follow=args.follow,
        )
    except GitError as e:
        eprint(f"sear: {e}")
        return 2

    shown = events if (args.report or args.porcelain or args.json) else brands_only(events)
    if args.json and not args.report:
        shown = events

    if not args.quiet:
        extra = {
            "scanned": scanned,
            "skipped": skipped,
            "commits": len(commits),
            "broken": broken,
            "follow": args.follow,
        }
        if args.json:
            sys.stdout.write(render_json(events if args.report else brands_only(events), extra))
        elif args.porcelain:
            sys.stdout.write(render_porcelain(events if args.report else brands_only(events)))
        elif args.report:
            sys.stdout.write(render_report(events, scanned, skipped, len(commits)))
        else:
            sys.stdout.write(render_debt(events))

    if broken and any(e.tag == "BROKEN" for e in events):
        return 3
    if brands_only(events):
        return 1
    if args.due and any(e.tag == "SKIP" for e in events):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
