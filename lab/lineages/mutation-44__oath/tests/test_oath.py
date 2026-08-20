#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import oath as O  # noqa: E402

FIX = ROOT / "fixtures"
PY = sys.executable
OATH = [PY, str(ROOT / "oath.py")]


def run(args, stdin=None):
    p = subprocess.run(
        OATH + args,
        input=stdin,
        text=True,
        capture_output=True,
        cwd=str(ROOT),
    )
    return p


class GoldTests(unittest.TestCase):
    def test_self_test(self):
        p = run(["--self-test"])
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)

    def test_comment_is_not_an_oath(self):
        p = run(["--json", str(FIX / "comment_only.py")])
        data = json.loads(p.stdout)
        self.assertNotIn("USER", data["require"])
        self.assertNotIn("HOME", data["require"])
        self.assertIn(data["status"], ("OPEN", "SPEC"))
        self.assertTrue(any(s["value"] == "alice" for s in data["silent"]), data["silent"])

    def test_env_assert_is_an_oath(self):
        p = run(["--json", str(FIX / "env_assert.py")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "BOUND")
        self.assertEqual(data["require"].get("USER"), "alice")
        self.assertTrue(any(s["value"] == "alice" for s in data["silent"]))

    def test_snap_comment_is_not_an_oath(self):
        p = run(["--json", str(FIX / "comment.snap")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "OPEN")
        self.assertEqual(data["require"], {})

    def test_title_is_fixture(self):
        p = run(["--json", str(FIX / "title.swift")])
        data = json.loads(p.stdout)
        self.assertNotIn("USER", data["require"])
        self.assertIn(data["status"], ("OPEN", "FIXTURE"))
        self.assertTrue(any(w["role"] == "fixture" for w in data["witnesses"]), data)


class InferTests(unittest.TestCase):
    def test_local_bound(self):
        p = run(["--json", str(FIX / "local.snap")])
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "BOUND")
        self.assertEqual(data["require"]["HOME"], "/Users/alice")
        self.assertEqual(data["require"]["platform"], "Darwin")
        self.assertEqual(data["predicate"]["gha"], "macos-latest")

    def test_ci_gha(self):
        p = run(["--json", str(FIX / "ci.snap")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "BOUND")
        self.assertEqual(data["require"]["CI"], "github-actions")
        self.assertEqual(data["require"]["HOME"], "/home/runner")
        self.assertEqual(data["predicate"]["gha"], "ubuntu-latest")

    def test_spec_open(self):
        p = run(["--json", str(FIX / "spec_only.snap")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "OPEN")
        self.assertEqual(data["require"], {})

    def test_conflict_unsat(self):
        p = run(["--json", str(FIX / "conflict.snap")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "UNSAT")

    def test_ugly_unicode(self):
        p = run(["--json", str(FIX / "ugly" / "日本語" / "期待.txt")])
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["require"]["HOME"], "/Users/alice")

    def test_ugly_spaces(self):
        p = run(["--json", str(FIX / "ugly" / "dir with spaces" / "snap.txt")])
        data = json.loads(p.stdout)
        self.assertEqual(data["require"]["HOME"], "/Users/alice")

    def test_emit_shell(self):
        p = run(["--emit", "shell", str(FIX / "local.snap")])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("/Users/alice", p.stdout)
        self.assertIn("Darwin", p.stdout)

    def test_apply_open(self):
        p = run(["--apply", str(FIX / "spec_only.snap")])
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_apply_alice_miss_on_this_host(self):
        home = str(Path.home())
        p = run(["--apply", "--json", str(FIX / "local.snap")])
        if home.rstrip("/") == "/Users/alice":
            self.assertEqual(p.returncode, 0)
        else:
            self.assertEqual(p.returncode, 1, p.stdout)

    def test_payload_textbook(self):
        p = run(["--json", str(FIX / "payload.rs")])
        data = json.loads(p.stdout)
        self.assertIn(data["status"], ("SPEC", "OPEN"))
        self.assertNotIn("HOME", data["require"])

    def test_expect_macro(self):
        p = run(["--json", str(FIX / "expect.swift")])
        data = json.loads(p.stdout)
        self.assertEqual(data["require"].get("USER"), "alice")
        self.assertEqual(data["status"], "BOUND")

    def test_macos_comment_not_bound(self):
        p = run(["--json", str(FIX / "comment_macos.ts")])
        data = json.loads(p.stdout)
        self.assertNotEqual(data["status"], "BOUND")

    def test_relative_path_is_not_fixture(self):
        v = O.infer(
            'await session.waitForText("src/auth.rs");\n',
            "tests/e2e/navigation.test.ts",
        )
        self.assertNotEqual(v.status, "FIXTURE", v.witnesses)
        self.assertFalse(any(w.role == "fixture" for w in v.witnesses), v.witnesses)

    def test_mime_and_url_are_not_user_fixtures(self):
        v = O.infer(
            'XCTAssertEqual(header, "application/json")\n'
            'let u = URL(string: "https://example.invalid/v1")!\n'
            'let d = repoRoot.appendingPathComponent("contracts/testcases")\n',
            "Engine/Tests/FooTests.swift",
        )
        self.assertFalse(any(w.role == "fixture" for w in v.witnesses), v.witnesses)
        self.assertNotIn("USER", v.require)


class FromFailTests(unittest.TestCase):
    def test_pytest(self):
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertTrue(data["files"])
        self.assertEqual(data["files"][0]["require"].get("platform"), "Darwin")

    def test_jest(self):
        blob = (FIX / "jest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        plats = [f["require"].get("platform") for f in data["files"]]
        self.assertIn("Darwin", plats, data)

    def test_junit(self):
        blob = (FIX / "junit_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        homes = [f["require"].get("HOME") for f in data["files"]]
        self.assertIn("/Users/alice", homes, data)

    def test_go(self):
        blob = (FIX / "go_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        homes = [f["require"].get("HOME") for f in data["files"]]
        self.assertIn("/Users/alice", homes, data)

    def test_cargo(self):
        blob = (FIX / "cargo_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["files"][0]["require"].get("platform"), "Darwin")

    def test_xctest(self):
        blob = (FIX / "xctest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        homes = [f["require"].get("HOME") for f in data["files"]]
        self.assertIn("/Users/alice", homes, data)

    def test_env_fail_src(self):
        blob = (FIX / "env_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        users = [f["require"].get("USER") for f in data["files"]]
        self.assertTrue(any(u == "alice" for u in users), data)


class MergeTests(unittest.TestCase):
    def test_quoted_john_doe_in_snapshot(self):
        v = O.infer("home: /Users/John Doe/kizu\n", "quote.snap")
        self.assertEqual(v.require.get("HOME"), "/Users/John Doe")
        self.assertEqual(v.require.get("platform"), "Darwin")
        self.assertEqual(v.status, "BOUND")

    def test_assert_eq_textbook(self):
        v = O.infer(
            'assert_eq!(cwd, Path::new("/home/user/project"));\n',
            "src/hook/tests.rs",
        )
        self.assertIn(v.status, ("SPEC", "OPEN"))
        self.assertNotIn("HOME", v.require)

    def test_env_tied_textbook_still_record(self):
        v = O.infer("assert os.environ['USER'] == 'alice'\n", "tests/test_user.py")
        self.assertEqual(v.status, "BOUND")
        self.assertEqual(v.require.get("USER"), "alice")

    def test_comment_home_not_record(self):
        v = O.infer("# HOME=/Users/alice\nassert True\n", "tests/test_x.py")
        self.assertNotIn("HOME", v.require)

    def test_match_live_stdin(self):
        home = str(Path.home())
        text = f"home: {home}\n"
        p = run(["--match", "--apply", "--json", "-"], stdin=text)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        data = json.loads(p.stdout)
        self.assertEqual(data["match"], "MATCH")


if __name__ == "__main__":
    unittest.main()
