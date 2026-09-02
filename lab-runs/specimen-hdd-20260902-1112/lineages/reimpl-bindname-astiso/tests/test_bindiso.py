#!/usr/bin/env python3
"""leftover vs moved; leftover ast.py; isolated query; static also."""

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
CLI = ROOT / "bindiso"

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
    loader = importlib.machinery.SourceFileLoader("bindiso_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


BI = load_mod()


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
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def write_fixture(tmp: str, files: dict[str, str]) -> Path:
    root = Path(tmp)
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def find_specimen() -> Path | None:
    env = os.environ.get("SPECIMEN")
    if env:
        cand = Path(env)
        if (cand / "files" / "pkg_util.py").is_file():
            return cand
    starts = [ROOT, Path.cwd(), Path(__file__).resolve()]
    seen: set[Path] = set()
    for start in starts:
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(start if start.is_dir() else start.parent),
                "rev-parse",
                "--show-toplevel",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            top = Path(proc.stdout.strip())
            if top not in seen:
                seen.add(top)
                cand = top / "lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013"
                if (cand / "files" / "pkg_util.py").is_file():
                    return cand
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(start if start.is_dir() else start.parent),
                "rev-parse",
                "--git-common-dir",
            ],
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
                cand = parent / "lab-runs/specimen-hdd-20260902-1112/specimens/specimen-013"
                if (cand / "files" / "pkg_util.py").is_file():
                    return cand
    return None


class SourceContractTests(unittest.TestCase):
    def test_cli_does_not_use_import_module(self):
        src = CLI.read_text(encoding="utf-8")
        self.assertNotIn("import_module", src)
        self.assertIn("spec_from_file_location", src)
        self.assertIn("_bindiso_", src)
        self.assertNotIn("inspect.getsource", src)


class LeftoverVsMovedTests(unittest.TestCase):
    def test_cli_from_util_reports_other_def(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED})
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

    def test_from_parse_binds_moved_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "--from", "pkg_parse", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["runs"], "pkg_parse.parse")
            self.assertIn("strip", source_text(row["source"]))
            self.assertEqual(row.get("also"), ["pkg_util.parse"])

    def test_list_two_defs_not_same(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED})
            proc = run_cli(["-C", tmp, "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "2")
            self.assertEqual(rows[0]["same_function"], "False")


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
            self.assertEqual(proc.stdout.splitlines()[0].split("\t", 1)[0], "query")
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

    def test_isolated_load_uses_unique_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(tmp, {"ast.py": AST_LEFTOVER, "pkg_parse.py": PARSE_MOVED})
            std_ast = sys.modules["ast"]
            module, unique = BI.load_isolated(root, "ast", root / "ast.py")
            self.assertTrue(unique.startswith("_bindiso_"), unique)
            self.assertNotEqual(unique, "ast")
            self.assertTrue(unique.endswith(".ast"), unique)
            self.assertEqual(module.parse("z"), ("leftover-ast", "z"))
            self.assertIs(sys.modules["ast"], std_ast)
            self.assertNotIn(unique, sys.modules)
            self.assertNotEqual(std_ast.parse, module.parse)


class ReexportTests(unittest.TestCase):
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

    def test_assignment_alias_is_reexport(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_parse.py": PARSE_MOVED,
                    "pkg_util.py": "import pkg_parse\nparse = pkg_parse.parse\n",
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "reexport")
            self.assertEqual(row["runs"], "pkg_parse.parse")
            self.assertEqual(row["same_function"], "True")


class ImporterFileTests(unittest.TestCase):
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
            proc = run_cli(
                ["-C", tmp, "--file", str(Path(tmp) / "test_parse_identity.py"), "parse"]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "2")
            self.assertEqual(rows[0]["same_function"], "False")
            binds = [r["bind"] for r in rows[1:]]
            self.assertEqual(binds, ["pkg_util.parse", "pkg_parse.parse"])

    def test_file_override_def_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                    "override.py": (
                        "from pkg_util import parse\n"
                        "def parse(x):\n"
                        "    return 'overridden-in-file'\n"
                    ),
                },
            )
            proc = run_cli(["-C", tmp, "--file", str(Path(tmp) / "override.py"), "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "1")
            self.assertEqual(rows[1]["kind"], "def")
            self.assertIn("overridden-in-file", source_text(rows[1]["source"]))
            self.assertNotIn("legacy", source_text(rows[1]["source"]))

    def test_file_as_alias_queryable(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                    "alias.py": "from pkg_util import parse as parse_legacy\n",
                },
            )
            missing = run_cli(["-C", tmp, "--file", str(Path(tmp) / "alias.py"), "parse"])
            self.assertEqual(missing.returncode, 1)
            self.assertIn("no uses of parse", missing.stderr)
            proc = run_cli(
                ["-C", tmp, "--file", str(Path(tmp) / "alias.py"), "parse_legacy"]
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[1]["bind"], "pkg_util.parse")
            self.assertIn("legacy", source_text(rows[1]["source"]))


class IsolationTests(unittest.TestCase):
    def test_sys_exit_sibling_does_not_hostage(self):
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
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["runs"], "keep.parse")
            self.assertIn("kept", source_text(row["source"]))
            self.assertEqual(row.get("also"), ["killer.parse"])

    def test_aaa_patch_does_not_rewrite_queried_bind(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": PARSE_MOVED,
                    "aaa_patch.py": (
                        "import pkg_util\n"
                        "def _patched(x):\n    return ('patched', x)\n"
                        "pkg_util.parse = _patched\n"
                    ),
                },
            )
            marker = Path(tmp) / "patched.flag"
            (root / "aaa_patch.py").write_text(
                "import pkg_util\n"
                "def _patched(x):\n    return ('patched', x)\n"
                "pkg_util.parse = _patched\n"
                f"open({str(marker)!r}, 'w').write('yes')\n",
                encoding="utf-8",
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            row = parse_output(proc.stdout)[0]
            self.assertEqual(row["kind"], "def")
            self.assertEqual(row["runs"], "pkg_util.parse")
            self.assertIn("legacy", source_text(row["source"]))
            self.assertNotIn("patched", source_text(row["source"]))
            self.assertFalse(marker.exists())

    def test_sibling_stdout_not_in_tsv(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "pkg_util.py": UTIL_LEGACY,
                    "pkg_parse.py": "print('SIDE_EFFECT_STDOUT')\n" + PARSE_MOVED,
                },
            )
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("SIDE_EFFECT_STDOUT", proc.stdout)
            self.assertTrue(proc.stdout.startswith("query\t"), proc.stdout)

    def test_queried_stdout_not_mixed_into_record(self):
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
            self.assertTrue(proc.stdout.startswith("query\t"), proc.stdout)


class PresenceVsBindTests(unittest.TestCase):
    def test_annotation_only_is_not_def(self):
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
            self.assertIn("has no name", proc.stderr)
            listed = run_cli(["-C", tmp, "parse"])
            self.assertEqual(listed.returncode, 0, listed.stderr)
            rows = parse_output(listed.stdout)
            binds = [r.get("bind") for r in rows if "bind" in r]
            self.assertEqual(binds, ["pkg_parse.parse"])
            self.assertNotIn("ann.parse", binds)

    def test_boom_import_fail_is_not_last_wins(self):
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
            self.assertNotIn("moved.parse", proc.stdout)
            self.assertFalse(proc.stdout.strip().startswith("query"))

    def test_non_utf8_sibling_does_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED})
            (root / "junk.py").write_bytes(b"def parse(x):\n    return \xff\n")
            proc = run_cli(["-C", tmp, "--from", "pkg_util", "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertNotIn("UnicodeDecodeError", proc.stderr)
            self.assertNotIn("UnicodeDecodeError", proc.stdout)
            row = parse_output(proc.stdout)[0]
            self.assertIn("legacy", source_text(row["source"]))


class IdentityTests(unittest.TestCase):
    def test_symlink_pair_keeps_both_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
            os.symlink(root / "pkg_util.py", root / "pkg_parse.py")
            proc = run_cli(["-C", tmp, "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "2")
            self.assertEqual(rows[0]["same_function"], "False")
            binds = [r["bind"] for r in rows if "bind" in r]
            self.assertEqual(sorted(binds), ["pkg_parse.parse", "pkg_util.parse"])

    def test_hardlink_pair_keeps_both_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
            os.link(root / "pkg_util.py", root / "pkg_parse.py")
            proc = run_cli(["-C", tmp, "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "2")
            self.assertEqual(rows[0]["same_function"], "False")


class DottedAndImportStmtTests(unittest.TestCase):
    def test_dotted_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY, "pkg_parse.py": PARSE_MOVED})
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

    def test_star_import_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(tmp, {"pkg_util.py": UTIL_LEGACY})
            proc = run_cli(["-C", tmp, "--import", "from pkg_util import *"])
            self.assertEqual(proc.returncode, 2)
            self.assertIn("star", proc.stderr)

    def test_nested_def_is_not_an_import_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_fixture(
                tmp,
                {
                    "nested.py": "def outer():\n    def parse(x):\n        return x\n    return parse\n",
                    "pkg_parse.py": PARSE_MOVED,
                },
            )
            proc = run_cli(["-C", tmp, "parse"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_output(proc.stdout)
            self.assertEqual(rows[0]["count"], "1")
            binds = [r["bind"] for r in rows if "bind" in r]
            self.assertEqual(binds, ["pkg_parse.parse"])


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


if __name__ == "__main__":
    unittest.main()
