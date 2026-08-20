#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import vow as V  # noqa: E402

FIX = ROOT / "fixtures"
PY = sys.executable
VOW = [PY, str(ROOT / "vow.py")]


def run(args, stdin=None):
    return subprocess.run(
        VOW + args,
        input=stdin,
        text=True,
        capture_output=True,
        cwd=str(ROOT),
    )


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

    def test_ci_gha(self):
        p = run(["--json", str(FIX / "ci.snap")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "BOUND")
        self.assertEqual(data["require"]["CI"], "github-actions")
        self.assertEqual(data["require"]["HOME"], "/home/runner")

    def test_spec_open(self):
        p = run(["--json", str(FIX / "spec_only.snap")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "OPEN")

    def test_conflict_unsat(self):
        p = run(["--json", str(FIX / "conflict.snap")])
        data = json.loads(p.stdout)
        self.assertEqual(data["status"], "UNSAT")

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
        v = V.infer(
            'await session.waitForText("src/auth.rs");\n',
            "tests/e2e/navigation.test.ts",
        )
        self.assertNotEqual(v.status, "FIXTURE", v.witnesses)
        self.assertFalse(any(w.role == "fixture" for w in v.witnesses), v.witnesses)

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


class PairTests(unittest.TestCase):
    def test_pytest_two_machines(self):
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["pair"], "EXPECTED-BOUND vs ACTUAL-BOUND", data)
        self.assertEqual(data["expected"]["require"].get("HOME"), "/Users/alice")
        self.assertEqual(data["expected"]["require"].get("platform"), "Darwin")
        self.assertEqual(data["actual"]["require"].get("HOME"), "/home/runner")
        self.assertEqual(data["actual"]["require"].get("platform"), "Linux")

    def test_xctest_tmp_vs_alice(self):
        blob = (FIX / "xctest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["pair"], "EXPECTED-OPEN vs ACTUAL-BOUND", data)
        self.assertEqual(data["actual"]["require"].get("HOME"), "/Users/alice")
        self.assertFalse(data["expected"]["require"])

    def test_pytest_vv_tmp_vs_alice(self):
        blob = (FIX / "pytest_vv_tmp.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["pair"], "EXPECTED-OPEN vs ACTUAL-BOUND", data)
        self.assertEqual(data["actual"]["require"].get("HOME"), "/Users/alice")
        self.assertNotIn("USER", data["expected"]["require"])

    def test_junit_tmp_vs_alice(self):
        blob = (FIX / "junit_tmp.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["pair"], "EXPECTED-OPEN vs ACTUAL-BOUND", data)
        self.assertEqual(data["actual"]["require"].get("HOME"), "/Users/alice")

    def test_junit_xml(self):
        blob = (FIX / "junit_xml.xml").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["pair"], "EXPECTED-OPEN vs ACTUAL-BOUND", data)
        self.assertEqual(data["actual"]["require"].get("HOME"), "/Users/alice")

    def test_ran_on_comment_in_fail_does_not_bind(self):
        blob = (FIX / "comment_in_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        for f in data["files"]:
            self.assertNotIn("USER", f["require"], f)
            self.assertNotIn("HOME", f["require"], f)
        self.assertTrue(data["pairs"])
        self.assertTrue(all("OPEN" in pr["pair"] for pr in data["pairs"]), data["pairs"])

    def test_jest_pair(self):
        blob = (FIX / "jest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        homes_e = [pr["expected"]["require"].get("HOME") for pr in data["pairs"]]
        homes_a = [pr["actual"]["require"].get("HOME") for pr in data["pairs"]]
        self.assertIn("/Users/alice", homes_e, data)
        self.assertIn("/home/runner", homes_a, data)

    def test_go_pair(self):
        blob = (FIX / "go_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["expected"]["require"].get("HOME"), "/Users/alice")
        self.assertEqual(data["actual"]["require"].get("HOME"), "/home/runner")

    def test_env_fail_both_user(self):
        blob = (FIX / "env_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["expected"]["require"].get("USER"), "alice", data)
        self.assertEqual(data["actual"]["require"].get("USER"), "runner", data)
        self.assertEqual(data["pair"], "EXPECTED-BOUND vs ACTUAL-BOUND")

    def test_side_actual_emit(self):
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--side", "actual", "--emit", "shell"], stdin=blob)
        self.assertIn("/home/runner", p.stdout)
        self.assertNotIn("/Users/alice", p.stdout)

    def test_not_lees_residue(self):
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail"], stdin=blob)
        self.assertNotIn("substitut", p.stdout.lower())
        self.assertIn("EXPECTED-BOUND vs ACTUAL-BOUND", p.stdout)
        self.assertIn("require  HOME=/Users/alice", p.stdout)
        self.assertIn("require  HOME=/home/runner", p.stdout)


class MergeTests(unittest.TestCase):
    def test_assert_eq_textbook(self):
        v = V.infer(
            'assert_eq!(cwd, Path::new("/home/user/project"));\n',
            "src/hook/tests.rs",
        )
        self.assertIn(v.status, ("SPEC", "OPEN"))
        self.assertNotIn("HOME", v.require)

    def test_env_tied_textbook_still_record(self):
        v = V.infer("assert os.environ['USER'] == 'alice'\n", "tests/test_user.py")
        self.assertEqual(v.status, "BOUND")
        self.assertEqual(v.require.get("USER"), "alice")

    def test_comment_home_not_record(self):
        v = V.infer("# HOME=/Users/alice\nassert True\n", "tests/test_x.py")
        self.assertNotIn("HOME", v.require)

    def test_host_role_neither_on_this_laptop(self):
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        live = V.live_axes()
        if live.get("HOME") == "/Users/alice":
            self.assertEqual(data["host"], "EXPECTED")
        elif live.get("HOME") == "/home/runner":
            self.assertEqual(data["host"], "ACTUAL")
        else:
            self.assertEqual(data["host"], "NEITHER")

    def test_host_actual_when_dump_is_this_home(self):
        home = str(Path.home())
        blob = f"E   - /tmp/x\nE   + {home}/proj\n"
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["host"], "ACTUAL", data)
        self.assertEqual(data["pair"], "EXPECTED-OPEN vs ACTUAL-BOUND")
        self.assertEqual(data["actual"]["require"].get("HOME"), home.rstrip("/"))

    def test_xctest_source_is_not_the_dump_line(self):
        blob = (FIX / "xctest_fail.txt").read_text(encoding="utf-8")
        raw = V.parse_fail(blob)
        self.assertTrue(raw)
        self.assertNotIn("is not equal to", raw[0][3])


if __name__ == "__main__":
    unittest.main()
