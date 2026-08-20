#!/usr/bin/env python3
"""Live sandwich tests against kizu / sitbone when those repos exist."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
SITBONE = Path("/Users/annenpolka/ghq/github.com/annenpolka/sitbone")

from graftcore.cli import main
import io
import sys


def _git_diff(repo: Path, a: str, b: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "diff", a, b, "--", path],
        capture_output=True,
        text=True,
    )
    proc.check_returncode()
    return proc.stdout


def _graft_tsv(repo: Path, base: str, diff: str) -> str:
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        rc = main(["-C", str(repo), "--base", base, "--tsv"], stdin=io.StringIO(diff))
    finally:
        sys.stdout = old
    assert rc == 0, buf.getvalue()
    return buf.getvalue()


@unittest.skipUnless((KIZU / "src/git/parse.rs").is_file(), "kizu not present")
class KizuSandwich(unittest.TestCase):
    def test_parse_rs_birth_line_60(self) -> None:
        diff = _git_diff(KIZU, "3b3e0a9^", "3b3e0a9", "src/git/parse.rs")
        self.assertTrue(diff.strip())
        tsv = _graft_tsv(KIZU, "3b3e0a9^", diff)
        row = [ln for ln in tsv.splitlines() if ln.startswith("src/git/parse.rs:60\t")]
        self.assertTrue(row, tsv[:500])
        body = row[0]
        self.assertIn("parse_diff_git_header", body)
        self.assertIn('bytes.starts_with(b"\\"a/")', body.replace(" ", ""))
        self.assertIn("given", body)
        self.assertIn("b_side", body)
        self.assertIn("\tpost\tok", body)


@unittest.skipUnless(
    (SITBONE / "Sources/SitboneCore/PresenceArbiter.swift").is_file(),
    "sitbone not present",
)
class SitboneSandwich(unittest.TestCase):
    def test_hysteresis_added_line_under_guards(self) -> None:
        diff = _git_diff(
            SITBONE,
            "e9b0f75^",
            "e9b0f75",
            "Sources/SitboneCore/PresenceArbiter.swift",
        )
        tsv = _graft_tsv(SITBONE, "e9b0f75^", diff)
        # the replacement in detect()
        hits = [ln for ln in tsv.splitlines() if "applyHysteresis(smoothedScore" in ln]
        self.assertTrue(hits, tsv)
        body = hits[0]
        self.assertIn("guard isEnabled", body)
        self.assertIn("detect()", body)
        # the new return inside case .present
        ret = [ln for ln in tsv.splitlines() if "absentThreshold" in ln and "return" in ln]
        self.assertTrue(ret)
        self.assertIn("case", ret[0])
        self.assertIn(". present", ret[0])


if __name__ == "__main__":
    unittest.main()
