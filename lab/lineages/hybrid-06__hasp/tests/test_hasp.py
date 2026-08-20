#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import hasp as H  # noqa: E402


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, check=check, capture_output=True, text=True)


def init_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "hasp@test")
    _git(repo, "config", "user.name", "hasp")
    _git(repo, "config", "commit.gpgsign", "false")
    return repo


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit_all(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


APP_BASE = """\
def add(a, b):
    return 0


# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
def extra():
    return 0


# pad9
# pad10
# pad11
# pad12
# pad13
# pad14
# pad15
# pad16
DEBUG = False
"""

APP_PR = """\
def add(a, b):
    return a + b


# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
def extra():
    return 1


# pad9
# pad10
# pad11
# pad12
# pad13
# pad14
# pad15
# pad16
DEBUG = True
"""

TEST_BASE = """\
import unittest
from app import extra


class TestApp(unittest.TestCase):
    def test_extra(self):
        self.assertEqual(extra(), 0)
"""

TEST_PR = """\
import unittest
from app import add, extra


class TestApp(unittest.TestCase):
    def test_extra(self):
        self.assertEqual(extra(), 1)

    def test_add(self):
        self.assertEqual(add(2, 3), 5)
"""


def make_pr(parent: Path, name: str) -> Path:
    repo = init_repo(parent, name)
    write(repo, "app.py", APP_BASE)
    write(repo, "tests/__init__.py", "")
    write(repo, "tests/test_app.py", TEST_BASE)
    write(repo, "README.md", "v1\n")
    commit_all(repo, "main")
    _git(repo, "checkout", "-b", "pr")
    write(repo, "app.py", APP_PR)
    write(repo, "tests/test_app.py", TEST_PR)
    write(repo, "README.md", "v2\n")
    commit_all(repo, "feature")
    return repo


def run_tool(repo: Path, extra: list[str] | None = None) -> tuple[int, dict]:
    cmd = [sys.executable, str(ROOT / "hasp.py"), "-C", str(repo), "--json"]
    if extra:
        cmd.extend(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    payload = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    if not payload:
        payload = {"_stderr": proc.stderr, "_stdout": proc.stdout}
    return proc.returncode, payload


class PathHeuristics(unittest.TestCase):
    def test_src_is_production(self):
        self.assertEqual(H.path_role("src/adder.py"), "production")
        self.assertEqual(H.path_role("README.md"), "other")
        self.assertEqual(H.path_role("AGENTS.md"), "other")

    def test_tests_are_tests(self):
        self.assertEqual(H.path_role("tests/test_adder.py"), "test")
        self.assertEqual(H.path_role("test.py"), "test")
        self.assertTrue(H.is_test_path("src/__tests__/foo.ts"))


class TestDiscovery(unittest.TestCase):
    def test_named_methods_and_functions(self):
        src = b"""\
import unittest
def test_top():
    pass
class TestApp(unittest.TestCase):
    def test_a(self):
        pass
    def helper(self):
        pass
    def test_b(self):
        pass
class NotTests:
    def test_c(self):
        pass
"""
        ids = H.python_test_ids(src)
        self.assertEqual(ids, ["test_top", "TestApp.test_a", "TestApp.test_b", "NotTests.test_c"])

    def test_old_names_are_not_new(self):
        old = set(H.python_test_ids(TEST_BASE.encode()))
        new = H.python_test_ids(TEST_PR.encode())
        born = [i for i in new if i not in old]
        self.assertEqual(born, ["TestApp.test_add"])
        self.assertIn("TestApp.test_extra", old)


class RangeParse(unittest.TestCase):
    def test_three_dot(self):
        self.assertEqual(H.split_range_token("main...HEAD"), ("main", "HEAD", "three"))
        self.assertEqual(H.split_range_token("main..."), ("main", None, "three"))

    def test_two_dot(self):
        self.assertEqual(H.split_range_token("a..b"), ("a", "b", "two"))

    def test_not_a_range(self):
        self.assertIsNone(H.split_range_token("main"))


class LanguageNames(unittest.TestCase):
    def test_swift_testing_and_xctest(self):
        src = b'''
        @Test("cross-batch units compose")
        func composesCrossBatchUnitsInOriginalOrder() throws {}
        func testXCTestStyle() {}
        func helper() {}
        '''
        ids = H.swift_test_ids(src)
        self.assertIn("composesCrossBatchUnitsInOriginalOrder", ids)
        self.assertIn("testXCTestStyle", ids)
        self.assertNotIn("helper", ids)

    def test_js_it_names(self):
        src = b'''
        it("round-trips Forced Slash", async () => {})
        test("selects only Result", () => {})
        '''
        ids = H.js_test_ids(src)
        self.assertEqual(ids, ["round-trips Forced Slash", "selects only Result"])

    def test_init_and_golden_are_not_runnable(self):
        self.assertFalse(H.is_runnable_test_path("tests/__init__.py"))
        self.assertFalse(H.is_runnable_test_path("data/fixtures/golden/foo.expected.json"))
        self.assertFalse(H.is_runnable_test_path("specs/mechanics/slash.pkl"))
        self.assertTrue(H.is_runnable_test_path("tests/test_hasp.py"))
        self.assertTrue(H.is_runnable_test_path("Engine/Tests/EditPlanComposerTests.swift"))
        self.assertTrue(H.is_runnable_test_path("apps/cli/src/cli.test.ts"))


class EmptySuite(unittest.TestCase):
    def test_exit_5_is_empty(self):
        r = H.RunResult(5, 0.01, "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n")
        self.assertTrue(H.empty_suite(r))


class EndToEnd(unittest.TestCase):
    def test_committed_pr_new_test_drops_updated_old_lock(self):
        with tempfile.TemporaryDirectory() as td:
            repo = make_pr(Path(td), "pr")
            # clean worktree: the object is the range, not dirt
            st = _git(repo, "status", "--porcelain")
            self.assertEqual(st.stdout.strip(), "")
            code, payload = run_tool(repo, ["main...HEAD"])
            self.assertEqual(payload.get("status"), "LOCKED", payload)
            self.assertEqual(code, 0, payload)
            new_ids = [t["id"] for t in payload["new_tests"]]
            bg_ids = [t["id"] for t in payload["background_tests"]]
            self.assertEqual(new_ids, ["TestApp.test_add"], payload)
            self.assertIn("TestApp.test_extra", bg_ids)
            wheat_added = " ".join(" ".join(w.get("added") or []) for w in payload["wheat"])
            chaff_added = " ".join(" ".join(c.get("added") or []) for c in payload["chaff"])
            self.assertIn("return a + b", wheat_added, payload)
            self.assertNotIn("return 1", wheat_added, payload)
            self.assertNotIn("DEBUG = True", wheat_added, payload)
            self.assertIn("return 1", chaff_added, payload)
            self.assertIn("DEBUG = True", chaff_added, payload)
            self.assertEqual(len(payload["wheat"]), 1, payload)

    def test_mute_when_only_old_tests_changed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "mute")
            write(repo, "app.py", APP_BASE)
            write(repo, "tests/__init__.py", "")
            write(repo, "tests/test_app.py", TEST_BASE)
            commit_all(repo, "main")
            _git(repo, "checkout", "-b", "pr")
            write(repo, "app.py", APP_PR)
            write(
                repo,
                "tests/test_app.py",
                TEST_BASE.replace("return 0", "return 1").replace("extra(), 0", "extra(), 1"),
            )
            commit_all(repo, "no new tests")
            code, payload = run_tool(repo, ["main...HEAD"])
            self.assertEqual(payload.get("status"), "MUTE", payload)
            self.assertEqual(code, 6, payload)
            self.assertEqual(payload.get("new_tests"), [], payload)
            self.assertTrue(payload.get("production_units", 0) >= 1, payload)

    def test_head_is_clean_on_committed_pr_without_range(self):
        with tempfile.TemporaryDirectory() as td:
            repo = make_pr(Path(td), "cleanhead")
            code, payload = run_tool(repo, [])  # HEAD vs worktree, clean
            self.assertEqual(payload.get("status"), "CLEAN", payload)
            self.assertEqual(code, 0, payload)
            self.assertEqual(payload.get("production_units"), 0, payload)


if __name__ == "__main__":
    unittest.main()
