#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from amidpath.cli import main
from amidpath.derive import derive_snippets
from amidpath.locators import iter_queries, parse_rg_json_line, queries_from_text
from amidpath.match import Matcher, fold, snippet_in_text
from amidpath.query import query_file
from amidpath.scan import collapse_hits, hits_in_file, scan_one_file


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
        self.assertNotIn(8, lines)

    def test_given_none_guard_is_fallthrough(self) -> None:
        hits = hits_in_file(self.path, Matcher(["user is not None"], kinds={"given"}))
        lines = {h.loc.line for h in hits}
        self.assertIn(8, lines)
        self.assertIn(13, lines)
        self.assertNotIn(6, lines)

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
        self.assertNotIn(3, lines)

    def test_contradict_not_x(self) -> None:
        hits = hits_in_file(ROOT / "fixtures" / "contradict.py", Matcher(["not x"]))
        self.assertTrue(any(h.loc.line == 4 for h in hits))

    def test_scan_one_file_collapses(self) -> None:
        hits = scan_one_file(ROOT / "fixtures" / "nested.py", Matcher(["user.locked"]))
        self.assertTrue(hits)
        self.assertTrue(any("denied" in h.loc.here for h in hits))


class LocatorParseTests(unittest.TestCase):
    def test_file_line_text(self) -> None:
        qs = queries_from_text("fixtures/nested.py:13:    return denied\n")
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0].file, "fixtures/nested.py")
        self.assertEqual(qs[0].line, 13)

    def test_bare_needs_default(self) -> None:
        self.assertEqual(queries_from_text("13:    return denied\n"), [])
        qs = queries_from_text("13:    return denied\n", default_file="nested.py")
        self.assertEqual(qs[0].file, "nested.py")
        self.assertEqual(qs[0].line, 13)

    def test_heading_then_bare(self) -> None:
        text = "fixtures/nested.py\n13:    return denied\n34:            return drained\n"
        qs = queries_from_text(text)
        self.assertEqual([q.line for q in qs], [13, 34])
        self.assertEqual(qs[0].file, "fixtures/nested.py")

    def test_stream_heading_switch(self) -> None:
        text = (
            "fixtures/nested.py\n"
            "13:x\n"
            "\n"
            "fixtures/guards.rs\n"
            "11:y\n"
        )
        qs = list(iter_queries(text.splitlines()))
        self.assertEqual(qs[0].file, "fixtures/nested.py")
        self.assertEqual(qs[1].file, "fixtures/guards.rs")

    def test_rg_json_always_has_file(self) -> None:
        rec = {
            "type": "match",
            "data": {
                "path": {"text": "fixtures/guards.rs"},
                "line_number": 8,
                "lines": {"text": '    if !bytes.starts_with(b"a/") {\n'},
            },
        }
        q, head = parse_rg_json_line(json.dumps(rec))
        self.assertIsNotNone(q)
        assert q is not None
        self.assertEqual(q.file, "fixtures/guards.rs")
        self.assertEqual(q.line, 8)
        self.assertEqual(head, "fixtures/guards.rs")


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

    def test_refuses_cwd_and_empty(self) -> None:
        rc, _, err = self._run(["user.locked"])
        self.assertEqual(rc, 2)
        self.assertIn("pipe locators", err)

    def test_refuses_directory_walk(self) -> None:
        rc, _, err = self._run(["user.locked", str(ROOT / "fixtures")])
        self.assertEqual(rc, 2)
        self.assertIn("refusing to walk", err)

    def test_locator_scan_expands_past_piped_line(self) -> None:
        # only line 13 is piped; scan of the same file must also hit db.flush (L10)
        loc = f"{ROOT / 'fixtures' / 'nested.py'}:13:    return \"denied\"\n"
        rc, out, _ = self._run(["user.locked", "--tsv"], stdin=loc)
        self.assertEqual(rc, 0)
        self.assertIn(":13", out)
        self.assertIn("denied", out)
        # expansion: a locus rg never printed
        self.assertTrue(":10" in out or "flush" in out)

    def test_bare_line_plus_file_operand(self) -> None:
        rc, out, _ = self._run(
            ["user.locked", "--tsv", str(ROOT / "fixtures" / "nested.py")],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        # default is scan-the-file, so drained's file is scanned but drained
        # itself is not under user.locked
        self.assertNotIn("drained", out)

    def test_pin_filters_locators(self) -> None:
        loc = (
            f"{ROOT / 'fixtures' / 'nested.py'}:13:    return \"denied\"\n"
            f"{ROOT / 'fixtures' / 'nested.py'}:34:            return \"drained\"\n"
        )
        rc, out, _ = self._run(["user.locked", "--pin", "--tsv"], stdin=loc)
        self.assertEqual(rc, 0)
        self.assertIn(":13", out)
        self.assertNotIn(":34", out)
        # pin does not expand to other lines in the file
        self.assertNotIn(":10", out)

    def test_rust_locator_expands_to_fallthrough(self) -> None:
        loc = f"{ROOT / 'fixtures' / 'guards.rs'}:8:    if !bytes.starts_with(b\"a/\") {{\n"
        rc, out, _ = self._run(["starts_with(a/)", "--tsv"], stdin=loc)
        self.assertEqual(rc, 0)
        self.assertIn("starts_with", out)
        self.assertTrue("let p" in out or "Some(p)" in out or ":11" in out)
        self.assertNotIn("return None", out)

    def test_heading_stream(self) -> None:
        text = f"{ROOT / 'fixtures' / 'guards.rs'}\n8:    if !bytes.starts_with\n"
        rc, out, _ = self._run(["starts_with(a/)", "--tsv"], stdin=text)
        self.assertEqual(rc, 0)
        self.assertTrue("let p" in out or "Some(p)" in out or "given bytes.starts_with" in out)

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

    def test_derive_peels_bang_if(self) -> None:
        loc = query_file(ROOT / "fixtures" / "guards.rs", 8)
        snips = derive_snippets(loc, peel_intro=True)
        self.assertTrue(any("starts_with" in s and not s.startswith("!") for s in snips))

    def test_rg_json_no_snippet_expands_fallthrough(self) -> None:
        rec = json.dumps(
            {
                "type": "match",
                "data": {
                    "path": {"text": str(ROOT / "fixtures" / "guards.rs")},
                    "line_number": 8,
                    "lines": {"text": '    if !bytes.starts_with(b"a/") {\n'},
                },
            }
        )
        rc, out, _ = self._run(["--tsv"], stdin=rec + "\n")
        self.assertEqual(rc, 0)
        self.assertTrue("let p" in out or "Some(p)" in out or "given bytes.starts_with" in out)
        self.assertNotIn("return None", out)

    def test_bare_line_error_mentions_json(self) -> None:
        rc, _, err = self._run(["starts_with(a/)"], stdin="8:    if !bytes.starts_with\n")
        self.assertEqual(rc, 2)
        self.assertIn("LINE:text", err)
        self.assertIn("--json", err)

    def test_diff_scans_named_file(self) -> None:
        rc, out, _ = self._run(
            ["can_delete", "--diff", str(ROOT / "fixtures" / "sample.diff"), "--tsv"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("can_delete", out)
        self.assertIn("denied", out)


if __name__ == "__main__":
    unittest.main()
