#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ambitpath.cli import main
from ambitpath.diffio import parse_locator_line
from ambitpath.match import Matcher, fold, snippet_in_text
from ambitpath.scan import collapse_hits, hits_in_file


class FoldTests(unittest.TestCase):
    def test_spacing_and_bytestring(self) -> None:
        self.assertIn(fold("starts_with(a/)"), fold('bytes.starts_with(b"a/")'))
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
        hits = hits_in_file(ROOT / "fixtures" / "guards.rs", Matcher(["starts_with(a/)"]))
        lines = {h.loc.line for h in hits}
        self.assertIn(11, lines)
        self.assertTrue(
            any("given" in h.matched_text or "starts_with" in h.loc.cond_path for h in hits)
        )
        early = hits_in_file(ROOT / "fixtures" / "guards.rs", Matcher(["len<7"]))
        self.assertTrue(any(h.loc.line == 6 for h in early))
        self.assertFalse(any(h.loc.line == 11 for h in early))
        given = hits_in_file(
            ROOT / "fixtures" / "guards.rs", Matcher(["len<7"], kinds={"given"})
        )
        self.assertTrue(any(h.loc.line == 11 for h in given))
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


class LocatorParseTests(unittest.TestCase):
    def test_rg_nh(self) -> None:
        loc = parse_locator_line('fixtures/guards.rs:8:        if !bytes.starts_with(b"a/") {')
        assert loc is not None
        self.assertEqual(loc.file, "fixtures/guards.rs")
        self.assertEqual(loc.line, 8)

    def test_rg_l(self) -> None:
        loc = parse_locator_line(str(ROOT / "fixtures" / "guards.rs"))
        assert loc is not None
        self.assertIsNone(loc.line)

    def test_bare_line_keeps_pin_without_file(self) -> None:
        loc = parse_locator_line('13:    return "denied"')
        assert loc is not None
        self.assertEqual(loc.file, "")
        self.assertEqual(loc.line, 13)
        loc = parse_locator_line('13:    return "denied"', default_file="fixtures/nested.py")
        assert loc is not None
        self.assertEqual(loc.file, "fixtures/nested.py")
        self.assertEqual(loc.line, 13)

    def test_file_line_only(self) -> None:
        loc = parse_locator_line("parse.rs:60")
        assert loc is not None
        self.assertEqual(loc.file, "parse.rs")
        self.assertEqual(loc.line, 60)


class CliTests(unittest.TestCase):
    def _run(self, argv, stdin: str | None = None) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            rc = main(argv, stdin=io.StringIO(stdin if stdin is not None else ""))
        finally:
            sys.stdout, sys.stderr = old_out, old_err
        return rc, out.getvalue(), err.getvalue()

    def test_explain_denied(self) -> None:
        rc, out, _ = self._run(
            ["user.locked", str(ROOT / "fixtures" / "nested.py"), "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("can_delete", out)
        self.assertIn('return "denied"', out)

    def test_missing_predicate(self) -> None:
        rc, _, err = self._run([])
        self.assertEqual(rc, 2)
        self.assertIn("predicate", err)

    def test_no_hit(self) -> None:
        rc, out, _ = self._run(
            ["no-such-predicate-xyz", str(ROOT / "fixtures" / "nested.py"), "--tsv"]
        )
        self.assertEqual(rc, 1)
        self.assertEqual(out.strip(), "")

    def test_refuses_cwd_walk(self) -> None:
        rc, _, err = self._run(["no-such-predicate-xyz"])
        self.assertEqual(rc, 2)
        self.assertIn("No cwd walk", err)

    def test_refuses_dir_walk(self) -> None:
        rc, _, err = self._run(["user.locked", str(ROOT / "fixtures")])
        self.assertEqual(rc, 2)
        self.assertIn("will not walk", err)

    def test_stdin_locators_scan_the_file_not_the_lines(self) -> None:
        # rg hit is the inverted `!starts_with` arm. Scanning the file still
        # finds the fallthrough `let p` which rg never printed.
        guards = ROOT / "fixtures" / "guards.rs"
        stdin = f'{guards}:8:        if !bytes.starts_with(b"a/") {{\n'
        rc, out, _ = self._run(["starts_with(a/)", "--tsv"], stdin=stdin)
        self.assertEqual(rc, 0)
        self.assertIn("let p", out)
        self.assertIn("given bytes.starts_with", out)
        self.assertNotIn("return None", out)

    def test_rg_l_scans_named_file(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(["user.locked", "--tsv"], stdin=f"{nested}\n")
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_bare_line_recovers_unique_git_file(self) -> None:
        # single-file rg omits the filename; (line, text) pins name nested.py
        rc, out, err = self._run(
            ["user.locked", "--tsv"],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_bare_line_plus_file_operand_scans(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            ["user.locked", "--tsv", str(nested)],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        # scan, not filter: the 13: locator only names the file
        self.assertNotIn("drained", out)

    def test_hits_filters_locator_lines(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            ["user.locked", "--hits", "--tsv", str(nested)],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn(":13", out)
        self.assertNotIn(":34", out)

    def test_same_as(self) -> None:
        rc, out, _ = self._run(
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
        rc, out, _ = self._run(
            ["can_delete", "--diff", str(ROOT / "fixtures" / "sample.diff"), "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("can_delete", out)
        self.assertIn("denied", out)


if __name__ == "__main__":
    unittest.main()
