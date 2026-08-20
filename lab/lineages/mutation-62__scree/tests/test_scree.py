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

import scree as C  # noqa: E402


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, check=check, capture_output=True, text=True)


def init_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "scree@test")
    _git(repo, "config", "user.name", "scree")
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
    cmd = [sys.executable, str(ROOT / "scree.py"), "-C", str(repo), "--json"]
    if extra:
        cmd.extend(extra)
    cmd += ["--", sys.executable, "test.py"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    payload = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
    return proc.returncode, payload


class PathHeuristics(unittest.TestCase):
    def test_src_is_production(self):
        self.assertEqual(C.path_role("src/adder.py"), "production")
        self.assertEqual(C.path_role("README.md"), "other")

    def test_tests_are_held(self):
        self.assertEqual(C.path_role("tests/test_adder.py"), "test")
        self.assertEqual(C.path_role("test.py"), "test")
        self.assertTrue(C.is_test_path("src/__tests__/foo.ts"))

    def test_sh_is_production_md_is_not(self):
        self.assertEqual(C.path_role("demo.sh"), "production")
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
        self.assertEqual(C.apply_hunks(head, [h1]).decode(), "A\nb\nc\nd\ne\nf\ng\nh\ni\n")
        self.assertEqual(C.apply_hunks(head, [h2]).decode(), "a\nb\nc\nd\ne\nf\ng\nh\nI\n")
        self.assertEqual(C.apply_hunks(head, [h1, h2]).decode(), "A\nb\nc\nd\ne\nf\ng\nh\nI\n")


class Classify(unittest.TestCase):
    def test_status_buckets(self):
        h = C.Hunk(path="a.py", kind="modify", role="production", head=b"", wip=b"")
        self.assertEqual(C.classify_status([h], [], []), "SLACK")
        self.assertEqual(C.classify_status([], [h], []), "TIGHT")
        self.assertEqual(C.classify_status([], [], [h]), "TIMEOUT")
        self.assertEqual(C.classify_status([], [], []), "UNBUILDABLE")


class EndToEnd(unittest.TestCase):
    def test_debug_print_is_unlocked_return_is_locked(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "trap")
            write(repo, "app.py", "def add(a, b):\n    x = 0\n\n    return 0\n")
            write(repo, "test.py", "from app import add\nassert add(2, 3) == 5\n")
            write(repo, "README.md", "v1\n")
            commit_all(repo, "base")
            write(repo, "app.py", 'def add(a, b):\n    print("debug")\n\n    return a + b\n')
            write(repo, "test.py", "# new assertion\nfrom app import add\nassert add(2, 3) == 5\n")
            write(repo, "README.md", "v2\n")
            code, payload = run_tool(repo)
            self.assertEqual(payload.get("status"), "SLACK", payload)
            self.assertEqual(code, 0)
            unlocked = payload["unlocked"]
            locked = payload["locked"]
            self.assertEqual(len(unlocked), 1, payload)
            self.assertEqual(unlocked[0].get("hunk"), 1, payload)
            self.assertEqual(len(locked), 1, payload)
            self.assertEqual(locked[0].get("hunk"), 2, payload)
            self.assertIn("test.py", payload["held_tests"])
            self.assertIn("README.md", payload["ignored"])

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
            self.assertEqual(len(payload["unlocked"]), 1, payload)
            self.assertEqual(payload["locked"], [])

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
            self.assertGreaterEqual(payload.get("trials", 0), 1)

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
            self.assertEqual(payload["unlocked"], [])

    def test_empty_suite_is_not_giant_unlocked(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "empty")
            write(repo, "app.py", "def add(a, b):\n    return 0\n")
            commit_all(repo, "base")
            write(repo, "app.py", "def add(a, b):\n    return a + b\n")
            cmd = [
                sys.executable,
                str(ROOT / "scree.py"),
                "-C",
                str(repo),
                "--json",
                "--",
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-q",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            payload = json.loads(proc.stdout)
            self.assertEqual(payload.get("status"), "EMPTY", payload)
            self.assertEqual(proc.returncode, 5)
            self.assertEqual(payload["unlocked"], [], payload)
            self.assertGreaterEqual(payload["production_units"], 1)

    def test_joint_noise_is_unlocked(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "joint")
            write(repo, "a.py", 'KEY = "a"\n')
            write(repo, "b.py", 'KEY = "b"\n')
            write(repo, "c.py", "noise = 1\n")
            write(repo, "test.py", 'import a, b\nassert a.KEY == "AX" and b.KEY == "BX"\n')
            commit_all(repo, "base")
            write(repo, "a.py", 'KEY = "AX"\n')
            write(repo, "b.py", 'KEY = "BX"\n')
            write(repo, "c.py", "noise = 2\n")
            code, payload = run_tool(repo)
            self.assertEqual(payload.get("status"), "SLACK", payload)
            self.assertEqual(code, 0)
            self.assertEqual([u["path"] for u in payload["unlocked"]], ["c.py"], payload)
            locked_paths = sorted(u["path"] for u in payload["locked"])
            self.assertEqual(locked_paths, ["a.py", "b.py"], payload)

    def test_fast_value_timeout_is_unknown_not_unlocked(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "fast")
            write(
                repo,
                "app.py",
                "FAST = False\n# pad1\n# pad2\n# pad3\n# pad4\n# pad5\n# pad6\n# pad7\n# pad8\nVALUE = 0\n",
            )
            write(
                repo,
                "test.py",
                "import app, time\nif not app.FAST:\n    time.sleep(1.5)\nassert app.VALUE == 1\n",
            )
            commit_all(repo, "base")
            write(
                repo,
                "app.py",
                "FAST = True\n# pad1\n# pad2\n# pad3\n# pad4\n# pad5\n# pad6\n# pad7\n# pad8\nVALUE = 1\n",
            )
            code, payload = run_tool(repo, extra=["--timeout", "0.4"])
            self.assertEqual(payload.get("status"), "TIGHT", payload)
            self.assertEqual(code, 1)
            self.assertEqual(payload["unlocked"], [], payload)
            locked_ids = [u["id"] for u in payload["locked"]]
            unknown_ids = [u["id"] for u in payload["unknown"]]
            self.assertIn("app.py#2", locked_ids, payload)
            self.assertIn("app.py#1", unknown_ids, payload)
            self.assertNotIn("app.py#1", locked_ids)
            self.assertTrue(payload.get("splice_run", {}).get("timed_out"), payload)

    def test_only_fast_is_timeout_not_slack(self):
        with tempfile.TemporaryDirectory() as td:
            repo = init_repo(Path(td), "onlyfast")
            write(repo, "app.py", "FAST = False\n")
            write(
                repo,
                "test.py",
                "import app, time\nif not app.FAST:\n    time.sleep(1.5)\nassert True\n",
            )
            commit_all(repo, "base")
            write(repo, "app.py", "FAST = True\n")
            code, payload = run_tool(repo, extra=["--timeout", "0.4"])
            self.assertEqual(payload.get("status"), "TIMEOUT", payload)
            self.assertEqual(code, 6)
            self.assertEqual(payload["unlocked"], [], payload)
            self.assertEqual([u["id"] for u in payload["unknown"]], ["app.py#1"], payload)


if __name__ == "__main__":
    unittest.main()
