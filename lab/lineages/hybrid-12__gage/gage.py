#!/usr/bin/env python3
"""gage — clearance of the lockset.

A test that vetoes old production is not one verdict. The world that
test assumes is OPEN (no machine) or BOUND (HOME/USER/platform/CI).
LOCKED-and-OPEN is a clearance. LOCKED-and-BOUND is a stained alibi.

This is not stain (production leaked a machine, tests never run) and
not alibi (suite fail vs pass; a pytest.skip is a pass). It is not
cinch: production is spliced whole, never 1-minimal hunks. The object
is the visa of a lock.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.2.0"

SKIP_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".gage-tmp",
    ".alibi-tmp",
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

SOURCE_EXTENSIONS = {
    ".py",
    ".pyi",
    ".rs",
    ".go",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".swift",
    ".rb",
    ".java",
    ".kt",
    ".cs",
    ".php",
    ".m",
    ".mm",
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

LANG_OF = {
    ".py": "py",
    ".swift": "swift",
    ".js": "js",
    ".jsx": "js",
    ".ts": "js",
    ".tsx": "js",
    ".mjs": "js",
    ".rs": "rs",
}

# Builtins / loggers / string methods whose args are not production worlds.
# ugly v0.1 harvested title.split(" - ", 1) and BROKEN the lockset.
SKIP_FUNCS = {
    "print",
    "printf",
    "println",
    "echo",
    "len",
    "range",
    "str",
    "int",
    "float",
    "bool",
    "list",
    "dict",
    "set",
    "tuple",
    "type",
    "isinstance",
    "repr",
    "format",
    "open",
    "sorted",
    "enumerate",
    "zip",
    "map",
    "filter",
    "log",
    "debug",
    "info",
    "warning",
    "error",
    "warn",
    "write",
    "writeln",
    "super",
    "getattr",
    "setattr",
    "hasattr",
    "split",
    "rsplit",
    "splitlines",
    "join",
    "replace",
    "strip",
    "lstrip",
    "rstrip",
    "startswith",
    "endswith",
    "encode",
    "decode",
    "find",
    "rfind",
    "index",
    "rindex",
    "lower",
    "upper",
    "title",
    "capitalize",
    "append",
    "extend",
    "insert",
    "pop",
    "remove",
    "get",
    "items",
    "keys",
    "values",
    "update",
    "copy",
    "read",
    "readline",
    "readlines",
    "close",
}

# Textbook identities are grammar, not a machine. alice in a *production*
# world stays a recording (stain's snapshot treatment).
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

PATH_RE = re.compile(
    r"(?:"
    r"/Users/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|/home/[^/\s'\"\\`]+(?: [^/\s'\"\\`]+)*(?:/[^/\s'\"\\`]+)*"
    r"|[A-Za-z]:\\(?:[^\\\s'\"`]+\\)+[^\\\s'\"`]+"
    r")"
)

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
CALL_RE = re.compile(
    r"(?:(?P<recv>[A-Za-z_][A-Za-z0-9_]*)\.)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\("
)

GITHUB_TITLE_RE = re.compile(r"GitHub\s*-|github\.com/|\b[\w.-]+/[\w.-]+\b", re.I)

FAIL_LINE_RE = re.compile(r"^(FAIL|ERROR|FAILED):\s+(\S+)", re.MULTILINE)
PYTEST_FAILED_RE = re.compile(r"^FAILED\s+(\S+::\S+|\S+\.py\S*)", re.MULTILINE)


# ---------------------------------------------------------------------------
# Visa (thin: argument-literal worlds, not file-as-golden)
# ---------------------------------------------------------------------------


def _tail(value: str) -> str:
    return value.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def derive_from_path(raw: str) -> dict[str, str]:
    n = raw.strip().replace("\\", "/")
    out: dict[str, str] = {}
    m = re.match(r"^/Users/([^/]+)", n)
    if m:
        user = m.group(1)
        out["platform"] = "Darwin"
        out["HOME"] = f"/Users/{user}"
        if user.lower() not in {"user", "shared"}:
            out["USER"] = user
        return out
    m = re.match(r"^/home/([^/]+)", n)
    if m:
        user = m.group(1)
        out["platform"] = "Linux"
        out["HOME"] = f"/home/{user}"
        if user.lower() not in {"user"}:
            out["USER"] = user
        if user == "runner":
            out["CI"] = "github-actions"
        return out
    m = re.match(r"^([A-Za-z]:)/Users/([^/]+)", n)
    if m:
        user = m.group(2)
        drive = m.group(1)
        out["platform"] = "Windows"
        out["HOME"] = f"{drive}/Users/{user}".replace("/", "\\")
        out["USER"] = user
        return out
    return out


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
        if t.lower() not in TEXTBOOK_TAILS:
            return False
    return True


def looks_like_github(text: str) -> bool:
    return bool(re.search(r"GitHub\s*-|github\.com/", text))


def live_axes() -> dict[str, str]:
    home = str(Path.home()).rstrip("/\\")
    user = getpass.getuser()
    plat = platform.system()
    axes = {"HOME": home, "USER": user, "platform": plat}
    if os.environ.get("GITHUB_ACTIONS"):
        axes["CI"] = "github-actions"
    elif os.environ.get("CI"):
        axes["CI"] = "ci"
    return axes


def infer_world_text(text: str) -> tuple[str, dict[str, str]]:
    """Visa of argument literals only. File-level Darwin comments are not this world."""
    if looks_like_github(text):
        return "OPEN", {}
    require: dict[str, str] = {}
    for m in PATH_RE.finditer(text):
        derived = derive_from_path(m.group(0))
        for axis in HARD_SKIP_AXES:
            if axis in derived and axis not in require:
                require[axis] = derived[axis]
    if require and require_is_textbook(require):
        return "SPEC", {}
    if require:
        return "BOUND", {k: v for k, v in require.items() if k in HARD_SKIP_AXES}
    return "OPEN", {}


def match_require(require: dict[str, str]) -> list[dict[str, str]]:
    live = live_axes()
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


# ---------------------------------------------------------------------------
# Git / roles
# ---------------------------------------------------------------------------


def git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def git_bytes(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=False, capture_output=True)


def repo_root(start: Path) -> Path:
    proc = git(["rev-parse", "--show-toplevel"], cwd=start, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"gage: not a git repository: {start}")
    return Path(proc.stdout.strip()).resolve()


def rev_parse(repo: Path, ref: str) -> str:
    proc = git(["rev-parse", "--verify", ref], cwd=repo, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"gage: unknown revision {ref!r}")
    return proc.stdout.strip()


def list_tree_files(repo: Path, ref: str) -> list[str]:
    proc = git(["ls-tree", "-r", "--name-only", ref], cwd=repo)
    return [ln for ln in proc.stdout.splitlines() if ln]


def list_worktree_files(repo: Path) -> list[str]:
    proc = git(["ls-files", "-co", "--exclude-standard"], cwd=repo)
    return [ln for ln in proc.stdout.splitlines() if ln]


def git_show(repo: Path, ref: str, path: str) -> bytes | None:
    proc = git_bytes(["show", f"{ref}:{path}"], cwd=repo)
    if proc.returncode != 0:
        return None
    return proc.stdout


def worktree_bytes(repo: Path, path: str) -> bytes | None:
    p = repo / path
    if not p.is_file():
        return None
    return p.read_bytes()


def should_skip_path(path: str) -> bool:
    parts = Path(path.replace("\\", "/")).parts
    return any(p in SKIP_DIR_NAMES for p in parts)


def is_test_path(path: str) -> bool:
    posix = path.replace("\\", "/")
    parts = [p.lower() for p in Path(posix).parts]
    if any(p in TEST_DIR_NAMES or p in FIXTURE_DIR_NAMES for p in parts):
        return True
    return bool(TEST_FILE_RE.match(Path(posix).name))


def is_source_path(path: str) -> bool:
    return Path(path.replace("\\", "/")).suffix.lower() in SOURCE_EXTENSIONS


def path_role(path: str) -> str:
    if is_test_path(path):
        return "test"
    if is_source_path(path):
        return "production"
    return "other"


def new_bytes(repo: Path, path: str) -> bytes | None:
    return worktree_bytes(repo, path)


# ---------------------------------------------------------------------------
# Harvest production worlds (call + string args)
# ---------------------------------------------------------------------------


def lang_of(path: str) -> str:
    return LANG_OF.get(Path(path).suffix.lower(), "")


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def line_is_comment(text: str, pos: int, lang: str) -> bool:
    start = text.rfind("\n", 0, pos) + 1
    raw = text[start:pos]
    stripped = raw.lstrip()
    if lang == "py":
        return stripped.startswith("#")
    return stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("/*")


def parse_string_args(src: str, open_paren: int) -> tuple[list[str], int] | None:
    """Return string literals at depth 1 and index after the matching close paren."""
    n = len(src)
    i = open_paren
    if i >= n or src[i] != "(":
        return None
    depth = 0
    in_str: str | None = None
    triple = False
    escape = False
    strings: list[str] = []
    buf: list[str] = []
    while i < n:
        c = src[i]
        if in_str:
            if escape:
                buf.append(c)
                escape = False
                i += 1
                continue
            if c == "\\" and not triple:
                escape = True
                i += 1
                continue
            if triple and src.startswith(in_str * 3, i):
                if depth == 1:
                    strings.append("".join(buf))
                buf = []
                i += 3
                in_str = None
                triple = False
                continue
            if not triple and c == in_str:
                if depth == 1:
                    strings.append("".join(buf))
                buf = []
                in_str = None
                i += 1
                continue
            buf.append(c)
            i += 1
            continue
        if c in "\"'":
            if src.startswith(c * 3, i):
                in_str = c
                triple = True
                i += 3
                continue
            in_str = c
            triple = False
            i += 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            i += 1
            if depth == 0:
                return strings, i
            continue
        elif lang_of_comment_at(src, i):
            break
        i += 1
    return None


def lang_of_comment_at(src: str, i: int) -> bool:
    return False


def extract_calls(text: str, path: str) -> list[dict]:
    lang = lang_of(path)
    out: list[dict] = []
    for m in CALL_RE.finditer(text):
        name = m.group("name")
        recv = m.group("recv") or ""
        if name in SKIP_FUNCS:
            continue
        if name[0].isupper() and lang == "py" and not recv:
            # Class construction is not a production world.
            continue
        if line_is_comment(text, m.start(), lang):
            continue
        parsed = parse_string_args(text, m.end() - 1)
        if not parsed:
            continue
        strings, end = parsed
        if not strings:
            continue
        # Drop empty / tiny punctuation strings.
        strings = [s for s in strings if len(s) >= 2]
        if not strings:
            continue
        raw = text[m.start() : end].strip()
        if len(raw) > 240:
            raw = raw[:237] + "..."
        out.append(
            {
                "path": path,
                "line": line_of(text, m.start()),
                "func": name,
                "recv": recv,
                "args": strings,
                "raw": raw,
                "lang": lang or "other",
            }
        )
    return out


def decode_text(data: bytes) -> str | None:
    if b"\0" in data[:800]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


@dataclass
class World:
    path: str
    line: int
    func: str
    recv: str
    args: list[str]
    raw: str
    lang: str
    visa: str
    require: dict[str, str]
    match: str
    origin: str = "production"  # production | suite

    @property
    def qualname(self) -> str:
        return f"{self.recv}.{self.func}" if self.recv else self.func

    @property
    def call(self) -> str:
        return self.raw

    @property
    def site(self) -> str:
        return f"{self.path}:{self.line}"

    @property
    def machine_key(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted((k, v) for k, v in self.require.items() if k in HARD_SKIP_AXES))

    @property
    def generable(self) -> bool:
        if self.lang != "py":
            return False
        posix = self.path.replace("\\", "/")
        if any(ch in posix for ch in (":", " ", "\t")):
            return False
        if not self.func.isidentifier():
            return False
        # Local receivers (title.split) are not module-level oracles.
        # Class/enum receivers (Parser.is_browser) stay generable.
        if self.recv and not self.recv[0].isupper():
            return False
        return True


def worlds_from_text(path: str, text: str, origin: str = "production") -> list[World]:
    found: list[World] = []
    for c in extract_calls(text, path):
        blob = "\n".join(c["args"])
        visa, require = infer_world_text(blob)
        found.append(
            World(
                path=c["path"],
                line=c["line"],
                func=c["func"],
                recv=c["recv"],
                args=c["args"],
                raw=c["raw"],
                lang=c["lang"],
                visa=visa,
                require=require,
                match=match_label(require),
                origin=origin,
            )
        )
    return found


def harvest_tree(files: dict[str, bytes], roles: dict[str, str] | None = None) -> list[World]:
    out: list[World] = []
    for path, data in files.items():
        if should_skip_path(path):
            continue
        role = (roles or {}).get(path) or path_role(path)
        if role != "production":
            continue
        if not is_source_path(path):
            continue
        text = decode_text(data)
        if text is None:
            continue
        out.extend(worlds_from_text(path, text, origin="production"))
    return drop_dupes(out)


def harvest_suite(files: dict[str, bytes]) -> list[World]:
    out: list[World] = []
    for path, data in files.items():
        if should_skip_path(path):
            continue
        if path_role(path) != "test":
            continue
        text = decode_text(data)
        if text is None:
            continue
        worlds = worlds_from_text(path, text, origin="suite")
        if worlds:
            out.extend(worlds)
            continue
        # A test file with no string-arg calls (assert add(2, 3) == 5) is OPEN.
        visa, require = infer_world_text(text)
        out.append(
            World(
                path=path,
                line=1,
                func=Path(path).stem,
                recv="",
                args=[],
                raw=path,
                lang=lang_of(path) or "py",
                visa=visa,
                require=require,
                match=match_label(require),
                origin="suite",
            )
        )
    return drop_dupes(out)


def drop_dupes(worlds: list[World]) -> list[World]:
    seen: set[tuple] = set()
    out: list[World] = []
    for w in worlds:
        key = (w.path, w.func, tuple(w.args), w.origin)
        if key in seen:
            continue
        seen.add(key)
        out.append(w)
    return out


# ---------------------------------------------------------------------------
# Occupancy: run a world against a tree
# ---------------------------------------------------------------------------


@dataclass
class Occupancy:
    status: str  # pass fail skip error unrun
    detail: str = ""


def py_load_and_call(tree: Path, world: World) -> Occupancy:
    if world.visa == "BOUND":
        misses = match_require(world.require)
        if misses:
            msg = "; ".join(f"{m['axis']} want={m['want']} have={m['have']}" for m in misses)
            return Occupancy("skip", "visa MISS " + msg)
    script = textwrap.dedent(
        f"""\
        import importlib.util
        import sys
        from pathlib import Path
        root = Path({str(tree.resolve())!r})
        sys.path.insert(0, str(root))
        path = root / {world.path!r}
        if not path.is_file():
            raise SystemExit("gage: missing " + str(path))
        spec = importlib.util.spec_from_file_location("gage_mod", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        recv = {world.recv!r}
        name = {world.func!r}
        obj = mod
        if recv:
            obj = getattr(obj, recv)
        fn = getattr(obj, name)
        args = {world.args!r}
        result = fn(*args)
        if not result:
            raise SystemExit(1)
        """
    )
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, "-c", script],
            cwd=tree,
            capture_output=True,
            text=True,
            timeout=20,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(tree)},
        )
    except subprocess.TimeoutExpired:
        return Occupancy("error", "timeout")
    _ = time.monotonic() - t0
    if proc.returncode == 0:
        return Occupancy("pass")
    err = ((proc.stderr or "") + (proc.stdout or "")).strip().splitlines()
    tail = err[-1] if err else f"exit {proc.returncode}"
    joined = (proc.stderr or "") + (proc.stdout or "")
    # Not a module-level function: occupancy, not a red suite.
    if any(
        k in joined
        for k in ("AttributeError", "ModuleNotFoundError", "ImportError")
    ):
        return Occupancy("unrun", tail)
    if proc.returncode == 1 and "Error" not in tail and "error" not in tail:
        return Occupancy("fail", tail)
    if "AssertionError" in joined or "SystemExit: 1" in joined:
        return Occupancy("fail", tail)
    if proc.returncode == 1:
        if "Traceback" in joined and "SystemExit" not in joined:
            return Occupancy("error", tail)
        return Occupancy("fail", tail)
    return Occupancy("error", tail)


def run_world(tree: Path, world: World) -> Occupancy:
    if not world.generable:
        return Occupancy("unrun", f"lang={world.lang}")
    return py_load_and_call(tree, world)


# ---------------------------------------------------------------------------
# Splice trees
# ---------------------------------------------------------------------------


def union_paths(repo: Path, base: str) -> list[str]:
    s = set(list_tree_files(repo, base)) | set(list_worktree_files(repo))
    return sorted(p for p in s if not should_skip_path(p))


def production_changed(repo: Path, base: str) -> list[str]:
    changed: list[str] = []
    for path in union_paths(repo, base):
        if path_role(path) != "production":
            continue
        a = git_show(repo, base, path)
        b = new_bytes(repo, path)
        if a != b:
            changed.append(path)
    return changed


def write_bytes(dest: Path, path: str, data: bytes) -> None:
    p = dest / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def materialize(repo: Path, dest: Path, base: str, overlay: str) -> None:
    """overlay='none' → NEW worktree; overlay='all' → tests@NEW, production@base."""
    for path in union_paths(repo, base):
        role = path_role(path)
        if overlay == "none":
            data = new_bytes(repo, path)
            if data is None:
                continue
            write_bytes(dest, path, data)
            continue
        if role != "production":
            data = new_bytes(repo, path)
            if data is None:
                continue
            write_bytes(dest, path, data)
        else:
            data = git_show(repo, base, path)
            if data is None:
                continue
            write_bytes(dest, path, data)


def collect_files(root: Path) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for name in filenames:
            p = Path(dirpath) / name
            rel = p.relative_to(root).as_posix()
            if should_skip_path(rel):
                continue
            try:
                out[rel] = p.read_bytes()
            except OSError:
                continue
    return out


# ---------------------------------------------------------------------------
# Suite fallback (existing tests, alibi-shaped splice, visa of the tests)
# ---------------------------------------------------------------------------


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
        return RunResult(124, out + f"\n[gage: timed out after {timeout}s]", time.monotonic() - t0, True)


def detect_cmd(root: Path) -> list[str]:
    if (root / "test.py").is_file():
        return [sys.executable, "test.py"]
    for name in ("tests", "test", "Tests"):
        if (root / name).is_dir():
            return [sys.executable, "-m", "unittest", "discover", "-s", name, "-q"]
    return [sys.executable, "-m", "unittest", "discover", "-q"]


def parse_witnesses(output: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()

    def add(name: str) -> None:
        name = name.strip().rstrip(":")
        if name and name not in seen:
            seen.add(name)
            found.append(name)

    for rx in (FAIL_LINE_RE, PYTEST_FAILED_RE):
        for m in rx.finditer(output):
            add(m.group(m.lastindex or 1))
    return found


def count_skips(output: str) -> int:
    m = re.search(r"skipped[= ](\d+)", output, re.I)
    if m:
        return int(m.group(1))
    return len(re.findall(r"\bSKIP(?:PED)?\b", output))


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


@dataclass
class Lock:
    world: World
    lock: str  # LOCKED LOOSE SKIP BROKEN UNRUN CLEAN
    new_occ: str
    splice_occ: str
    parent: str  # LEAKED CLEAN -

    @property
    def visa(self) -> str:
        return self.world.visa

    @property
    def verdict(self) -> str:
        if self.lock in {"LOCKED", "LOOSE", "SKIP"}:
            return f"{self.lock}-and-{self.visa}"
        return self.lock

    @property
    def is_bound_lock(self) -> bool:
        return self.lock == "LOCKED" and self.visa == "BOUND"


def classify_pair(new_occ: Occupancy, sp_occ: Occupancy) -> str:
    if new_occ.status == "skip":
        return "SKIP"
    if new_occ.status in {"fail", "error"}:
        return "BROKEN"
    if new_occ.status == "unrun":
        return "UNRUN"
    # new passed
    if sp_occ.status in {"fail", "error"}:
        return "LOCKED"
    if sp_occ.status == "skip":
        return "SKIP"
    if sp_occ.status == "unrun":
        return "UNRUN"
    return "LOOSE"


def parent_of(world: World, old_machines: set[tuple[tuple[str, str], ...]]) -> str:
    if world.visa != "BOUND":
        return "-"
    return "LEAKED" if world.machine_key in old_machines else "CLEAN"


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


@dataclass
class Report:
    status: str
    base: str
    new: str
    mode: str
    production_changed: list[str]
    locks: list[Lock] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    suite_new: RunResult | None = None
    suite_splice: RunResult | None = None

    @property
    def bound_locks(self) -> list[Lock]:
        return [lk for lk in self.locks if lk.is_bound_lock]

    @property
    def machines(self) -> list[tuple[tuple[tuple[str, str], ...], list[Lock]]]:
        order: list[tuple[tuple[str, str], ...]] = []
        buckets: dict[tuple[tuple[str, str], ...], list[Lock]] = {}
        for lk in self.bound_locks:
            k = lk.world.machine_key
            if k not in buckets:
                buckets[k] = []
                order.append(k)
            buckets[k].append(lk)
        return [(k, buckets[k]) for k in order]


def overall_status(report: Report) -> str:
    # A getattr miss is UNRUN. BROKEN is an oracle that already fails on NEW.
    if any(lk.lock == "BROKEN" and lk.new_occ == "fail" for lk in report.locks):
        return "BROKEN"
    if not report.production_changed:
        return "CLEAN"
    if report.bound_locks:
        return "BOUND-LOCK"
    return "CLEAR"


def render_debt(report: Report) -> str:
    """Default CI stdout: LOCKED-and-BOUND only. Empty when the lockset is cleared."""
    stains = report.machines
    if not stains:
        return ""
    n_miss = sum(1 for lk in report.bound_locks if lk.world.match == "MISS")
    n_worlds = sum(len(ws) for _, ws in stains)
    lines = [
        f"gage  machines={len(stains)}  bound-locks={n_worlds}  miss={n_miss}",
    ]
    for key, group in stains:
        w0 = group[0].world
        req = " ".join(f"{k}={v}" for k, v in w0.require.items())
        parent = group[0].parent
        head = f"  LOCKED  BOUND  {w0.match}"
        if req:
            head += f"  {req}"
        head += f"  parent={parent}"
        lines.append(head)
        for lk in group:
            lines.append(f"    {lk.world.qualname}  {lk.world.call}  {lk.world.site}")
    return "\n".join(lines) + "\n"


def render_report(report: Report) -> str:
    n_locked = sum(1 for lk in report.locks if lk.lock == "LOCKED")
    n_bound = sum(1 for lk in report.locks if lk.visa == "BOUND")
    n_open = sum(1 for lk in report.locks if lk.visa == "OPEN")
    n_skip = sum(1 for lk in report.locks if lk.lock == "SKIP")
    n_loose = sum(1 for lk in report.locks if lk.lock == "LOOSE")
    lines = [
        f"gage  base={report.base}  new={report.new}  status={report.status}  mode={report.mode}",
        f"prod   {len(report.production_changed)} path(s) differ",
    ]
    for p in report.production_changed[:12]:
        lines.append(f"         {p}")
    if len(report.production_changed) > 12:
        lines.append(f"         … {len(report.production_changed) - 12} more")
    lines.append(
        f"locks  {len(report.locks)}  locked={n_locked}  bound={n_bound}  "
        f"open={n_open}  skip={n_skip}  loose={n_loose}  bound-locks={len(report.bound_locks)}"
    )
    meaning = {
        "CLEAR": "lockset cleared — no LOCKED-and-BOUND (OPEN locks are a clearance)",
        "BOUND-LOCK": "a lock assumes a machine — stained alibi",
        "CLEAN": "no production files differ from base",
        "BROKEN": "a world-test already fails on the new tree",
    }.get(report.status, "")
    if meaning:
        lines.append(meaning)
    for lk in report.locks:
        req = " ".join(f"{k}={v}" for k, v in lk.world.require.items())
        extra = f"  {req}" if req else ""
        parent = f"  parent={lk.parent}" if lk.parent != "-" else ""
        lines.append(
            f"  {lk.lock:6s}  {lk.visa:5s}  {lk.world.match:5s}  "
            f"new={lk.new_occ:5s} splice={lk.splice_occ:5s}{parent}{extra}"
        )
        lines.append(f"         {lk.world.qualname}  {lk.world.call}  {lk.world.site}")
        lines.append(f"         verdict {lk.verdict}")
    for note in report.notes:
        lines.append(f"note: {note}")
    return "\n".join(lines) + "\n"


def render_porcelain(report: Report) -> str:
    lines = []
    for lk in report.locks:
        req = ",".join(f"{k}={v}" for k, v in lk.world.require.items())
        lines.append(
            "\t".join(
                [
                    "gage",
                    lk.lock,
                    lk.visa,
                    lk.world.match,
                    lk.parent,
                    req,
                    lk.world.qualname,
                    lk.world.call.replace("\t", " ").replace("\n", " "),
                    lk.world.site,
                    lk.verdict,
                ]
            )
        )
    return ("\n".join(lines) + "\n") if lines else ""


def report_to_json(report: Report) -> dict:
    return {
        "status": report.status,
        "base": report.base,
        "new": report.new,
        "mode": report.mode,
        "production_changed": report.production_changed,
        "notes": report.notes,
        "bound_locks": len(report.bound_locks),
        "machines": len(report.machines),
        "locks": [
            {
                "verdict": lk.verdict,
                "lock": lk.lock,
                "visa": lk.visa,
                "match": lk.world.match,
                "parent": lk.parent,
                "require": lk.world.require,
                "new": lk.new_occ,
                "splice": lk.splice_occ,
                "func": lk.world.qualname,
                "call": lk.world.call,
                "site": lk.world.site,
                "path": lk.world.path,
                "origin": lk.world.origin,
            }
            for lk in report.locks
        ],
    }


# ---------------------------------------------------------------------------
# Drive
# ---------------------------------------------------------------------------


def files_at_new(repo: Path) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for path in list_worktree_files(repo):
        data = new_bytes(repo, path)
        if data is not None:
            out[path] = data
    return out


def files_at_base(repo: Path, base: str) -> dict[str, bytes]:
    out: dict[str, bytes] = {}
    for path in list_tree_files(repo, base):
        data = git_show(repo, base, path)
        if data is not None:
            out[path] = data
    return out


def run_world_mode(
    repo: Path,
    base: str,
    worlds: list[World],
    old_machines: set[tuple[tuple[str, str], ...]],
    timeout: float,
    keep_tmp: bool,
) -> tuple[list[Lock], list[str]]:
    tmp = Path(tempfile.mkdtemp(prefix="gage-"))
    new_dir = tmp / "new"
    sp_dir = tmp / "splice"
    new_dir.mkdir()
    sp_dir.mkdir()
    notes: list[str] = []
    try:
        materialize(repo, new_dir, base, overlay="none")
        materialize(repo, sp_dir, base, overlay="all")
        locks: list[Lock] = []
        for w in worlds:
            n = run_world(new_dir, w)
            s = run_world(sp_dir, w)
            lock = classify_pair(n, s)
            locks.append(
                Lock(
                    world=w,
                    lock=lock,
                    new_occ=n.status,
                    splice_occ=s.status,
                    parent=parent_of(w, old_machines),
                )
            )
        return locks, notes
    finally:
        if keep_tmp:
            notes.append(f"kept tmp {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


def run_suite_mode(
    repo: Path,
    base: str,
    timeout: float,
    keep_tmp: bool,
    old_machines: set[tuple[tuple[str, str], ...]],
) -> tuple[list[Lock], list[str], RunResult | None, RunResult | None]:
    notes: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="gage-"))
    new_dir = tmp / "new"
    sp_dir = tmp / "splice"
    new_dir.mkdir()
    sp_dir.mkdir()
    try:
        materialize(repo, new_dir, base, overlay="none")
        materialize(repo, sp_dir, base, overlay="all")
        cmd = detect_cmd(repo)
        new_run = run_cmd(cmd, new_dir, timeout)
        if not new_run.ok:
            # If NEW is skip-only that's still ok (exit 0). Fail is BROKEN.
            test_files = {
                p: data
                for p, data in files_at_new(repo).items()
                if path_role(p) == "test"
            }
            worlds = harvest_suite(test_files) or [
                World(
                    path="(suite)",
                    line=1,
                    func="suite",
                    recv="",
                    args=[],
                    raw=" ".join(cmd),
                    lang="py",
                    visa="OPEN",
                    require={},
                    match="MATCH",
                    origin="suite",
                )
            ]
            locks = [
                Lock(world=w, lock="BROKEN", new_occ="fail", splice_occ="-", parent=parent_of(w, old_machines))
                for w in worlds
            ]
            notes.append("refusing to splice while the new tree is already red")
            return locks, notes, new_run, None
        sp_run = run_cmd(cmd, sp_dir, timeout)
        test_files = {
            p: data for p, data in files_at_new(repo).items() if path_role(p) == "test"
        }
        worlds = harvest_suite(test_files)
        if not worlds:
            worlds = [
                World(
                    path="(suite)",
                    line=1,
                    func="suite",
                    recv="",
                    args=[],
                    raw=" ".join(cmd),
                    lang="py",
                    visa="OPEN",
                    require={},
                    match="MATCH",
                    origin="suite",
                )
            ]
        skips = count_skips(sp_run.output)
        if not sp_run.ok:
            lock_s = "LOCKED"
            n_occ, s_occ = "pass", "fail"
        elif skips and re.search(r"ran 0 tests|NO TESTS RAN|skipped", sp_run.output, re.I):
            lock_s = "SKIP"
            n_occ, s_occ = "pass", "skip"
        else:
            lock_s = "LOOSE"
            n_occ, s_occ = "pass", "pass"
        # Visa the lockset: if the suite vetoes, every harvested test-world
        # shares the suite occupancy, but BOUND vs OPEN still splits them.
        # Witnesses, when parseable, keep only those tests.
        witnesses = parse_witnesses(sp_run.output)
        chosen = worlds
        if lock_s == "LOCKED" and witnesses:
            filtered = []
            for w in worlds:
                blob = w.func + " " + w.path + " " + w.raw
                if any(wt in blob or w.func in wt or Path(w.path).name in wt for wt in witnesses):
                    filtered.append(w)
            if filtered:
                chosen = filtered
        locks = [
            Lock(
                world=w,
                lock=lock_s,
                new_occ=n_occ,
                splice_occ=s_occ,
                parent=parent_of(w, old_machines),
            )
            for w in chosen
        ]
        return locks, notes, new_run, sp_run
    finally:
        if keep_tmp:
            notes.append(f"kept tmp {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


def run_gage(
    repo: Path,
    base: str,
    mode_flag: str,
    timeout: float,
    keep_tmp: bool,
) -> Report:
    repo = repo.resolve()
    base_sha = rev_parse(repo, base)
    changed = production_changed(repo, base)
    new_files = files_at_new(repo)
    old_files = files_at_base(repo, base)
    new_worlds = harvest_tree(new_files)
    old_worlds = harvest_tree(old_files)
    old_machines = {w.machine_key for w in old_worlds if w.visa == "BOUND"}

    py_worlds = [w for w in new_worlds if w.generable]
    has_tests = any(path_role(p) == "test" for p in new_files)

    if mode_flag == "suite":
        mode = "suite"
    elif mode_flag == "emit":
        mode = "worlds"
    elif py_worlds:
        mode = "worlds"
    elif has_tests:
        mode = "suite"
    else:
        mode = "worlds"

    report = Report(
        status="CLEAN",
        base=f"{base} ({base_sha[:12]})",
        new="worktree",
        mode=mode,
        production_changed=changed,
    )

    if not changed:
        report.notes.append("no production source files differ from base")
        # Still list NEW worlds so --report can show them, but they are not locks.
        report.status = "CLEAN"
        return report

    if mode == "worlds":
        if not py_worlds and not new_worlds:
            report.notes.append("no production worlds harvested; no tests to fall back on")
            report.status = "CLEAR"
            return report
        targets = py_worlds if py_worlds else new_worlds
        locks, notes = run_world_mode(repo, base, targets, old_machines, timeout, keep_tmp)
        # Non-generable worlds still appear as UNRUN (Swift Brave, etc.).
        seen = {(lk.world.path, lk.world.func, tuple(lk.world.args)) for lk in locks}
        for w in new_worlds:
            key = (w.path, w.func, tuple(w.args))
            if key in seen:
                continue
            if not w.generable:
                locks.append(
                    Lock(
                        world=w,
                        lock="UNRUN",
                        new_occ="unrun",
                        splice_occ="unrun",
                        parent=parent_of(w, old_machines),
                    )
                )
        report.locks = locks
        report.notes.extend(notes)
    else:
        locks, notes, nr, sr = run_suite_mode(repo, base, timeout, keep_tmp, old_machines)
        report.locks = locks
        report.notes.extend(notes)
        report.suite_new = nr
        report.suite_splice = sr

    report.status = overall_status(report)
    return report


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------


def _init_repo(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)
    git(["init"], cwd=d)
    git(["config", "user.email", "gage@demo"], cwd=d)
    git(["config", "user.name", "gage"], cwd=d)
    git(["config", "commit.gpgsign", "false"], cwd=d)


def _commit(d: Path, msg: str) -> None:
    git(["add", "-A"], cwd=d)
    git(["commit", "-qm", msg], cwd=d)


def self_test() -> int:
    failures: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        if cond:
            print(f"  ok  {msg}")
        else:
            failures.append(msg)
            print(f"  FAIL  {msg}", file=sys.stderr)

    home = str(Path.home())
    user = getpass.getuser()

    tmp = Path(tempfile.mkdtemp(prefix="gage-self-"))

    # 1. LOCKED-and-OPEN: Brave-like member. Default empty.
    d = tmp / "open-lock"
    _init_repo(d)
    (d / "app.py").write_text(
        "BROWSERS = ['Chrome', 'Safari']\n"
        "def is_browser(name):\n"
        "    return name in BROWSERS\n"
        "def tick():\n"
        "    is_browser('Chrome')\n",
        encoding="utf-8",
    )
    _commit(d, "old browsers")
    (d / "app.py").write_text(
        "BROWSERS = ['Chrome', 'Safari', 'Brave Browser']\n"
        "def is_browser(name):\n"
        "    return name in BROWSERS\n"
        "def tick():\n"
        "    is_browser('Brave Browser')\n",
        encoding="utf-8",
    )
    r = run_gage(d, "HEAD", "auto", 30, False)
    open_locked = [lk for lk in r.locks if lk.lock == "LOCKED" and lk.visa == "OPEN"]
    ok(r.status == "CLEAR", f"open-lock status CLEAR got {r.status}")
    ok(bool(open_locked), f"open-lock has LOCKED-and-OPEN { [lk.verdict for lk in r.locks] }")
    ok(render_debt(r) == "", f"open-lock default empty {render_debt(r)!r}")
    ok(all(lk.world.require == {} for lk in open_locked), "Brave require empty")
    ok("Brave Browser" in " ".join(lk.world.call for lk in open_locked), "Brave pinned")

    # 2. LOCKED-and-BOUND: this-host HOME encoded. Default debt.
    d = tmp / "bound-lock"
    _init_repo(d)
    (d / "app.py").write_text(
        "def who(home):\n"
        "    return home == '/tmp/nobody'\n"
        "def boot():\n"
        "    who('/tmp/nobody')\n",
        encoding="utf-8",
    )
    _commit(d, "old who")
    (d / "app.py").write_text(
        f"def who(home):\n"
        f"    return home == {home!r}\n"
        f"def boot():\n"
        f"    who({home!r})\n",
        encoding="utf-8",
    )
    r = run_gage(d, "HEAD", "auto", 30, False)
    ok(r.status == "BOUND-LOCK", f"bound-lock status got {r.status} {[lk.verdict for lk in r.locks]}")
    ok(bool(r.bound_locks), "bound-lock has LOCKED-and-BOUND")
    debt = render_debt(r)
    ok("LOCKED  BOUND" in debt, f"debt names BOUND {debt!r}")
    ok(home in debt or user in debt, f"debt names live home {debt!r}")
    ok("parent=CLEAN" in debt, f"new leak parent=CLEAN {debt!r}")
    ok(r.bound_locks[0].world.match == "MATCH", "live HOME MATCH")

    # 3. SKIP-and-BOUND: Alice isdir skipif. Default empty (not a lock).
    d = tmp / "bound-skip"
    _init_repo(d)
    (d / "app.py").write_text(
        "import os\n"
        "def load_profile(home):\n"
        "    return os.path.isdir(home)\n"
        "def start():\n"
        "    load_profile('/tmp')\n",
        encoding="utf-8",
    )
    _commit(d, "tmp profile")
    (d / "app.py").write_text(
        "import os\n"
        "def load_profile(home):\n"
        "    return os.path.isdir(home)\n"
        "def start():\n"
        "    load_profile('/Users/alice')\n",
        encoding="utf-8",
    )
    r = run_gage(d, "HEAD", "auto", 30, False)
    skips = [lk for lk in r.locks if lk.lock == "SKIP" and lk.visa == "BOUND"]
    ok(r.status == "CLEAR", f"alice skip status CLEAR got {r.status} {[lk.verdict for lk in r.locks]}")
    ok(bool(skips), f"alice occupancy SKIP { [lk.verdict for lk in r.locks] }")
    ok(skips and skips[0].world.match == "MISS", "alice MISS on this host")
    ok(render_debt(r) == "", "alice skip default empty (skip is not a lock)")

    # 4. debug-print vs return: suite fallback, LOCKED-and-OPEN.
    d = tmp / "debug-print"
    _init_repo(d)
    (d / "app.py").write_text("def add(a, b):\n    return 0\n", encoding="utf-8")
    (d / "test.py").write_text("from app import add\nassert add(2, 3) == 5\n", encoding="utf-8")
    _commit(d, "red add")
    (d / "app.py").write_text(
        'def add(a, b):\n    print("debug")\n    return a + b\n', encoding="utf-8"
    )
    (d / "test.py").write_text(
        "from app import add\nassert add(2, 3) == 5\n", encoding="utf-8"
    )
    r = run_gage(d, "HEAD", "auto", 30, False)
    ok(r.mode == "suite", f"debug-print falls back to suite got {r.mode}")
    ok(r.status == "CLEAR", f"debug-print CLEAR got {r.status} {[lk.verdict for lk in r.locks]}")
    ok(any(lk.lock == "LOCKED" and lk.visa == "OPEN" for lk in r.locks), "debug-print LOCKED-and-OPEN")
    ok(render_debt(r) == "", "debug-print default empty")

    # 5. textbook SPEC, not BOUND.
    visa, req = infer_world_text("/home/user/project")
    ok(visa == "SPEC" and req == {}, f"textbook SPEC got {visa} {req}")
    visa, req = infer_world_text("/Users/alice")
    ok(visa == "BOUND" and req.get("USER") == "alice", f"alice BOUND got {visa} {req}")
    visa, req = infer_world_text("GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome")
    ok(visa == "OPEN" and req == {}, f"github title OPEN got {visa} {req}")
    visa, req = infer_world_text("Brave Browser")
    ok(visa == "OPEN", f"Brave OPEN got {visa}")

    # 6. file-level Darwin comment is not a world of an OPEN call.
    text = '// when the macOS PollWatcher fallback is active.\ndef tick():\n    is_browser("Brave Browser")\n'
    ws = worlds_from_text("App.swift", text)
    ok(any(w.visa == "OPEN" and "Brave" in w.call for w in ws), f"comment+Brave harvested {ws}")
    ok(all(w.visa != "BOUND" for w in ws), "Darwin comment is not the Brave world")

    # 7. print("debug") is not a world.
    ws = worlds_from_text("app.py", 'def add(a, b):\n    print("debug")\n    return a + b\n')
    ok(not any(w.func == "print" for w in ws), f"print skipped {ws}")

    # 7b. ugly v0.1: title.split is not a world; GitHub title stays OPEN.
    titles_src = (
        "def extract_title(title):\n"
        '    return title.split(" - ", 1)[0]\n'
        "def crawl():\n"
        '    extract_title("GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome")\n'
    )
    ws = worlds_from_text("src/titles.py", titles_src)
    ok(not any(w.func == "split" for w in ws), f"title.split is not a world {ws}")
    ok(
        any(w.func == "extract_title" and w.visa == "OPEN" for w in ws),
        f"github title still harvested OPEN {ws}",
    )

    # 8. parent LEAKED: old already had the live HOME.
    d = tmp / "parent-leaked"
    _init_repo(d)
    (d / "app.py").write_text(
        f"def who(home):\n"
        f"    return home == {home!r}\n"
        f"def boot():\n"
        f"    who({home!r})\n",
        encoding="utf-8",
    )
    _commit(d, "already stained")
    (d / "app.py").write_text(
        f"def who(home):\n"
        f"    return home == {home!r}  # still\n"
        f"def boot():\n"
        f"    who({home!r})\n",
        encoding="utf-8",
    )
    r = run_gage(d, "HEAD", "auto", 30, False)
    # comment-only: production bytes differ, who() still True on both → LOOSE-and-BOUND
    loose_b = [lk for lk in r.locks if lk.lock == "LOOSE" and lk.visa == "BOUND"]
    ok(bool(loose_b), f"comment-only LOOSE-and-BOUND { [lk.verdict for lk in r.locks] }")
    ok(all(lk.parent == "LEAKED" for lk in loose_b), "parent LEAKED")
    ok(r.status == "CLEAR", f"LOOSE-and-BOUND is not a lock {r.status}")

    # 9. CLEAN
    d = tmp / "clean"
    _init_repo(d)
    (d / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (d / "test.py").write_text("from app import add\nassert add(2, 3) == 5\n", encoding="utf-8")
    _commit(d, "ok")
    r = run_gage(d, "HEAD", "auto", 30, False)
    ok(r.status == "CLEAN", f"clean {r.status}")
    ok(render_debt(r) == "", "clean empty")

    # 10. two Alice worlds, one machine.
    d = tmp / "two-alice"
    _init_repo(d)
    (d / "app.py").write_text(
        f"def who(home):\n    return home == '/tmp/nobody'\n"
        f"def also(home):\n    return home == '/tmp/nobody'\n"
        f"def boot():\n    who('/tmp/nobody')\n    also('/tmp/nobody')\n",
        encoding="utf-8",
    )
    _commit(d, "old")
    (d / "app.py").write_text(
        f"def who(home):\n    return home == {home!r}\n"
        f"def also(home):\n    return home == {home!r}\n"
        f"def boot():\n    who({home!r})\n    also({home!r})\n",
        encoding="utf-8",
    )
    r = run_gage(d, "HEAD", "auto", 30, False)
    ok(len(r.machines) == 1, f"two worlds one machine got {len(r.machines)}")
    ok(len(r.bound_locks) == 2, f"two bound-locks evidence got {len(r.bound_locks)}")
    debt = render_debt(r)
    ok(debt.count("LOCKED  BOUND") == 1, f"visa printed once {debt!r}")

    shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print(f"self-test failed: {len(failures)}", file=sys.stderr)
        return 1
    print("self-test ok")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gage",
        description=(
            "Clearance of the lockset: splice world-tests onto old production "
            "and name LOCKED-and-BOUND vs LOCKED-and-OPEN. Default is the CI "
            "gate: empty stdout when no lock assumes a machine."
        ),
    )
    p.add_argument(
        "base",
        nargs="?",
        default="HEAD",
        help="revision whose production files are spliced in (default: HEAD)",
    )
    p.add_argument("-C", "--repo", default=".", help="repository path")
    p.add_argument(
        "--emit",
        action="store_true",
        help="lockset = production-world tests (even if a suite exists)",
    )
    p.add_argument(
        "--suite",
        action="store_true",
        help="lockset = existing tests (visa of the tests that veto)",
    )
    p.add_argument("--report", "--human", action="store_true", help="all verdicts, not only BOUND locks")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--porcelain",
        action="store_true",
        help="gage\\tlock\\tvisa\\tmatch\\tparent\\trequire\\tfunc\\tcall\\tsite\\tverdict",
    )
    p.add_argument("--list", action="store_true", help="worlds and production diff; do not run")
    p.add_argument(
        "--due",
        action="store_true",
        help="fail on SKIP-and-BOUND too (stained tests that did not occupy the lock)",
    )
    p.add_argument("-q", "--quiet", action="store_true")
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--keep-tmp", action="store_true")
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
    try:
        repo = repo_root(Path(args.repo).resolve())
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2

    mode_flag = "auto"
    if args.emit and args.suite:
        print("gage: --emit and --suite are mutually exclusive", file=sys.stderr)
        return 2
    if args.emit:
        mode_flag = "emit"
    elif args.suite:
        mode_flag = "suite"

    if args.list:
        changed = production_changed(repo, args.base)
        new_files = files_at_new(repo)
        old_files = files_at_base(repo, args.base)
        worlds = harvest_tree(new_files)
        old_worlds = harvest_tree(old_files)
        old_machines = {w.machine_key for w in old_worlds if w.visa == "BOUND"}
        payload = {
            "base": args.base,
            "production_changed": changed,
            "worlds": [
                {
                    "func": w.qualname,
                    "call": w.call,
                    "site": w.site,
                    "visa": w.visa,
                    "require": w.require,
                    "match": w.match,
                    "parent": parent_of(w, old_machines),
                    "generable": w.generable,
                    "lang": w.lang,
                }
                for w in worlds
            ],
        }
        if args.json:
            json.dump(payload, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(f"gage --list  base={args.base}  prod={len(changed)}  worlds={len(worlds)}")
            for pth in changed:
                print(f"  prod  {pth}")
            for w in worlds:
                req = " ".join(f"{k}={v}" for k, v in w.require.items())
                extra = f"  {req}" if req else ""
                print(
                    f"  {w.visa:5s}  {w.match:5s}  parent={parent_of(w, old_machines)}"
                    f"{extra}  {w.call}  {w.site}"
                )
        return 0

    report = run_gage(repo, args.base, mode_flag, args.timeout, args.keep_tmp)
    if not args.quiet:
        if args.json:
            json.dump(report_to_json(report), sys.stdout, indent=2)
            sys.stdout.write("\n")
        elif args.porcelain:
            sys.stdout.write(render_porcelain(report))
        elif args.report:
            sys.stdout.write(render_report(report))
        else:
            sys.stdout.write(render_debt(report))

    if report.status == "BROKEN":
        return 3
    if report.status == "BOUND-LOCK":
        return 1
    if args.due and any(lk.lock == "SKIP" and lk.visa == "BOUND" for lk in report.locks):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
