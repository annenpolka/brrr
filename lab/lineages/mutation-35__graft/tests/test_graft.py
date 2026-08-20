#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from graftcore.cli import main
from graftcore.index import query_source
from graftcore.overlay import overlay_diff


class OverlayStackTests(unittest.TestCase):
    def test_insert_under_existing_if(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(
                ["-C", str(ROOT), "--base", ":wt", "--diff", str(ROOT / "fixtures" / "insert.diff"), "--explain"]
            )
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0, buf.getvalue())
        out = buf.getvalue()
        self.assertIn("can_delete", out)
        self.assertIn("audit.block", out)
        self.assertIn("[post]", out)

    def test_new_if_on_post_image(self) -> None:
        """The new `if bytes.len() > 100` is not in HEAD; overlay must see it."""
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(
                ["-C", str(ROOT), "--base", ":wt", "--diff", str(ROOT / "fixtures" / "newif.diff"), "--tsv"]
            )
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0, buf.getvalue())
        rows = [r for r in buf.getvalue().splitlines() if r.strip()]
        self.assertTrue(rows)
        # the `return None` inside the NEW if must mention len() > 100
        joined = "\n".join(rows)
        self.assertIn("100", joined)
        self.assertIn("if", joined)

    def test_new_file_post_image(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(
                ["-C", str(ROOT), "--base", ":wt", "--diff", str(ROOT / "fixtures" / "newfile.diff"), "--explain"]
            )
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("x > 10", buf.getvalue())
        self.assertIn("only_after_apply", buf.getvalue())

    def test_mismatch_exits_1(self) -> None:
        buf = io.StringIO()
        err = io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout = buf
        sys.stderr = err
        try:
            rc = main(
                ["-C", str(ROOT), "--base", ":wt", "--diff", str(ROOT / "fixtures" / "mismatch.diff"), "--tsv"]
            )
        finally:
            sys.stdout, sys.stderr = old_out, old_err
        self.assertEqual(rc, 1)

    def test_no_diff_is_usage(self) -> None:
        rc = main(["--tsv"])
        self.assertEqual(rc, 2)

    def test_now_opt_in(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(["--now", str(ROOT / "fixtures" / "nested.py:13"), "--explain"])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("[now]", buf.getvalue())
        self.assertIn("can_delete", buf.getvalue())

    def test_quoted_diff_carries_nested_total_given(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(
                ["-C", str(ROOT), "--base", ":wt", "--diff", str(ROOT / "fixtures" / "quoted.diff"), "--explain"]
            )
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0, buf.getvalue())
        out = buf.getvalue()
        self.assertIn("grafted", out)
        self.assertTrue('\\"a/' in out or '"a/' in out, out)


class SandwichSelfTests(unittest.TestCase):
    """graft(diff of A→B against A) == stack at B, on fixtures."""

    def test_newif_sandwich(self) -> None:
        diff = (ROOT / "fixtures" / "newif.diff").read_text()
        images = overlay_diff(diff, root=ROOT, base=":wt")
        self.assertEqual(len(images), 1)
        post = images[0].post
        self.assertIsNotNone(post)
        # added `return None` inside the new if
        ret = [a for a in images[0].added if "return None" in a.text]
        self.assertTrue(ret)
        loc = query_source(post or "", "fixtures/guards.rs", ret[0].line)
        self.assertIn("100", loc.cond_path)


if __name__ == "__main__":
    unittest.main()
