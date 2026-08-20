#!/usr/bin/env python3
from __future__ import annotations

import getpass
import json
import os
import platform
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import writ  # noqa: E402

CMD = [sys.executable, "-m", "unittest", "discover", "-q"]
HOME = str(Path.home())
USER = getpass.getuser()


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=repo, check=check, capture_output=True, text=True
    )


def init_repo(parent: Path, name: str) -> Path:
    repo = parent / name
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "writ@test")
    _git(repo, "config", "user.name", "writ")
    _git(repo, "config", "commit.gpgsign", "false")
    return repo


def write(repo: Path, rel: str, text: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def commit_all(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message)


def run(repo: Path, **kwargs) -> writ.Report:
    return writ.run_writ(
        repo=repo,
        base=kwargs.get("base", "HEAD"),
        new_ref=kwargs.get("new_ref"),
        cmd=kwargs.get("cmd", CMD),
        timeout=kwargs.get("timeout", 30.0),
        keep=[],
    )


class PathHeuristics(unittest.TestCase):
    def test_test_py_is_a_test(self):
        self.assertTrue(writ.is_test_path("test.py"))
        self.assertEqual(writ.path_role("test.py"), "test")

    def test_agents_md_is_not_production(self):
        self.assertEqual(writ.path_role("AGENTS.md"), "other")
        self.assertEqual(writ.path_role("README.md"), "other")

    def test_src_is_production(self):
        self.assertEqual(writ.path_role("who.py"), "production")
        self.assertEqual(writ.path_role("Sources/App/Foo.swift"), "production")

    def test_coordinator_lab_is_skipped(self):
        self.assertTrue(
            writ.should_skip_path("lab/lineages/x/demo.sh", skip_lab=True)
        )
        self.assertFalse(writ.should_skip_path("demo.sh", skip_lab=True))
        self.assertFalse(
            writ.should_skip_path("lab/lineages/x/demo.sh", skip_lab=False)
        )


class OathLiteral(unittest.TestCase):
    def test_tmp_open(self):
        self.assertEqual(writ.oath_literal("/tmp/x").status, "OPEN")

    def test_alice_bound(self):
        o = writ.oath_literal("/Users/alice/proj")
        self.assertEqual(o.status, "BOUND")
        self.assertEqual(o.require.get("HOME"), "/Users/alice")

    def test_home_user_is_spec(self):
        self.assertEqual(writ.oath_literal("/home/user/project").status, "SPEC")

    def test_github_fixture(self):
        self.assertEqual(
            writ.oath_literal("GitHub - annenpolka/sitbone - Google Chrome").status,
            "FIXTURE",
        )

    def test_comment_is_not_an_oath(self):
        self.assertEqual(writ.oath_literal("# ran on alice").status, "OPEN")

    def test_number_open(self):
        self.assertEqual(writ.oath_literal("5").status, "OPEN")
        self.assertEqual(writ.oath_literal("0").status, "OPEN")


class ParseFail(unittest.TestCase):
    def test_unittest_assertEqual_uses_source_expected(self):
        dump = (
            '  File "test_who.py", line 6, in test_tmp\n'
            '    self.assertEqual(who.who(), "/tmp/x")\n'
            "AssertionError: '/Users/alice/Library' != '/tmp/x'\n"
        )
        pairs = writ.parse_fail(dump)
        self.assertEqual(len(pairs), 1)
        _kind, exp, act, _src = pairs[0]
        self.assertEqual(exp, "/tmp/x")
        self.assertIn("alice", act)

    def test_numeric_polarity(self):
        dump = "    self.assertEqual(adder.add(2, 3), 5)\nAssertionError: 0 != 5\n"
        pairs = writ.parse_fail(dump)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][1], "5")
        self.assertEqual(pairs[0][2], "0")

    def test_comment_in_dump_is_not_a_window(self):
        dump = "# ran on alice\nAssertionError: 0 != 5\n"
        pairs = writ.parse_fail(dump)
        self.assertTrue(pairs)
        p = writ.make_pair(*pairs[0][:3], pairs[0][3])
        self.assertEqual(p.expected.status, "OPEN")
        self.assertEqual(p.actual.status, "OPEN")


class HostRoleApply(unittest.TestCase):
    def test_open_expected_applies_when_actual_is_alice(self):
        p = writ.bind_host(
            writ.make_pair("unittest", "/tmp/x", "/Users/alice/Library"),
            live={"HOME": HOME, "USER": USER, "platform": "Darwin", "layout": "macos-home"},
        )
        self.assertEqual(p.expected.status, "OPEN")
        self.assertEqual(p.actual.status, "BOUND")
        self.assertEqual(p.host, "NEITHER")
        self.assertIn("OPEN", p.legal)
        self.assertEqual(p.apply, "APPLY")
        self.assertEqual(p.fixture, "")

    def test_live_home_actual_is_legal_fixture(self):
        p = writ.bind_host(
            writ.make_pair("unittest", "/tmp/x", HOME + "/proj"),
        )
        self.assertEqual(p.host, "ACTUAL")
        self.assertIn("OPEN", p.legal)
        self.assertIn("ACTUAL", p.legal)
        self.assertEqual(p.apply, "APPLY")
        self.assertTrue(p.fixture)
        self.assertIn("HOME", p.fixture)

    def test_alice_expected_skips_here(self):
        p = writ.bind_host(
            writ.make_pair("unittest", "/Users/alice/proj", "/tmp/x"),
        )
        self.assertEqual(p.expected.status, "BOUND")
        self.assertEqual(p.actual.status, "OPEN")
        self.assertEqual(p.host, "NEITHER")
        self.assertEqual(p.apply, "SKIP")
        self.assertEqual(p.legal, [])
        self.assertEqual(p.fixture, "")

    def test_lock_label(self):
        p = writ.bind_host(writ.make_pair("u", "/tmp/x", "/Users/alice/x"))
        self.assertEqual(
            p.lock, "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-BOUND"
        )


class SkipIsNotALock(unittest.TestCase):
    def test_skipunless_alice_fires(self):
        src = (
            "import os, unittest\n"
            "@unittest.skipUnless(os.environ.get('HOME') == '/Users/alice', 'alice')\n"
            "def test_alice():\n"
            "    assert True\n"
        )
        self.assertTrue(writ.tests_would_skip([src]))

    def test_comment_skip_is_not_an_oath(self):
        src = (
            "# @unittest.skipUnless(os.environ.get('HOME') == '/Users/alice', 'alice')\n"
            "def test_sum():\n"
            "    assert True\n"
        )
        self.assertFalse(writ.tests_would_skip([src]))


class SpliceThenOath(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_portable_lock_is_open_vs_open(self):
        repo = init_repo(self.root, "open")
        write(repo, "adder.py", "def add(a, b):\n    return 0\n")
        write(
            repo,
            "test_adder.py",
            "import unittest, adder\n"
            "class T(unittest.TestCase):\n"
            "    def test_sum(self):\n"
            "        self.assertEqual(adder.add(2, 3), 5)\n",
        )
        commit_all(repo, "red")
        write(repo, "adder.py", "def add(a, b):\n    return a + b\n")
        r = run(repo)
        self.assertEqual(r.status, "LOCKED")
        self.assertEqual(r.lock, "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN")
        self.assertEqual(r.apply, "APPLY")
        self.assertIn("OPEN", r.legal)
        self.assertEqual(r.wheat if hasattr(r, "wheat") else [], [])

    def test_actual_bound_old_production_leaks_this_host(self):
        repo = init_repo(self.root, "actual")
        write(repo, "who.py", f"def who():\n    return {HOME!r}\n")
        write(
            repo,
            "test_who.py",
            "import unittest, who\n"
            "class T(unittest.TestCase):\n"
            "    def test_tmp(self):\n"
            "        self.assertEqual(who.who(), '/tmp/x')\n",
        )
        commit_all(repo, "leaky")
        write(repo, "who.py", "def who():\n    return '/tmp/x'\n")
        r = run(repo)
        self.assertEqual(r.status, "LOCKED")
        self.assertIsNotNone(r.pair)
        self.assertEqual(r.pair.expected.status, "OPEN")
        self.assertEqual(r.pair.actual.status, "BOUND")
        self.assertEqual(r.host, "ACTUAL")
        self.assertIn("ACTUAL", r.legal)
        self.assertIn("OPEN", r.legal)
        self.assertEqual(r.apply, "APPLY")
        self.assertTrue(r.fixture)
        self.assertEqual(
            r.lock, "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-BOUND"
        )

    def test_expected_bound_alice_golden(self):
        repo = init_repo(self.root, "expected")
        write(repo, "who.py", "def who():\n    return '/tmp/x'\n")
        write(
            repo,
            "test_who.py",
            "import unittest, who\n"
            "class T(unittest.TestCase):\n"
            "    def test_alice(self):\n"
            "        self.assertEqual(who.who(), '/Users/alice/proj')\n",
        )
        commit_all(repo, "tmp")
        write(repo, "who.py", "def who():\n    return '/Users/alice/proj'\n")
        r = run(repo)
        self.assertEqual(r.status, "LOCKED")
        self.assertEqual(r.pair.expected.status, "BOUND")
        self.assertEqual(r.pair.actual.status, "OPEN")
        self.assertEqual(r.host, "NEITHER")
        self.assertEqual(r.apply, "SKIP")
        self.assertEqual(r.fixture, "")
        self.assertEqual(
            r.lock, "LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-OPEN"
        )

    def test_skip_is_not_a_lock(self):
        repo = init_repo(self.root, "skip")
        write(repo, "who.py", "def who():\n    return '/tmp/x'\n")
        write(
            repo,
            "test_who.py",
            "import os, unittest, who\n"
            "class T(unittest.TestCase):\n"
            "    @unittest.skipUnless(os.environ.get('HOME') == '/Users/alice', 'alice')\n"
            "    def test_alice(self):\n"
            "        self.assertEqual(who.who(), '/Users/alice')\n",
        )
        commit_all(repo, "tmp")
        write(repo, "who.py", "def who():\n    return '/Users/alice'\n")
        r = run(repo)
        self.assertEqual(r.status, "SKIP")
        self.assertEqual(r.pair, None)
        self.assertFalse(r.lock)

    def test_comment_only_alice_is_open_lock(self):
        repo = init_repo(self.root, "comment")
        write(repo, "adder.py", "def add(a, b):\n    return 0\n")
        write(
            repo,
            "test_adder.py",
            "import unittest, adder\n"
            "class T(unittest.TestCase):\n"
            "    def test_sum(self):\n"
            "        # ran on alice\n"
            "        self.assertEqual(adder.add(2, 3), 5)\n",
        )
        commit_all(repo, "red")
        write(repo, "adder.py", "def add(a, b):\n    return a + b\n")
        r = run(repo)
        self.assertEqual(r.status, "LOCKED")
        self.assertEqual(r.lock, "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN")

    def test_loose_comment_production(self):
        repo = init_repo(self.root, "loose")
        write(repo, "adder.py", "def add(a, b):\n    return a + b\n")
        write(
            repo,
            "test_adder.py",
            "import unittest, adder\n"
            "class T(unittest.TestCase):\n"
            "    def test_sum(self):\n"
            "        self.assertEqual(adder.add(2, 3), 5)\n",
        )
        commit_all(repo, "green")
        write(repo, "adder.py", "def add(a, b):\n    # note\n    return a + b\n")
        r = run(repo)
        self.assertEqual(r.status, "LOOSE")

    def test_test_only_red_is_broken(self):
        repo = init_repo(self.root, "broken")
        write(repo, "adder.py", "def add(a, b):\n    return a + b\n")
        write(
            repo,
            "test_adder.py",
            "import unittest, adder\n"
            "class T(unittest.TestCase):\n"
            "    def test_sum(self):\n"
            "        self.assertEqual(adder.add(2, 3), 5)\n",
        )
        commit_all(repo, "green")
        write(
            repo,
            "test_adder.py",
            "import unittest, adder\n"
            "class T(unittest.TestCase):\n"
            "    def test_sum(self):\n"
            "        self.assertEqual(adder.add(2, 3), 99)\n",
        )
        r = run(repo)
        self.assertEqual(r.status, "BROKEN")

    def test_debug_print_is_not_cinch(self):
        """Whole production splice. No wheat/hunk peel of print vs return."""
        repo = init_repo(self.root, "cinchish")
        write(repo, "app.py", "def add(a, b):\n    x = 0\n    return 0\n")
        write(
            repo,
            "test.py",
            "import unittest, app\n"
            "class T(unittest.TestCase):\n"
            "    def test_sum(self):\n"
            "        self.assertEqual(app.add(2, 3), 5)\n",
        )
        commit_all(repo, "zero")
        write(
            repo,
            "app.py",
            'def add(a, b):\n    print("debug")\n    return a + b\n',
        )
        r = run(repo)
        self.assertEqual(r.status, "LOCKED")
        self.assertEqual(r.lock, "LOCKED-and-EXPECTED-OPEN vs LOCKED-and-ACTUAL-OPEN")
        blob = json.dumps(writ.report_to_json(r))
        self.assertEqual(json.loads(blob)["wheat"], [])
        self.assertEqual(json.loads(blob)["hunks"], [])
        self.assertIn("app.py", r.production_changed)
        self.assertTrue(writ.is_test_path("test.py"))

    def test_markdown_only_is_clean(self):
        repo = init_repo(self.root, "docs")
        write(repo, "adder.py", "def add(a, b):\n    return a + b\n")
        write(
            repo,
            "test_adder.py",
            "import unittest, adder\n"
            "class T(unittest.TestCase):\n"
            "    def test_sum(self):\n"
            "        self.assertEqual(adder.add(2, 3), 5)\n",
        )
        write(repo, "README.md", "hello\n")
        commit_all(repo, "green")
        write(repo, "README.md", "hello world\n")
        r = run(repo)
        self.assertEqual(r.status, "CLEAN")

    def test_added_module_unbuildable_is_not_a_pair(self):
        repo = init_repo(self.root, "newmod")
        write(repo, "README.md", "n\n")
        write(
            repo,
            "test_who.py",
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n",
        )
        commit_all(repo, "no module")
        write(repo, "who.py", "def who():\n    return '/tmp/x'\n")
        write(
            repo,
            "test_who.py",
            "import unittest, who\n"
            "class T(unittest.TestCase):\n"
            "    def test_tmp(self):\n"
            "        self.assertEqual(who.who(), '/tmp/x')\n",
        )
        r = run(repo)
        self.assertEqual(r.status, "UNBUILDABLE")
        self.assertTrue(any("who.py" in n for n in r.notes))
        self.assertTrue(any("not a fail pair" in n for n in r.notes))
        self.assertEqual(r.pair, None)


class CliExit(unittest.TestCase):
    def test_clearance_and_bound_exits(self):
        open_p = writ.bind_host(writ.make_pair("u", "5", "0"))
        r = writ.Report(
            status="LOCKED",
            base="HEAD",
            new="worktree",
            cmd=CMD,
            production_changed=["adder.py"],
            tests_kept=["test_adder.py"],
            pair=open_p,
            pairs=[open_p],
            lock=open_p.lock,
            host=open_p.host,
            legal=open_p.legal,
            apply=open_p.apply,
        )
        self.assertEqual(writ.exit_code(r), 0)
        self.assertTrue(writ.clearance_empty(r))

        bound = writ.bind_host(writ.make_pair("u", "/tmp/x", HOME + "/x"))
        r2 = writ.Report(
            status="LOCKED",
            base="HEAD",
            new="worktree",
            cmd=CMD,
            production_changed=["who.py"],
            tests_kept=["test_who.py"],
            pair=bound,
            pairs=[bound],
            lock=bound.lock,
            host=bound.host,
            legal=bound.legal,
            apply=bound.apply,
            fixture=bound.fixture,
        )
        self.assertEqual(writ.exit_code(r2), 1)
        self.assertEqual(writ.exit_code(r2, apply=True), 0)
        self.assertEqual(writ.exit_code(r2, fixture=True), 0)
        self.assertFalse(writ.clearance_empty(r2))


if __name__ == "__main__":
    unittest.main()
