#!/usr/bin/env python3
"""veil — cover-type of a production diff against the test suite.

A changed production name is:
  LIVE   a test calls/imports it without mocking it
  VEIL   tests only ever see a mock of it (or of its module)
  BARE   no test cites it and no test mocks it

Coverage says a line executed. alibi says the tree is necessary.
veil asks whether the tests can even observe the change.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.2"

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
    ".veil-tmp",
    "demo-tmp",
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
    ".swift",
    ".rb",
    ".java",
    ".kt",
    ".kts",
    ".cs",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".m",
    ".mm",
}

TEST_FILE_RE = re.compile(
    r"""
    (?:^|/)(?:test|spec)s?_
    | (?:^|/)test_[^/]+$
    | [^/]+_test\.[^/]+$
    | [^/]+_spec\.[^/]+$
    | [^/]+\.(?:test|spec)\.[^/]+$
    | (?:^|/)conftest\.py$
    """,
    re.VERBOSE | re.IGNORECASE,
)

IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")

PY_DEF_RE = re.compile(r"^[ \t]*(?:async[ \t]+)?def[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)", re.M)
PY_CLASS_RE = re.compile(r"^[ \t]*class[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)", re.M)

# Top-level-ish defs in brace languages. Intentionally line-oriented.
RUST_DEF_RE = re.compile(
    r"^[ \t]*(?:pub(?:\([^)]*\))?[ \t]+)?(?:async[ \t]+)?(?:unsafe[ \t]+)?"
    r"(?:fn|struct|enum|trait|type)[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
SWIFT_DEF_RE = re.compile(
    r"^[ \t]*(?:(?:public|internal|private|fileprivate|open|package)[ \t]+)*"
    r"(?:static[ \t]+|class[ \t]+)?(?:func|class|struct|enum|protocol|actor)[ \t]+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
JS_FN_RE = re.compile(
    r"^[ \t]*(?:export[ \t]+(?:default[ \t]+)?)?(?:async[ \t]+)?function[ \t]+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
JS_CONST_FN_RE = re.compile(
    r"^[ \t]*(?:export[ \t]+)?(?:const|let|var)[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"[ \t]*=[ \t]*(?:async[ \t]*)?(?:\(|<)",
    re.M,
)
JS_CLASS_RE = re.compile(
    r"^[ \t]*(?:export[ \t]+(?:default[ \t]+)?)?class[ \t]+(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)
GO_FN_RE = re.compile(
    r"^[ \t]*func[ \t]+(?:\([^)]+\)[ \t]+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)",
    re.M,
)

JS_MOCK_RE = re.compile(
    r"""(?:vi|jest)\.(?:do)?mock\(\s*['"]([^'"]+)['"]""",
    re.M,
)
JS_IMPORT_RE = re.compile(
    r"""(?:import\s+(?:[^'"]+\s+from\s+)?|require\()\s*['"]([^'"]+)['"]""",
    re.M,
)
PY_PATCH_STR_RE = re.compile(
    r"""(?:patch(?:\.object)?|mocker\.patch|mock\.patch)\(\s*['"]([^'"]+)['"]""",
    re.M,
)

NODE_EXTERNALS = {
    "fs",
    "path",
    "os",
    "util",
    "http",
    "https",
    "net",
    "crypto",
    "child_process",
    "stream",
    "events",
    "url",
    "assert",
    "buffer",
    "module",
    "process",
    "vitest",
    "jest",
}

SHORT_NEED_MODULE = 6

# Status of one changed production name.
LIVE, VEIL, BARE = "LIVE", "VEIL", "BARE"
# Rollup of a diff.
CLEAN, COVERED, THEATER, EXPOSED, OPEN = (
    "CLEAN",
    "COVERED",
    "THEATER",
    "EXPOSED",
    "OPEN",
)


@dataclass
class ChangedName:
    name: str
    qualname: str
    file: str
    kind: str
    body_hash: str
    public: bool = True

    @property
    def key(self) -> tuple[str, str]:
        return (self.file, self.qualname)


@dataclass
class Evidence:
    kind: str  # live | veil
    test: str
    via: str
    line: int
    file: str


@dataclass
class NameReport:
    name: ChangedName
    status: str
    lives: list[Evidence] = field(default_factory=list)
    veils: list[Evidence] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name.name,
            "qualname": self.name.qualname,
            "file": self.name.file,
            "kind": self.name.kind,
            "public": self.name.public,
            "status": self.status,
            "lives": [e.__dict__ for e in self.lives],
            "veils": [e.__dict__ for e in self.veils],
        }


@dataclass
class Report:
    repo: str
    base: str
    head: str
    status: str
    names: list[NameReport]
    production_files: list[str]
    test_files: list[str]

    def as_dict(self) -> dict:
        counts = {LIVE: 0, VEIL: 0, BARE: 0}
        for n in self.names:
            counts[n.status] = counts.get(n.status, 0) + 1
        return {
            "repo": self.repo,
            "base": self.base,
            "head": self.head,
            "status": self.status,
            "counts": counts,
            "production_files": self.production_files,
            "test_files": self.test_files,
            "names": [n.as_dict() for n in self.names],
        }


def die(msg: str, code: int = 2) -> None:
    print(f"veil: {msg}", file=sys.stderr)
    raise SystemExit(code)


def git_run(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git(repo: Path, *args: str, check: bool = True) -> bytes:
    r = git_run(repo, *args)
    if check and r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip()
        die(f"git {' '.join(args)}: {err or r.returncode}")
    return r.stdout


def git_text(repo: Path, *args: str, check: bool = True) -> str:
    return git(repo, *args, check=check).decode("utf-8", "replace")


def posix(p: str | Path) -> str:
    return str(p).replace("\\", "/")


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()[:16]


def read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8", "replace")


def is_source(path: str) -> bool:
    return Path(path).suffix.lower() in SOURCE_EXTENSIONS


def path_parts(path: str) -> list[str]:
    return [p for p in posix(path).split("/") if p and p != "."]


def is_skipped_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES


def is_test_path(path: str) -> bool:
    parts = path_parts(path)
    lower = [p.lower() for p in parts]
    if any(p in TEST_DIR_NAMES for p in lower[:-1]):
        return True
    if any(p in FIXTURE_DIR_NAMES for p in lower):
        return True
    # Swift/Java packages: TenaoshiEngineTests, FooTests/
    if any(
        p.endswith("tests") or p.endswith("specs") or p.endswith("test")
        for p in lower[:-1]
    ):
        return True
    return bool(TEST_FILE_RE.search(posix(path)))


def is_production_path(path: str) -> bool:
    if not is_source(path):
        return False
    parts = path_parts(path)
    if any(is_skipped_dir(p) for p in parts):
        return False
    if is_test_path(path):
        return False
    return True


def is_under_nested_git(repo: Path, path: str) -> bool:
    root = repo.resolve()
    cur = (root / path).resolve().parent
    while True:
        try:
            cur.relative_to(root)
        except ValueError:
            return False
        if cur == root:
            return False
        if (cur / ".git").exists():
            return True
        cur = cur.parent


def strip_ext(name: str) -> str:
    p = Path(name)
    if p.suffix.lower() in SOURCE_EXTENSIONS | {".js"}:
        return p.stem
    return name


def parse_name_status(raw: bytes) -> list[tuple[str, str, str | None]]:
    items = raw.split(b"\0")
    out: list[tuple[str, str, str | None]] = []
    i = 0
    while i < len(items) and items[i]:
        st = items[i].decode("utf-8", "replace")
        if st.startswith("R") or st.startswith("C"):
            if i + 2 >= len(items):
                break
            old = items[i + 1].decode("utf-8", "replace")
            new = items[i + 2].decode("utf-8", "replace")
            out.append((st, new, old))
            i += 3
        else:
            if i + 1 >= len(items):
                break
            path = items[i + 1].decode("utf-8", "replace")
            out.append((st, path, None))
            i += 2
    return out


def changed_paths(repo: Path, base: str, head: str | None) -> list[tuple[str, str, str | None]]:
    if head is None:
        raw = git(repo, "diff", "--name-status", "-z", "--no-renames", base)
        extra = git(repo, "ls-files", "-o", "--exclude-standard", "-z", check=False)
        rows = parse_name_status(raw)
        for p in extra.split(b"\0"):
            if not p:
                continue
            path = p.decode("utf-8", "replace")
            rows.append(("A", path, None))
        return rows
    raw = git(repo, "diff", "--name-status", "-z", "--no-renames", base, head)
    return parse_name_status(raw)


def blob_at(repo: Path, rev: str | None, path: str) -> str | None:
    if rev is None:
        fp = repo / path
        if not fp.is_file():
            return None
        return read_text(fp)
    r = git_run(repo, "show", f"{rev}:{path}")
    if r.returncode != 0:
        return None
    return r.stdout.decode("utf-8", "replace")


def attr_path(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = attr_path(node.value)
        return f"{left}.{node.attr}" if left else node.attr
    return ""


def const_str(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def py_defs(src: str) -> dict[str, tuple[str, str, bool]]:
    """qualname -> (kind, body_hash, public). Nested functions inside functions omitted."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return regex_py_defs(src)
    out: dict[str, tuple[str, str, bool]] = {}

    def dump(n: ast.AST) -> str:
        return sha1(ast.dump(n, include_attributes=False))

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test"):
                continue
            out[node.name] = ("fn", dump(node), not node.name.startswith("_"))
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("Test") or node.name.endswith("Test"):
                continue
            pub = not node.name.startswith("_")
            out[node.name] = ("class", dump(node), pub)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith("test"):
                        continue
                    q = f"{node.name}.{item.name}"
                    out[q] = (
                        "method",
                        dump(item),
                        pub and not item.name.startswith("_"),
                    )
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper() and len(t.id) > 1:
                    out[t.id] = ("const", dump(node), True)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id.isupper() and len(node.target.id) > 1:
                out[node.target.id] = ("const", dump(node), True)
    return out


def regex_py_defs(src: str) -> dict[str, tuple[str, str, bool]]:
    out: dict[str, tuple[str, str, bool]] = {}
    for m in PY_CLASS_RE.finditer(src):
        name = m.group("name")
        if name.startswith("Test"):
            continue
        out[name] = ("class", sha1(name + str(m.start())), not name.startswith("_"))
    for m in PY_DEF_RE.finditer(src):
        name = m.group("name")
        if name.startswith("test"):
            continue
        out[name] = ("fn", sha1(_slice_from(src, m.start())), not name.startswith("_"))
    return out


def _slice_from(src: str, start: int, limit: int = 4000) -> str:
    return src[start : start + limit]


def _brace_span(src: str, start: int) -> str:
    """Source from a def to the matching close-brace, or the statement if none."""
    n = len(src)
    i = start
    in_str: str | None = None
    escape = False
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == in_str:
                in_str = None
            i += 1
            continue
        if c in "\"'`":
            in_str = c
            i += 1
            continue
        if c == "/" and nxt == "/":
            while i < n and src[i] != "\n":
                i += 1
            continue
        if c == "/" and nxt == "*":
            i += 2
            while i + 1 < n and not (src[i] == "*" and src[i + 1] == "/"):
                i += 1
            i += 2
            continue
        if c == "{":
            break
        if c == ";" and i > start:
            return src[start : i + 1]
        i += 1
    if i >= n:
        return src[start : min(n, start + 4000)]
    depth = 0
    in_str = None
    escape = False
    j = i
    while j < n:
        c = src[j]
        nxt = src[j + 1] if j + 1 < n else ""
        if in_str:
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == in_str:
                in_str = None
            j += 1
            continue
        if c in "\"'`":
            in_str = c
            j += 1
            continue
        if c == "/" and nxt == "/":
            while j < n and src[j] != "\n":
                j += 1
            continue
        if c == "/" and nxt == "*":
            j += 2
            while j + 1 < n and not (src[j] == "*" and src[j + 1] == "/"):
                j += 1
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[start : j + 1]
        j += 1
    return src[start : min(n, start + 8000)]


def _uses_braces(path: str) -> bool:
    return Path(path).suffix.lower() in {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".rs",
        ".go",
        ".swift",
        ".java",
        ".kt",
        ".kts",
        ".c",
        ".h",
        ".cc",
        ".cpp",
        ".cs",
    }


def is_exported_match(src: str, match: re.Match[str], path: str) -> bool:
    """Is this def part of the file's public surface?"""
    ext = Path(path).suffix.lower()
    text = match.group(0)
    name = match.group("name")
    if ext == ".py":
        return not name.startswith("_")
    if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        line_start = src.rfind("\n", 0, match.start()) + 1
        window = src[line_start : match.end()]
        return bool(re.search(r"\bexport\b", window))
    if ext == ".rs":
        return bool(re.search(r"\bpub(?:\([^)]*\))?\b", text))
    if ext == ".swift":
        return not bool(re.search(r"\b(?:private|fileprivate)\b", text))
    if ext == ".go":
        return bool(name) and name[0].isupper()
    if ext in {".java", ".kt", ".kts", ".cs"}:
        return bool(re.search(r"\bpublic\b", text))
    return True


def regex_defs(src: str, path: str) -> dict[str, tuple[str, str, bool]]:
    ext = Path(path).suffix.lower()
    pats: list[re.Pattern[str]] = []
    if ext == ".py":
        return regex_py_defs(src)
    if ext == ".rs":
        pats = [RUST_DEF_RE]
    elif ext == ".swift":
        pats = [SWIFT_DEF_RE]
    elif ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        pats = [JS_FN_RE, JS_CONST_FN_RE, JS_CLASS_RE]
    elif ext == ".go":
        pats = [GO_FN_RE]
    else:
        pats = [JS_FN_RE, PY_DEF_RE, RUST_DEF_RE, SWIFT_DEF_RE, GO_FN_RE]
    out: dict[str, tuple[str, str, bool]] = {}
    brace = _uses_braces(path)
    for pat in pats:
        for m in pat.finditer(src):
            name = m.group("name")
            if name.startswith("test") or name.startswith("Test"):
                continue
            kind = "class" if "class" in m.group(0) else "fn"
            body = _brace_span(src, m.start()) if brace else _slice_from(src, m.start())
            out[name] = (kind, sha1(body), is_exported_match(src, m, path))
    return out


def defs_for(src: str, path: str) -> dict[str, tuple[str, str, bool]]:
    if Path(path).suffix.lower() == ".py":
        return py_defs(src)
    return regex_defs(src, path)


def is_private(qualname: str) -> bool:
    parts = qualname.split(".")
    return any(p.startswith("_") and p != "__init__" for p in parts)


def changed_names_in_file(path: str, old: str | None, new: str | None) -> list[ChangedName]:
    if new is None:
        return []
    new_defs = defs_for(new, path)
    old_defs = defs_for(old, path) if old is not None else {}
    out: list[ChangedName] = []
    for q, (kind, h, public) in new_defs.items():
        if is_private(q):
            continue
        prev = old_defs.get(q)
        if prev is None or prev[1] != h:
            out.append(
                ChangedName(
                    name=q.split(".")[-1],
                    qualname=q,
                    file=posix(path),
                    kind=kind,
                    body_hash=h,
                    public=public,
                )
            )
    return out


def expand_existing(repo: Path, cand: Path) -> list[Path]:
    found: list[Path] = []
    variants: list[Path] = [cand]
    suffixes = list(SOURCE_EXTENSIONS) + [".js"]
    if cand.suffix.lower() in {".js", ".mjs", ".cjs"}:
        variants.append(cand.with_suffix(".ts"))
        variants.append(cand.with_suffix(".tsx"))
        variants.append(cand.with_suffix(".jsx"))
    if cand.suffix.lower() in {".ts", ".tsx"}:
        variants.append(cand.with_suffix(".js"))
    if cand.suffix == "":
        for ext in suffixes:
            variants.append(Path(str(cand) + ext))
            variants.append(cand.with_suffix(ext))
    for v in variants:
        if v.is_file():
            found.append(v)
        idx_dir = v if v.suffix == "" else v
        if idx_dir.is_dir():
            for idx in (
                "index.ts",
                "index.js",
                "index.tsx",
                "index.jsx",
                "__init__.py",
                "mod.rs",
            ):
                p = idx_dir / idx
                if p.is_file():
                    found.append(p)
    # If cand is foo.js and foo.ts exists
    if cand.suffix:
        for ext in suffixes:
            p = cand.with_suffix(ext)
            if p.is_file():
                found.append(p)
    uniq: list[Path] = []
    seen: set[str] = set()
    for p in found:
        try:
            rp = p.resolve()
        except OSError:
            continue
        key = str(rp)
        if key in seen:
            continue
        seen.add(key)
        try:
            rp.relative_to(repo.resolve())
        except ValueError:
            continue
        uniq.append(rp)
    return uniq


def resolve_spec(repo: Path, from_file: Path, spec: str) -> list[Path]:
    spec = spec.strip().split("?", 1)[0].split("#", 1)[0]
    if not spec or spec.startswith("node:"):
        return []
    if spec in NODE_EXTERNALS or spec.split("/")[0] in NODE_EXTERNALS:
        return []
    if spec.startswith("@"):  # scoped npm package
        return []
    repo = repo.resolve()
    cands: list[Path] = []
    if spec.startswith("."):
        cands.append((from_file.parent / spec))
    else:
        dotted = repo / spec.replace(".", "/")
        cands.append(dotted)
        cands.append(repo / spec)
        bits = spec.split(".")
        for i in range(len(bits), 0, -1):
            cands.append(repo / "/".join(bits[:i]))
    found: list[Path] = []
    for c in cands:
        found.extend(expand_existing(repo, c))
    return found


def rel_to_repo(repo: Path, path: Path) -> str:
    try:
        return posix(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return posix(path)


def mock_target_last(spec: str) -> str:
    s = spec.replace("\\", "/")
    last = s.split("/")[-1]
    last = last.split(".")[-1] if "/" not in spec and spec.count(".") >= 1 else strip_ext(last)
    return strip_ext(last.split(".")[-1])


@dataclass
class TestFileFacts:
    path: str
    mocks: list[tuple[str, int]]  # (spec, line)
    imports: list[tuple[str, int]]
    idents: set[str]
    tests: list[str]


def line_of(src: str, idx: int) -> int:
    return src[:idx].count("\n") + 1


def py_test_facts(src: str, path: str) -> TestFileFacts:
    facts = TestFileFacts(path=posix(path), mocks=[], imports=[], idents=set(), tests=[])
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return regex_test_facts(src, path)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            ln = getattr(node, "lineno", 1)
            if isinstance(node, ast.Import):
                for a in node.names:
                    facts.imports.append((a.name, ln))
                    facts.idents.add(a.name.split(".")[0])
            else:
                mod = node.module or ""
                if mod:
                    facts.imports.append((mod, ln))
                    facts.idents.add(mod.split(".")[0])
                for a in node.names:
                    facts.idents.add(a.name)
        if isinstance(node, ast.Name):
            facts.idents.add(node.id)
        if isinstance(node, ast.Attribute):
            facts.idents.add(node.attr)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test"):
                facts.tests.append(node.name)
            for dec in node.decorator_list:
                spec = patch_spec_from_call(dec if isinstance(dec, ast.Call) else None)
                if spec:
                    facts.mocks.append((spec, getattr(dec, "lineno", 1)))
        if isinstance(node, ast.ClassDef):
            for dec in node.decorator_list:
                spec = patch_spec_from_call(dec if isinstance(dec, ast.Call) else None)
                if spec:
                    facts.mocks.append((spec, getattr(dec, "lineno", 1)))
        if isinstance(node, ast.Call):
            spec = patch_spec_from_call(node)
            if spec:
                facts.mocks.append((spec, getattr(node, "lineno", 1)))
    return facts


def patch_spec_from_call(node: ast.Call | None) -> str | None:
    if node is None:
        return None
    name = attr_path(node.func)
    tail = name.split(".")[-1]
    parent = name.split(".")[-2] if "." in name else ""
    if tail == "object" and parent == "patch":
        if len(node.args) >= 2:
            cls = attr_path(node.args[0])
            attr = const_str(node.args[1])
            if cls and attr:
                return f"{cls}.{attr}"
        return None
    if tail not in {"patch", "doMock", "mock"}:
        return None
    if not node.args:
        return None
    s = const_str(node.args[0])
    return s


def regex_test_facts(src: str, path: str) -> TestFileFacts:
    facts = TestFileFacts(path=posix(path), mocks=[], imports=[], idents=set(), tests=[])
    ext = Path(path).suffix.lower()
    if ext == ".py":
        for m in PY_PATCH_STR_RE.finditer(src):
            facts.mocks.append((m.group(1), line_of(src, m.start())))
        for m in re.finditer(
            r"^(?:from[ \t]+([\w.]+)[ \t]+import|import[ \t]+([\w.]+))", src, re.M
        ):
            spec = m.group(1) or m.group(2)
            facts.imports.append((spec, line_of(src, m.start())))
        for m in PY_DEF_RE.finditer(src):
            if m.group("name").startswith("test"):
                facts.tests.append(m.group("name"))
    if ext in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
        for m in JS_MOCK_RE.finditer(src):
            facts.mocks.append((m.group(1), line_of(src, m.start())))
        for m in JS_IMPORT_RE.finditer(src):
            facts.imports.append((m.group(1), line_of(src, m.start())))
    if ext == ".rs":
        for m in re.finditer(r"mockall|mock!|#\[automock\]|mock::", src):
            facts.mocks.append((m.group(0), line_of(src, m.start())))
        for m in re.finditer(r"^use[ \t]+([^;]+);", src, re.M):
            facts.imports.append((m.group(1).strip(), line_of(src, m.start())))
    if ext == ".swift":
        for m in re.finditer(r"import[ \t]+([A-Za-z_][A-Za-z0-9_]*)", src):
            facts.imports.append((m.group(1), line_of(src, m.start())))
    facts.idents = set(IDENT_RE.findall(src))
    return facts


def test_facts_for(src: str, path: str) -> TestFileFacts:
    if Path(path).suffix.lower() == ".py":
        facts = py_test_facts(src, path)
        # regex mocks as backup for pytest-mock string forms already in AST
        extra = regex_test_facts(src, path)
        have = {(m[0], m[1]) for m in facts.mocks}
        have_spec = {m[0] for m in facts.mocks}
        for spec, ln in extra.mocks:
            if spec in have_spec or (spec, ln) in have:
                continue
            facts.mocks.append((spec, ln))
        seen: set[tuple[str, int]] = set()
        uniq: list[tuple[str, int]] = []
        for spec, ln in facts.mocks:
            if (spec, ln) in seen:
                continue
            seen.add((spec, ln))
            uniq.append((spec, ln))
        facts.mocks = uniq
        return facts
    return regex_test_facts(src, path)


def list_test_files(repo: Path, head: str | None) -> list[str]:
    if head is None:
        raw = git(repo, "ls-files", "-z", "-c", "-o", "--exclude-standard")
    else:
        raw = git(repo, "ls-tree", "-r", "-z", "--name-only", head)
    paths = [p.decode("utf-8", "replace") for p in raw.split(b"\0") if p]
    return [p for p in paths if is_test_path(p) and is_source(p)]


def module_guess(path: str) -> set[str]:
    """Candidate module strings for a production file."""
    p = posix(path)
    noext = str(Path(p).with_suffix(""))
    parts = path_parts(noext)
    if parts and parts[-1] in {"__init__", "index", "mod"}:
        parts = parts[:-1]
    dotted = ".".join(parts)
    out = {dotted, parts[-1] if parts else "", noext, p, Path(p).name, Path(p).stem}
    # src/foo/bar.py also lives as foo.bar
    if parts and parts[0] in {"src", "lib", "app", "apps", "packages", "Sources"}:
        out.add(".".join(parts[1:]))
        if len(parts) > 1:
            out.add(parts[-1])
    return {x for x in out if x}


def file_cited_by_import(prod: str, spec: str, test_path: str, repo: Path) -> bool:
    if not spec:
        return False
    mods = module_guess(prod)
    spec_n = spec.replace("\\", "/")
    if spec_n in mods or spec_n.replace("/", ".") in mods:
        return True
    stem = Path(prod).stem
    last = spec_n.split("/")[-1]
    last = strip_ext(last.split(".")[-1] if "." in last and "/" not in spec_n else last)
    if last == stem:
        # weak: same stem
        return True
    resolved = resolve_spec(repo, repo / test_path, spec)
    prod_res = (repo / prod).resolve()
    for r in resolved:
        if r.resolve() == prod_res:
            return True
    return False


def mock_hits_name(
    spec: str,
    test_path: str,
    cn: ChangedName,
    repo: Path,
) -> bool:
    last = mock_target_last(spec)
    if last == cn.name or last == cn.qualname or spec.endswith(cn.qualname) or spec.endswith("." + cn.name):
        # require module agreement for short names
        if len(cn.name) < SHORT_NEED_MODULE:
            mods = module_guess(cn.file)
            if not any(m and (m in spec or spec.startswith(".") or spec.endswith(cn.name)) for m in mods):
                if not file_cited_by_import(cn.file, spec, test_path, repo):
                    # still allow exact dotted match shop.checkout
                    if spec.endswith("." + cn.name) or spec.endswith("/" + cn.name):
                        return True
                    if spec.startswith("."):
                        return file_cited_by_import(cn.file, spec, test_path, repo)
                    return False
        else:
            if spec.endswith("." + cn.name) or last == cn.name:
                return True
    resolved = resolve_spec(repo, repo / test_path, spec)
    prod_res = (repo / cn.file).resolve()
    for r in resolved:
        if r.resolve() == prod_res:
            # file-level mock of the production module
            if "." in spec and not spec.startswith(".") and "/" not in spec:
                # shop.checkout — name-level if last != stem
                stem = Path(cn.file).stem
                if last != stem and last != cn.name and last != cn.qualname:
                    return False
                if last == cn.name or last == cn.qualname:
                    return True
                if last == stem:
                    return True
            return True
    return False


def live_hits_name(facts: TestFileFacts, cn: ChangedName, repo: Path) -> Evidence | None:
    cited = cn.name in facts.idents or cn.qualname in facts.idents
    if not cited:
        return None
    imported = False
    via = f"cite {cn.qualname}"
    ln = 1
    for spec, sln in facts.imports:
        if file_cited_by_import(cn.file, spec, facts.path, repo):
            imported = True
            via = f"import {spec} + cite {cn.qualname}"
            ln = sln
            break
    stem = Path(cn.file).stem
    test_stem = (
        Path(facts.path)
        .stem.replace(".test", "")
        .replace(".spec", "")
        .replace("test_", "")
        .replace("_test", "")
        .replace("test ", "")
    )
    same_stem = stem in test_stem or test_stem in stem
    if len(cn.name) < SHORT_NEED_MODULE and not imported and not same_stem:
        return None
    if not imported and not same_stem and len(cn.name) < 12:
        # medium names still need some module agreement unless unique-looking
        if not any(cn.name in spec or stem in spec for spec, _ in facts.imports):
            # ident-only hit in an unrelated test file is a false LIVE
            if stem not in facts.path and cn.name not in Path(facts.path).stem:
                return None
    return Evidence("live", _test_label(facts), via, ln, facts.path)


def _test_label(facts: TestFileFacts) -> str:
    if len(facts.tests) == 1:
        return f"{facts.path}::{facts.tests[0]}"
    if facts.tests:
        return f"{facts.path}::({len(facts.tests)} tests)"
    return facts.path


def _dedupe_ev(rows: list[Evidence]) -> list[Evidence]:
    seen: set[tuple[str, str, int, str]] = set()
    out: list[Evidence] = []
    for e in rows:
        key = (e.kind, e.test, e.line, e.via)
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out


def classify_name(
    cn: ChangedName, tests: list[TestFileFacts], repo: Path
) -> NameReport:
    lives: list[Evidence] = []
    veils: list[Evidence] = []
    for tf in tests:
        veiled_here = False
        for spec, ln in tf.mocks:
            if mock_hits_name(spec, tf.path, cn, repo):
                veils.append(
                    Evidence("veil", _test_label(tf), f"mock {spec}", ln, tf.path)
                )
                veiled_here = True
        if veiled_here:
            continue
        hit = live_hits_name(tf, cn, repo)
        if hit:
            lives.append(hit)
    lives = _dedupe_ev(lives)
    veils = _dedupe_ev(veils)
    if lives:
        status = LIVE
    elif veils:
        status = VEIL
    else:
        status = BARE
    return NameReport(name=cn, status=status, lives=lives, veils=veils)


def drop_private_bare(names: list[NameReport]) -> list[NameReport]:
    """Internal helpers that nobody cites are coverage noise. Internal VEIL stays."""
    return [n for n in names if n.name.public or n.status != BARE]


def rollup(names: list[NameReport]) -> str:
    if not names:
        return CLEAN
    has_bare = any(n.status == BARE for n in names)
    has_veil = any(n.status == VEIL for n in names)
    if has_bare and has_veil:
        return OPEN
    if has_bare:
        return EXPOSED
    if has_veil:
        return THEATER
    return COVERED


def analyze(repo: Path, base: str, head: str | None, all_names: bool = False) -> Report:
    repo = repo.resolve()
    rows = changed_paths(repo, base, head)
    prod_files: list[str] = []
    names: list[ChangedName] = []
    seen: set[tuple[str, str]] = set()
    for st, path, _old in rows:
        if st.startswith("D"):
            continue
        if not is_production_path(path):
            continue
        if is_under_nested_git(repo, path):
            continue
        prod_files.append(path)
        new = blob_at(repo, head, path)
        old_path = path
        old = blob_at(repo, base, old_path) if not st.startswith("A") else None
        if st.startswith("A"):
            old = None
        for cn in changed_names_in_file(path, old, new):
            if cn.key in seen:
                continue
            seen.add(cn.key)
            names.append(cn)
    prod_files = sorted(set(prod_files))
    tfiles = list_test_files(repo, head)
    facts: list[TestFileFacts] = []
    for tp in tfiles:
        src = blob_at(repo, head, tp)
        if src is None:
            continue
        facts.append(test_facts_for(src, tp))
    reports = [classify_name(cn, facts, repo) for cn in names]
    if not all_names:
        reports = drop_private_bare(reports)
    reports.sort(key=lambda r: ({BARE: 0, VEIL: 1, LIVE: 2}[r.status], r.name.file, r.name.qualname))
    return Report(
        repo=str(repo),
        base=base,
        head=head or "worktree",
        status=rollup(reports),
        names=reports,
        production_files=prod_files,
        test_files=sorted(tfiles),
    )


def fmt_text(rep: Report, explain: bool) -> str:
    counts = {LIVE: 0, VEIL: 0, BARE: 0}
    for n in rep.names:
        counts[n.status] += 1
    lines = [
        f"veil  base={rep.base}  head={rep.head}  status={rep.status}  "
        f"names={len(rep.names)}  LIVE={counts[LIVE]}  VEIL={counts[VEIL]}  BARE={counts[BARE]}"
    ]
    if not rep.names:
        lines.append("  (no changed production names)")
        return "\n".join(lines) + "\n"
    width = max((len(n.name.qualname) for n in rep.names), default=8)
    for n in rep.names:
        ev = ""
        if n.status == LIVE and n.lives:
            ev = n.lives[0].via + "  " + n.lives[0].test
        elif n.status == VEIL and n.veils:
            ev = n.veils[0].via + "  " + n.veils[0].test
        lines.append(
            f"  {n.status:<5}  {n.name.qualname:<{width}}  {n.name.file}  {ev}".rstrip()
        )
        if explain:
            for e in n.lives:
                lines.append(f"           live  {e.test}:{e.line}  {e.via}")
            for e in n.veils:
                lines.append(f"           veil  {e.test}:{e.line}  {e.via}")
    return "\n".join(lines) + "\n"


def fmt_porcelain(rep: Report) -> str:
    lines = [f"status\t{rep.status}"]
    for n in rep.names:
        evs = n.lives if n.status == LIVE else n.veils if n.status == VEIL else []
        if not evs:
            lines.append(
                f"{n.status}\t{n.name.qualname}\t{n.name.file}\t-\t-"
            )
            continue
        for e in evs:
            lines.append(
                f"{n.status}\t{n.name.qualname}\t{n.name.file}\t{e.test}\t{e.via}"
            )
    return "\n".join(lines) + "\n"


# --- self-test fixture -------------------------------------------------------


def _git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "veil@demo"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "veil"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "commit.gpgsign", "false"], check=True)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_ugly_fixture(root: Path) -> Path:
    """Python + JS + unicode/spaces + nested git. Returns repo path."""
    repo = root / "ugly"
    _git_init(repo)
    _write(
        repo / "shop.py",
        "def add(a, b):\n    return 0\n\n"
        "def checkout(cart):\n    return 0\n\n"
        "def retry_budget():\n    return 0\n\n"
        "RETRY = 1\n",
    )
    _write(
        repo / "src" / "loader.ts",
        "export function loadTemplate(name: string): string {\n  return 'old'\n}\n",
    )
    _write(repo / "README.md", "# shop\n")
    _write(repo / "vendor" / "nested" / "x.py", "def stolen():\n    return 1\n")
    subprocess.run(["git", "init", "-q", str(repo / "vendor" / "nested")], check=True)
    _write(repo / ".gitignore", "vendor/\n")
    subprocess.run(
        ["git", "-C", str(repo), "add", "shop.py", "src/loader.ts", "README.md", ".gitignore"],
        check=True,
    )
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "old production"], check=True)

    _write(
        repo / "shop.py",
        "def add(a, b):\n    return a + b\n\n"
        "def checkout(cart):\n    return charge(cart)\n\n"
        "def charge(cart):\n    return 42\n\n"
        "def retry_budget():\n    return 3\n\n"
        "RETRY = 3\n",
    )
    _write(
        repo / "src" / "loader.ts",
        "export function loadTemplate(name: string): string {\n  return 'new-' + name\n}\n"
        "export function parseFrontmatter(s: string): object { return {} }\n",
    )
    _write(
        repo / "src" / "composer.ts",
        "import { loadTemplate } from './loader.js'\n"
        "export function compose(name: string): string {\n"
        "  return loadTemplate(name)\n}\n",
    )
    _write(
        repo / "tests" / "test add.py",
        "from shop import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
    )
    _write(
        repo / "tests" / "test_checkout.py",
        "from unittest.mock import patch\n\n"
        "@patch('shop.checkout')\n"
        "def test_ok(m):\n"
        "    from shop import checkout\n"
        "    checkout({})\n"
        "    m.assert_called()\n",
    )
    _write(
        repo / "src" / "composer.test.ts",
        "import { describe, it, vi, expect } from 'vitest'\n"
        "vi.mock('./loader.js', () => ({ loadTemplate: () => 'fake' }))\n"
        "import { compose } from './composer.js'\n"
        "describe('compose', () => {\n"
        "  it('uses the mock', () => { expect(compose('x')).toBe('fake') })\n"
        "})\n",
    )
    _write(
        repo / "実験" / "notes.md",
        "retry_budget is definitely 3 now\n",
    )
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "new production + theater tests"],
        check=True,
    )
    return repo


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def run_selftest() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="veil-selftest-"))
    try:
        repo = build_ugly_fixture(tmp)
        # committed range: first commit is old, HEAD is new
        parent = git_text(repo, "rev-parse", "HEAD~1").strip()
        rep = analyze(repo, parent, "HEAD")
        by = {n.name.qualname: n for n in rep.names}
        _assert("add" in by, f"missing add in {list(by)}")
        _assert(by["add"].status == LIVE, f"add should be LIVE not {by['add'].status}")
        _assert("checkout" in by, "missing checkout")
        _assert(
            by["checkout"].status == VEIL,
            f"checkout should be VEIL not {by['checkout'].status} lives={by['checkout'].lives} veils={by['checkout'].veils}",
        )
        _assert("retry_budget" in by, "missing retry_budget")
        _assert(
            by["retry_budget"].status == BARE,
            f"retry_budget should be BARE not {by['retry_budget'].status}",
        )
        _assert("charge" in by, "missing new fn charge")
        _assert(by["charge"].status == BARE, f"charge should be BARE not {by['charge'].status}")
        _assert("loadTemplate" in by, f"missing loadTemplate in {list(by)}")
        _assert(
            by["loadTemplate"].status == VEIL,
            f"loadTemplate should be VEIL (composer.test mocks the module) not {by['loadTemplate'].status} {by['loadTemplate'].lives} {by['loadTemplate'].veils}",
        )
        _assert("parseFrontmatter" in by, "missing parseFrontmatter")
        _assert(
            by["parseFrontmatter"].status == VEIL,
            f"parseFrontmatter is in mocked loader module, want VEIL not {by['parseFrontmatter'].status}",
        )
        _assert("compose" in by, "compose is new")
        _assert(
            by["compose"].status == LIVE,
            f"compose imported live by composer.test.ts, want LIVE not {by['compose'].status}",
        )
        _assert(rep.status == OPEN, f"rollup want OPEN got {rep.status}")
        # markdown / nested git must not invent production names
        _assert(all("notes.md" not in n.name.file for n in rep.names), "markdown treated as prod")
        _assert(all("vendor/" not in n.name.file for n in rep.names), "nested git leaked")
        # worktree vs HEAD is CLEAN
        clean = analyze(repo, "HEAD", None)
        _assert(clean.status == CLEAN, f"clean tree want CLEAN got {clean.status}")
        # porcelain
        porc = fmt_porcelain(rep)
        _assert("VEIL\tcheckout\tshop.py" in porc, porc)
        _assert("BARE\tretry_budget\tshop.py" in porc, porc)
        _assert("LIVE\tadd\tshop.py" in porc, porc)
        print("selftest: ok")
    finally:
        shutil.rmtree(tmp, onerror=_chmod_and_retry)


def _chmod_and_retry(func, path, _exc):  # type: ignore[no-untyped-def]
    os.chmod(path, stat.S_IWRITE)
    func(path)


# --- CLI ---------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="veil",
        description="Classify a production diff by whether tests live-call, mock, or ignore each changed name.",
    )
    p.add_argument("-C", "--repo", default=".", help="repository path")
    p.add_argument(
        "--base",
        default="HEAD",
        help="old revision (default HEAD; worktree is new unless --to is set)",
    )
    p.add_argument("--from", dest="rev_from", default=None, help="old revision (alias of --base)")
    p.add_argument(
        "--to",
        dest="rev_to",
        default=None,
        help="new revision (default: worktree when omitted)",
    )
    p.add_argument("--json", action="store_true", help="JSON on stdout")
    p.add_argument("--porcelain", action="store_true", help="stable TSV")
    p.add_argument("--explain", action="store_true", help="print every live/veil witness")
    p.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any name is VEIL or BARE",
    )
    p.add_argument(
        "--all-names",
        action="store_true",
        help="include unexported BARE helpers (default hides them)",
    )
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--version", action="store_true")
    p.add_argument(
        "names",
        nargs="*",
        help="optional qualname filter (substring)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.version:
        print(VERSION)
        return 0
    if args.self_test:
        run_selftest()
        return 0
    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists() and not (repo / ".git").is_file():
        # allow worktrees / subdirs
        probe = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if probe.returncode != 0:
            die(f"not a git repo: {repo}")
        repo = Path(probe.stdout.decode().strip())
    base = args.rev_from or args.base
    head = args.rev_to
    try:
        rep = analyze(repo, base, head, all_names=args.all_names)
    except SystemExit:
        raise
    except Exception as e:
        die(str(e))
    if args.names:
        want = args.names
        rep.names = [
            n
            for n in rep.names
            if any(w in n.name.qualname or w in n.name.file for w in want)
        ]
        rep.status = rollup(rep.names)
    if args.json:
        sys.stdout.write(json.dumps(rep.as_dict(), indent=2, ensure_ascii=False) + "\n")
    elif args.porcelain:
        sys.stdout.write(fmt_porcelain(rep))
    else:
        sys.stdout.write(fmt_text(rep, args.explain))
    if args.check and rep.status not in {CLEAN, COVERED}:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
