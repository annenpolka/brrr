#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import visa as V  # noqa: E402

FIX = ROOT / "fixtures"
PY = sys.executable
VISA = [PY, str(ROOT / "visa.py")]


def run(args, stdin=None):
    p = subprocess.run(
        VISA + args,
        input=stdin,
        text=True,
        capture_output=True,
        cwd=str(ROOT),
    )
    return p


class InferTests(unittest.TestCase):
    def test_self_test(self):
        p = run(["--self-test"])
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)

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

    def test_title_not_user_visa(self):
        p = run(["--json", str(FIX / "title.swift")])
        data = json.loads(p.stdout)
        self.assertNotIn("USER", data["require"])
        self.assertIn(data["status"], ("OPEN", "FIXTURE"))

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

    def test_from_fail(self):
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        files = data["files"]
        self.assertTrue(files)
        self.assertEqual(files[0]["require"].get("platform"), "Darwin")

    def test_match_live(self):
        home = str(Path.home())
        text = f"home: {home}\n"
        p = run(["--match", "--apply", "--json", "-"], stdin=text)
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        data = json.loads(p.stdout)
        self.assertEqual(data["match"], "MATCH")


class MergeTests(unittest.TestCase):
    def test_quoted_john_doe_in_snapshot(self):
        v = V.infer("home: /Users/John Doe/kizu\n", "quote.snap")
        self.assertEqual(v.require.get("HOME"), "/Users/John Doe")
        self.assertEqual(v.require.get("platform"), "Darwin")
        self.assertEqual(v.status, "BOUND")

    def test_payload_two_layouts_are_spec(self):
        text = (FIX / "payload.rs").read_text(encoding="utf-8")
        v = V.infer(text, str(FIX / "payload.rs"))
        self.assertEqual(v.status, "SPEC", v.require)
        self.assertEqual(v.require, {})

    def test_snapshot_alice_still_bound(self):
        v = V.infer((FIX / "local.snap").read_text(encoding="utf-8"), str(FIX / "local.snap"))
        self.assertEqual(v.status, "BOUND")
        self.assertEqual(v.require.get("HOME"), "/Users/alice")

    def test_textbook_home_in_tests_is_spec(self):
        v = V.infer('cwd = "/home/user/project"\n', "src/hook/tests.rs")
        self.assertEqual(v.status, "SPEC")
        self.assertNotIn("HOME", v.require)

    def test_macos_word_in_ts_test_is_not_bound(self):
        v = V.infer("// macOS PollWatcher fallback\n", "tests/e2e/reactive.test.ts")
        self.assertNotEqual(v.status, "BOUND")

    def test_tmp_not_home(self):
        v = V.infer('PathBuf::from("/tmp/foo.rs")\n', "t.rs")
        self.assertNotEqual(v.status, "BOUND")
        self.assertNotIn("HOME", v.require)


if __name__ == "__main__":
    unittest.main()
