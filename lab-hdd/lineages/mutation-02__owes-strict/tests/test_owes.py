#!/usr/bin/env python3
"""Tests drive the shipped `owes` CLI, not imported internals."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OWES = ROOT / "owes"
FIXTURES = ROOT / "fixtures"


def run_owes(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(OWES), *args],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
    )


class OwesCLITests(unittest.TestCase):
    def test_deleted_function_still_mentioned(self) -> None:
        result = run_owes(str(FIXTURES / "deleted-fn"))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("validate_input", result.stdout)
        self.assertIn("README.md", result.stdout)
        self.assertIn("unkept references", result.stdout)

    def test_missing_companion_from_remaining_docs(self) -> None:
        result = run_owes(str(FIXTURES / "missing-companion"))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("SECURITY.decision.md", result.stdout)
        self.assertIn("missing companions", result.stdout)
        self.assertIn("docs/threat-model.md", result.stdout)
        self.assertNotIn("docs/adr.md", result.stdout)
        self.assertNotIn("make test", result.stdout)

    def test_clean_change_has_no_unkept_obligations(self) -> None:
        result = run_owes(str(FIXTURES / "clean"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no unkept obligations", result.stdout)
        self.assertNotIn("scratch_helper", result.stdout)

    def test_tree_diff_flags(self) -> None:
        result = run_owes(
            "--tree",
            str(FIXTURES / "deleted-fn" / "tree"),
            "--diff",
            str(FIXTURES / "deleted-fn" / "change.diff"),
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("validate_input", result.stdout)

    def test_json_shape(self) -> None:
        result = run_owes("--json", str(FIXTURES / "deleted-fn"))
        self.assertEqual(result.returncode, 2, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("unkept_references", payload)
        self.assertIn("missing_companions", payload)
        names = {item["identifier"] for item in payload["unkept_references"]}
        self.assertIn("validate_input", names)
        self.assertTrue(payload["unkept_references"][0]["path"].endswith("README.md"))

    def test_json_missing_companion(self) -> None:
        result = run_owes("--json", str(FIXTURES / "missing-companion"))
        self.assertEqual(result.returncode, 2, result.stderr)
        payload = json.loads(result.stdout)
        paths = {item["path"] for item in payload["missing_companions"]}
        self.assertIn("SECURITY.decision.md", paths)
        self.assertIn("docs/threat-model.md", paths)
        self.assertNotIn("docs/adr.md", paths)
        self.assertNotIn("make test", paths)

    def test_usage_error_without_args(self) -> None:
        result = run_owes()
        self.assertEqual(result.returncode, 1)
        self.assertIn("owes:", result.stderr)

    def test_usage_error_missing_dir(self) -> None:
        result = run_owes(str(FIXTURES / "does-not-exist"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("not found", result.stderr)

    def test_usage_error_tree_without_diff(self) -> None:
        result = run_owes("--tree", str(FIXTURES / "clean" / "tree"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("--tree requires --diff", result.stderr)

    def test_plus_line_changelog_mention_is_ignored(self) -> None:
        result = run_owes(str(FIXTURES / "plus-line-changelog"))
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("README.md", result.stdout)
        self.assertIn("validate_input", result.stdout)
        self.assertNotIn("CHANGELOG.md", result.stdout)

    def test_prose_backticks_are_not_companions(self) -> None:
        result = run_owes(str(FIXTURES / "prose-backticks"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("no unkept obligations", result.stdout)
        self.assertNotIn("README.md", result.stdout)
        self.assertNotIn("CONTRIBUTING.md", result.stdout)
        self.assertNotIn("LICENSE.md", result.stdout)
        self.assertNotIn("missing companions", result.stdout)

    def test_json_prose_backticks_empty(self) -> None:
        result = run_owes("--json", str(FIXTURES / "prose-backticks"))
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["unkept_references"], [])
        self.assertEqual(payload["missing_companions"], [])


if __name__ == "__main__":
    unittest.main()
