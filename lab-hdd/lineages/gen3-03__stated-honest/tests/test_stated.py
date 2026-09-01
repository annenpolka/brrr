#!/usr/bin/env python3
"""Drive the shipped stated CLI. No imports of internal helpers."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATED = ROOT / "stated"
FIXTURES = ROOT / "fixtures"


def run_stated(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(STATED), *args],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )


class UsageTests(unittest.TestCase):
    def test_missing_key_exits_1(self) -> None:
        proc = run_stated()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing KEY", proc.stderr)

    def test_help_exits_0(self) -> None:
        proc = run_stated("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("usage: stated", proc.stdout)

    def test_unknown_flag_exits_1(self) -> None:
        proc = run_stated("--nope", "timeout")
        self.assertEqual(proc.returncode, 1)

    def test_missing_dir_exits_1(self) -> None:
        proc = run_stated("timeout", str(ROOT / "no-such-dir"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not found", proc.stderr)


class FixtureTests(unittest.TestCase):
    def test_disagree_exits_2_and_prints_pair(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "disagree"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("status: DISAGREE", proc.stdout)
        self.assertIn("declared", proc.stdout)
        self.assertIn("contradicted", proc.stdout)
        self.assertIn("config.yaml:1", proc.stdout)
        self.assertIn("app.py:3", proc.stdout)
        self.assertIn("\tvalue=5", proc.stdout)
        self.assertIn("\tvalue=10", proc.stdout)

    def test_agree_exits_0(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "agree"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("status: AGREE", proc.stdout)
        self.assertIn("value: 5", proc.stdout)
        self.assertIn("config.yaml:1", proc.stdout)
        self.assertIn("app.py:3", proc.stdout)

    def test_config_only_exits_0(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "config_only"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("status: DECLARED_ONLY", proc.stdout)
        self.assertIn("config.yaml:1", proc.stdout)
        self.assertNotIn("assignments:", proc.stdout)

    def test_unknown_not_statically_comparable_exits_0(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "unknown"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("status: UNKNOWN", proc.stdout)
        self.assertIn("none statically comparable", proc.stdout)

    def test_json_disagree(self) -> None:
        proc = run_stated("--json", "timeout", str(FIXTURES / "disagree"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "disagree")
        self.assertEqual(payload["key"], "timeout")
        self.assertEqual(len(payload["pairs"]), 1)
        pair = payload["pairs"][0]
        self.assertEqual(pair["declared_value"], "5")
        self.assertEqual(pair["contradicted_value"], "10")
        self.assertTrue(pair["declaration"]["path"].endswith("config.yaml"))
        self.assertTrue(pair["contradiction"]["path"].endswith("app.py"))

    def test_json_agree(self) -> None:
        proc = run_stated("--json", "timeout", str(FIXTURES / "agree"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "agree")
        self.assertEqual(payload["agreed_value"], "5")

    def test_no_sites(self) -> None:
        proc = run_stated("no_such_key_zzz", str(FIXTURES / "agree"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("status: NONE", proc.stdout)

    def test_does_not_match_longer_identifier(self) -> None:
        # max_timeout in a file should not fire for key timeout
        tmp = FIXTURES / "agree"
        proc = run_stated("max_timeout", str(tmp))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("status: NONE", proc.stdout)

    def test_comments_are_labeled_not_contradictions(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "comments"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("status: AGREE", proc.stdout)
        self.assertIn("value: 5", proc.stdout)
        self.assertIn("comments (ignored for comparison):", proc.stdout)
        self.assertIn("timeout = 99", proc.stdout)
        self.assertNotIn("status: DISAGREE", proc.stdout)
        # Typed C assignment is a real site, not dropped.
        self.assertIn("legacy.c:", proc.stdout)
        self.assertIn("int timeout = 5", proc.stdout)

    def test_json_comments_separated(self) -> None:
        proc = run_stated("--json", "timeout", str(FIXTURES / "comments"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "agree")
        self.assertEqual(payload["agreed_value"], "5")
        self.assertTrue(payload["comments"])
        self.assertTrue(all(c["in_comment"] for c in payload["comments"]))
        self.assertTrue(all(not a["in_comment"] for a in payload["assignments"]))
        comment_values = {c["raw_value"] for c in payload["comments"]}
        self.assertIn("99", comment_values)
        assign_values = {a["raw_value"] for a in payload["assignments"]}
        self.assertEqual(assign_values, {"5"})

    def test_compact_json_object_member_is_a_declaration(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "compact_json"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("status: DISAGREE", proc.stdout)
        self.assertIn("config.json:1", proc.stdout)
        self.assertIn("app.py:1", proc.stdout)
        self.assertIn("\tvalue=5", proc.stdout)
        self.assertIn("\tvalue=10", proc.stdout)
        self.assertNotIn("ASSIGNED_ONLY", proc.stdout)

    def test_json_compact_object_pair(self) -> None:
        proc = run_stated("--json", "timeout", str(FIXTURES / "compact_json"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "disagree")
        self.assertEqual(len(payload["pairs"]), 1)
        pair = payload["pairs"][0]
        self.assertEqual(pair["declared_value"], "5")
        self.assertEqual(pair["contradicted_value"], "10")
        self.assertTrue(pair["declaration"]["path"].endswith("config.json"))
        self.assertEqual(pair["declaration"]["line"], 1)
        self.assertIn("timeout", pair["declaration"]["text"])

    def test_dotenv_is_not_a_declaration_for_timeout(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "dotenv_not_decl"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("status: DISAGREE", proc.stdout)
        self.assertIn("config.yaml:1", proc.stdout)
        self.assertIn("app.py:", proc.stdout)
        self.assertIn("\tvalue=5", proc.stdout)
        self.assertIn("\tvalue=10", proc.stdout)
        self.assertNotIn(".env", proc.stdout)
        self.assertNotIn("value=99", proc.stdout)
        self.assertNotIn("value=30", proc.stdout)

    def test_dotenv_TIMEOUT_is_none_not_declared_only(self) -> None:
        proc = run_stated("TIMEOUT", str(FIXTURES / "dotenv_not_decl"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("status: NONE", proc.stdout)
        self.assertNotIn("DECLARED_ONLY", proc.stdout)
        self.assertNotIn(".env", proc.stdout)

    def test_quoted_timeout_equals_is_not_an_assignment(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "strlit"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("status: DECLARED_ONLY", proc.stdout)
        self.assertIn("value: 5", proc.stdout)
        self.assertNotIn("status: UNKNOWN", proc.stdout)
        self.assertNotIn("assignments:", proc.stdout)
        self.assertNotIn("99 is wrong", proc.stdout)

    def test_json_quoted_timeout_has_no_assignment_site(self) -> None:
        proc = run_stated("--json", "timeout", str(FIXTURES / "strlit"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "declared_only")
        self.assertEqual(payload["agreed_value"], "5")
        self.assertEqual(payload["assignments"], [])

    def test_real_assignment_still_pairs_next_to_string_mention(self) -> None:
        proc = run_stated("timeout", str(FIXTURES / "strlit_and_assign"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertIn("status: DISAGREE", proc.stdout)
        self.assertIn("\tvalue=5", proc.stdout)
        self.assertIn("\tvalue=10", proc.stdout)
        self.assertNotIn("99 is wrong", proc.stdout)

    def test_json_dotenv_excluded_from_declarations(self) -> None:
        proc = run_stated("--json", "timeout", str(FIXTURES / "dotenv_not_decl"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "disagree")
        paths = [h["path"] for h in payload["declarations"]]
        self.assertTrue(any(p.endswith("config.yaml") for p in paths))
        self.assertFalse(any(p.endswith(".env") or "/.env" in p or p == ".env" for p in paths))
        values = {h["raw_value"] for h in payload["declarations"]}
        self.assertEqual(values, {"5"})


if __name__ == "__main__":
    unittest.main()
