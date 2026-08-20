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

import mute as M  # noqa: E402


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, check=check, capture_output=True, text=True)


def init_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "mute@test")
    _git(repo, "config", "user.name", "mute")
    _git(repo, "config", "commit.gpgsign", "false")
    return repo


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit_all(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


# Pads keep add(), extra(), DEBUG, and a debug print in separate -U0 hunks.
APP_BASE = """\
def add(a, b):
    x = 0

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
    print("debug")

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
    cmd = [sys.executable, str(ROOT / "mute.py"), "-C", str(repo), "--json"]
    if extra:
        cmd.extend(extra)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    payload = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    if not payload:
        payload = {"_stderr": proc.stderr, "_stdout": proc.stdout, "_code": proc.returncode}
    return proc.returncode, payload


def added(units: list[dict]) -> str:
    return " ".join(" ".join(u.get("added") or []) for u in units)


class PathHeuristics(unittest.TestCase):
    def test_src_is_production(self):
        self.assertEqual(M.path_role("src/adder.py"), "production")
        self.assertEqual(M.path_role("README.md"), "other")
        self.assertEqual(M.path_role("AGENTS.md"), "other")

    def test_tests_are_tests(self):
        self.assertEqual(M.path_role("tests/test_adder.py"), "test")
        self.assertEqual(M.path_role("test.py"), "test")
        self.assertTrue(M.is_test_path("src/__tests__/foo.ts"))

    def test_extensionless_without_blob_is_other(self):
        self.assertEqual(M.path_role("mute"), "other")

    def test_extensionless_shebang_is_production(self):
        blob = b"#!/usr/bin/env bash\nset -euo pipefail\n"
        self.assertEqual(M.path_role("mute", blob=blob), "production")
        self.assertTrue(M.is_shebang_script("mute", blob))
        self.assertFalse(M.is_shebang_script("README.md", b"#!/usr/bin/env\n"))
        self.assertFalse(M.is_shebang_script("mute", b"echo hi\n"))


class TestDiscovery(unittest.TestCase):
    def test_old_names_are_not_new(self):
        old = set(M.python_test_ids(TEST_BASE.encode()))
        new = M.python_test_ids(TEST_PR.encode())
        born = [i for i in new if i not in old]
        self.assertEqual(born, ["TestApp.test_add"])
        self.assertIn("TestApp.test_extra", old)


class RangeParse(unittest.TestCase):
    def test_three_dot(self):
        self.assertEqual(M.split_range_token("main...HEAD"), ("main", "HEAD", "three"))

    def test_two_dot(self):
        self.assertEqual(M.split_range_token("a..b"), ("a", "b", "two"))


class ExitCodes(unittest.TestCase):
    def test_mute_empty_is_zero(self):
        self.assertEqual(M.status_exit("LOCKED"), 0)
        self.assertEqual(M.status_exit("CLEAN"), 0)

    def test_unlocked_is_one(self):
        self.assertEqual(M.status_exit("MUTE"), 1)

    def test_error_is_two(self):
        self.assertEqual(M.status_exit("BROKEN"), 2)
        self.assertEqual(M.status_exit("FOREIGN"), 2)
        self.assertEqual(M.status_exit("EMPTY"), 2)


class EndToEnd(unittest.TestCase):
    def test_new_test_locks_add_not_debug_print(self):
        with tempfile.TemporaryDirectory() as td:
            repo = make_pr(Path(td), "pr")
            self.assertEqual(_git(repo, "status", "--porcelain").stdout.strip(), "")
            code, payload = run_tool(repo, ["main...HEAD"])
            self.assertEqual(payload.get("status"), "MUTE", payload)
            self.assertEqual(code, 1, payload)
            self.assertEqual([t["id"] for t in payload["new_tests"]], ["TestApp.test_add"], payload)
            mute_added = added(payload["mute"])
            locked_added = added(payload["locked"])
            self.assertIn("return a + b", locked_added, payload)
            self.assertNotIn('print("debug")', locked_added, payload)
            self.assertIn('print("debug")', mute_added, payload)
            self.assertNotIn("return a + b", mute_added, payload)
            self.assertIn("DEBUG = True", mute_added, payload)
            self.assertIn("return 1", mute_added, payload)

    def test_production_only_pr_is_all_mute(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "prodonly")
            write(repo, "app.py", APP_BASE)
            write(repo, "tests/__init__.py", "")
            write(repo, "tests/test_app.py", TEST_BASE)
            commit_all(repo, "main")
            _git(repo, "checkout", "-b", "pr")
            write(repo, "app.py", APP_PR)
            write(
                repo,
                "tests/test_app.py",
                TEST_BASE.replace("extra(), 0", "extra(), 1"),
            )
            commit_all(repo, "no new tests")
            code, payload = run_tool(repo, ["main...HEAD"])
            self.assertEqual(payload.get("status"), "MUTE", payload)
            self.assertEqual(code, 1, payload)
            self.assertEqual(payload.get("new_tests"), [], payload)
            self.assertEqual(payload.get("reason"), "no-new-tests", payload)
            self.assertTrue(payload.get("mute"), payload)
            self.assertEqual(payload.get("locked"), [], payload)
            self.assertGreaterEqual(len(payload["mute"]), payload["production_units"])

    def test_tests_only_pr_is_empty_mute(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "testsonly")
            write(repo, "app.py", "def add(a, b):\n    return a + b\n")
            write(repo, "tests/__init__.py", "")
            write(
                repo,
                "tests/test_app.py",
                "import unittest\nfrom app import add\n"
                "class TestApp(unittest.TestCase):\n"
                "    def test_old(self):\n"
                "        self.assertEqual(add(2, 3), 5)\n",
            )
            commit_all(repo, "green")
            _git(repo, "checkout", "-b", "pr")
            write(
                repo,
                "tests/test_app.py",
                "import unittest\nfrom app import add\n"
                "class TestApp(unittest.TestCase):\n"
                "    def test_old(self):\n"
                "        self.assertEqual(add(2, 3), 5)\n"
                "    def test_new(self):\n"
                "        self.assertEqual(add(0, 0), 0)\n",
            )
            commit_all(repo, "tests only")
            code, payload = run_tool(repo, ["main...HEAD"])
            self.assertEqual(payload.get("status"), "CLEAN", payload)
            self.assertEqual(code, 0, payload)
            self.assertEqual(payload.get("mute"), [], payload)
            self.assertEqual(payload.get("production_units"), 0, payload)

    def test_shebang_wrapper_is_mute_not_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "shebang")
            write(repo, "app.py", "def add(a, b):\n    return 0\n")
            write(repo, "tests/__init__.py", "")
            write(
                repo,
                "tests/test_app.py",
                "import unittest\nclass T(unittest.TestCase):\n"
                "    def test_placeholder(self):\n"
                "        self.assertTrue(True)\n",
            )
            commit_all(repo, "base")
            _git(repo, "checkout", "-b", "pr")
            write(repo, "app.py", "def add(a, b):\n    return a + b\n")
            write(repo, "tool", "#!/usr/bin/env bash\nexec python3 app.py\n")
            write(
                repo,
                "tests/test_app.py",
                "import unittest\nfrom app import add\n"
                "class T(unittest.TestCase):\n"
                "    def test_placeholder(self):\n"
                "        self.assertTrue(True)\n"
                "    def test_add(self):\n"
                "        self.assertEqual(add(2, 3), 5)\n",
            )
            commit_all(repo, "fix + wrapper")
            code, payload = run_tool(repo, ["main...HEAD"])
            self.assertEqual(payload.get("status"), "MUTE", payload)
            self.assertEqual(code, 1, payload)
            mute_paths = {m["path"] for m in payload["mute"]}
            locked_paths = {m["path"] for m in payload["locked"]}
            self.assertIn("tool", mute_paths, payload)
            self.assertIn("app.py", locked_paths, payload)
            self.assertNotIn("tool", payload.get("ignored", []), payload)

    def test_all_production_locked_is_empty_mute(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "alllocked")
            write(repo, "app.py", "def add(a, b):\n    return 0\n")
            write(repo, "tests/__init__.py", "")
            write(
                repo,
                "tests/test_app.py",
                "import unittest\nclass T(unittest.TestCase):\n"
                "    def test_placeholder(self):\n"
                "        self.assertTrue(True)\n",
            )
            commit_all(repo, "base")
            _git(repo, "checkout", "-b", "pr")
            write(repo, "app.py", "def add(a, b):\n    return a + b\n")
            write(
                repo,
                "tests/test_app.py",
                "import unittest\nfrom app import add\n"
                "class T(unittest.TestCase):\n"
                "    def test_placeholder(self):\n"
                "        self.assertTrue(True)\n"
                "    def test_add(self):\n"
                "        self.assertEqual(add(2, 3), 5)\n",
            )
            commit_all(repo, "fix")
            code, payload = run_tool(repo, ["main...HEAD"])
            self.assertEqual(payload.get("status"), "LOCKED", payload)
            self.assertEqual(code, 0, payload)
            self.assertEqual(payload.get("mute"), [], payload)
            self.assertTrue(payload.get("locked"), payload)


if __name__ == "__main__":
    unittest.main()
