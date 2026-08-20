#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import alibi  # noqa: E402


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=check,
        capture_output=True,
        text=True,
    )


def init_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "alibi@test")
    _git(repo, "config", "user.name", "alibi")
    _git(repo, "config", "commit.gpgsign", "false")
    return repo


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit_all(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


LOCKED_PROD_HEAD = "def add(a, b):\n    return 0\n"
LOCKED_PROD_NEW = "def add(a, b):\n    return a + b\n"
LOCKED_TEST = """\
import unittest
import adder

class AddTest(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
"""

LOOSE_PROD_HEAD = "def add(a, b):\n    return a + b\n"
LOOSE_PROD_NEW = "def add(a, b):\n    # definitely correct\n    return a + b\n"

UNBUILD_PROD_HEAD = "def add(a, b):\n    return a + b\n"
UNBUILD_PROD_NEW = "def add(a, b):\n    return a + b\n\ndef mul(a, b):\n    return a * b\n"
UNBUILD_TEST = """\
import unittest
import adder

class AddTest(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 5)
    def test_mul(self):
        self.assertEqual(adder.mul(2, 3), 6)
"""

BROKEN_TEST = """\
import unittest
import adder

class AddTest(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(adder.add(2, 3), 99)
"""

CMD = [sys.executable, "-m", "unittest", "discover", "-q"]


class PathHeuristics(unittest.TestCase):
    def test_src_is_production(self):
        self.assertFalse(alibi.is_test_path("src/adder.py"))
        self.assertFalse(alibi.is_test_path("adder.py"))
        self.assertFalse(alibi.is_test_path("Sources/App/Foo.swift"))
        self.assertEqual(alibi.path_role("src/adder.py"), "production")
        self.assertEqual(alibi.path_role("Sources/App/Foo.swift"), "production")
        self.assertEqual(alibi.path_role("README.md"), "other")
        self.assertEqual(alibi.path_role("AGENTS.md"), "other")
        self.assertEqual(alibi.path_role(".gitignore"), "other")

    def test_fixtures_are_tests(self):
        self.assertTrue(alibi.is_test_path("data/fixtures/golden/foo.expected.json"))
        self.assertTrue(alibi.is_test_path("src/__snapshots__/a.snap"))
        self.assertEqual(alibi.path_role("data/fixtures/golden/foo.json"), "test")

    def test_tests_dir(self):
        self.assertTrue(alibi.is_test_path("tests/test_adder.py"))
        self.assertTrue(alibi.is_test_path("Tests/AppTests/Foo.swift"))
        self.assertTrue(alibi.is_test_path("src/__tests__/foo.test.ts"))

    def test_filename_patterns(self):
        self.assertTrue(alibi.is_test_path("test_adder.py"))
        self.assertTrue(alibi.is_test_path("adder_test.go"))
        self.assertTrue(alibi.is_test_path("foo.test.ts"))
        self.assertTrue(alibi.is_test_path("foo.spec.tsx"))
        self.assertTrue(alibi.is_test_path("conftest.py"))

    def test_extra_keep_regex(self):
        rx = alibi.re.compile(r"^schema/")
        self.assertTrue(alibi.is_test_path("schema/case.json", [rx]))
        self.assertFalse(alibi.is_test_path("schema/case.json"))
        self.assertEqual(alibi.path_role("schema/case.json"), "other")


class ClassifyFailure(unittest.TestCase):
    def test_assertion_is_locked(self):
        out = "FAIL: test_sum (test_adder.AddTest)\nAssertionError: 0 != 5\n"
        st = alibi.classify_splice_failure(out, alibi.parse_witnesses(out))
        self.assertEqual(st, "LOCKED")

    def test_import_is_unbuildable(self):
        out = "ERROR: test_adder (unittest.loader._FailedTest.test_adder)\nModuleNotFoundError: No module named 'adder'\n"
        st = alibi.classify_splice_failure(out, alibi.parse_witnesses(out))
        self.assertEqual(st, "UNBUILDABLE")


class WitnessParse(unittest.TestCase):
    def test_unittest_fail(self):
        out = "FAIL: test_sum (test_adder.AddTest.test_sum)\n"
        self.assertIn("test_sum", alibi.parse_witnesses(out)[0])

    def test_pytest_failed(self):
        out = "FAILED tests/test_adder.py::AddTest::test_sum - assert 0 == 5\n"
        self.assertTrue(any("test_adder" in w for w in alibi.parse_witnesses(out)))

    def test_cargo_failed(self):
        out = "test parse::new_syntax ... FAILED\n"
        self.assertEqual(alibi.parse_witnesses(out), ["parse::new_syntax"])


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="alibi-test-")
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _locked_repo(self) -> Path:
        repo = init_repo(self.tmp, "locked")
        write(repo, "adder.py", LOCKED_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "red implementation")
        write(repo, "adder.py", LOCKED_PROD_NEW)
        return repo

    def test_locked_uncommitted_production(self):
        repo = self._locked_repo()
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "LOCKED")
        self.assertEqual(report.production_changed, ["adder.py"])
        self.assertTrue(report.new_run and report.new_run.ok)
        self.assertTrue(report.splice_run and not report.splice_run.ok)

    def test_loose_comment_only(self):
        repo = init_repo(self.tmp, "loose")
        write(repo, "adder.py", LOOSE_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "green")
        write(repo, "adder.py", LOOSE_PROD_NEW)
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "LOOSE")
        self.assertEqual(report.production_changed, ["adder.py"])

    def test_clean_when_nothing_changed(self):
        repo = init_repo(self.tmp, "clean")
        write(repo, "adder.py", LOOSE_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "green")
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "CLEAN")
        self.assertEqual(report.production_changed, [])

    def test_test_only_change_is_clean_for_production(self):
        repo = init_repo(self.tmp, "testonly")
        write(repo, "adder.py", LOOSE_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "green")
        write(repo, "test_adder.py", LOCKED_TEST + "\n# extra coverage of existing behavior\n")
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "CLEAN")

    def test_broken_new_tree(self):
        repo = init_repo(self.tmp, "broken")
        write(repo, "adder.py", LOOSE_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "green")
        write(repo, "adder.py", LOOSE_PROD_NEW)
        write(repo, "test_adder.py", BROKEN_TEST)
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "BROKEN")
        self.assertEqual(report.production_changed, ["adder.py"])

    def test_markdown_only_is_clean(self):
        repo = init_repo(self.tmp, "docs")
        write(repo, "adder.py", LOOSE_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        write(repo, "README.md", "# v1\n")
        commit_all(repo, "green")
        write(repo, "README.md", "# v2 dirty docs\n")
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "CLEAN")
        self.assertEqual(report.production_changed, [])

    def test_per_path_mixed_locked_and_loose(self):
        repo = init_repo(self.tmp, "mixed")
        write(repo, "adder.py", LOCKED_PROD_HEAD)
        write(repo, "util.py", "def ping():\n    return 'ok'\n")
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "red add, unused util")
        write(repo, "adder.py", LOCKED_PROD_NEW)
        write(repo, "util.py", "def ping():\n    # comment only\n    return 'ok'\n")
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=True)
        self.assertEqual(report.status, "LOCKED")
        self.assertEqual(report.per_path.get("adder.py"), "LOCKED")
        self.assertEqual(report.per_path.get("util.py"), "LOOSE")

    def test_unbuildable_new_symbol(self):
        repo = init_repo(self.tmp, "unbuild")
        write(repo, "adder.py", UNBUILD_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "only add")
        write(repo, "adder.py", UNBUILD_PROD_NEW)
        write(repo, "test_adder.py", UNBUILD_TEST)
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        # splice deletes mul(); tests import/call it → fail. AttributeError is
        # closer to LOCKED than collection ImportError; accept either.
        self.assertIn(report.status, {"LOCKED", "UNBUILDABLE"})
        self.assertTrue(report.splice_run and not report.splice_run.ok)

    def test_added_production_module_is_locked(self):
        repo = init_repo(self.tmp, "added")
        write(repo, "adder.py", LOOSE_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "add only")
        write(repo, "mul.py", "def mul(a, b):\n    return a * b\n")
        write(
            repo,
            "test_mul.py",
            "import unittest\nimport mul\nclass T(unittest.TestCase):\n    def test_m(self):\n        self.assertEqual(mul.mul(2, 3), 6)\n",
        )
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertIn(report.status, {"LOCKED", "UNBUILDABLE"})
        self.assertIn("mul.py", report.production_changed)

    def test_list_plan_does_not_run_tests(self):
        repo = self._locked_repo()
        from io import StringIO
        from contextlib import redirect_stdout
        buf = StringIO()
        with redirect_stdout(buf):
            code = alibi.main(["-C", str(repo), "--list", "--json"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["production_changed"], ["adder.py"])

    def test_json_locked_exit_zero(self):
        repo = self._locked_repo()
        from io import StringIO
        from contextlib import redirect_stdout
        buf = StringIO()
        with redirect_stdout(buf):
            code = alibi.main(["-C", str(repo), "--json", "--cmd", " ".join(CMD)])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["status"], "LOCKED")
        self.assertTrue(all("failures=" not in w for w in payload["witnesses"]))

    def test_json_loose_exit_two(self):
        repo = init_repo(self.tmp, "loose-cli")
        write(repo, "adder.py", LOOSE_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "green")
        write(repo, "adder.py", LOOSE_PROD_NEW)
        from io import StringIO
        from contextlib import redirect_stdout
        buf = StringIO()
        with redirect_stdout(buf):
            code = alibi.main(["-C", str(repo), "--json", "--cmd", " ".join(CMD)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(buf.getvalue())["status"], "LOOSE")

    def test_tests_dir_kept_from_new(self):
        repo = init_repo(self.tmp, "testsdir")
        write(repo, "adder.py", LOCKED_PROD_HEAD)
        write(repo, "tests/test_adder.py", LOCKED_TEST)
        write(repo, "tests/__init__.py", "")
        commit_all(repo, "red")
        write(repo, "adder.py", LOCKED_PROD_NEW)
        report = alibi.run_alibi(repo, "HEAD", None, CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "LOCKED")
        self.assertTrue(any(p.path.endswith("test_adder.py") and p.source == "new" for p in report.plan))
        self.assertTrue(any(p.path == "adder.py" and p.source == "base" for p in report.plan))

    def test_new_ref_ignores_worktree(self):
        repo = init_repo(self.tmp, "newref")
        write(repo, "adder.py", LOCKED_PROD_HEAD)
        write(repo, "test_adder.py", LOCKED_TEST)
        commit_all(repo, "red")
        write(repo, "adder.py", LOCKED_PROD_NEW)
        commit_all(repo, "green")
        # dirty the worktree with a broken test; --new HEAD should still be green/LOCKED vs HEAD~1
        write(repo, "test_adder.py", BROKEN_TEST)
        report = alibi.run_alibi(repo, "HEAD~1", "HEAD", CMD, 30.0, [], per_path=False)
        self.assertEqual(report.status, "LOCKED")
        self.assertEqual(report.new, "HEAD")


class ListAndDetect(unittest.TestCase):
    def test_detect_unittest_default(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "tests").mkdir()
            cmd = alibi.detect_cmd(root)
            self.assertEqual(cmd[-1], "-q")
            self.assertIn("unittest", cmd)
            self.assertIn("-s", cmd)
            self.assertIn("tests", cmd)


if __name__ == "__main__":
    unittest.main()
