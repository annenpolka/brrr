#!/usr/bin/env python3
"""leftover same-name helper vs moved definition; import path selects the body."""

from __future__ import annotations

import ast
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bindname"

UTIL_LEGACY = "def parse(x):\n    return ('legacy', x)\n"
PARSE_MOVED = "def parse(x):\n    return ('moved', x.strip())\n"
AST_LEFTOVER = "def parse(x):\n    return ('leftover-ast', x)\n"
TEST_STALE = (
    "import pkg_util, pkg_parse\n"
    'a = pkg_util.parse("  z  ")\n'
    'b = pkg_parse.parse("  z  ")\n'
    'print("util", a)\n'
    'print("parse", b)\n'
    'print("same_function", pkg_util.parse is pkg_parse.parse)\n'
    'print("stale_test_would_see", a[0])\n'
)


def load_mod():
    loader = importlib.machinery.SourceFileLoader("bindname_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


BN = load_mod()


def parse_output(text: str) -> list[dict]:
    records: list[dict] = []
    current: dict = {}
    for line in text.splitlines():
        if not line.strip():
            if current:
                records.append(current)
                current = {}
            continue
        key, _, value = line.partition("\t")
        if key == "also":
            current.setdefault("also", []).append(value)
        elif key == "miss":
            current.setdefault("miss", []).append(value)
        else:
            current[key] = value
    if current:
        records.append(current)
    return records


def source_text(repr_value: str) -> str:
    return ast.literal_eval(repr_value)


def run_cli(args, *, cwd=None):
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return proc


def write_fixture(tmp: str, files: dict[str, str]) -> Path:
    root = Path(tmp)
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def find_run_specimen(name: str) -> Path | None:
    marker = {
        "specimen-013": "files/pkg_util.py",
        "specimen-010": "files/loader.py",
    }.get(name, "files")
    env = os.environ.get("SPECIMEN")
    if env and name == "specimen-013":
        cand = Path(env)
        if (cand / "files" / "pkg_util.py").is_file():
            return cand
    starts = [ROOT, Path.cwd(), Path(__file__).resolve()]
    seen: set[Path] = set()
    for start in starts:
        proc = subprocess.run(
            ["git", "-C", str(start if start.is_dir() else start.parent), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            top = Path(proc.stdout.strip())
            if top not in seen:
                seen.add(top)
                cand = top / "lab-runs/specimen-hdd-20260902-1112/specimens" / name
                if (cand / marker).is_file() if "/" in marker else cand.is_dir():
                    return cand
        proc = subprocess.run(
            ["git", "-C", str(start if start.is_dir() else start.parent), "rev-parse", "--git-common-dir"],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            common = Path(proc.stdout.strip())
            if not common.is_absolute():
                base = start if start.is_dir() else start.parent
                common = (base / common).resolve()
            parent = common.parent if common.name == ".git" else common.parent
            if parent not in seen:
                seen.add(parent)
                cand = parent / "lab-runs/specimen-hdd-20260902-1112/specimens" / name
                if (cand / marker).is_file() if "/" in marker else cand.is_dir():
                    return cand
    return None


def find_specimen() -> Path | None:
    return find_run_specimen("specimen-013")


class LeftoverVsMovedTests(unittest.TestCase):
    def test_two_defs_are_not_the_same_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED},
            )
            bindings = BN.bindings_for_name(root, "parse")
            self.assertEqual(len(bindings), 2)
            self.assertFalse(BN.same_function(bindings))
            by_bind = {b.bind: b for b in bindings}
            self.assertIn("legacy", by_bind["pkg_util.parse"].source)
            self.assertIn("moved", by_bind["pkg_parse.parse"].source)
            self.assertEqual(by_bind["pkg_util.parse"].kind, "def")
            self.assertEqual(by_bind["pkg_parse.parse"].kind, "def")
            self.assertEqual(by_bind["pkg_util.parse"].runs, "pkg_util.parse")
            self.assertEqual(by_bind["pkg_parse.parse"].runs, "pkg_parse.parse")

    def test_stale_from_util_binds_leftover_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED},
            )
            binding, bindings = BN.binding_from_import(root, "pkg_util", "parse")
            self.assertIsNotNone(binding)
            assert binding is not None
            others = BN.other_defs(binding, bindings)
            self.assertEqual(binding.kind, "def")
            self.assertEqual(binding.runs, "pkg_util.parse")
            self.assertIn("legacy", binding.source)
            self.assertNotIn("strip", binding.source)
            self.assertEqual([o.runs for o in others], ["pkg_parse.parse"])

    def test_from_parse_binds_moved_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED},
            )
            binding, bindings = BN.binding_from_import(root, "pkg_parse", "parse")
            self.assertIsNotNone(binding)
            assert binding is not None
            others = BN.other_defs(binding, bindings)
            self.assertEqual(binding.runs, "pkg_parse.parse")
            self.assertIn("strip", binding.source)
            self.assertEqual([o.runs for o in others], ["pkg_util.parse"])

    def test_cli_from_util_reports_other_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED},
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["query"], "from pkg_util import parse")
            self.assertEqual(row["bind"], "pkg_util.parse")
            self.assertEqual(row["runs"], "pkg_util.parse")
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["same_function"], "False")
            self.assertEqual(row.get("also"), ["pkg_parse.parse"])
            self.assertIn("legacy", source_text(row["source"]))


class LeftoverAstShadowTests(unittest.TestCase):
    def test_cli_from_leftover_ast_binds_helper_not_stdlib(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from ast import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('leftover-ast', 'z')")

            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["query"], "from ast import parse")
            self.assertEqual(row["bind"], "ast.parse")
            self.assertEqual(row["runs"], "ast.parse")
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["file"], "ast.py")
            self.assertEqual(row["same_function"], "False")
            self.assertEqual(row.get("also"), ["pkg_parse.parse"])
            src = source_text(row["source"])
            self.assertIn("leftover-ast", src)
            self.assertNotIn("filename", src)
            self.assertNotIn("lib/python", row["file"])
            self.assertNotIn("Cellar", row["file"])

    def test_leftover_ast_binding_is_local_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED}
            )
            binding, bindings = BN.binding_from_import(root, "ast", "parse")
            self.assertIsNotNone(binding)
            assert binding is not None
            others = BN.other_defs(binding, bindings)
            self.assertEqual(binding.kind, "def")
            self.assertEqual(binding.runs, "ast.parse")
            self.assertEqual(binding.file, "ast.py")
            self.assertIn("leftover-ast", binding.source)
            self.assertNotIn("Cellar", binding.file)
            self.assertNotIn("lib/python", binding.file)
            self.assertEqual([o.runs for o in others], ["pkg_parse.parse"])


class ReexportTests(unittest.TestCase):
    def test_reexport_runs_moved_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "pkg_util.py": "from pkg_parse import parse\n",
                },
            )
            binding, bindings = BN.binding_from_import(root, "pkg_util", "parse")
            self.assertIsNotNone(binding)
            assert binding is not None
            self.assertEqual(binding.kind, "reexport")
            self.assertEqual(binding.bind, "pkg_util.parse")
            self.assertEqual(binding.runs, "pkg_parse.parse")
            self.assertIn("moved", binding.source)
            others = BN.other_defs(binding, bindings)
            self.assertEqual(others, [])
            self.assertTrue(BN.same_function(bindings))

    def test_cli_reexport_same_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "pkg_util.py": "from pkg_parse import parse\n",
                },
            )
            proc = run_cli(["-C", tmp, "--import", "from pkg_util import parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "reexport")
            self.assertEqual(row["runs"], "pkg_parse.parse")
            self.assertEqual(row["same_function"], "True")
            self.assertNotIn("also", row)


class ImporterFileTests(unittest.TestCase):
    def test_file_attr_uses_bind_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                    "test_parse_identity.py": TEST_STALE,
                },
            )
            bindings = BN.bindings_from_file(root, root / "test_parse_identity.py", "parse")
            self.assertEqual([b.bind for b in bindings], ["pkg_util.parse", "pkg_parse.parse"])
            self.assertFalse(BN.same_function(bindings))

    def test_cli_file_on_stale_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                    "test_parse_identity.py": TEST_STALE,
                },
            )
            proc = run_cli(["-C", tmp, "--file", str(Path(tmp) / "test_parse_identity.py"), "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "2")
            self.assertEqual(rows[0]["same_function"], "False")
            binds = [r["bind"] for r in rows[1:]]
            self.assertEqual(binds, ["pkg_util.parse", "pkg_parse.parse"])


class DottedAndImportStmtTests(unittest.TestCase):
    def test_dotted_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED},
            )
            proc = run_cli(["-C", tmp, "pkg_util.parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["bind"], "pkg_util.parse")
            self.assertIn("legacy", source_text(row["source"]))

    def test_missing_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
            proc = run_cli(["-C", tmp, "nope"])
            self.assertEqual(proc.returncode, 1)
            self.assertIn("no bindings", proc.stderr)


class Specimen013Tests(unittest.TestCase):
    def test_owned_fixture_matches_observed(self):
        specimen = find_specimen()
        if specimen is None:
            self.skipTest("specimen-013 not found")
        files = specimen / "files"
        proc = run_cli(["-C", str(files), "--from", "pkg_util", "parse"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        row = parse_output(proc.stdout)[0]
        self.assertEqual(row["kind"], "def")
        self.assertEqual(row["runs"], "pkg_util.parse")
        self.assertEqual(row["same_function"], "False")
        self.assertIn("pkg_parse.parse", row.get("also", []))
        self.assertIn("legacy", source_text(row["source"]))

        moved = run_cli(["-C", str(files), "--from", "pkg_parse", "parse"])
        self.assertEqual(moved.returncode, 0, moved.stderr)
        moved_row = parse_output(moved.stdout)[0]
        self.assertEqual(moved_row["runs"], "pkg_parse.parse")
        self.assertIn("moved", source_text(moved_row["source"]))
        self.assertIn("strip", source_text(moved_row["source"]))


class IsolatedQueryTests(unittest.TestCase):
    def test_sys_exit_sibling_does_not_hijack(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "keep.py": "def parse(x):\n    return 'kept'\n",
                    "killer.py": (
                        "import sys\n"
                        "def parse(x):\n    return 'dead'\n"
                        "sys.exit(9)\n"
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--from", "keep", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.returncode, 0)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["query"], "from keep import parse")
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "keep.parse")
            self.assertIn("kept", source_text(row["source"]))
            self.assertEqual(row.get("also"), ["killer.parse"])
            self.assertTrue(proc.stdout.startswith("query\t"))

    def test_aaa_patch_does_not_rewrite_queried_bind(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                    "aaa_patch.py": (
                        "import pkg_util\n"
                        "pkg_util.parse = lambda x: ('patched', x)\n"
                        "def parse(x):\n    return ('patcher', x)\n"
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "pkg_util.parse")
            self.assertIn("legacy", source_text(row["source"]))
            self.assertNotIn("patched", source_text(row["source"]))
            self.assertEqual(
                sorted(row.get("also", [])),
                ["aaa_patch.parse", "pkg_parse.parse"],
            )

    def test_sibling_side_effect_does_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": (
                        "open('SIDE', 'w', encoding='utf-8').write('ran')\n"
                        + PARSE_MOVED
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse((root / "SIDE").exists())
            self.assertTrue(proc.stdout.startswith("query\t"))

    def test_queried_print_is_not_in_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": "print('QUERY_PRINT')\n" + UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("QUERY_PRINT", proc.stdout)
            self.assertTrue(proc.stdout.startswith("query\t"))
            row = parse_output(proc.stdout)[0]
            self.assertIn("legacy", source_text(row["source"]))

    def test_leftover_ast_uses_logical_module_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED}
            )
            stdlib_ast = sys.modules["ast"]
            path = root / "ast.py"
            with BN.isolated_import(root):
                mod, logical = BN.load_query(root, "ast", path)
                self.assertEqual(logical, "ast")
                self.assertEqual(mod.__name__, "ast")
                self.assertEqual(mod.parse("z"), ("leftover-ast", "z"))
                self.assertIs(sys.modules.get("ast"), mod)
                self.assertNotIn("Cellar", getattr(mod, "__file__", ""))
                self.assertNotIn("lib/python", getattr(mod, "__file__", ""))
            self.assertIs(sys.modules["ast"], stdlib_ast)
            binding, _bindings = BN.binding_from_import(root, "ast", "parse")
            self.assertIsNotNone(binding)
            assert binding is not None
            self.assertEqual(binding.runs, "ast.parse")
            self.assertEqual(binding.kind, "def")
            self.assertIn("leftover-ast", binding.source)
            self.assertIs(sys.modules["ast"], stdlib_ast)

    def test_if_body_def_is_a_static_also(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": (
                        "flag = True\n"
                        "if flag:\n"
                        "    def parse(x):\n"
                        "        return ('legacy', x)\n"
                    ),
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_parse", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row.get("also"), ["pkg_util.parse"])
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertEqual(parse_output(listed.stdout)[0]["count"], "2")


class PresenceVsBindTests(unittest.TestCase):
    def test_annotation_only_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "ann.py": "from typing import Callable\nparse: Callable\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            proc = run_cli(["-C", tmp, "--from", "ann", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(proc.stdout.startswith("query\t"))
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            self.assertEqual(rows[0]["count"], "1")
            binds = [r["bind"] for r in rows[1:]]
            self.assertEqual(binds, ["pkg_parse.parse"])
            self.assertNotIn("ann.parse", binds)

    def test_boom_import_fail_is_not_last_wins_reexport(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "moved.py": PARSE_MOVED,
                    "boom.py": (
                        "def parse(x):\n"
                        "    return 'actually-bound-then-raise'\n"
                        "raise RuntimeError('import dies')\n"
                        "from moved import parse\n"
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--from", "boom", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("import failed", proc.stderr)
            self.assertIn("RuntimeError", proc.stderr)
            self.assertNotIn("kind\treexport", proc.stdout)
            self.assertNotIn("moved.parse", proc.stdout)

    def test_non_utf8_sibling_is_visible_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED},
            )
            (root / "weird.py").write_bytes(b"def parse(x):\n    return b'\xff'\n")
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("UnicodeDecodeError", proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "pkg_util.parse")
            self.assertTrue(any("UnicodeDecodeError" in m for m in row.get("miss", [])))
            self.assertEqual(row["same_function"], "False")

    def test_syntax_error_leftover_is_visible_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": "def parse(x)\n    return 1\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            row = parse_output(listed.stdout)[0]
            self.assertEqual(row["count"], "1")
            self.assertEqual(row["same_function"], "False")
            self.assertTrue(any("SyntaxError" in m for m in row.get("miss", [])))
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("import failed", proc.stderr)


class FileLastBindingTests(unittest.TestCase):
    def test_file_as_alias_is_queryable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                    "importer.py": "from pkg_util import parse as parse_legacy\n",
                },
            )
            path = str(root / "importer.py")
            proc = run_cli(["-C", tmp, "--file", path, "parse_legacy"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "1")
            self.assertEqual(rows[1]["runs"], "pkg_util.parse")
            self.assertIn("legacy", source_text(rows[1]["source"]))
            missing = run_cli(["-C", tmp, "--file", path, "parse"])
            self.assertEqual(missing.returncode, 1)
            self.assertIn("no uses of parse", missing.stderr)

    def test_file_following_def_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "override.py": (
                        "from pkg_util import parse\n"
                        "def parse(x):\n"
                        "    return 'overridden-in-file'\n"
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--file", str(root / "override.py"), "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "1")
            self.assertEqual(rows[1]["kind"], "def")
            self.assertIn("overridden-in-file", source_text(rows[1]["source"]))
            self.assertNotIn("legacy", source_text(rows[1]["source"]))

    def test_file_dead_import_is_not_a_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "dead.py": (
                        "def f():\n"
                        "    from pkg_util import parse\n"
                        "if False:\n"
                        "    from pkg_util import parse\n"
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--file", str(root / "dead.py"), "parse"])
            self.assertEqual(proc.returncode, 1)
            self.assertIn("no uses of parse", proc.stderr)


class LinkIdentityTests(unittest.TestCase):
    def test_symlink_pair_matches_is_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
            os.symlink("pkg_util.py", root / "pkg_parse.py")
            honesty = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import pkg_util, pkg_parse; print(pkg_util.parse is pkg_parse.parse)",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "False")
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            row = parse_output(listed.stdout)[0]
            self.assertEqual(row["count"], "2")
            self.assertEqual(row["same_function"], "False")
            proc = run_cli(["-C", tmp, "--from", "pkg_parse", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            q = parse_output(proc.stdout)[0]
            self.assertEqual(q["file"], "pkg_parse.py")
            self.assertEqual(q["same_function"], "False")
            self.assertEqual(q.get("also"), ["pkg_util.parse"])

    def test_hardlink_pair_matches_is_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
            os.link(root / "pkg_util.py", root / "pkg_parse.py")
            honesty = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import pkg_util, pkg_parse; print(pkg_util.parse is pkg_parse.parse)",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "False")
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            row = parse_output(listed.stdout)[0]
            self.assertEqual(row["count"], "2")
            self.assertEqual(row["same_function"], "False")

    def test_symlink_dir_cycle_does_not_hang(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
            os.symlink(root, root / "loop")
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertEqual(parse_output(listed.stdout)[0]["count"], "1")


class LogicalNameHonestyTests(unittest.TestCase):
    def test_name_gated_leftover_ast_reports_leftover_body(self):
        gated = (
            "if __name__ == 'ast':\n"
            "    def parse(x):\n"
            "        return ('name-gated-leftover', x)\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": gated, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from ast import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('name-gated-leftover', 'z')")
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["bind"], "ast.parse")
            self.assertEqual(row["runs"], "ast.parse")
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["file"], "ast.py")
            src = source_text(row["source"])
            self.assertIn("name-gated-leftover", src)
            self.assertNotIn("filename", src)
            self.assertNotIn("lib/python", row["file"])
            self.assertNotIn("Cellar", row["file"])
            self.assertIs(sys.modules["ast"], ast)

    def test_unique_only_branch_reports_honesty_leftover(self):
        branched = (
            "if __name__ != 'ast':\n"
            "    def parse(x):\n"
            "        return ('unique-only', x)\n"
            "else:\n"
            "    def parse(x):\n"
            "        return ('honesty-leftover', x)\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": branched, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from ast import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('honesty-leftover', 'z')")
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            src = source_text(row["source"])
            self.assertIn("honesty-leftover", src)
            self.assertNotIn("unique-only", src)
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "ast.parse")
            self.assertEqual(row["file"], "ast.py")
            self.assertIs(sys.modules["ast"], ast)


class SubmoduleImportTests(unittest.TestCase):
    def test_from_pkg_import_name_binds_submodule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg/__init__.py": "",
                    "pkg/parse.py": "def parse(x):\n    return ('submodule', x)\n",
                },
            )
            honesty = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from pkg import parse; print(type(parse).__name__, parse.__name__)",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "module pkg.parse")
            proc = run_cli(["-C", tmp, "--from", "pkg", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("has no name", proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["query"], "from pkg import parse")
            self.assertEqual(row["bind"], "pkg.parse")
            self.assertEqual(row["runs"], "pkg.parse")
            self.assertEqual(row["kind"], "module")
            self.assertEqual(row["file"], "pkg/parse.py")
            self.assertNotEqual(row["kind"], "def")
            binding, _bindings = BN.binding_from_import(root, "pkg", "parse")
            self.assertIsNotNone(binding)
            assert binding is not None
            self.assertEqual(binding.kind, "module")
            self.assertTrue(isinstance(binding.obj_id, int))

    def test_list_submodule_is_not_inner_function_same(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg/__init__.py": "",
                    "pkg/parse.py": "def parse(x):\n    return ('submodule', x)\n",
                },
            )
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            self.assertGreaterEqual(int(rows[0]["count"]), 2)
            self.assertEqual(rows[0]["same_function"], "False")
            kinds = {r.get("bind"): r.get("kind") for r in rows[1:]}
            self.assertEqual(kinds.get("pkg.parse"), "module")
            self.assertEqual(kinds.get("pkg.parse.parse"), "def")


class DeadBranchAlsoTests(unittest.TestCase):
    def test_if_false_and_type_checking_not_in_also(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "dead.py": (
                        "if False:\n"
                        "    def parse(x):\n"
                        "        return 'dead'\n"
                    ),
                    "typed.py": (
                        "from typing import TYPE_CHECKING\n"
                        "if TYPE_CHECKING:\n"
                        "    def parse(x):\n"
                        "        return 'typed'\n"
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_parse", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            also = row.get("also") or []
            self.assertNotIn("dead.parse", also)
            self.assertNotIn("typed.parse", also)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            self.assertEqual(rows[0]["count"], "1")
            binds = [r["bind"] for r in rows[1:]]
            self.assertEqual(binds, ["pkg_parse.parse"])
            missing = run_cli(["-C", tmp, "--from", "dead", "parse"])
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("has no name", missing.stderr)


class EncodingCookieTests(unittest.TestCase):
    def test_latin1_leftover_does_not_miss_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = (
                "# -*- coding: latin-1 -*-\n"
                "def parse(x):\n"
                "    return 'café'\n"
            )
            (root / "latin.py").write_bytes(body.encode("latin-1"))
            (root / "pkg_parse.py").write_text(PARSE_MOVED, encoding="utf-8")
            honesty = subprocess.run(
                [sys.executable, "-c", "from latin import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "café")
            proc = run_cli(["-C", tmp, "--from", "latin", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "latin.parse")
            self.assertEqual(row["file"], "latin.py")
            self.assertIn("café", source_text(row["source"]))
            misses = row.get("miss") or []
            self.assertFalse(any("latin.py" in m for m in misses))
            self.assertNotIn("UnicodeDecodeError", proc.stderr)


class QueriedStderrTests(unittest.TestCase):
    def test_queried_stderr_is_not_on_cli_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": (
                        "import sys\n"
                        "print('ERR', file=sys.stderr)\n"
                        + UTIL_LEGACY
                    ),
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("ERR", proc.stderr)
            self.assertNotIn("ERR", proc.stdout)
            self.assertTrue(proc.stdout.startswith("query\t"))


class BuiltinLeftoverTests(unittest.TestCase):
    def test_leftover_sys_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from sys import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            self.assertIn("ImportError", honesty.stderr)
            proc = run_cli(["-C", tmp, "--from", "sys", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("kind\tdef", proc.stdout)
            self.assertNotIn("leftover-sys", proc.stdout)
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            binds = [r["bind"] for r in rows[1:]]
            self.assertEqual(binds, ["pkg_parse.parse"])
            self.assertNotIn("sys.parse", binds)
            self.assertTrue(any("sys.py" in m and "builtin" in m for m in rows[0].get("miss", [])))

    def test_leftover_builtins_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from builtins import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            self.assertIn("ImportError", honesty.stderr)
            proc = run_cli(["-C", tmp, "--from", "builtins", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("kind\tdef", proc.stdout)
            self.assertNotIn("leftover-builtins", proc.stdout)
            self.assertIn("has no name", proc.stderr)

    def test_also_does_not_list_builtin_leftover_ghosts(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "inspect.py": "def parse(x):\n    return ('leftover-inspect', x)\n",
                    "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                    "builtins.py": "def parse(x):\n    return ('leftover-builtins', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from inspect import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('leftover-inspect', 'z')")
            proc = run_cli(["-C", tmp, "--from", "inspect", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "inspect.parse")
            self.assertEqual(row["file"], "inspect.py")
            self.assertIn("leftover-inspect", source_text(row["source"]))
            also = row.get("also") or []
            self.assertIn("pkg_parse.parse", also)
            self.assertNotIn("sys.parse", also)
            self.assertNotIn("builtins.parse", also)
            self.assertNotIn("lib/python", row["file"])
            self.assertNotIn("Cellar", row["file"])

    def test_leftover_ast_still_helper_not_stdlib(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "ast.parse")
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            self.assertNotIn("lib/python", row["file"])
            self.assertNotIn("Cellar", row["file"])
            src = Path(__file__).resolve().parents[1] / "bindname"
            text = src.read_text(encoding="utf-8")
            self.assertNotIn("import_module", text)


class DeadComplementListTests(unittest.TestCase):
    def test_if_not_type_checking_list_is_live(self):
        body = (
            "from typing import TYPE_CHECKING\n"
            "if not TYPE_CHECKING:\n"
            "    def parse(x):\n"
            "        return 'live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'typed-else'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"nottyped.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from nottyped import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "live")
            proc = run_cli(["-C", tmp, "--from", "nottyped", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertIn("live", source_text(row["source"]))
            self.assertNotIn("typed-else", source_text(row["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            by_bind = {r["bind"]: r for r in rows[1:]}
            self.assertIn("nottyped.parse", by_bind)
            src = source_text(by_bind["nottyped.parse"]["source"])
            self.assertIn("live", src)
            self.assertNotIn("typed-else", src)

    def test_if_not_false_list_is_live(self):
        body = (
            "if not False:\n"
            "    def parse(x):\n"
            "        return 'live-not-false'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'dead-else'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"notfalse.py": body})
            proc = run_cli(["-C", tmp, "--from", "notfalse", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("live-not-false", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            src = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("live-not-false", src)
            self.assertNotIn("dead-else", src)

    def test_reverse_match_list_matches_query(self):
        body = (
            "x = 1\n"
            "match x:\n"
            "    case 1:\n"
            "        def parse(y):\n"
            "            return 'live-first'\n"
            "    case 0:\n"
            "        def parse(y):\n"
            "            return 'dead-last'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"revmatch.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from revmatch import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "live-first")
            proc = run_cli(["-C", tmp, "--from", "revmatch", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            qsrc = source_text(parse_output(proc.stdout)[0]["source"])
            self.assertIn("live-first", qsrc)
            self.assertNotIn("dead-last", qsrc)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("live-first", lsrc)
            self.assertNotIn("dead-last", lsrc)


class FileAttributeAssignTests(unittest.TestCase):
    def test_file_attr_assign_follows_moved_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "assign.py": "import pkg_parse\nparse = pkg_parse.parse\n",
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from assign import parse; print(parse(' z '))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('moved', 'z')")
            fproc = run_cli(["-C", tmp, "--file", str(root / "assign.py"), "parse"])
            qproc = run_cli(["-C", tmp, "--from", "assign", "parse"])
            self.assertEqual(fproc.returncode, 0, fproc.stderr)
            self.assertEqual(qproc.returncode, 0, qproc.stderr)
            frow = parse_output(fproc.stdout)[1]
            qrow = parse_output(qproc.stdout)[0]
            self.assertEqual(frow["runs"], "pkg_parse.parse")
            self.assertEqual(qrow["runs"], "pkg_parse.parse")
            self.assertIn("moved", source_text(frow["source"]))
            self.assertIn("strip", source_text(frow["source"]))
            self.assertIn("moved", source_text(qrow["source"]))
            self.assertIn("strip", source_text(qrow["source"]))
            self.assertNotIn("parse = pkg_parse.parse", source_text(frow["source"]))
            self.assertNotEqual(frow["kind"], "assign")
            self.assertNotEqual(qrow["kind"], "assign")

    def test_file_import_module_assign_stays_assign(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "dyn.py": (
                        "import importlib\n"
                        "m = importlib.import_module('pkg_parse')\n"
                        "parse = m.parse\n"
                    ),
                },
            )
            fproc = run_cli(["-C", tmp, "--file", str(root / "dyn.py"), "parse"])
            self.assertEqual(fproc.returncode, 0, fproc.stderr)
            frow = parse_output(fproc.stdout)[1]
            self.assertEqual(frow["kind"], "assign")
            self.assertIn("parse = m.parse", source_text(frow["source"]))


class PartialRunsTests(unittest.TestCase):
    def test_partial_query_runs_is_not_functools_parse(self):
        body = (
            "import functools\n"
            "def _p(pre, x):\n    return pre+x\n"
            "parse = functools.partial(_p, 'pre')\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"partialer.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from partialer import parse; print(type(parse).__name__, parse(' z'))",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertIn("partial", honesty.stdout)
            proc = run_cli(["-C", tmp, "--from", "partialer", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertNotEqual(row["runs"], "functools.parse")
            self.assertEqual(row["runs"], "partialer._p")
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
            self.assertEqual(by_bind["partialer.parse"]["runs"], "partialer._p")
            self.assertEqual(by_bind["partialer.parse"]["kind"], row["kind"])


class AlreadyImportedLeftoverTests(unittest.TestCase):
    def test_leftover_io_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "io.py": "def parse(x):\n    return ('leftover-io', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from io import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            self.assertIn("ImportError", honesty.stderr)
            proc = run_cli(["-C", tmp, "--from", "io", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("kind\tdef", proc.stdout)
            self.assertNotIn("leftover-io", proc.stdout)
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            binds = [r["bind"] for r in rows[1:]]
            self.assertEqual(binds, ["pkg_parse.parse"])
            self.assertNotIn("io.parse", binds)
            self.assertTrue(any("io.py" in m for m in rows[0].get("miss", [])))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))

    def test_leftover_encodings_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "encodings.py": "def parse(x):\n    return ('leftover-encodings', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from encodings import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            self.assertIn("ImportError", honesty.stderr)
            proc = run_cli(["-C", tmp, "--from", "encodings", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("kind\tdef", proc.stdout)
            self.assertNotIn("leftover-encodings", proc.stdout)
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            binds = [r["bind"] for r in parse_output(listed.stdout)[1:]]
            self.assertEqual(binds, ["pkg_parse.parse"])
            self.assertNotIn("encodings.parse", binds)

    def test_leftover_os_list_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "os.py": "def parse(x):\n    return ('leftover-os', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from os import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            self.assertIn("ImportError", honesty.stderr)
            proc = run_cli(["-C", tmp, "--from", "os", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("kind\tdef", proc.stdout)
            self.assertNotIn("leftover-os", proc.stdout)
            self.assertNotIn("has no attribute 'stat'", proc.stderr)
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            binds = [r["bind"] for r in rows[1:]]
            self.assertEqual(binds, ["pkg_parse.parse"])
            self.assertNotIn("os.parse", binds)
            self.assertTrue(any("os.py" in m for m in rows[0].get("miss", [])))

    def test_leftover_tokenize_is_leftover_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "tokenize.py": "def parse(x):\n    return ('leftover-tokenize', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from tokenize import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('leftover-tokenize', 'z')")
            proc = run_cli(["-C", tmp, "--from", "tokenize", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "tokenize.parse")
            self.assertEqual(row["file"], "tokenize.py")
            self.assertIn("leftover-tokenize", source_text(row["source"]))
            self.assertNotIn("has no attribute 'open'", proc.stderr)
            self.assertNotIn("lib/python", row["file"])
            self.assertNotIn("Cellar", row["file"])
            also = row.get("also") or []
            self.assertIn("pkg_parse.parse", also)


class ConstKnownIfListTests(unittest.TestCase):
    def test_flag_true_list_is_live_not_dead_else(self):
        body = (
            "flag = True\n"
            "if flag:\n"
            "    def parse(x):\n"
            "        return 'live-flag'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'dead-else'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"flagtrue.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from flagtrue import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "live-flag")
            proc = run_cli(["-C", tmp, "--from", "flagtrue", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            qsrc = source_text(parse_output(proc.stdout)[0]["source"])
            self.assertIn("live-flag", qsrc)
            self.assertNotIn("dead-else", qsrc)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("live-flag", lsrc)
            self.assertNotIn("dead-else", lsrc)

    def test_eq_one_list_matches_query(self):
        body = (
            "if 1 == 1:\n"
            "    def parse(x):\n"
            "        return 'eq-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'eq-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"eqone.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from eqone import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "eq-live")
            proc = run_cli(["-C", tmp, "--from", "eqone", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("eq-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("eq-live", lsrc)
            self.assertNotIn("eq-dead", lsrc)

    def test_debug_and_walrus_list_is_live(self):
        debug_body = (
            "if __debug__:\n"
            "    def parse(x):\n"
            "        return 'debug-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'debug-dead'\n"
        )
        walrus_body = (
            "if (flag := True):\n"
            "    def parse(x):\n"
            "        return 'walrus-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'walrus-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"dbg.py": debug_body, "walrus.py": walrus_body})
            for mod, live, dead in (
                ("dbg", "debug-live", "debug-dead"),
                ("walrus", "walrus-live", "walrus-dead"),
            ):
                honesty = subprocess.run(
                    [sys.executable, "-c", f"from {mod} import parse; print(parse('z'))"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                )
                self.assertEqual(honesty.returncode, 0, honesty.stderr)
                self.assertEqual(honesty.stdout.strip(), live)
                proc = run_cli(["-C", tmp, "--from", mod, "parse"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(live, source_text(parse_output(proc.stdout)[0]["source"]))
                listed = run_cli(["-C", tmp, "parse"])
                self.assertEqual(listed.returncode, 0, listed.stderr)
                by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
                src = source_text(by_bind[f"{mod}.parse"]["source"])
                self.assertIn(live, src)
                self.assertNotIn(dead, src)

    def test_type_checking_alias_list_is_live(self):
        body = (
            "from typing import TYPE_CHECKING as TC\n"
            "if not TC:\n"
            "    def parse(x):\n"
            "        return 'live-not-tc'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'typed-else-tc'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"tcalias.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from tcalias import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "live-not-tc")
            proc = run_cli(["-C", tmp, "--from", "tcalias", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            qsrc = source_text(parse_output(proc.stdout)[0]["source"])
            self.assertIn("live-not-tc", qsrc)
            self.assertNotIn("typed-else-tc", qsrc)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("live-not-tc", lsrc)
            self.assertNotIn("typed-else-tc", lsrc)


class FileGetattrAndAliasTests(unittest.TestCase):
    def test_file_getattr_assign_follows_moved_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "getattrer.py": (
                        "import pkg_parse\n"
                        "parse = getattr(pkg_parse, 'parse')\n"
                    ),
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from getattrer import parse; print(parse(' z '))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('moved', 'z')")
            fproc = run_cli(["-C", tmp, "--file", str(root / "getattrer.py"), "parse"])
            qproc = run_cli(["-C", tmp, "--from", "getattrer", "parse"])
            self.assertEqual(fproc.returncode, 0, fproc.stderr)
            self.assertEqual(qproc.returncode, 0, qproc.stderr)
            frow = parse_output(fproc.stdout)[1]
            qrow = parse_output(qproc.stdout)[0]
            self.assertEqual(frow["runs"], "pkg_parse.parse")
            self.assertEqual(qrow["runs"], "pkg_parse.parse")
            self.assertIn("moved", source_text(frow["source"]))
            self.assertIn("strip", source_text(frow["source"]))
            self.assertNotIn("getattr", source_text(frow["source"]))
            self.assertNotEqual(frow["kind"], "assign")
            self.assertNotEqual(qrow["kind"], "assign")

    def test_file_name_alias_follows_moved_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "aliaser.py": (
                        "from pkg_parse import parse as p\n"
                        "parse = p\n"
                    ),
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from aliaser import parse; print(parse(' z '))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('moved', 'z')")
            fproc = run_cli(["-C", tmp, "--file", str(root / "aliaser.py"), "parse"])
            qproc = run_cli(["-C", tmp, "--from", "aliaser", "parse"])
            self.assertEqual(fproc.returncode, 0, fproc.stderr)
            self.assertEqual(qproc.returncode, 0, qproc.stderr)
            frow = parse_output(fproc.stdout)[1]
            qrow = parse_output(qproc.stdout)[0]
            self.assertEqual(frow["runs"], "pkg_parse.parse")
            self.assertEqual(qrow["runs"], "pkg_parse.parse")
            self.assertIn("moved", source_text(frow["source"]))
            self.assertIn("strip", source_text(frow["source"]))
            self.assertNotIn("parse = p", source_text(frow["source"]))
            self.assertNotEqual(frow["kind"], "assign")
            self.assertNotEqual(qrow["kind"], "assign")


class FrozenSubmoduleLeftoverTests(unittest.TestCase):
    def test_leftover_importlib_util_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "importlib/__init__.py": (
                        "def parse(x):\n    return ('leftover-importlib', x)\n"
                    ),
                    "importlib/util.py": (
                        "def parse(x):\n    return ('leftover-importlib-util', x)\n"
                    ),
                    "importlib/machinery.py": (
                        "def parse(x):\n    return ('leftover-importlib-mach', x)\n"
                    ),
                    "importlib/abc.py": (
                        "def parse(x):\n    return ('leftover-importlib-abc', x)\n"
                    ),
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from importlib.util import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "importlib.util", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("kind\tdef", proc.stdout)
            self.assertNotIn("leftover-importlib-util", proc.stdout)
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            binds = [r["bind"] for r in parse_output(listed.stdout)[1:]]
            self.assertNotIn("importlib.util.parse", binds)
            self.assertTrue(
                any("importlib/util.py" in m for m in parse_output(listed.stdout)[0].get("miss", []))
            )

    def test_leftover_importlib_machinery_is_not_kind_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "importlib/__init__.py": (
                        "def parse(x):\n    return ('leftover-importlib', x)\n"
                    ),
                    "importlib/machinery.py": (
                        "def parse(x):\n    return ('leftover-importlib-mach', x)\n"
                    ),
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from importlib.machinery import parse; print(parse('z'))",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "importlib.machinery", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertNotIn("kind\tdef", proc.stdout)
            self.assertNotIn("leftover-importlib-mach", proc.stdout)

    def test_leftover_importlib_file_still_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "importlib.py": (
                        "def parse(x):\n    return ('leftover-importlib-file', x)\n"
                    ),
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from importlib import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('leftover-importlib-file', 'z')")
            proc = run_cli(["-C", tmp, "--from", "importlib", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["file"], "importlib.py")
            self.assertIn("leftover-importlib-file", source_text(row["source"]))
            self.assertNotIn("lib/python", row["file"])
            self.assertNotIn("Cellar", row["file"])

    def test_leftover_importlib_abc_still_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "importlib/__init__.py": (
                        "def parse(x):\n    return ('leftover-importlib', x)\n"
                    ),
                    "importlib/abc.py": (
                        "def parse(x):\n    return ('leftover-importlib-abc', x)\n"
                    ),
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from importlib.abc import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "('leftover-importlib-abc', 'z')")
            proc = run_cli(["-C", tmp, "--from", "importlib.abc", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["file"], "importlib/abc.py")
            self.assertIn("leftover-importlib-abc", source_text(row["source"]))

    def test_leftover_io_still_miss_and_tokenize_still_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "io.py": "def parse(x):\n    return ('leftover-io', x)\n",
                    "tokenize.py": "def parse(x):\n    return ('leftover-tokenize', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            io_h = subprocess.run(
                [sys.executable, "-c", "from io import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(io_h.returncode, 0)
            io_cli = run_cli(["-C", tmp, "--from", "io", "parse"])
            self.assertNotEqual(io_cli.returncode, 0)
            self.assertNotIn("leftover-io", io_cli.stdout)
            tok_h = subprocess.run(
                [sys.executable, "-c", "from tokenize import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(tok_h.returncode, 0, tok_h.stderr)
            tok = run_cli(["-C", tmp, "--from", "tokenize", "parse"])
            self.assertEqual(tok.returncode, 0, tok.stderr)
            self.assertIn("leftover-tokenize", source_text(parse_output(tok.stdout)[0]["source"]))

    def test_leftover_ast_still_helper_and_sys_still_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "ast.py": AST_LEFTOVER,
                    "sys.py": "def parse(x):\n    return ('leftover-sys', x)\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            ast_h = subprocess.run(
                [sys.executable, "-c", "from ast import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(ast_h.returncode, 0, ast_h.stderr)
            self.assertEqual(ast_h.stdout.strip(), "('leftover-ast', 'z')")
            ast_cli = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(ast_cli.returncode, 0, ast_cli.stderr)
            row = parse_output(ast_cli.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            self.assertNotIn("lib/python", row["file"])
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))
            sys_h = subprocess.run(
                [sys.executable, "-c", "from sys import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(sys_h.returncode, 0)
            sys_cli = run_cli(["-C", tmp, "--from", "sys", "parse"])
            self.assertNotEqual(sys_cli.returncode, 0)
            self.assertNotIn("leftover-sys", sys_cli.stdout)
            self.assertIn("has no name", sys_cli.stderr)


class ConstBinOpEmptyIfTests(unittest.TestCase):
    def test_add_one_list_is_live_not_dead_else(self):
        body = (
            "if 1 + 1:\n"
            "    def parse(x):\n"
            "        return 'add-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'add-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"add.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from add import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "add-live")
            proc = run_cli(["-C", tmp, "--from", "add", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            qsrc = source_text(parse_output(proc.stdout)[0]["source"])
            self.assertIn("add-live", qsrc)
            self.assertNotIn("add-dead", qsrc)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("add-live", lsrc)
            self.assertNotIn("add-dead", lsrc)

    def test_empty_list_if_without_else_is_not_list_bind(self):
        body = (
            "if []:\n"
            "    def parse(x):\n"
            "        return 'dead-only'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"emptyif.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from emptyif import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            self.assertIn("cannot import name 'parse'", honesty.stderr)
            proc = run_cli(["-C", tmp, "--from", "emptyif", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            binds = [r["bind"] for r in parse_output(listed.stdout)[1:]]
            self.assertNotIn("emptyif.parse", binds)
            for row in parse_output(listed.stdout)[1:]:
                self.assertNotIn("dead-only", source_text(row["source"]))

    def test_ifexp_and_multi_target_list_is_live(self):
        ifexp = (
            "flag = True if True else False\n"
            "if flag:\n"
            "    def parse(x):\n"
            "        return 'ifexp-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'ifexp-dead'\n"
        )
        multi = (
            "flag = other = True\n"
            "if flag:\n"
            "    def parse(x):\n"
            "        return 'multi-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'multi-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ifexp.py": ifexp, "multi.py": multi})
            for mod, live, dead in (
                ("ifexp", "ifexp-live", "ifexp-dead"),
                ("multi", "multi-live", "multi-dead"),
            ):
                honesty = subprocess.run(
                    [sys.executable, "-c", f"from {mod} import parse; print(parse('z'))"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                )
                self.assertEqual(honesty.returncode, 0, honesty.stderr)
                self.assertEqual(honesty.stdout.strip(), live)
                proc = run_cli(["-C", tmp, "--from", mod, "parse"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(live, source_text(parse_output(proc.stdout)[0]["source"]))
                listed = run_cli(["-C", tmp, "parse"])
                self.assertEqual(listed.returncode, 0, listed.stderr)
                by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
                src = source_text(by_bind[f"{mod}.parse"]["source"])
                self.assertIn(live, src)
                self.assertNotIn(dead, src)

    def test_typing_extensions_type_checking_list_is_live(self):
        body = (
            "from typing_extensions import TYPE_CHECKING as TC\n"
            "if not TC:\n"
            "    def parse(x):\n"
            "        return 'live-tex'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'typed-tex'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "tex.py": body,
                    "typing_extensions.py": "TYPE_CHECKING = False\n",
                },
            )
            honesty = subprocess.run(
                [sys.executable, "-c", "from tex import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "live-tex")
            proc = run_cli(["-C", tmp, "--from", "tex", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            qsrc = source_text(parse_output(proc.stdout)[0]["source"])
            self.assertIn("live-tex", qsrc)
            self.assertNotIn("typed-tex", qsrc)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("live-tex", lsrc)
            self.assertNotIn("typed-tex", lsrc)


class ConstUnaryInUnpackTests(unittest.TestCase):
    def test_uadd_invert_list_is_live_not_dead_else(self):
        uadd = (
            "if +1:\n"
            "    def parse(x):\n"
            "        return 'uadd-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'uadd-dead'\n"
        )
        invert = (
            "if ~0:\n"
            "    def parse(x):\n"
            "        return 'inv-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'inv-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"uadd.py": uadd, "invert.py": invert})
            for mod, live, dead in (
                ("uadd", "uadd-live", "uadd-dead"),
                ("invert", "inv-live", "inv-dead"),
            ):
                honesty = subprocess.run(
                    [sys.executable, "-c", f"from {mod} import parse; print(parse('z'))"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                )
                self.assertEqual(honesty.returncode, 0, honesty.stderr)
                self.assertEqual(honesty.stdout.strip(), live)
                proc = run_cli(["-C", tmp, "--from", mod, "parse"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(live, source_text(parse_output(proc.stdout)[0]["source"]))
                listed = run_cli(["-C", tmp, "parse"])
                self.assertEqual(listed.returncode, 0, listed.stderr)
                by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
                src = source_text(by_bind[f"{mod}.parse"]["source"])
                self.assertIn(live, src)
                self.assertNotIn(dead, src)

    def test_uadd_zero_without_else_is_not_list_bind(self):
        body = (
            "if +0:\n"
            "    def parse(x):\n"
            "        return 'uadd-dead-only'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"uzero.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from uzero import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "uzero", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            binds = [r["bind"] for r in parse_output(listed.stdout)[1:]]
            self.assertNotIn("uzero.parse", binds)

    def test_in_compare_list_is_live(self):
        body = (
            "if 1 in [1]:\n"
            "    def parse(x):\n"
            "        return 'in-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'in-dead'\n"
        )
        empty = (
            "if 1 in []:\n"
            "    def parse(x):\n"
            "        return 'in-empty-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"inin.py": body, "inempty.py": empty, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from inin import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "in-live")
            proc = run_cli(["-C", tmp, "--from", "inin", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("in-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
            self.assertIn("in-live", source_text(by_bind["inin.parse"]["source"]))
            self.assertNotIn("in-dead", source_text(by_bind["inin.parse"]["source"]))
            empty_h = subprocess.run(
                [sys.executable, "-c", "from inempty import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(empty_h.returncode, 0)
            empty_cli = run_cli(["-C", tmp, "--from", "inempty", "parse"])
            self.assertNotEqual(empty_cli.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("inempty.parse", binds)

    def test_tuple_unpack_list_is_live(self):
        body = (
            "flag, other = True, True\n"
            "if flag:\n"
            "    def parse(x):\n"
            "        return 'unpack-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'unpack-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"unpack.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from unpack import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "unpack-live")
            proc = run_cli(["-C", tmp, "--from", "unpack", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("unpack-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("unpack-live", lsrc)
            self.assertNotIn("unpack-dead", lsrc)

    def test_local_type_checking_true_list_is_live(self):
        body = (
            "TYPE_CHECKING = True\n"
            "if TYPE_CHECKING:\n"
            "    def parse(x):\n"
            "        return 'local-tc-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'local-tc-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"localtc.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from localtc import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "local-tc-live")
            proc = run_cli(["-C", tmp, "--from", "localtc", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            qsrc = source_text(parse_output(proc.stdout)[0]["source"])
            self.assertIn("local-tc-live", qsrc)
            self.assertNotIn("local-tc-dead", qsrc)
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("local-tc-live", lsrc)
            self.assertNotIn("local-tc-dead", lsrc)

    def test_leftover_ast_still_helper_after_unary_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstSubscriptJoinUnpackTests(unittest.TestCase):
    def test_subscript_list_is_live(self):
        body = (
            "if [1][0]:\n"
            "    def parse(x):\n"
            "        return 'subl-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'subl-dead'\n"
        )
        dead = (
            "if [0][0]:\n"
            "    def parse(x):\n"
            "        return 'sub0-dead-only'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"subl.py": body, "sub0.py": dead, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from subl import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "subl-live")
            proc = run_cli(["-C", tmp, "--from", "subl", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("subl-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
            self.assertIn("subl-live", source_text(by_bind["subl.parse"]["source"]))
            self.assertNotIn("subl-dead", source_text(by_bind["subl.parse"]["source"]))
            dead_h = subprocess.run(
                [sys.executable, "-c", "from sub0 import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(dead_h.returncode, 0)
            dead_cli = run_cli(["-C", tmp, "--from", "sub0", "parse"])
            self.assertNotEqual(dead_cli.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("sub0.parse", binds)

    def test_joinedstr_list_is_live(self):
        body = (
            "if f'{1}':\n"
            "    def parse(x):\n"
            "        return 'join-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'join-dead'\n"
        )
        empty = (
            "if f'':\n"
            "    def parse(x):\n"
            "        return 'join-empty'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"join.py": body, "jempty.py": empty, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from join import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "join-live")
            proc = run_cli(["-C", tmp, "--from", "join", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("join-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
            self.assertIn("join-live", source_text(by_bind["join.parse"]["source"]))
            empty_cli = run_cli(["-C", tmp, "--from", "jempty", "parse"])
            self.assertNotEqual(empty_cli.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("jempty.parse", binds)

    def test_nested_and_star_unpack_list_is_live(self):
        nested = (
            "flag, (other,) = True, (True,)\n"
            "if flag:\n"
            "    def parse(x):\n"
            "        return 'nest-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'nest-dead'\n"
        )
        star = (
            "flag, *rest = True, True\n"
            "if flag:\n"
            "    def parse(x):\n"
            "        return 'star-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'star-dead'\n"
        )
        pair = (
            "pair = True, True\n"
            "flag, other = pair\n"
            "if flag:\n"
            "    def parse(x):\n"
            "        return 'pair-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'pair-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"nest.py": nested, "staru.py": star, "pair.py": pair})
            for mod, live, dead in (
                ("nest", "nest-live", "nest-dead"),
                ("staru", "star-live", "star-dead"),
                ("pair", "pair-live", "pair-dead"),
            ):
                honesty = subprocess.run(
                    [sys.executable, "-c", f"from {mod} import parse; print(parse('z'))"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                )
                self.assertEqual(honesty.returncode, 0, f"{mod}: {honesty.stderr}")
                self.assertEqual(honesty.stdout.strip(), live, mod)
                proc = run_cli(["-C", tmp, "--from", mod, "parse"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(live, source_text(parse_output(proc.stdout)[0]["source"]))
                listed = run_cli(["-C", tmp, "parse"])
                by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
                src = source_text(by_bind[f"{mod}.parse"]["source"])
                self.assertIn(live, src)
                self.assertNotIn(dead, src)

    def test_starred_collection_list_is_live(self):
        body = (
            "if [*[1]]:\n"
            "    def parse(x):\n"
            "        return 'starcol-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'starcol-dead'\n"
        )
        empty = (
            "if [*[]]:\n"
            "    def parse(x):\n"
            "        return 'starcol-empty'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"scol.py": body, "sempty.py": empty, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from scol import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "starcol-live")
            proc = run_cli(["-C", tmp, "--from", "scol", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("starcol-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
            self.assertIn("starcol-live", source_text(by_bind["scol.parse"]["source"]))
            empty_cli = run_cli(["-C", tmp, "--from", "sempty", "parse"])
            self.assertNotEqual(empty_cli.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("sempty.parse", binds)

    def test_leftover_ast_still_helper_after_subscript(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstForAttrCompTests(unittest.TestCase):
    def test_for_const_iter_list_is_live(self):
        body = (
            "for _ in [1]:\n"
            "    def parse(x):\n"
            "        return 'for-live'\n"
        )
        empty = (
            "for _ in ():\n"
            "    def parse(x):\n"
            "        return 'for-empty'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"forlive.py": body, "forempty.py": empty, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from forlive import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "for-live")
            proc = run_cli(["-C", tmp, "--from", "forlive", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("for-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
            self.assertIn("for-live", source_text(by_bind["forlive.parse"]["source"]))
            empty_h = subprocess.run(
                [sys.executable, "-c", "from forempty import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(empty_h.returncode, 0)
            empty_cli = run_cli(["-C", tmp, "--from", "forempty", "parse"])
            self.assertNotEqual(empty_cli.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("forempty.parse", binds)

    def test_const_attr_and_class_attr_list_is_live(self):
        real = (
            "if (1).real:\n"
            "    def parse(x):\n"
            "        return 'real-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'real-dead'\n"
        )
        klass = (
            "class T:\n"
            "    x = 1\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'tx-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'tx-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"real.py": real, "tx.py": klass})
            for mod, live, dead in (("real", "real-live", "real-dead"), ("tx", "tx-live", "tx-dead")):
                honesty = subprocess.run(
                    [sys.executable, "-c", f"from {mod} import parse; print(parse('z'))"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                )
                self.assertEqual(honesty.returncode, 0, f"{mod}: {honesty.stderr}")
                self.assertEqual(honesty.stdout.strip(), live)
                proc = run_cli(["-C", tmp, "--from", mod, "parse"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(live, source_text(parse_output(proc.stdout)[0]["source"]))
                listed = run_cli(["-C", tmp, "parse"])
                by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
                src = source_text(by_bind[f"{mod}.parse"]["source"])
                self.assertIn(live, src)
                self.assertNotIn(dead, src)

    def test_listcomp_and_genexp_list_matches_query(self):
        comp = (
            "if [x for x in [1]]:\n"
            "    def parse(x):\n"
            "        return 'comp-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'comp-dead'\n"
        )
        gen = (
            "if (x for x in []):\n"
            "    def parse(x):\n"
            "        return 'gen-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'gen-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"comp.py": comp, "gen.py": gen})
            for mod, live, dead in (("comp", "comp-live", "comp-dead"), ("gen", "gen-live", "gen-dead")):
                honesty = subprocess.run(
                    [sys.executable, "-c", f"from {mod} import parse; print(parse('z'))"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                )
                self.assertEqual(honesty.returncode, 0, f"{mod}: {honesty.stderr}")
                self.assertEqual(honesty.stdout.strip(), live)
                proc = run_cli(["-C", tmp, "--from", mod, "parse"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(live, source_text(parse_output(proc.stdout)[0]["source"]))
                listed = run_cli(["-C", tmp, "parse"])
                by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
                src = source_text(by_bind[f"{mod}.parse"]["source"])
                self.assertIn(live, src)
                self.assertNotIn(dead, src)

    def test_leftover_ast_still_helper_after_for_attr(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstCompGenexpForTests(unittest.TestCase):
    def test_setcomp_dictcomp_list_is_live(self):
        sc = (
            "if {x for x in [1]}:\n"
            "    def parse(x):\n"
            "        return 'set-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'set-dead'\n"
        )
        dc = (
            "if {x: 1 for x in [1]}:\n"
            "    def parse(x):\n"
            "        return 'dict-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'dict-dead'\n"
        )
        filt = (
            "if [x for x in [1, 0] if x]:\n"
            "    def parse(x):\n"
            "        return 'filt-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'filt-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"sc.py": sc, "dc.py": dc, "filt.py": filt})
            for mod, live, dead in (
                ("sc", "set-live", "set-dead"),
                ("dc", "dict-live", "dict-dead"),
                ("filt", "filt-live", "filt-dead"),
            ):
                honesty = subprocess.run(
                    [sys.executable, "-c", f"from {mod} import parse; print(parse('z'))"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=tmp,
                )
                self.assertEqual(honesty.returncode, 0, f"{mod}: {honesty.stderr}")
                self.assertEqual(honesty.stdout.strip(), live)
                proc = run_cli(["-C", tmp, "--from", mod, "parse"])
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn(live, source_text(parse_output(proc.stdout)[0]["source"]))
                listed = run_cli(["-C", tmp, "parse"])
                by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
                src = source_text(by_bind[f"{mod}.parse"]["source"])
                self.assertIn(live, src)
                self.assertNotIn(dead, src)

    def test_empty_genexp_for_is_not_list_bind(self):
        body = (
            "for _ in (x for x in []):\n"
            "    def parse(x):\n"
            "        return 'genfor-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"genfor.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from genfor import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "genfor", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("genfor.parse", binds)

    def test_instance_attr_after_call_list_is_live(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'inst-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'inst-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"inst.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from inst import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "inst-live")
            proc = run_cli(["-C", tmp, "--from", "inst", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("inst-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("inst-live", lsrc)
            self.assertNotIn("inst-dead", lsrc)

    def test_leftover_ast_still_helper_after_comp_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstGenexpRowsFormatTests(unittest.TestCase):
    def test_nonempty_genexp_for_is_list_bind(self):
        body = (
            "for _ in (x for x in [1]):\n"
            "    def parse(x):\n"
            "        return 'genfor-live'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"genfor1.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from genfor1 import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "genfor-live")
            proc = run_cli(["-C", tmp, "--from", "genfor1", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("genfor-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            by_bind = {r["bind"]: r for r in parse_output(listed.stdout)[1:]}
            self.assertIn("genfor-live", source_text(by_bind["genfor1.parse"]["source"]))

    def test_format_spec_joinedstr_list_is_live(self):
        body = (
            "if f'{1:d}':\n"
            "    def parse(x):\n"
            "        return 'fmt-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'fmt-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"fmt.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from fmt import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "fmt-live")
            proc = run_cli(["-C", tmp, "--from", "fmt", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("fmt-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("fmt-live", lsrc)
            self.assertNotIn("fmt-dead", lsrc)

    def test_empty_genexp_for_still_not_bind(self):
        body = (
            "for _ in (x for x in []):\n"
            "    def parse(x):\n"
            "        return 'genfor-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"genfor0.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from genfor0 import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "genfor0", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("genfor0.parse", binds)

    def test_leftover_ast_still_helper_after_genexp_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstAttrAssignMultiCompTests(unittest.TestCase):
    def test_post_class_attr_assign_list_is_dead(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "T.x = 0\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'tx-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'tx-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"txas.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from txas import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "tx-dead")
            proc = run_cli(["-C", tmp, "--from", "txas", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("tx-dead", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("tx-dead", lsrc)
            self.assertNotIn("tx-live", lsrc)

    def test_multi_generator_listcomp_list_is_live(self):
        body = (
            "if [x+y for x in [1] for y in [0]]:\n"
            "    def parse(x):\n"
            "        return 'multi-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'multi-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"multi.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from multi import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "multi-live")
            proc = run_cli(["-C", tmp, "--from", "multi", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("multi-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("multi-live", lsrc)
            self.assertNotIn("multi-dead", lsrc)

    def test_conversion_then_spec_s_is_live(self):
        body = (
            "if f'{1!s:s}':\n"
            "    def parse(x):\n"
            "        return 'cs-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cs-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cs.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cs import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cs-live")
            proc = run_cli(["-C", tmp, "--from", "cs", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cs-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cs-live", lsrc)
            self.assertNotIn("cs-dead", lsrc)

    def test_leftover_ast_still_helper_after_attr_assign(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstInstanceFollowsClassTests(unittest.TestCase):
    def test_instance_follows_later_class_attr_assign(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "t = T()\n"
            "T.x = 0\n"
            "if t.x:\n"
            "    def parse(x):\n"
            "        return 'follow-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'follow-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"follow.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from follow import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "follow-dead")
            proc = run_cli(["-C", tmp, "--from", "follow", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("follow-dead", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("follow-dead", lsrc)
            self.assertNotIn("follow-live", lsrc)

    def test_delete_class_attr_if_is_not_list_bind(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'del-live'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"delx.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from delx import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "delx", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("delx.parse", binds)

    def test_class_body_reads_outer_const(self):
        body = (
            "flag = True\n"
            "class T:\n"
            "    x = flag\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'outer-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'outer-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"outer.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from outer import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "outer-live")
            proc = run_cli(["-C", tmp, "--from", "outer", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("outer-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("outer-live", lsrc)
            self.assertNotIn("outer-dead", lsrc)

    def test_leftover_ast_still_helper_after_instance_follow(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstFailIfClassBodyTests(unittest.TestCase):
    def test_missing_attr_if_else_is_not_list_bind(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'miss-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'miss-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"misselse.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from misselse import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "misselse", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("misselse.parse", binds)

    def test_del_name_if_is_not_list_bind(self):
        body = (
            "x = 1\n"
            "del x\n"
            "if x:\n"
            "    def parse(y):\n"
            "        return 'deln-live'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"deln.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from deln import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "deln", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("deln.parse", binds)

    def test_class_body_if_true_attr(self):
        body = (
            "class T:\n"
            "    if True:\n"
            "        x = 1\n"
            "    else:\n"
            "        x = 0\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cif-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cif-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cif.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cif import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cif-live")
            proc = run_cli(["-C", tmp, "--from", "cif", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cif-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cif-live", lsrc)
            self.assertNotIn("cif-dead", lsrc)

    def test_leftover_ast_still_helper_after_fail_if(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstClassBodyForMatchWalrusTests(unittest.TestCase):
    def test_class_body_for_attr_is_live(self):
        body = (
            "class T:\n"
            "    for _ in [1]:\n"
            "        x = 1\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cfb-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cfb-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cfb.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cfb import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cfb-live")
            proc = run_cli(["-C", tmp, "--from", "cfb", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cfb-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cfb-live", lsrc)
            self.assertNotIn("cfb-dead", lsrc)

    def test_class_body_if_for_attr_is_live(self):
        body = (
            "class T:\n"
            "    if True:\n"
            "        for _ in [1]:\n"
            "            x = 1\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cifor-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cifor-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cifor.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cifor import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cifor-live")
            proc = run_cli(["-C", tmp, "--from", "cifor", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cifor-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cifor-live", lsrc)
            self.assertNotIn("cifor-dead", lsrc)

    def test_class_body_empty_for_else_is_dead(self):
        body = (
            "class T:\n"
            "    for _ in []:\n"
            "        x = 1\n"
            "    else:\n"
            "        x = 0\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cff2-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cff2-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cff2.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cff2 import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cff2-dead")
            proc = run_cli(["-C", tmp, "--from", "cff2", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cff2-dead", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cff2-dead", lsrc)
            self.assertNotIn("cff2-live", lsrc)

    def test_class_body_nested_if_attr_is_live(self):
        body = (
            "class T:\n"
            "    if True:\n"
            "        if True:\n"
            "            x = 1\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cni-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cni-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cni.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cni import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cni-live")
            proc = run_cli(["-C", tmp, "--from", "cni", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cni-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cni-live", lsrc)
            self.assertNotIn("cni-dead", lsrc)

    def test_class_body_match_attr_is_live(self):
        body = (
            "class T:\n"
            "    match 1:\n"
            "        case 1:\n"
            "            x = 1\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'cmh-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cmh-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cmh.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cmh import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cmh-live")
            proc = run_cli(["-C", tmp, "--from", "cmh", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cmh-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cmh-live", lsrc)
            self.assertNotIn("cmh-dead", lsrc)

    def test_class_body_if_test_walrus_is_live(self):
        body = (
            "class T:\n"
            "    if (x := 1):\n"
            "        y = x\n"
            "if T.y:\n"
            "    def parse(x):\n"
            "        return 'cw-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'cw-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"cw.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from cw import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "cw-live")
            proc = run_cli(["-C", tmp, "--from", "cw", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("cw-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("cw-live", lsrc)
            self.assertNotIn("cw-dead", lsrc)

    def test_not_missing_attr_if_else_is_not_list_bind(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if not T.x:\n"
            "    def parse(x):\n"
            "        return 'nda2-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'nda2-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"nda2.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from nda2 import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "nda2", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("nda2.parse", binds)

    def test_or_missing_attr_if_else_is_not_list_bind(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if T.x or True:\n"
            "    def parse(x):\n"
            "        return 'oda-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'oda-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"oda.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from oda import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "oda", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("oda.parse", binds)

    def test_del_name_not_if_else_is_not_list_bind(self):
        body = (
            "x = 1\n"
            "del x\n"
            "if not x:\n"
            "    def parse(y):\n"
            "        return 'ndn-live'\n"
            "else:\n"
            "    def parse(y):\n"
            "        return 'ndn-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ndn.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from ndn import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "ndn", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("ndn.parse", binds)

    def test_leftover_ast_still_helper_after_class_body_for(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class ConstBoolOpMatchMissingCollTests(unittest.TestCase):
    def test_and_returns_operand_eq(self):
        body = (
            "if (1 and 2) == 2:\n"
            "    def parse(x):\n"
            "        return 'ae-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'ae-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"andeq.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from andeq import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "ae-live")
            proc = run_cli(["-C", tmp, "--from", "andeq", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("ae-live", source_text(parse_output(proc.stdout)[0]["source"]))
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("ae-live", lsrc)
            self.assertNotIn("ae-dead", lsrc)

    def test_and_is_true_is_dead(self):
        body = (
            "if (1 and 2) is True:\n"
            "    def parse(x):\n"
            "        return 'ait-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'ait-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ait.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from ait import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "ait-dead")
            proc = run_cli(["-C", tmp, "--from", "ait", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("ait-dead", lsrc)
            self.assertNotIn("ait-live", lsrc)

    def test_mixed_name_attr_assign_is_dead(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "T.x = y = 0\n"
            "if T.x:\n"
            "    def parse(x):\n"
            "        return 'mx-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'mx-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"mx.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from mx import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "mx-dead")
            proc = run_cli(["-C", tmp, "--from", "mx", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("mx-dead", lsrc)
            self.assertNotIn("mx-live", lsrc)

    def test_list_missing_attr_if_else_is_not_list_bind(self):
        body = (
            "class T:\n"
            "    x = 1\n"
            "del T.x\n"
            "if [T.x]:\n"
            "    def parse(x):\n"
            "        return 'lda-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'lda-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"lda.py": body, "pkg_parse.py": PARSE_MOVED})
            honesty = subprocess.run(
                [sys.executable, "-c", "from lda import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertNotEqual(honesty.returncode, 0)
            proc = run_cli(["-C", tmp, "--from", "lda", "parse"])
            self.assertNotEqual(proc.returncode, 0)
            binds = [r["bind"] for r in parse_output(run_cli(["-C", tmp, "parse"]).stdout)[1:]]
            self.assertNotIn("lda.parse", binds)

    def test_match_sequence_is_live(self):
        body = (
            "match (1,):\n"
            "    case (1,):\n"
            "        def parse(x):\n"
            "            return 'msq-live'\n"
            "    case _:\n"
            "        def parse(x):\n"
            "            return 'msq-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"msq.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from msq import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "msq-live")
            proc = run_cli(["-C", tmp, "--from", "msq", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("msq-live", lsrc)
            self.assertNotIn("msq-dead", lsrc)

    def test_class_match_as_capture_is_live(self):
        body = (
            "class T:\n"
            "    match 1:\n"
            "        case x:\n"
            "            y = x\n"
            "if T.y:\n"
            "    def parse(x):\n"
            "        return 'mas-live'\n"
            "else:\n"
            "    def parse(x):\n"
            "        return 'mas-dead'\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"mas.py": body})
            honesty = subprocess.run(
                [sys.executable, "-c", "from mas import parse; print(parse('z'))"],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
            self.assertEqual(honesty.returncode, 0, honesty.stderr)
            self.assertEqual(honesty.stdout.strip(), "mas-live")
            proc = run_cli(["-C", tmp, "--from", "mas", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            lsrc = source_text(parse_output(listed.stdout)[1]["source"])
            self.assertIn("mas-live", lsrc)
            self.assertNotIn("mas-dead", lsrc)

    def test_leftover_ast_still_helper_after_boolop_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "ast", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["file"], "ast.py")
            self.assertIn("leftover-ast", source_text(row["source"]))
            src = Path(__file__).resolve().parents[1] / "bindname"
            self.assertNotIn("import_module", src.read_text(encoding="utf-8"))


class Specimen010StdoutTests(unittest.TestCase):
    def test_loader_prints_are_not_in_tsv(self):
        specimen = find_run_specimen("specimen-010")
        if specimen is None:
            self.skipTest("specimen-010 not found")
        files = specimen / "files"
        proc = run_cli(["-C", str(files), "--from", "loader", "load_skip_empty"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(proc.stdout.startswith("query\t"), proc.stdout)
        self.assertNotIn("skip_empty", proc.stdout.split("\t")[0])
        self.assertNotIn("skip_empty '/x'", proc.stdout)
        self.assertNotIn("after_eval", proc.stdout)
        row = parse_output(proc.stdout)[0]
        self.assertEqual(row["query"], "from loader import load_skip_empty")
        self.assertEqual(row["bind"], "loader.load_skip_empty")
        self.assertEqual(row["kind"], "def")


if __name__ == "__main__":
    unittest.main()

