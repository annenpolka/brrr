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

import tock as C  # noqa: E402


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, check=check, capture_output=True, text=True)


def init_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "cinch@test")
    _git(repo, "config", "user.name", "cinch")
    _git(repo, "config", "commit.gpgsign", "false")
    return repo


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit_all(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


def run_tool(repo: Path, extra: list[str] | None = None) -> tuple[int, dict]:
    cmd = [sys.executable, str(ROOT / "tock.py"), "-C", str(repo), "--json"]
    if extra:
        cmd.extend(extra)
    cmd += ["--", sys.executable, "test.py"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    payload = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    return proc.returncode, payload


class PathHeuristics(unittest.TestCase):
    def test_src_is_production(self):
        self.assertEqual(C.path_role("src/adder.py"), "production")
        self.assertEqual(C.path_role("Sources/App/Foo.swift"), "production")
        self.assertEqual(C.path_role("README.md"), "other")
        self.assertEqual(C.path_role("AGENTS.md"), "other")
        self.assertEqual(C.path_role(".gitignore"), "other")

    def test_tests_are_held(self):
        self.assertEqual(C.path_role("tests/test_adder.py"), "test")
        self.assertEqual(C.path_role("test.py"), "test")
        self.assertEqual(C.path_role("test_adder.py"), "test")
        self.assertEqual(C.path_role("adder_test.go"), "test")
        self.assertEqual(C.path_role("data/fixtures/golden/foo.expected.json"), "test")
        self.assertTrue(C.is_test_path("src/__tests__/foo.ts"))

    def test_sh_is_production_md_is_not(self):
        self.assertEqual(C.path_role("demo.sh"), "production")
        self.assertEqual(C.path_role("Makefile"), "production")
        self.assertEqual(C.path_role("package.json"), "other")


class EmptySuite(unittest.TestCase):
    def test_exit_5_is_empty(self):
        r = C.RunResult(5, 0.01, "Ran 0 tests in 0.000s\n\nNO TESTS RAN\n")
        self.assertTrue(C.empty_suite(r))
        self.assertFalse(r.ok)

    def test_assertion_failure_is_not_empty(self):
        r = C.RunResult(1, 0.01, "FAIL: test_sum\nAssertionError\n")
        self.assertFalse(C.empty_suite(r))


class HunkApply(unittest.TestCase):
    def test_apply_two_separated_hunks(self):
        head = b"a\nb\nc\nd\ne\nf\ng\nh\ni\n"
        # replace line 1 'a' with 'A', and line 9 'i' with 'I'
        h1 = C.Hunk(
            path="t.txt",
            kind="modify",
            role="production",
            head=head,
            wip=None,
            hunk_index=1,
            hunk_header="@@ -1 +1 @@",
            old_start=1,
            old_count=1,
            body=("-a", "+A"),
        )
        h2 = C.Hunk(
            path="t.txt",
            kind="modify",
            role="production",
            head=head,
            wip=None,
            hunk_index=2,
            hunk_header="@@ -9 +9 @@",
            old_start=9,
            old_count=1,
            body=("-i", "+I"),
        )
        out = C.apply_hunks(head, [h1]).decode()
        self.assertEqual(out, "A\nb\nc\nd\ne\nf\ng\nh\ni\n")
        out = C.apply_hunks(head, [h2]).decode()
        self.assertEqual(out, "a\nb\nc\nd\ne\nf\ng\nh\nI\n")
        out = C.apply_hunks(head, [h1, h2]).decode()
        self.assertEqual(out, "A\nb\nc\nd\ne\nf\ng\nh\nI\n")

    def test_parse_u0(self):
        diff = """\
@@ -2 +2 @@
-    return 0
+    return a + b
@@ -10 +10 @@
-    return 1
+    print("debug")
"""
        parsed = C.parse_u0_hunks(diff)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0][1], 2)
        self.assertEqual(parsed[1][1], 10)


class EndToEnd(unittest.TestCase):
    def test_lockset_drops_debug_print_and_held_tests(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "trap")
            write(
                repo,
                "app.py",
                "def add(a, b):\n    x = 0\n\n    return 0\n",
            )
            write(repo, "test.py", "from app import add\nassert add(2, 3) == 5\n")
            write(repo, "README.md", "v1\n")
            commit_all(repo, "base")
            write(
                repo,
                "app.py",
                'def add(a, b):\n    print("debug")\n\n    return a + b\n',
            )
            write(repo, "test.py", "# new assertion\nfrom app import add\nassert add(2, 3) == 5\n")
            write(repo, "README.md", "v2\n")
            code, payload = run_tool(repo)
            self.assertEqual(payload.get("status"), "LOCKED", payload)
            self.assertEqual(code, 0)
            wheat_ids = [w["id"] for w in payload["wheat"]]
            self.assertEqual([w["path"] for w in payload["wheat"]], ["app.py"], payload)
            self.assertEqual(len(payload["wheat"]), 1, payload)
            # git -U0: line 2 is the debug print (chaff), line 4 is the return (wheat)
            self.assertEqual(payload["wheat"][0].get("hunk"), 2, payload)
            self.assertTrue(
                any(c["path"] == "app.py" and c.get("hunk") == 1 for c in payload["chaff"]),
                payload,
            )
            self.assertIn("test.py", payload["held_tests"])
            self.assertIn("README.md", payload["ignored"])
            self.assertTrue(all(not i.startswith("test.py") for i in wheat_ids), wheat_ids)

    def test_loose_comment_only(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "loose")
            write(repo, "app.py", "def add(a, b):\n    return a + b\n")
            write(repo, "test.py", "from app import add\nassert add(2, 3) == 5\n")
            commit_all(repo, "green")
            write(repo, "app.py", "def add(a, b):\n    # note\n    return a + b\n")
            code, payload = run_tool(repo)
            self.assertEqual(payload.get("status"), "LOOSE", payload)
            self.assertEqual(code, 2)
            self.assertEqual(payload["wheat"], [])

    def test_clean_test_only(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "clean")
            write(repo, "app.py", "def add(a, b):\n    return a + b\n")
            write(repo, "test.py", "from app import add\nassert add(2, 3) == 5\n")
            commit_all(repo, "green")
            write(repo, "test.py", "# extra\nfrom app import add\nassert add(2, 3) == 5\n")
            code, payload = run_tool(repo)
            self.assertEqual(payload.get("status"), "CLEAN", payload)
            self.assertEqual(code, 0)
            self.assertEqual(payload["production_units"], 0)

    def test_test_only_red_is_broken(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "red")
            write(repo, "app.py", "def add(a, b):\n    return a + b\n")
            write(repo, "test.py", "from app import add\nassert add(2, 3) == 5\n")
            commit_all(repo, "green")
            write(repo, "test.py", "from app import add\nassert add(2, 3) == 99\n")
            code, payload = run_tool(repo)
            self.assertEqual(payload.get("status"), "BROKEN", payload)
            self.assertEqual(code, 3)
            self.assertEqual(payload["production_units"], 0)
            self.assertEqual(payload["wheat"], [])
            self.assertIn("test.py", payload["held_tests"])


class TimeoutGuilt(unittest.TestCase):
    """A splice timeout is not a fail witness and must not mint wheat."""

    FAST_HEAD = (
        "FAST = False\n"
        "# pad1\n# pad2\n# pad3\n# pad4\n"
        "# pad5\n# pad6\n# pad7\n# pad8\n"
        "VALUE = 0\n"
    )
    FAST_WIP = (
        "FAST = True\n"
        "# pad1\n# pad2\n# pad3\n# pad4\n"
        "# pad5\n# pad6\n# pad7\n# pad8\n"
        "VALUE = 1\n"
    )
    FAST_TEST = (
        "import app, time\n"
        "if not app.FAST:\n"
        "    time.sleep(1.5)\n"
        "assert app.VALUE == 1\n"
        "print('pass')\n"
    )

    def test_timeout_is_not_fail(self):
        r = C.RunResult(124, 0.4, "[tock: timed out after 0.4s]\n", True)
        self.assertFalse(r.ok)
        self.assertFalse(r.failed)
        self.assertTrue(r.timed_out)

    def test_fast_hunk_is_chaff_value_is_wheat(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "fast")
            write(repo, "app.py", self.FAST_HEAD)
            write(repo, "test.py", self.FAST_TEST)
            commit_all(repo, "base")
            write(repo, "app.py", self.FAST_WIP)
            code, payload = run_tool(repo, extra=["--timeout", "0.4"])
            self.assertEqual(payload.get("status"), "LOCKED", payload)
            self.assertEqual(code, 0)
            wheat = payload["wheat"]
            chaff = payload["chaff"]
            self.assertEqual(len(wheat), 1, payload)
            self.assertEqual(wheat[0].get("hunk"), 2, wheat)
            self.assertTrue(
                any(c.get("hunk") == 1 for c in chaff),
                chaff,
            )
            self.assertTrue(payload.get("splice_run", {}).get("timed_out"), payload)
            notes = " ".join(payload.get("notes") or [])
            self.assertIn("timeout", notes.lower())

    def test_only_fast_times_out_without_wheat(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "onlyfast")
            write(repo, "app.py", "FAST = False\n")
            write(
                repo,
                "test.py",
                "import app, time\n"
                "if not app.FAST:\n"
                "    time.sleep(1.5)\n"
                "print('pass')\n",
            )
            commit_all(repo, "base")
            write(repo, "app.py", "FAST = True\n")
            code, payload = run_tool(repo, extra=["--timeout", "0.4"])
            self.assertEqual(payload.get("status"), "TIMEOUT", payload)
            self.assertEqual(code, 6)
            self.assertEqual(payload.get("wheat"), [], payload)
            self.assertTrue(payload.get("splice_run", {}).get("timed_out"), payload)

    def test_new_timeout_is_broken(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "newto")
            write(repo, "app.py", "VALUE = 0\n")
            write(repo, "test.py", "import time\ntime.sleep(1.5)\nassert True\n")
            commit_all(repo, "base")
            write(repo, "app.py", "VALUE = 1\n")
            write(repo, "test.py", "import time\ntime.sleep(1.5)\nassert True\n")
            code, payload = run_tool(repo, extra=["--timeout", "0.4"])
            self.assertEqual(payload.get("status"), "BROKEN", payload)
            self.assertEqual(code, 3)
            self.assertEqual(payload.get("wheat"), [], payload)
            self.assertTrue(payload.get("new_run", {}).get("timed_out"), payload)


if __name__ == "__main__":
    unittest.main()
