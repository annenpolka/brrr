#!/usr/bin/env python3
"""Live sandwich tests against kizu / sitbone when those repos exist."""

from __future__ import annotations

import io
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
SITBONE = Path("/Users/annenpolka/ghq/github.com/annenpolka/sitbone")

from likenpkg.cli import main


def _git_diff(repo: Path, a: str, b: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "diff", a, b, "--", path],
        capture_output=True,
        text=True,
    )
    proc.check_returncode()
    return proc.stdout


def _porcelain(repo: Path, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--", path],
        capture_output=True,
        text=True,
    )
    proc.check_returncode()
    return proc.stdout


def _run(argv, diff: str):
    buf = io.StringIO()
    err = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buf, err
    try:
        rc = main(argv, stdin=io.StringIO(diff))
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    return rc, buf.getvalue(), err.getvalue()


@unittest.skipUnless((KIZU / "src/git/parse.rs").is_file(), "kizu not present")
class KizuSandwich(unittest.TestCase):
    def test_parse_rs_birth_same_as_a_slash(self) -> None:
        before = _porcelain(KIZU, "src/git/parse.rs")
        diff = _git_diff(KIZU, "3b3e0a9^", "3b3e0a9", "src/git/parse.rs")
        self.assertTrue(diff.strip())
        rc, out, err = _run(
            [
                "-C",
                str(KIZU),
                "--base",
                "3b3e0a9^",
                "--same-as",
                "fn parse_diff_git_header | given starts_with(a/)",
                "--payload",
                "--tsv",
            ],
            diff,
        )
        after = _porcelain(KIZU, "src/git/parse.rs")
        self.assertEqual(before, after, "overlay dirtied the worktree")
        self.assertEqual(rc, 0, err + out)
        self.assertIn("let a_side", out)
        self.assertIn("let b_side", out)
        self.assertNotIn("return Some(bytes_to_path(&b_decoded[2..]))", out)

    def test_same_as_line_60(self) -> None:
        diff = _git_diff(KIZU, "3b3e0a9^", "3b3e0a9", "src/git/parse.rs")
        rc, out, err = _run(
            [
                "-C",
                str(KIZU),
                "--base",
                "3b3e0a9^",
                "--same-as",
                "src/git/parse.rs:60",
                "--payload",
                "--tsv",
            ],
            diff,
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("let b_side", out)
        # a_side sits above the b/ separator given — not the same stack
        self.assertNotIn("let a_side", out)
        # exact (default for pins): nested if-arm is a superstack, not the same
        self.assertNotIn("if a_side != b_side", out)
        self.assertNotIn("bytes_to_path(a_side)", out)

    def test_line_60_under_includes_deeper_arms(self) -> None:
        diff = _git_diff(KIZU, "3b3e0a9^", "3b3e0a9", "src/git/parse.rs")
        rc, out, err = _run(
            [
                "-C",
                str(KIZU),
                "--base",
                "3b3e0a9^",
                "--same-as",
                "src/git/parse.rs:60",
                "--under",
                "--payload",
                "--tsv",
            ],
            diff,
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("let b_side", out)
        self.assertIn("if a_side != b_side", out)


@unittest.skipUnless(
    (SITBONE / "Sources/SitboneCore/PresenceArbiter.swift").is_file(),
    "sitbone not present",
)
class SitboneSandwich(unittest.TestCase):
    def test_hysteresis_same_as_guards(self) -> None:
        before = _porcelain(SITBONE, "Sources/SitboneCore/PresenceArbiter.swift")
        diff = _git_diff(
            SITBONE,
            "e9b0f75^",
            "e9b0f75",
            "Sources/SitboneCore/PresenceArbiter.swift",
        )
        rc, out, err = _run(
            [
                "-C",
                str(SITBONE),
                "--base",
                "e9b0f75^",
                "--same-as",
                "guard isEnabled",
                "--payload",
                "--tsv",
            ],
            diff,
        )
        after = _porcelain(SITBONE, "Sources/SitboneCore/PresenceArbiter.swift")
        self.assertEqual(before, after, "overlay dirtied the worktree")
        self.assertEqual(rc, 0, err + out)
        self.assertIn("applyHysteresis(smoothedScore: smoothedScore)", out)
        self.assertNotIn("precondition", out)
        self.assertNotIn("absentThreshold", out)

    def test_case_present_not_the_other_arm(self) -> None:
        diff = _git_diff(
            SITBONE,
            "e9b0f75^",
            "e9b0f75",
            "Sources/SitboneCore/PresenceArbiter.swift",
        )
        rc, out, err = _run(
            [
                "-C",
                str(SITBONE),
                "--base",
                "e9b0f75^",
                "--same-as",
                "case .present",
                "--payload",
                "--tsv",
            ],
            diff,
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("absentThreshold", out)
        self.assertNotIn("presentThreshold", out)


if __name__ == "__main__":
    unittest.main()
