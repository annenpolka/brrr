#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from underpath.cli import main
from underpath.match import Matcher, fold, snippet_in_text
from underpath.query import query_file
from underpath.scan import hits_in_file, collapse_hits


class FoldTests(unittest.TestCase):
    def test_spacing_and_bytestring(self) -> None:
        self.assertIn(fold('starts_with(a/)'), fold('bytes.starts_with(b"a/")'))
        self.assertEqual(fold("len < 7"), fold("len<7"))
        self.assertTrue(snippet_in_text("user.locked", "if user.locked"))
        self.assertTrue(snippet_in_text("starts_with a/", 'bytes.starts_with(b"a/")'))
        self.assertFalse(snippet_in_text("user is None", "user is not None"))
        self.assertFalse(snippet_in_text("unknownID", "unknownSelectionUnitID"))
        self.assertFalse(snippet_in_text("invalidRange", "range.isEmpty"))
        self.assertFalse(snippet_in_text("Decision:", "decision_section"))
        self.assertTrue(snippet_in_text("Decision:", "'Decision:' not in decision_section"))


class NestedUnderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = ROOT / "fixtures" / "nested.py"

    def test_user_locked_covers_denied_not_drained(self) -> None:
        hits = hits_in_file(self.path, Matcher(["user.locked"]))
        lines = {h.loc.line for h in hits}
        self.assertIn(13, lines)
        self.assertIn(10, lines)
        self.assertNotIn(34, lines)
        self.assertNotIn(8, lines)  # eval-only if-line is not "under"

    def test_given_none_guard_is_fallthrough(self) -> None:
        hits = hits_in_file(self.path, Matcher(["user is not None"], kinds={"given"}))
        lines = {h.loc.line for h in hits}
        self.assertIn(8, lines)
        self.assertIn(13, lines)
        self.assertNotIn(6, lines)  # inside the None arm, not the given

    def test_and_path_narrows(self) -> None:
        wide = hits_in_file(self.path, Matcher(["user is not None"]))
        narrow = hits_in_file(self.path, Matcher(["user is not None", "can_delete"]))
        self.assertGreater(len(wide), len(narrow))
        self.assertTrue(any(h.loc.line == 13 for h in narrow))
        self.assertFalse(any(h.loc.line == 34 for h in narrow))

    def test_collapse_same_stack(self) -> None:
        raw = hits_in_file(self.path, Matcher(["user.pending"]))
        collapsed = collapse_hits(raw)
        self.assertLess(len(collapsed), len(raw))
        self.assertTrue(any(h.start <= 34 <= h.end for h in collapsed))


class BraceUnderTests(unittest.TestCase):
    def test_rust_prefix_given(self) -> None:
        hits = hits_in_file(ROOT / "fixtures" / "guards.rs", Matcher(['starts_with(a/)']))
        lines = {h.loc.line for h in hits}
        self.assertIn(11, lines)
        self.assertTrue(any("given" in h.matched_text or "starts_with" in h.loc.cond_path for h in hits))
        # raw len<7 is the early-return arm, not the fallthrough given ¬(len<7)
        early = hits_in_file(ROOT / "fixtures" / "guards.rs", Matcher(["len<7"]))
        self.assertTrue(any(h.loc.line == 6 for h in early))
        self.assertFalse(any(h.loc.line == 11 for h in early))
        given = hits_in_file(
            ROOT / "fixtures" / "guards.rs", Matcher(["len<7"], kinds={"given"})
        )
        self.assertTrue(any(h.loc.line == 11 for h in given))
        # leading ! is a negation: the early-return arm is NOT under starts_with(a/)
        bang = hits_in_file(ROOT / "fixtures" / "guards.rs", Matcher(["starts_with(a/)"]))
        self.assertFalse(any(h.loc.line == 9 for h in bang))
        self.assertTrue(any(h.loc.line == 11 for h in bang))

    def test_swift_guard(self) -> None:
        hits = hits_in_file(ROOT / "fixtures" / "sample.swift", Matcher(["isEnabled"]))
        lines = {h.loc.line for h in hits}
        self.assertIn(6, lines)
        self.assertNotIn(3, lines)  # the return inside guard-else

    def test_contradict_not_x(self) -> None:
        hits = hits_in_file(ROOT / "fixtures" / "contradict.py", Matcher(["not x"]))
        self.assertTrue(any(h.loc.line == 4 for h in hits))


class CliTests(unittest.TestCase):
    def _run(self, argv, stdin: str | None = None) -> tuple[int, str]:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(argv, stdin=io.StringIO(stdin) if stdin is not None else io.StringIO(""))
        finally:
            sys.stdout = old
        return rc, buf.getvalue()

    def test_explain_denied(self) -> None:
        rc, out = self._run(
            ["user.locked", str(ROOT / "fixtures" / "nested.py"), "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("can_delete", out)
        self.assertIn("return \"denied\"", out)

    def test_missing_predicate(self) -> None:
        buf = io.StringIO()
        old = sys.stderr
        sys.stderr = buf
        try:
            rc = main([], stdin=io.StringIO(""))
        finally:
            sys.stderr = old
        self.assertEqual(rc, 2)

    def test_no_hit(self) -> None:
        rc, out = self._run(
            ["no-such-predicate-xyz", str(ROOT / "fixtures" / "nested.py"), "--tsv"]
        )
        self.assertEqual(rc, 1)
        self.assertEqual(out.strip(), "")

    def test_grep_filter(self) -> None:
        rc, out = self._run(
            ["user.locked", "--tsv", str(ROOT / "fixtures" / "nested.py")],
            stdin="13:    return \"denied\"\n34:            return \"drained\"\n",
        )
        self.assertEqual(rc, 0)
        self.assertIn(":13", out)
        self.assertNotIn(":34", out)

    def test_same_as(self) -> None:
        rc, out = self._run(
            [
                "--same-as",
                f"{ROOT / 'fixtures' / 'nested.py'}:13",
                "--tsv",
                str(ROOT / "fixtures" / "nested.py"),
            ]
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)

    def test_diff_filter(self) -> None:
        rc, out = self._run(
            ["can_delete", "--diff", str(ROOT / "fixtures" / "sample.diff"), "--explain"]
        )
        self.assertEqual(rc, 0)
        # unapplied patch maps + onto the working-tree line (return denied)
        self.assertIn("can_delete", out)
        self.assertIn("denied", out)


if __name__ == "__main__":
    unittest.main()
