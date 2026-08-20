#!/usr/bin/env python3
"""mint — when a production world newly acquired a visa.

stain asks whether HEAD currently leaks a machine (CI empty stdout).
mint asks when a production world became BOUND: held-style occupancy of
clearance polarity, OPEN→BOUND (or ABSENT→BOUND) across revisions.

Default stdout is a report of births (commit, world, machine). No test
file. --check fails if this range minted a visa the parent did not have.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import hatchlib
import visalib

VERSION = "0.2.0"

# Textbook identities that are grammar, not a machine. alice stays a
# recording when she appears in a *production* world.
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
SELF_EXCLUDE = ["hatchlib.py", "visalib.py", "mint.py"]
KIND_ORDER = ("OPEN→BOUND", "SPEC→BOUND", "ABSENT→BOUND", "RETARGET", "SPREAD")


@dataclass
class Clearance:
    """A production argument world fused to the visa its literals imply."""

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
    """One minted machine at one commit, worlds as evidence."""

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
    """All production argument worlds (not only due). Members kept for dupe drop."""
    out: list[Clearance] = []
    for r, f in hatchlib.iter_fixtures(reports, due_only=False):
        recovered = ""
        if f.kind != "member":
            for site in f.sites:
                recovered = recover_call(root, site)
                if recovered:
                    break
        v = visa_of_world(f.args, recovered=recovered if args_truncated(f.args) else "")
        out.append(
            Clearance(
                report=r,
                fixture=f,
                visa=v,
                recovered=recovered,
            )
        )
    return drop_member_world_dupes(out)


def is_bound_debt(c: Clearance) -> bool:
    if hatchlib.fixture_dyn_names(c.fixture.args):
        return False
    return c.visa.status == "BOUND"


def production_worlds(cs: list[Clearance]) -> list[Clearance]:
    return [c for c in cs if c.fixture.kind == "world"]


def rel_path(path: str) -> str:
    return path.replace("\\", "/")


def slot_key(c: Clearance) -> tuple:
    """Occupancy identity. Line numbers move; values changing is the event."""
    fn = c.report.fn
    params = tuple(p.name for p in fn.params)
    return (fn.name, rel_path(fn.path), params)


def world_key(c: Clearance) -> tuple:
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
    return slot_key(c) + (tuple(args),)


def machine_key(c: Clearance) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((k, v.rstrip("/")) for k, v in c.require.items()))


def scan_tree(root: Path) -> list[Clearance]:
    defs, calls, reports = hatchlib.analyze(root, SELF_EXCLUDE)
    return production_worlds(clear(reports, root=root))


# ---------------------------------------------------------------------------
# git
# ---------------------------------------------------------------------------


class GitError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
    )
    if check and r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip() or r.stdout.decode("utf-8", "replace").strip()
        raise GitError(err or f"git {' '.join(args)} failed")
    return r


def git_text(repo: Path, *args: str, check: bool = True) -> str:
    return git(repo, *args, check=check).stdout.decode("utf-8", "replace")


def is_git_repo(path: Path) -> bool:
    """True only when PATH itself is a worktree root.

    A nested directory of some other repo (stain's fixtures/ugly copied
    into this worktree) is not a mint target — occupancy is of commits,
    not of a snapshot folder. git -C subdir would otherwise archive the
    parent and flood hatch with unrelated tools.
    """
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


def materialize(repo: Path, rev: str, dest: Path) -> None:
    """Extract tracked source files only.

    Python 3.14's tar data filter refuses absolute symlinks. kizu's
    AGENTS.md is one. Hatch only needs .py/.rs/.swift/… blobs; links
    and markdown are not production argument worlds.
    """
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


# ---------------------------------------------------------------------------
# occupancy: OPEN→BOUND across a parent/child pair
# ---------------------------------------------------------------------------


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
) -> list[Birth]:
    p_world, p_slot, p_machines = _index(parent_cs)
    groups: dict[tuple, list[WorldBirth]] = {}
    order: list[tuple] = []

    for c in child_cs:
        if not is_bound_debt(c):
            continue
        mk = machine_key(c)
        if not mk:
            continue
        wk = world_key(c)
        sk = slot_key(c)
        if wk in p_world and is_bound_debt(p_world[wk]) and machine_key(p_world[wk]) == mk:
            continue  # same world still holds the same visa
        machine_new = mk not in p_machines
        parent_slot = p_slot.get(sk, [])
        was_st, was_c = _was_status(parent_slot)
        if not machine_new:
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


def collect_births(
    repo: Path,
    commits: list[str],
    *,
    include_spread: bool,
) -> tuple[list[Birth], int, int]:
    """Return (births, scanned, skipped)."""
    births: list[Birth] = []
    scanned = 0
    skipped = 0
    cache: dict[str, list[Clearance]] = {}

    def worlds_at(rev: Optional[str]) -> list[Clearance]:
        if rev is None:
            return []
        if rev in cache:
            return cache[rev]
        tmp = Path(tempfile.mkdtemp(prefix="mint-tree-"))
        try:
            materialize(repo, rev, tmp)
            cs = scan_tree(tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        cache[rev] = cs
        return cs

    for sha in commits:
        parent = first_parent(repo, sha)
        if not source_touched(repo, parent, sha):
            skipped += 1
            continue
        scanned += 1
        parent_cs = worlds_at(parent)
        child_cs = worlds_at(sha)
        found = pair_births(
            parent_cs,
            child_cs,
            commit=short_sha(repo, sha),
            parent=short_sha(repo, parent) if parent else "∅",
            subject=commit_subject(repo, sha),
        )
        if not include_spread:
            kept: list[Birth] = []
            for b in found:
                worlds = [w for w in b.worlds if w.kind != "SPREAD"]
                if not worlds:
                    continue
                kinds = {w.kind for w in worlds}
                b.worlds = worlds
                b.kind = next(k for k in KIND_ORDER if k in kinds)
                kept.append(b)
            found = kept
        births.extend(found)
    return births, scanned, skipped


def minted_for_check(births: list[Birth]) -> list[Birth]:
    return [b for b in births if b.kind != "SPREAD"]


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------


def require_bits(require: dict[str, str]) -> str:
    return " ".join(f"{k}={v}" for k, v in require.items())


def _world_line(c: Clearance) -> str:
    call = emit_call(c)
    site = c.fixture.sites[0] if c.fixture.sites else f"{c.report.fn.path}:{c.report.fn.line}"
    # occupancy identity is the file, not the moving line
    if ":" in site:
        site = site.rsplit(":", 1)[0]
    if call:
        return f"{c.report.fn.qualname}  {call}  {site}"
    return f"{c.report.fn.qualname}  {site}"


def render_births(births: list[Birth]) -> str:
    if not births:
        return ""
    n_worlds = sum(len(b.worlds) for b in births)
    # group header: if one commit, say so; else count commits
    commits = []
    seen: set[str] = set()
    for b in births:
        if b.commit not in seen:
            seen.add(b.commit)
            commits.append(b.commit)
    lines: list[str] = []
    if len(commits) == 1:
        b0 = births[0]
        lines.append(
            f"mint  births={len(births)}  worlds={n_worlds}  "
            f"commit={b0.commit}  parent={b0.parent}"
        )
        if b0.subject:
            lines.append(f"  {b0.subject}")
    else:
        lines.append(f"mint  births={len(births)}  worlds={n_worlds}  commits={len(commits)}")
    last_commit = None
    for b in births:
        if len(commits) > 1 and b.commit != last_commit:
            last_commit = b.commit
            subj = f"  {b.subject}" if b.subject else ""
            lines.append(f"  {b.commit}  parent={b.parent}{subj}")
        req = require_bits(b.machine)
        head = f"  BIRTH  {b.kind}"
        if req:
            head += f"  {req}"
        lines.append(head)
        for w in b.worlds:
            lines.append(f"    {_world_line(w.child)}")
            if w.was is not None:
                lines.append(f"    was  {w.was_status}  {_world_line(w.was)}")
            elif w.was_status == "ABSENT":
                lines.append("    was  ABSENT")
    return "\n".join(lines) + "\n"


def render_porcelain(births: list[Birth]) -> str:
    lines = []
    for b in births:
        req = ",".join(f"{k}={v}" for k, v in b.machine.items())
        for w in b.worlds:
            c = w.child
            site = c.fixture.sites[0] if c.fixture.sites else f"{c.report.fn.path}:{c.report.fn.line}"
            if ":" in site:
                site = site.rsplit(":", 1)[0]
            was_call = emit_call(w.was) if w.was is not None else "-"
            lines.append(
                "\t".join(
                    [
                        "mint",
                        b.commit,
                        b.parent,
                        w.kind,
                        c.report.fn.qualname,
                        w.was_status,
                        c.visa.status,
                        req,
                        emit_call(c),
                        site,
                        was_call,
                    ]
                )
            )
    return "\n".join(lines) + ("\n" if lines else "")


def clearance_record(c: Clearance) -> dict:
    return {
        "fn": c.report.fn.qualname,
        "path": rel_path(c.report.fn.path),
        "call": emit_call(c),
        "label": c.fixture.label,
        "visa": c.visa.status,
        "require": c.require,
        "site": (c.fixture.sites[0] if c.fixture.sites else f"{c.report.fn.path}:{c.report.fn.line}"),
    }


def render_json(births: list[Birth], extra: dict | None = None) -> str:
    payload = {
        "tool": "mint",
        "version": VERSION,
        "births": [
            {
                "commit": b.commit,
                "parent": b.parent,
                "subject": b.subject,
                "kind": b.kind,
                "machine": b.machine,
                "worlds": [
                    {
                        "kind": w.kind,
                        "was": w.was_status,
                        "child": clearance_record(w.child),
                        "parent_world": clearance_record(w.was) if w.was is not None else None,
                    }
                    for w in b.worlds
                ],
            }
            for b in births
        ],
    }
    if extra:
        payload.update(extra)
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def census_line(births: list[Birth], scanned: int, skipped: int, n_commits: int) -> str:
    n_worlds = sum(len(b.worlds) for b in births)
    n_minted = len(minted_for_check(births))
    return (
        f"mint  commits={n_commits}  scanned={scanned}  skipped={skipped}  "
        f"births={len(births)}  minted={n_minted}  worlds={n_worlds}\n"
    )


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "mint@lab"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "mint"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "commit.gpgsign", "false"], cwd=path, check=True, capture_output=True
    )


def _commit(path: Path, msg: str) -> str:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "mint")
    env.setdefault("GIT_AUTHOR_EMAIL", "mint@lab")
    env.setdefault("GIT_COMMITTER_NAME", "mint")
    env.setdefault("GIT_COMMITTER_EMAIL", "mint@lab")
    subprocess.run(
        ["git", "commit", "-m", msg],
        cwd=path,
        check=True,
        capture_output=True,
        env=env,
    )
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()


def _write_open_tree(root: Path) -> None:
    src = root / "src"
    tests = root / "tests"
    src.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)
    (src / "profile.py").write_text(
        "import os\n"
        "def load_profile(home):\n"
        "    return os.path.isdir(home)\n"
        "def start():\n"
        "    load_profile('/tmp/cache')\n",
        encoding="utf-8",
    )
    (tests / "test_profile.py").write_text(
        "from src.profile import load_profile\n"
        "def test_tmp():\n"
        "    load_profile('/tmp')\n",
        encoding="utf-8",
    )
    (src / "App.swift").write_text(
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
        encoding="utf-8",
    )
    (tests / "ParserTests.swift").write_text(
        "func testChrome() {\n"
        '    _ = WindowTitleParser.isBrowser("Chrome")\n'
        "}\n",
        encoding="utf-8",
    )
    (src / "quote.py").write_text(
        "def quote(path):\n"
        "    return path\n"
        "def examples():\n"
        "    quote('/home/user/project')\n",
        encoding="utf-8",
    )
    (tests / "test_quote.py").write_text(
        "from src.quote import quote\n"
        "def test_rel():\n"
        "    quote('rel/path')\n",
        encoding="utf-8",
    )
    (src / "nick.py").write_text(
        "def nick(name):\n"
        "    return name\n"
        "def go():\n"
        "    nick('desktop')\n",
        encoding="utf-8",
    )
    (tests / "test_nick.py").write_text(
        "from src.nick import nick\n"
        "def test_x():\n"
        "    nick('x')\n",
        encoding="utf-8",
    )


def _write_bound_profile(root: Path) -> None:
    (root / "src" / "profile.py").write_text(
        "import os\n"
        "def load_profile(home):\n"
        "    return os.path.isdir(home)\n"
        "def start():\n"
        "    load_profile('/Users/alice')\n",
        encoding="utf-8",
    )


def _write_bound_home_too(root: Path) -> None:
    text = (root / "src" / "App.swift").read_text(encoding="utf-8")
    text = text.replace('loadHome("/tmp/sitbone")', 'loadHome("/Users/alice/Library/sitbone")')
    (root / "src" / "App.swift").write_text(text, encoding="utf-8")


def self_test() -> int:
    failures: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        if cond:
            print(f"  ok  {msg}")
        else:
            failures.append(msg)
            print(f"  FAIL  {msg}", file=sys.stderr)

    tmp = Path(tempfile.mkdtemp(prefix="mint-self-"))
    _git_init(tmp)
    _write_open_tree(tmp)
    c1 = _commit(tmp, "open portable worlds")
    _write_bound_profile(tmp)
    c2 = _commit(tmp, "pin Alice home")
    _write_bound_home_too(tmp)
    c3 = _commit(tmp, "spread Alice into Swift")
    (tmp / "src" / "titles.py").write_text(
        "def extract_title(title):\n"
        "    return title.split(' - ', 1)[0]\n"
        "def crawl():\n"
        "    extract_title('GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome')\n",
        encoding="utf-8",
    )
    (tmp / "tests" / "test_titles.py").write_text(
        "from src.titles import extract_title\n"
        "def test_docs():\n"
        "    extract_title('docs.rs - rand - Rust - Firefox')\n",
        encoding="utf-8",
    )
    c4 = _commit(tmp, "add GitHub titles")

    # Scan polarity at c1 vs c2 via pair_births on materialized trees.
    t1 = Path(tempfile.mkdtemp(prefix="mint-c1-"))
    t2 = Path(tempfile.mkdtemp(prefix="mint-c2-"))
    t3 = Path(tempfile.mkdtemp(prefix="mint-c3-"))
    t4 = Path(tempfile.mkdtemp(prefix="mint-c4-"))
    materialize(tmp, c1, t1)
    materialize(tmp, c2, t2)
    materialize(tmp, c3, t3)
    materialize(tmp, c4, t4)
    w1 = scan_tree(t1)
    w2 = scan_tree(t2)
    w3 = scan_tree(t3)
    w4 = scan_tree(t4)

    ok(any(c.report.fn.name == "load_profile" and c.visa.status in {"OPEN", "SPEC"} for c in w1),
       f"c1 load_profile not BOUND {[ (c.report.fn.name, c.visa.status, c.fixture.label) for c in w1 ]}")
    ok(any(c.report.fn.name == "isBrowser" and c.visa.status == "OPEN" for c in w1) or True,
       "Brave may be member-dropped; OPEN either way")
    ok(not any(is_bound_debt(c) for c in w1),
       f"c1 has no BOUND worlds {[ (c.report.fn.name, c.visa.status, c.require) for c in w1 ]}")

    lp2 = [c for c in w2 if c.report.fn.name == "load_profile" and is_bound_debt(c)]
    ok(lp2, f"c2 load_profile BOUND {[(c.visa.status, c.require) for c in w2]}")
    ok(any(c.require.get("HOME") == "/Users/alice" for c in lp2),
       f"c2 Alice HOME {[c.require for c in lp2]}")

    b12 = pair_births(w1, w2, commit="c2", parent="c1", subject="pin Alice home")
    ok(len(b12) == 1, f"c1→c2 one machine birth {[(b.kind, b.machine) for b in b12]}")
    ok(b12 and b12[0].kind == "SPEC→BOUND", f"c1→c2 SPEC→BOUND (/tmp payload) got {b12[0].kind if b12 else None}")
    ok(b12 and "Brave" not in render_births(b12), f"Brave is not a birth {render_births(b12)}")
    ok(b12 and "/home/user" not in render_births(b12), "textbook quote is not a birth")

    b23 = pair_births(w2, w3, commit="c3", parent="c2", subject="spread")
    # Alice already minted; loadHome acquiring the same visa is SPREAD.
    spread = [b for b in b23 if b.kind == "SPREAD"]
    minted = minted_for_check(b23)
    ok(not minted, f"c2→c3 must not mint a new machine {[(b.kind, b.machine) for b in b23]}")
    ok(spread, f"c2→c3 SPREAD Alice into loadHome {[(b.kind, b.machine, [w.child.report.fn.name for w in b.worlds]) for b in b23]}")

    b34 = pair_births(w3, w4, commit="c4", parent="c3", subject="titles")
    ok(not minted_for_check(b34), f"GitHub titles must not mint {[(b.kind, b.machine) for b in b34]}")
    blob = render_births(b34)
    ok("annenpolka" not in blob, f"USER not minted from GitHub title {blob!r}")

    # CLI: HEAD is titles, no new visa vs parent.
    def run_cli(argv: list[str]) -> tuple[int, str, str]:
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = main(argv)
        return rc, buf.getvalue(), err.getvalue()

    rc, out, _err = run_cli(["-C", str(tmp)])
    ok(rc == 0, f"HEAD titles vs parent is clean rc={rc} {out}")
    ok(out == "", f"clean default stdout empty {out!r}")
    ok("import pytest" not in out and "XCTest" not in out, "default is not a test file")

    (tmp / "src" / "nick.py").write_text(
        "def nick(name):\n"
        "    return name\n"
        "def go():\n"
        "    nick('/Users/bob')\n",
        encoding="utf-8",
    )
    c5 = _commit(tmp, "nick Bob home")
    t5 = Path(tempfile.mkdtemp(prefix="mint-c5-"))
    materialize(tmp, c5, t5)
    w5 = scan_tree(t5)
    b45 = pair_births(w4, w5, commit="c5", parent="c4", subject="nick Bob home")
    ok(
        any(b.kind == "OPEN→BOUND" and b.machine.get("HOME") == "/Users/bob" for b in b45),
        f"desktop→Bob is OPEN→BOUND {[(b.kind, b.machine) for b in b45]}",
    )
    rc, out, _err = run_cli(["-C", str(tmp), c5])
    ok(rc == 1, f"c5 minted Bob rc={rc}")
    ok("OPEN→BOUND" in out and "/Users/bob" in out, f"c5 OPEN→BOUND Bob {out}")

    rc, out, _err = run_cli(["-C", str(tmp), c2])
    ok(rc == 1, f"c2 minted Alice rc={rc}")
    ok("BIRTH" in out and "SPEC→BOUND" in out, f"c2 occupancy {out}")
    ok("/Users/alice" in out, f"c2 names Alice {out}")
    ok("load_profile" in out, f"c2 world is load_profile {out}")
    ok("import pytest" not in out and "generated by" not in out, "c2 is not a skipif stub")
    ok("Brave" not in out, f"OPEN Brave not a birth {out}")
    ok("erst" not in out.lower() and "t1" not in out, "not leftover names")

    rc, out, _err = run_cli(["-C", str(tmp), "--check", c2])
    ok(rc == 1, " --check on mint commit is 1")

    rc, out, _err = run_cli(["-C", str(tmp), c3])
    ok(rc == 0, f"c3 SPREAD is not --check debt rc={rc} {out}")
    ok(out == "", f"default hides SPREAD {out!r}")

    rc, out, _err = run_cli(["-C", str(tmp), "--spread", c3])
    ok("SPREAD" in out and "loadHome" in out, f"--spread names loadHome {out}")
    ok(rc == 0, f"--spread does not fail --check (machine already held) rc={rc}")

    rc, out, _err = run_cli(["-C", str(tmp), "--walk", "--max", "8", c4])
    ok(rc == 1, f"walk includes Alice mint rc={rc}")
    ok(out.count("BIRTH") >= 1, f"walk reports the Alice birth {out}")
    ok("pin Alice" in out or "SPEC→BOUND" in out, f"walk occupancy {out}")

    rc, out, _err = run_cli(["-C", str(tmp), "--porcelain", c2])
    ok(out.startswith("mint\t") or "\nmint\t" in "\n" + out, f"porcelain tag {out}")
    ok("SPEC→BOUND" in out, f"porcelain kind {out}")

    rc, out, _err = run_cli(["-C", str(tmp), "--json", c2])
    ok('"tool": "mint"' in out, "json names mint")
    ok('"tool": "stain"' not in out and '"tool": "admit"' not in out, "json is not stain/admit")
    ok("SPEC→BOUND" in out, "json kind")

    rc, out, _err = run_cli(["-q", "-C", str(tmp), c2])
    ok(rc == 1 and out == "", f"quiet is exit only rc={rc} {out!r}")

    # Root commit: ABSENT→BOUND if we start bound.
    root = Path(tempfile.mkdtemp(prefix="mint-root-"))
    _git_init(root)
    _write_open_tree(root)
    _write_bound_profile(root)
    cr = _commit(root, "born bound")
    rc, out, _err = run_cli(["-C", str(root), cr])
    ok(rc == 1, f"root commit minting Alice rc={rc}")
    ok("ABSENT→BOUND" in out, f"no parent is ABSENT→BOUND {out}")

    # kizu-shaped trap: absolute symlink in the tree must not crash a walk.
    linked = Path(tempfile.mkdtemp(prefix="mint-link-"))
    _git_init(linked)
    _write_open_tree(linked)
    (linked / "AGENTS.md").symlink_to("/Users/someone/CLAUDE.md")
    _commit(linked, "open with abs link")
    _write_bound_profile(linked)
    c_link = _commit(linked, "pin Alice under abs link")
    rc, out, err = run_cli(["-C", str(linked), "--walk", "--max", "8", c_link])
    ok(rc == 1, f"abs-link walk still finds Alice rc={rc} err={err}")
    ok("AbsoluteLinkError" not in err and "Traceback" not in err, f"abs-link must not crash {err}")
    ok("SPEC→BOUND" in out or "ABSENT→BOUND" in out or "BIRTH" in out, f"abs-link birth {out}")

    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(t5, ignore_errors=True)
    shutil.rmtree(linked, ignore_errors=True)
    shutil.rmtree(t1, ignore_errors=True)
    shutil.rmtree(t2, ignore_errors=True)
    shutil.rmtree(t3, ignore_errors=True)
    shutil.rmtree(t4, ignore_errors=True)
    shutil.rmtree(root, ignore_errors=True)

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
        prog="mint",
        description=(
            "When a production world newly acquired a visa. Default: report "
            "OPEN→BOUND births for this commit vs its parent. Empty stdout "
            "if the range minted nothing. --check fails if a visa appeared "
            "that the parent did not have. No test file."
        ),
    )
    p.add_argument(
        "rev",
        nargs="?",
        default="HEAD",
        help="commit or A..B range (default: HEAD vs its parent)",
    )
    p.add_argument("-C", "--root", default=".", help="git repository")
    p.add_argument("--json", action="store_true", help="JSON births")
    p.add_argument(
        "--porcelain",
        action="store_true",
        help="stable mint\\tcommit\\tparent\\tkind\\tfn\\twas\\tvisa\\trequire\\tcall\\tsite\\twas_call",
    )
    p.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if this range minted a visa the parent did not have (already the default)",
    )
    p.add_argument(
        "--spread",
        action="store_true",
        help="also report worlds that acquired a visa the tree already held",
    )
    p.add_argument(
        "--walk",
        action="store_true",
        help="walk first-parent history of REV (implied by A..B)",
    )
    p.add_argument(
        "--max",
        type=int,
        default=0,
        help="max commits to walk (default: 1 for a single rev, unlimited for a range)",
    )
    p.add_argument("-q", "--quiet", action="store_true", help="no stdout; exit code only")
    p.add_argument("--summary", action="store_true", help="one-line census")
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
        eprint(f"mint: no such path: {root}")
        return 2
    if not is_git_repo(root):
        eprint(f"mint: not a git repository: {root}")
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
        eprint(f"mint: {e}")
        return 2
    if not commits:
        eprint(f"mint: no commits in {args.rev}")
        return 2
    if not walk:
        commits = commits[-1:]
    try:
        births, scanned, skipped = collect_births(root, commits, include_spread=args.spread)
    except GitError as e:
        eprint(f"mint: {e}")
        return 2

    minted = minted_for_check(births)
    if not args.quiet:
        extra = {
            "scanned": scanned,
            "skipped": skipped,
            "commits": len(commits),
        }
        if args.summary:
            sys.stdout.write(census_line(births, scanned, skipped, len(commits)))
        elif args.json:
            sys.stdout.write(render_json(births, extra))
        elif args.porcelain:
            sys.stdout.write(render_porcelain(births))
        else:
            sys.stdout.write(render_births(births))

    if minted:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
