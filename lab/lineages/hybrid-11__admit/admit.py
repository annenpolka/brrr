#!/usr/bin/env python3
"""admit — write the tests production inhabits, already visad.

hatch writes a test for each production argument world the suite never
passes. visa emits the skip/apply predicate an oracle implies. Concatenation
visas the production *file* (or the generated file) and wraps every test.

admit's object is one clearance: the visa implied by the world's argument
literals, fused to the assertion of that world. OPEN/SPEC worlds assert.
BOUND worlds assert and skip on machine mismatch. A macOS comment next to
isBrowser is not Brave's visa.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import hatchlib
import visalib

VERSION = "0.2.0"

# Textbook identities that are grammar, not a machine. alice stays a
# recording when she appears in a *production* world (snapshot treatment);
# /home/user and "John Doe" do not become a skip.
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


@dataclass
class Clearance:
    """A due production world fused to the visa its literals imply."""

    report: hatchlib.Report
    fixture: hatchlib.Fixture
    visa: visalib.Visa
    fate: str  # assert | skipif | skip
    match: str = ""
    misses: list[dict[str, str]] = field(default_factory=list)
    recovered: str = ""  # full production call at the site (not hatch's abridgement)

    @property
    def require(self) -> dict[str, str]:
        return {k: v for k, v in self.visa.require.items() if k in HARD_SKIP_AXES}


def eprint(*a: object) -> None:
    print(*a, file=sys.stderr)


def strip_canon(val: object) -> str:
    raw = str(val)
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def world_oracle_text(args: dict) -> str:
    """Oracle text of a production world: argument literals only.

    Not the production file. File-level Darwin comments / neighboring
    homes must not become this world's visa.
    """
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
    """True when every identifying axis is a classic example identity."""
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
    """Full call text at path:line, including multiline string literals.

    hatch canon_lit cuts at 45 chars and Call.raw at 120. sitbone's
    `tell application "Safari"` AppleScript is longer than both.
    """
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
    """Visa implied by a production world's literals.

    Production callers are recordings (snapshot path) so a real HOME leak
    stays BOUND. Textbook homes (/home/user, John Doe) demote to SPEC.
    Prefer the recovered site span when hatch abridged the value.
    """
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


def fate_of(fx: hatchlib.Fixture, visa: visalib.Visa) -> str:
    if hatchlib.fixture_dyn_names(fx.args):
        return "skip"
    if visa.status == "UNSAT":
        return "skip"
    if visa.status == "BOUND":
        return "skipif"
    return "assert"


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
    """Prefer the recovered production span over hatch's abridged args."""
    if c.recovered and c.fixture.kind != "member":
        return qualify_call(c.report.fn, c.recovered)
    return hatchlib._emit_call(c.report.fn, c.fixture.args)


def drop_member_world_dupes(cs: list[Clearance]) -> list[Clearance]:
    """Production `isBrowser("Brave Browser")` is already the Brave member."""
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


def clear(
    reports: list[hatchlib.Report],
    due_only: bool = True,
    root: Path | None = None,
) -> list[Clearance]:
    out: list[Clearance] = []
    for r, f in hatchlib.iter_fixtures(reports, due_only):
        recovered = ""
        if f.kind != "member":
            for site in f.sites:
                recovered = recover_call(root, site)
                if recovered:
                    break
        v = visa_of_world(f.args, recovered=recovered if args_truncated(f.args) else "")
        live = visalib.match_visa(v)
        out.append(
            Clearance(
                report=r,
                fixture=f,
                visa=v,
                fate=fate_of(f, v),
                match=live.match,
                misses=list(live.misses),
                recovered=recovered,
            )
        )
    return drop_member_world_dupes(out)


def generable(cs: list[Clearance]) -> list[Clearance]:
    return [c for c in cs if c.fixture.generable]


def require_repr(require: dict[str, str]) -> str:
    return "{" + ", ".join(f"{k!r}: {v!r}" for k, v in require.items()) + "}"


def wrap_oracle(call: str, dialect: str, c: Clearance) -> str:
    """BOUND worlds are oracles (assert). Members stay assert. Else a call."""
    assert_it = (
        c.fixture.kind == "member"
        or c.fate == "skipif"
        or c.visa.status == "BOUND"
    )
    if not assert_it:
        return call
    if dialect == "xctest":
        return f"XCTAssertTrue({call})"
    return f"assert {call}"


def py_imports(cs: list[Clearance]) -> list[str]:
    seen: set[tuple[str, str]] = set()
    lines: list[str] = []
    for c in cs:
        fn = c.report.fn
        if fn.lang != "py":
            continue
        path = fn.path.replace("\\", "/")
        if not path.endswith(".py"):
            continue
        if any(ch in path for ch in (":", " ", "\t")):
            continue
        mod = path[:-3].replace("/", ".")
        name = fn.recv or fn.name
        key = (mod, name)
        if key in seen:
            continue
        if not name.isidentifier() or not all(p.isidentifier() for p in mod.split(".")):
            continue
        seen.add(key)
        lines.append(f"from {mod} import {name}")
    return lines


def render_pytest(cs: list[Clearance], langs: set[str] | None = None) -> str:
    items = []
    omitted = 0
    for c in generable(cs):
        if langs is not None and c.report.fn.lang not in langs:
            omitted += 1
            continue
        items.append(c)
    lines = [
        "# generated by admit — production worlds; skip unless the visa holds",
        "from __future__ import annotations",
        "import pytest",
    ]
    if any(c.fate == "skipif" for c in items):
        lines += [
            "import getpass",
            "import os",
            "import pathlib",
            "import sys",
            "",
            "def _admit_misses(require):",
            "    plat = 'Linux' if sys.platform.startswith('linux') else {",
            "        'darwin': 'Darwin', 'win32': 'Windows',",
            "    }.get(sys.platform, sys.platform)",
            "    live = {",
            "        'platform': plat,",
            "        'HOME': pathlib.Path.home().as_posix(),",
            "        'USER': getpass.getuser(),",
            "    }",
            "    if os.environ.get('GITHUB_ACTIONS'):",
            "        live['CI'] = 'github-actions'",
            "    misses = []",
            "    for axis, want in require.items():",
            "        have = live.get(axis, '')",
            "        if axis == 'HOME':",
            "            if have.rstrip('/') != str(want).rstrip('/'):",
            "                misses.append(f'{axis} want={want} have={have or \"(unset)\"}')",
            "        elif have != want:",
            "            misses.append(f'{axis} want={want} have={have or \"(unset)\"}')",
            "    return misses",
        ]
    imps = py_imports(items)
    if imps:
        lines.append("")
        lines.extend(imps)
    lines.append("")
    n = 0
    seen: set[str] = set()
    for c in items:
        f = c.fixture
        r = c.report
        name = hatchlib._unique_name(f.suggest, seen)
        call = emit_call(c)
        lines.append(f"def {name}():")
        lines.append(f"    # {r.fn.path}:{r.fn.line}  {f.kind}  {f.label}")
        lines.append(f"    # visa {c.visa.status}  fate={c.fate}")
        if c.require:
            bits = " ".join(f"{k}={v}" for k, v in c.require.items())
            lines.append(f"    # require {bits}")
        if f.collection:
            lines.append(f"    # member of {f.collection}")
        if f.sites:
            lines.append(f"    # production: {', '.join(f.sites[:3])}")
        if c.fate == "skip":
            if c.visa.status == "UNSAT":
                lines.append("    pytest.skip('visa UNSAT — contradictory machine')")
            else:
                lines.append(f"    pytest.skip({hatchlib.skip_reason(f.args)!r})")
        elif c.fate == "skipif":
            lines.append(f"    _m = _admit_misses({require_repr(c.require)})")
            lines.append("    if _m:")
            lines.append("        pytest.skip('visa MISS ' + '; '.join(_m))")
            lines.append(f"    {wrap_oracle(call, 'pytest', c)}")
        else:
            lines.append(f"    {wrap_oracle(call, 'pytest', c)}")
        lines.append("")
        n += 1
    if n == 0:
        lines.append("# no generable due fixtures")
        lines.append("")
    if omitted:
        eprint(f"admit: omitted {omitted} fixture(s) from other languages")
    return "\n".join(lines)


def swift_require_literal(require: dict[str, str]) -> str:
    parts = [f'"{k}": "{v.replace(chr(92), chr(92)*2).replace(chr(34), chr(92)+chr(34))}"' for k, v in require.items()]
    return "[" + ", ".join(parts) + "]"


def render_xctest(cs: list[Clearance]) -> str:
    groups: dict[str, list[Clearance]] = {}
    modules: list[str] = []
    seen_mod: set[str] = set()
    omitted = 0
    items: list[Clearance] = []
    for c in generable(cs):
        if c.report.fn.lang != "swift":
            omitted += 1
            continue
        items.append(c)
        cls = hatchlib.xctest_class_name(c.report.fn).replace("HatchTests", "AdmitTests")
        groups.setdefault(cls, []).append(c)
        mod = hatchlib.infer_swift_module(c.report.fn.path)
        if mod and mod not in seen_mod:
            seen_mod.add(mod)
            modules.append(mod)
    lines = [
        "// generated by admit — production worlds; skip unless the visa holds",
        "import XCTest",
    ]
    for mod in modules:
        lines.append(f"@testable import {mod}")
    if not modules:
        lines.append("import Foundation")
    lines.append("")
    if any(c.fate == "skipif" for c in items):
        lines += [
            "private func admitMisses(_ require: [String: String]) -> [String] {",
            "    var misses: [String] = []",
            "    let home = FileManager.default.homeDirectoryForCurrentUser.path",
            "#if os(macOS)",
            '    let plat = "Darwin"',
            "#elseif os(Linux)",
            '    let plat = "Linux"',
            "#else",
            '    let plat = "other"',
            "#endif",
            '    if let want = require["platform"], want != plat {',
            '        misses.append("platform want=\\(want) have=\\(plat)")',
            "    }",
            '    if let want = require["HOME"] {',
            '        let a = home.trimmingCharacters(in: CharacterSet(charactersIn: "/"))',
            '        let b = want.trimmingCharacters(in: CharacterSet(charactersIn: "/"))',
            "        if a != b {",
            '            misses.append("HOME want=\\(want) have=\\(home)")',
            "        }",
            "    }",
            '    if let want = require["USER"] {',
            "        let user = NSUserName()",
            "        if user != want {",
            '            misses.append("USER want=\\(want) have=\\(user)")',
            "        }",
            "    }",
            "    return misses",
            "}",
            "",
        ]
    if not groups:
        lines.append("// no generable due Swift fixtures")
        lines.append("")
        if omitted:
            eprint(f"admit: omitted {omitted} non-Swift fixture(s) (use --emit pytest)")
        return "\n".join(lines)
    seen: set[str] = set()
    for cls, group in groups.items():
        lines.append(f"final class {cls}: XCTestCase {{")
        for c in group:
            f = c.fixture
            r = c.report
            name = hatchlib._unique_name(hatchlib.swift_func_name(f.suggest), seen)
            call = emit_call(c)
            needs_throws = c.fate in {"skip", "skipif"}
            sig = "() throws" if needs_throws else "()"
            lines.append(f"    func {name}{sig} {{")
            lines.append(f"        // {r.fn.path}:{r.fn.line}  {f.kind}  {f.label}")
            lines.append(f"        // visa {c.visa.status}  fate={c.fate}")
            if c.require:
                bits = " ".join(f"{k}={v}" for k, v in c.require.items())
                lines.append(f"        // require {bits}")
            if f.collection:
                lines.append(f"        // member of {f.collection}")
            if f.sites:
                lines.append(f"        // production: {', '.join(f.sites[:3])}")
            if c.fate == "skip":
                if c.visa.status == "UNSAT":
                    lines.append('        throw XCTSkip("visa UNSAT — contradictory machine")')
                else:
                    reason = hatchlib.skip_reason(f.args).replace("\\", "\\\\").replace('"', '\\"')
                    lines.append(f'        throw XCTSkip("{reason}")')
            elif c.fate == "skipif":
                lines.append(f"        let _m = admitMisses({swift_require_literal(c.require)})")
                lines.append("        if !_m.isEmpty {")
                lines.append('            throw XCTSkip("visa MISS \\(_m.joined(separator: \"; \"))")')
                lines.append("        }")
                lines.append(f"        {wrap_oracle(call, 'xctest', c)}")
            else:
                lines.append(f"        {wrap_oracle(call, 'xctest', c)}")
            lines.append("    }")
            lines.append("")
        if lines[-1] == "":
            lines.pop()
        lines.append("}")
        lines.append("")
    if omitted:
        eprint(f"admit: omitted {omitted} non-Swift fixture(s) (use --emit pytest)")
    return "\n".join(lines)


def choose_dialect(cs: list[Clearance], emit: Optional[str]) -> str:
    if emit in ("pytest", "xctest"):
        return emit
    n_swift = n_other = 0
    for c in generable(cs):
        if c.report.fn.lang == "swift":
            n_swift += 1
        else:
            n_other += 1
    return "xctest" if n_swift > n_other else "pytest"


def render_tests(cs: list[Clearance], emit: Optional[str] = None) -> str:
    dialect = choose_dialect(cs, emit)
    if dialect == "xctest":
        return render_xctest(cs)
    langs = None if emit == "pytest" else {"py", "js", "rs", "go"}
    if emit == "pytest":
        langs = None
    return render_pytest(cs, langs=langs)


def clearance_record(c: Clearance) -> dict:
    rec = hatchlib.fixture_record(c.report, c.fixture)
    rec.update(
        {
            "fate": c.fate,
            "visa": {
                "status": c.visa.status,
                "require": c.require,
                "soft": c.visa.soft,
                "match": c.match,
                "misses": c.misses,
            },
        }
    )
    return rec


def render_json(cs: list[Clearance]) -> str:
    return (
        json.dumps(
            {
                "tool": "admit",
                "version": VERSION,
                "clearances": [clearance_record(c) for c in cs],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )


def render_porcelain(cs: list[Clearance]) -> str:
    lines = []
    for c in cs:
        req = ",".join(f"{k}={v}" for k, v in c.require.items())
        lines.append(
            "\t".join(
                [
                    "admit",
                    c.report.fn.qualname,
                    c.fixture.kind,
                    c.fixture.label,
                    c.fate,
                    c.visa.status,
                    req,
                    c.fixture.suggest,
                    f"{c.report.fn.path}:{c.report.fn.line}",
                ]
            )
        )
    return "\n".join(lines) + ("\n" if lines else "")


def render_report(cs: list[Clearance], color: bool) -> str:
    lines: list[str] = []
    by_fn: dict[str, list[Clearance]] = {}
    order: list[str] = []
    for c in cs:
        key = f"{c.report.fn.qualname}\t{c.report.fn.path}:{c.report.fn.line}"
        if key not in by_fn:
            by_fn[key] = []
            order.append(key)
        by_fn[key].append(c)
    for key in order:
        group = by_fn[key]
        fn = group[0].report.fn
        params = ", ".join(p.name for p in fn.params)
        ndue = len(group)
        nskipif = sum(1 for c in group if c.fate == "skipif")
        head = f"{fn.qualname}  {fn.path}:{fn.line}  ({params})  {ndue} due"
        if nskipif:
            head += f"  {nskipif} skipif"
        lines.append(head)
        for c in group:
            req = " ".join(f"{k}={v}" for k, v in c.require.items())
            extra = f"  {req}" if req else ""
            lines.append(
                f"  {c.fate:6s}  {c.visa.status:5s}  {c.fixture.kind:6s}  {c.fixture.label}{extra}"
            )
            lines.append(f"         {c.fixture.suggest}")
        lines.append("")
    if not lines:
        lines.append("no due fixtures")
    return "\n".join(lines).rstrip() + "\n"


def census(cs: list[Clearance], reports: list[hatchlib.Report]) -> str:
    n_due = len(cs)
    n_fn = len({(c.report.fn.path, c.report.fn.line, c.report.fn.name) for c in cs})
    n_assert = sum(1 for c in cs if c.fate == "assert")
    n_skipif = sum(1 for c in cs if c.fate == "skipif")
    n_skip = sum(1 for c in cs if c.fate == "skip")
    n_bound = sum(1 for c in cs if c.visa.status == "BOUND")
    n_open = sum(1 for c in cs if c.visa.status == "OPEN")
    n_spec = sum(1 for c in cs if c.visa.status == "SPEC")
    n_prod = sum(1 for r in reports if any(not c.is_test for c in r.calls))
    return (
        f"admit  prod_fns={n_prod}  due_fns={n_fn}  due={n_due}  "
        f"assert={n_assert}  skipif={n_skipif}  skip={n_skip}  "
        f"bound={n_bound}  open={n_open}  spec={n_spec}\n"
    )


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------


def self_test() -> int:
    failures: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        if cond:
            print(f"  ok  {msg}")
        else:
            failures.append(msg)
            print(f"  FAIL  {msg}", file=sys.stderr)

    tmp = Path(tempfile.mkdtemp(prefix="admit-self-"))
    src = tmp / "src"
    tests = tmp / "tests"
    src.mkdir()
    tests.mkdir()

    (src / "profile.py").write_text(
        "import os\n"
        "def load_profile(home):\n"
        "    return os.path.isdir(home)\n"
        "def start():\n"
        "    load_profile('/Users/alice')\n",
        encoding="utf-8",
    )
    (tests / "test_profile.py").write_text(
        "from src.profile import load_profile\n"
        "def test_tmp():\n"
        "    load_profile('/tmp')\n",
        encoding="utf-8",
    )
    (src / "quote.py").write_text(
        "def quote(path):\n"
        "    return path\n"
        "def examples():\n"
        "    quote('/home/user/project')\n"
        "    quote('/Users/John Doe/kizu')\n",
        encoding="utf-8",
    )
    (tests / "test_quote.py").write_text(
        "from src.quote import quote\n"
        "def test_rel():\n"
        "    quote('rel/path')\n",
        encoding="utf-8",
    )
    (src / "titles.py").write_text(
        "def extract_title(title):\n"
        "    return title.split(' - ', 1)[0]\n"
        "def crawl():\n"
        "    extract_title('GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome')\n",
        encoding="utf-8",
    )
    (tests / "test_titles.py").write_text(
        "from src.titles import extract_title\n"
        "def test_docs():\n"
        "    extract_title('docs.rs - rand - Rust - Firefox')\n",
        encoding="utf-8",
    )
    (src / "connect.py").write_text(
        "def connect(host, timeout=30):\n"
        "    return f'{host}:{timeout}'\n"
        "def run(argv):\n"
        "    connect(argv[1], timeout=0)\n"
        "    connect('db.example.com')\n",
        encoding="utf-8",
    )
    (tests / "test_connect.py").write_text(
        "from src.connect import connect\n"
        "def test_local():\n"
        "    connect('localhost', timeout=30)\n",
        encoding="utf-8",
    )
    (src / "App.swift").write_text(
        "// when the macOS PollWatcher fallback is active.\n"
        "public enum WindowTitleParser {\n"
        '    private static let browsers: Set<String> = ["Chrome", "Safari", "Brave Browser", "Microsoft Edge"]\n'
        "    public static func isBrowser(_ appName: String) -> Bool {\n"
        "        browsers.contains(appName)\n"
        "    }\n"
        "}\n"
        "public func loadHome(_ path: String) -> Bool { true }\n"
        "public func boot() {\n"
        '    _ = loadHome("/Users/alice/Library/sitbone")\n'
        '    _ = WindowTitleParser.isBrowser("Brave Browser")\n'
        "}\n"
        "public func tick(app: String) {\n"
        "    _ = WindowTitleParser.isBrowser(app)\n"
        "}\n",
        encoding="utf-8",
    )
    (tests / "ParserTests.swift").write_text(
        "func testChrome() {\n"
        '    _ = WindowTitleParser.isBrowser("Chrome")\n'
        '    _ = WindowTitleParser.isBrowser("Safari")\n'
        "}\n",
        encoding="utf-8",
    )

    defs, calls, reports = hatchlib.analyze(tmp)
    by = {r.fn.name: r for r in reports}

    ok("load_profile" in by, "found load_profile")
    ok("isBrowser" in by, "found isBrowser")
    ok("quote" in by, "found quote")
    ok("extract_title" in by, "found extract_title")
    ok("connect" in by, "found connect")
    ok("loadHome" in by, "found loadHome")

    cs = clear(reports, due_only=True, root=tmp)
    fate_by: dict[str, list[Clearance]] = {}
    for c in cs:
        fate_by.setdefault(c.report.fn.name, []).append(c)

    # Alice's home is a production recording → skipif, not a bare assert.
    lp = fate_by.get("load_profile", [])
    ok(any(c.fate == "skipif" and c.visa.status == "BOUND" for c in lp), f"load_profile skipif BOUND {[(c.fate, c.visa.status, c.fixture.label) for c in lp]}")
    ok(
        any(c.require.get("HOME") == "/Users/alice" for c in lp),
        f"load_profile requires Alice HOME {[c.require for c in lp]}",
    )
    ok(
        any(c.require.get("platform") == "Darwin" for c in lp),
        f"load_profile requires Darwin {[c.require for c in lp]}",
    )

    # Textbook quoting paths are SPEC, not a Darwin/Linux skip.
    qq = fate_by.get("quote", [])
    ok(qq, f"quote has dues {qq}")
    ok(
        all(c.fate == "assert" and c.visa.status in {"SPEC", "OPEN"} for c in qq),
        f"quote textbook is assert/SPEC {[ (c.fate, c.visa.status, c.fixture.label) for c in qq ]}",
    )
    ok(
        all("HOME" not in c.require for c in qq),
        f"quote must not require HOME {[c.require for c in qq]}",
    )

    # GitHub title is not USER=annenpolka.
    tt = fate_by.get("extract_title", [])
    ok(tt, "extract_title due")
    ok(
        all(c.fate == "assert" and c.visa.status in {"OPEN", "FIXTURE", "SPEC"} for c in tt),
        f"github title not BOUND {[ (c.fate, c.visa.status, c.require) for c in tt ]}",
    )
    ok(
        all("USER" not in c.require for c in tt),
        f"github title must not visa USER {[c.require for c in tt]}",
    )

    # Brave is OPEN — file-level macOS comment is not this world's visa.
    br = [c for c in fate_by.get("isBrowser", []) if "Brave" in c.fixture.label]
    ok(br, f"Brave due {[(c.fixture.label, c.fate) for c in fate_by.get('isBrowser', [])]}")
    ok(
        all(c.fate == "assert" and c.visa.status == "OPEN" for c in br),
        f"Brave OPEN assert (file macOS is not the world) {[(c.fate, c.visa.status) for c in br]}",
    )

    # loadHome Alice path is skipif even though it shares App.swift with isBrowser.
    lh = fate_by.get("loadHome", [])
    ok(
        any(c.fate == "skipif" and c.require.get("HOME") == "/Users/alice" for c in lh),
        f"loadHome skipif Alice {[(c.fate, c.require, c.fixture.label) for c in lh]}",
    )

    # dyn timeout stays skip (not a visa miss).
    cn = fate_by.get("connect", [])
    ok(
        any(c.fate == "skip" and "timeout=0" in c.fixture.label for c in cn),
        f"timeout=0 dyn skip {[ (c.fate, c.fixture.label) for c in cn ]}",
    )
    ok(
        any(c.fate == "assert" and "db.example.com" in c.fixture.label for c in cn),
        f"db.example.com OPEN assert {[ (c.fate, c.fixture.label) for c in cn ]}",
    )

    # Anti-concat: visa of App.swift (the file) is not Brave's visa.
    app_text = (src / "App.swift").read_text(encoding="utf-8")
    file_visa = visalib.infer(app_text, str(src / "App.swift"))
    # source + macOS word is payload; /Users/alice in the same file is a recording.
    # File-level visa may be BOUND. Brave world must stay OPEN.
    ok(
        all(c.visa.status == "OPEN" for c in br),
        "Brave world visa is not the file visa",
    )

    # Emit: Brave XCTest has no XCTSkip; loadHome has skip + assert.
    swift_cs = [c for c in cs if c.report.fn.name in {"isBrowser", "loadHome"}]
    xct = render_tests(swift_cs, emit="xctest")
    ok("import XCTest" in xct, "xctest import")
    ok("AdmitTests" in xct, f"AdmitTests class {xct[:200]}")
    ok("HatchTests" not in xct, "must not speak hatch class names")
    ok("Brave Browser" in xct, "Brave pinned")
    ok("XCTAssertTrue" in xct and 'isBrowser("Brave Browser")' in xct, "member oracle")
    # Brave test body must not XCTSkip
    brave_fn = xct.split("BraveBrowser")[-1].split("func ")[0] if "BraveBrowser" in xct else ""
    ok("XCTSkip" not in brave_fn or "loadHome" in brave_fn, f"Brave test must not skip {brave_fn[:300]}")
    ok("admitMisses" in xct, "skipif helper present because loadHome is BOUND")
    ok("/Users/alice/Library/sitbone" in xct, "loadHome pins Alice path")
    ok("visa MISS" in xct, "loadHome skip reason")
    ok("XCTAssertTrue(loadHome(" in xct or "XCTAssertTrue(loadHome" in xct, f"BOUND world asserts {xct}")

    py_cs = [c for c in cs if c.report.fn.name == "load_profile"]
    pyt = render_tests(py_cs, emit="pytest")
    ok("from src.profile import load_profile" in pyt, f"subject import {pyt[:300]}")
    ok("_admit_misses" in pyt, "pytest visa helper")
    ok("pytest.skip('visa MISS" in pyt or 'pytest.skip("visa MISS' in pyt or "visa MISS" in pyt, f"skip polarity {pyt}")
    ok("assert load_profile(" in pyt, f"BOUND world asserts {pyt}")
    ok("/Users/alice" in pyt, "alice path pinned")

    # This host is not alice → match MISS.
    ok(any(c.match == "MISS" for c in lp), f"alice MISS on this host {[c.match for c in lp]}")

    quote_py = render_tests(fate_by.get("quote", []), emit="pytest")
    ok("_admit_misses" not in quote_py, "SPEC quote must not emit a skip helper")
    ok("pytest.skip" not in quote_py, f"SPEC quote must not skip {quote_py}")

    title_py = render_tests(fate_by.get("extract_title", []), emit="pytest")
    ok("annenpolka" not in title_py.split("skip")[0] or "pytest.skip" not in title_py, "title is not a skip")
    ok("pytest.skip" not in title_py, f"github title must not skip {title_py}")
    ok("Pull Request #3" in title_py, f"recovered full GitHub title {title_py}")
    call_side = title_py.split("extract_title(")[-1] if "extract_title(" in title_py else ""
    ok("Pull Reque..." not in call_side, f"call is not hatch abridgement {call_side}")

    # Production isBrowser("Brave Browser") is the member, not a second world.
    brave_worlds = [c for c in fate_by.get("isBrowser", []) if c.fixture.kind == "world"]
    ok(not brave_worlds, f"member+world dupe dropped {[(c.fixture.kind, c.fixture.label) for c in fate_by.get('isBrowser', [])]}")

    porc = render_porcelain(cs)
    ok(porc.startswith("admit\t") or "\nadmit\t" in "\n" + porc, "porcelain tag")
    ok("skipif" in porc and "BOUND" in porc, f"porcelain skipif BOUND {porc[:400]}")
    ok("load_profile" in porc, "porcelain load_profile")

    blob = render_json(cs)
    ok('"tool": "admit"' in blob, "json names admit")
    ok('"fate"' in blob and '"visa"' in blob, "json is clearances, not hatch fixtures")
    ok("hatch" not in blob.lower() or '"tool": "hatch"' not in blob, "json must not claim hatch")

    # world_oracle_text ignores file comments
    v_brave = visa_of_world({"appName": {"kind": "lit", "value": '"Brave Browser"'}})
    ok(v_brave.status == "OPEN", f"Brave literals OPEN {v_brave.status} {v_brave.require}")
    v_alice = visa_of_world({"home": {"kind": "lit", "value": '"/Users/alice"'}})
    ok(
        v_alice.status == "BOUND" and v_alice.require.get("HOME") == "/Users/alice",
        f"alice literals BOUND {v_alice.status} {v_alice.require}",
    )
    v_user = visa_of_world({"path": {"kind": "lit", "value": '"/home/user/project"'}})
    ok(v_user.status == "SPEC", f"textbook /home/user SPEC {v_user.status} {v_user.require}")

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
        prog="admit",
        description=(
            "Write the tests production already inhabits, already visad. "
            "Each due world asserts on the machine it implies and skips on mismatch. "
            "Default stdout is a runnable pytest module or XCTestCase."
        ),
    )
    p.add_argument("names", nargs="*", help="function names (default: those with due fixtures)")
    p.add_argument("-C", "--root", default=".", help="repository / tree root")
    p.add_argument("--report", "--human", action="store_true", help="human clearance listing (opt-in)")
    p.add_argument("--json", action="store_true", help="JSON clearances")
    p.add_argument("--porcelain", action="store_true", help="stable admit\\tfn\\tkind\\tlabel\\tfate\\tvisa lines")
    p.add_argument(
        "--emit",
        choices=["auto", "pytest", "xctest"],
        default="auto",
        help="test dialect (default auto: XCTest if most dues are Swift, else pytest)",
    )
    p.add_argument("--all", action="store_true", help="include already-witnessed (have) fixtures")
    p.add_argument("--check", action="store_true", help="exit 1 if any due fixture (stdout still the tests)")
    p.add_argument(
        "--bound",
        action="store_true",
        help="only BOUND/skipif clearances (machine-tied debt)",
    )
    p.add_argument("--min-callers", type=int, default=1, help="minimum production call sites (default 1)")
    p.add_argument("--test-defs", action="store_true", help="include functions defined in tests as subjects")
    p.add_argument("--exclude", action="append", default=[], help="substring of relative path to skip")
    p.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--summary", action="store_true", help="one-line census")
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
        eprint(f"admit: no such path: {root}")
        return 2
    defs, calls, reports = hatchlib.analyze(root, args.exclude, include_test_defs=args.test_defs)
    due_only = not args.all
    filtered = hatchlib.filter_reports(reports, args.names, args.min_callers, due_only=False)
    if args.names:
        view = filtered
    elif args.all:
        view = filtered
    else:
        view = [r for r in filtered if r.due]
    cs = clear(view, due_only=due_only, root=root)
    if args.bound:
        cs = [c for c in cs if c.fate == "skipif" or c.visa.status == "BOUND"]

    if args.summary:
        sys.stdout.write(census(cs, reports if not args.names else view))
        if args.check and any(c.fixture.status == "due" for c in cs):
            return 1
        return 0
    if args.json:
        sys.stdout.write(render_json(cs))
    elif args.porcelain:
        sys.stdout.write(render_porcelain(cs))
    elif args.report:
        color = hatchlib.use_color(args.color)
        sys.stdout.write(render_report(cs, color))
    else:
        emit = None if args.emit == "auto" else args.emit
        sys.stdout.write(render_tests(cs, emit=emit))

    if args.check and any(
        c.fixture.status == "due"
        for c in (clear(view, due_only=True, root=root) if not args.bound else cs)
    ):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
