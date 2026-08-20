#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from likenpkg.cli import main
from likenpkg.index import query_source
from likenpkg.overlay import overlay_diff
from likenpkg.query import parse_path_query, pred_contains, stack_matches


def run_cli(argv, stdin_text=None):
    buf = io.StringIO()
    err = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = buf, err
    try:
        rc = main(argv, stdin=io.StringIO(stdin_text) if stdin_text is not None else None)
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    return rc, buf.getvalue(), err.getvalue()


class QueryNormTests(unittest.TestCase):
    def test_starts_with_a_matches_unquoted_byte_string(self) -> None:
        self.assertTrue(pred_contains('bytes.starts_with(b"a/")', "starts_with(a/)"))
        self.assertFalse(pred_contains('bytes.starts_with(b"\\"a/")', "starts_with(a/)"))

    def test_path_query_subsequence(self) -> None:
        from likenpkg.model import Frame

        frames = [
            Frame("fn", "parse_header(bytes: &[u8]) -> Option<usize>", 1),
            Frame("given", 'bytes.starts_with(b"a/")', 8),
        ]
        clauses = parse_path_query("fn parse_header | given starts_with(a/)")
        self.assertTrue(stack_matches(frames, clauses))


class InvertTests(unittest.TestCase):
    def test_kin_same_as_a_slash_groups_two_lets(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "kin.diff"),
                "--same-as",
                "fn parse_header | given starts_with(a/)",
                "--payload",
                "--tsv",
            ]
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("let a_side", out)
        self.assertIn("let b_side", out)
        self.assertNotIn("return Some(1)", out)
        self.assertNotIn("fn other_arm", out)

    def test_kin_quoted_if_is_a_different_stack(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "kin.diff"),
                "--same-as",
                r'if starts_with("a/)',
                "--payload",
                "--tsv",
            ]
        )
        # quoted form is if bytes.starts_with(b"\"a/") — not the unquoted given
        # our query uses the escaped-quote content; may be empty if matching is strict
        self.assertNotIn("let a_side", out)
        self.assertNotIn("let b_side", out)

    def test_newif_post_image_not_head(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "newif.diff"),
                "--same-as",
                "if bytes.len() > 100",
                "--explain",
            ]
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("return None", out)
        self.assertIn("100", out)

    def test_same_as_post_image_line(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "kin.diff"),
                "--same-as",
                "fixtures/kin.rs:12",
                "--payload",
                "--tsv",
            ]
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("let a_side", out)
        self.assertIn("let b_side", out)

    def test_explain_prints_shared_once(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "kin.diff"),
                "--same-as",
                "given starts_with(a/)",
            ]
        )
        self.assertEqual(rc, 0, err + out)
        self.assertEqual(out.count("given  bytes.starts_with(b\"a/\")"), 1, out)
        self.assertIn("[same]", out)

    def test_mismatch_none(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "mismatch.diff"),
                "--same-as",
                "given starts_with(a/)",
            ]
        )
        self.assertEqual(rc, 1)

    def test_no_diff_is_usage(self) -> None:
        rc, out, err = run_cli(["--tsv"])
        self.assertEqual(rc, 2)

    def test_dir_operand_is_usage(self) -> None:
        rc, out, err = run_cli(["--diff", str(ROOT / "fixtures" / "kin.diff"), str(ROOT / "fixtures")])
        self.assertEqual(rc, 2)
        self.assertIn("will not walk", err)

    def test_insert_python(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "insert.diff"),
                "--same-as",
                "if not user.can_delete",
                "--explain",
            ]
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("audit.block", out)

    def test_hyst_two_lines_under_guards(self) -> None:
        rc, out, err = run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "hyst.diff"),
                "--same-as",
                "guard isEnabled",
                "--payload",
                "--tsv",
            ]
        )
        self.assertEqual(rc, 0, err + out)
        self.assertIn("applyHysteresis", out)
        self.assertIn("twin", out)

    def test_overlay_does_not_create_kin_rs(self) -> None:
        kin = ROOT / "fixtures" / "kin.rs"
        self.assertFalse(kin.exists())
        run_cli(
            [
                "-C",
                str(ROOT),
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures" / "kin.diff"),
                "--same-as",
                "given starts_with(a/)",
            ]
        )
        self.assertFalse(kin.exists())


class SandwichSelfTests(unittest.TestCase):
    def test_newif_sandwich(self) -> None:
        diff = (ROOT / "fixtures" / "newif.diff").read_text()
        images = overlay_diff(diff, root=ROOT, base=":wt")
        self.assertEqual(len(images), 1)
        post = images[0].post
        self.assertIsNotNone(post)
        ret = [a for a in images[0].added if "return None" in a.text]
        self.assertTrue(ret)
        loc = query_source(post or "", "fixtures/guards.rs", ret[0].line)
        self.assertIn("100", loc.cond_path)


if __name__ == "__main__":
    unittest.main()
