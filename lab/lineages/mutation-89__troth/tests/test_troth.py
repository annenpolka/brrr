#!/usr/bin/env python3
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import troth as V  # noqa: E402

FIX = ROOT / "fixtures"
PY = sys.executable
TROTH = [PY, str(ROOT / "troth.py")]


def run(args, stdin=None):
    return subprocess.run(
        TROTH + args,
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


class HostApplyTests(unittest.TestCase):
    """The object: --apply from host role ∪ OPEN expected. Not expected-only."""

    def test_open_expected_applies_when_neither(self):
        blob = (FIX / "xctest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--apply", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        live = V.live_axes()
        self.assertEqual(data["pair"], "EXPECTED-OPEN vs ACTUAL-BOUND", data)
        self.assertIn("OPEN", data["legal"], data)
        self.assertEqual(data["apply"], "APPLY", data)
        self.assertEqual(p.returncode, 0, p.stdout)
        if live.get("HOME") != "/Users/alice":
            self.assertEqual(data["host"], "NEITHER", data)
            self.assertEqual(data["legal"], ["OPEN"], data)

    def test_side_both_skips_open_expected_actual_miss(self):
        """vow polarity: AND actual MISS into OPEN expected → skip. The hole."""
        home = str(Path.home()).rstrip("/")
        if home == "/Users/alice":
            self.skipTest("this host is Alice; actual would MATCH")
        blob = (FIX / "xctest_fail.txt").read_text(encoding="utf-8")
        both = run(["--from-fail", "--apply", "--side", "both"], stdin=blob)
        host = run(["--from-fail", "--apply", "--side", "host"], stdin=blob)
        self.assertEqual(both.returncode, 1, both.stdout)
        self.assertEqual(host.returncode, 0, host.stdout)

    def test_actual_bound_apply_when_dump_is_this_home(self):
        home = str(Path.home())
        blob = f"E   - /Users/alice/proj\nE   + {home}/proj\n"
        p = run(["--from-fail", "--apply", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        if home.rstrip("/") == "/Users/alice":
            self.assertEqual(data["host"], "BOTH")
            self.assertIn("EXPECTED", data["legal"])
            self.assertIn("ACTUAL", data["legal"])
        else:
            self.assertEqual(data["host"], "ACTUAL", data)
            self.assertEqual(data["legal"], ["ACTUAL"], data)
            self.assertEqual(data["expected"]["match"], "MISS", data)
        self.assertEqual(data["apply"], "APPLY", data)
        self.assertEqual(p.returncode, 0, p.stdout)
        expected_only = run(
            ["--from-fail", "--apply", "--side", "expected"], stdin=blob
        )
        if home.rstrip("/") == "/Users/alice":
            self.assertEqual(expected_only.returncode, 0)
        else:
            self.assertEqual(expected_only.returncode, 1, expected_only.stdout)

    def test_open_plus_actual_legal_on_live_dump(self):
        home = str(Path.home())
        blob = f"E   - /tmp/x\nE   + {home}/proj\n"
        p = run(["--from-fail", "--apply", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(data["host"], "ACTUAL", data)
        self.assertEqual(data["pair"], "EXPECTED-OPEN vs ACTUAL-BOUND")
        self.assertIn("OPEN", data["legal"], data)
        self.assertIn("ACTUAL", data["legal"], data)
        self.assertEqual(data["apply"], "APPLY")
        self.assertEqual(p.returncode, 0, p.stdout)
        # OPEN expected still emits true, not the actual skip.
        em = run(["--from-fail", "--emit", "shell"], stdin=blob)
        self.assertEqual(em.stdout.strip(), "true", em.stdout)

    def test_neither_bound_pair_skips(self):
        home = str(Path.home()).rstrip("/")
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--apply", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        if home == "/Users/alice":
            self.assertEqual(data["host"], "EXPECTED")
            self.assertEqual(p.returncode, 0)
        elif home == "/home/runner":
            self.assertEqual(data["host"], "ACTUAL")
            self.assertEqual(p.returncode, 0)
            self.assertEqual(data["legal"], ["ACTUAL"])
        else:
            self.assertEqual(data["host"], "NEITHER", data)
            self.assertEqual(data["legal"], [], data)
            self.assertEqual(data["apply"], "SKIP", data)
            self.assertEqual(p.returncode, 1, p.stdout)

    def test_comment_in_fail_open_still_applies(self):
        blob = (FIX / "comment_in_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--apply", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertTrue(all(pr["apply"] == "APPLY" for pr in data["pairs"]), data)
        self.assertTrue(all("OPEN" in pr["legal"] for pr in data["pairs"]), data)


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

    def test_bind_host_legal_set(self):
        live = V.live_axes()
        home = live["HOME"]
        raw = V.parse_fail(f"E   - /tmp/x\nE   + {home}/proj\n")
        pair = V.bind_host(V.make_pair(*raw[0]), live)
        self.assertEqual(pair.host, "ACTUAL")
        self.assertEqual(set(pair.legal), {"OPEN", "ACTUAL"})
        self.assertEqual(pair.apply, "APPLY")
        self.assertIn(home.rstrip("/"), pair.fixture)


class FixtureTests(unittest.TestCase):
    """v0.2: emit actual-side skip iff this host is ACTUAL-BOUND."""

    def test_fixture_legal_on_live_actual(self):
        home = str(Path.home())
        blob = f"E   - /tmp/x\nE   + {home}/proj\n"
        p = run(["--from-fail", "--fixture"], stdin=blob)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn(home.rstrip("/"), p.stdout)
        self.assertNotEqual(p.stdout.strip(), "true")
        # OPEN expected --apply is unchanged
        a = run(["--from-fail", "--apply"], stdin=blob)
        self.assertEqual(a.returncode, 0)

    def test_fixture_not_legal_when_neither(self):
        home = str(Path.home()).rstrip("/")
        if home == "/Users/alice":
            self.skipTest("this host is Alice; xctest actual would MATCH")
        blob = (FIX / "xctest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--fixture"], stdin=blob)
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertEqual(p.stdout.strip(), "false")
        # OPEN expected still applies
        a = run(["--from-fail", "--apply"], stdin=blob)
        self.assertEqual(a.returncode, 0, a.stdout)
        # --side actual --emit still prints Alice's skip (not gated on host)
        em = run(["--from-fail", "--side", "actual", "--emit", "shell"], stdin=blob)
        self.assertIn("/Users/alice", em.stdout)

    def test_fixture_json_null_when_neither(self):
        home = str(Path.home()).rstrip("/")
        blob = (FIX / "pytest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--json"], stdin=blob)
        data = json.loads(p.stdout)
        if home not in {"/Users/alice", "/home/runner"}:
            self.assertIsNone(data.get("fixture"), data)
            self.assertEqual(data["apply"], "SKIP")

    def test_side_both_names_polarity_skip(self):
        home = str(Path.home()).rstrip("/")
        if home == "/Users/alice":
            self.skipTest("this host is Alice; actual would MATCH")
        blob = (FIX / "xctest_fail.txt").read_text(encoding="utf-8")
        p = run(["--from-fail", "--apply", "--side", "both"], stdin=blob)
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("side     both  SKIP", p.stdout)
        self.assertIn("AND actual MISS into OPEN expected", p.stdout)
        self.assertIn("apply    APPLY", p.stdout)


if __name__ == "__main__":
    unittest.main()
