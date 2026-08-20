#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from whenline.cli import main
from whenline.diffio import parse_grep_lines, parse_unified_diff
from whenline.query import query_file


class PythonLocusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = ROOT / "fixtures" / "nested.py"

    def test_denied_is_under_admin_and_not_can_delete(self) -> None:
        loc = query_file(self.path, 13)
        kinds = [f.kind for f in loc.frames]
        preds = [f.pred for f in loc.frames]
        self.assertIn("fn", kinds)
        self.assertIn("if", kinds)
        self.assertIn("try", kinds)
        joined = loc.cond_path
        self.assertIn("user.locked", joined)
        self.assertIn("user.role == 'admin'", joined)
        self.assertIn("not user.can_delete", joined)
        self.assertNotIn("except", joined)

    def test_except_arm(self) -> None:
        loc = query_file(self.path, 19)
        self.assertIn("except", loc.cond_path)
        self.assertIn("retry", loc.cond_path)
        self.assertNotIn("try |", loc.cond_path.replace("try-else", ""))

    def test_for_else(self) -> None:
        loc = query_file(self.path, 34)
        self.assertIn("for-else", loc.cond_path)

    def test_match_case_guard(self) -> None:
        loc = query_file(self.path, 38)
        self.assertIn("match", loc.cond_path)
        self.assertIn("case", loc.cond_path)
        self.assertIn("age", loc.cond_path)

    def test_decorator_line(self) -> None:
        loc = query_file(self.path, 52)
        self.assertTrue(loc.frames)
        self.assertTrue("decorating" in loc.cond_path or "top" in loc.cond_path)

    def test_comprehension(self) -> None:
        loc = query_file(self.path, 54)
        self.assertTrue(any("comp" in f.kind or "for" in f.kind for f in loc.frames) or "n in x" in loc.path)

    def test_fallthrough_after_none_guard(self) -> None:
        loc = query_file(self.path, 8)
        kinds = [f.kind for f in loc.frames]
        self.assertIn("given", kinds)
        self.assertTrue(any("is not None" in f.pred or "¬" in f.pred for f in loc.frames))


class BraceLocusTests(unittest.TestCase):
    def test_rust_nested_if(self) -> None:
        loc = query_file(ROOT / "fixtures" / "sample.rs", 7)
        self.assertIn("if", loc.cond_path)
        self.assertIn("success", loc.cond_path.lower() + loc.path.lower())

    def test_swift_guard_body(self) -> None:
        loc = query_file(ROOT / "fixtures" / "sample.swift", 3)
        # v1: at least inside detect()
        self.assertTrue(loc.function or loc.cond_path or loc.frames)

    def test_swift_after_guard(self) -> None:
        loc = query_file(ROOT / "fixtures" / "sample.swift", 6)
        self.assertTrue(loc.frames)

    def test_rust_early_return_given_and_string(self) -> None:
        loc = query_file(ROOT / "fixtures" / "guards.rs", 11)
        self.assertIn("given", loc.cond_path)
        self.assertIn("a/", loc.cond_path)
        self.assertIn("7", loc.cond_path)

    def test_swift_switch_second_case(self) -> None:
        loc = query_file(ROOT / "fixtures" / "sample.swift", 18)
        self.assertTrue("elif" in loc.cond_path or "else" in loc.cond_path or "present" in loc.cond_path)


class DiffTests(unittest.TestCase):
    def test_parse_and_annotate(self) -> None:
        text = (ROOT / "fixtures" / "sample.diff").read_text()
        hits = parse_unified_diff(text)
        self.assertTrue(hits)
        self.assertEqual(hits[0].side, "+")
        loc = query_file(ROOT / hits[0].path, hits[0].line)
        self.assertIn("can_delete", loc.cond_path)

    def test_cli_diff(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(["--diff", str(ROOT / "fixtures" / "sample.diff"), "--explain"])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        self.assertIn("can_delete", buf.getvalue())


class GrepTests(unittest.TestCase):
    def test_file_line_colon(self) -> None:
        qs = parse_grep_lines("fixtures/nested.py:13:return denied\n")
        self.assertEqual(qs[0].file, "fixtures/nested.py")
        self.assertEqual(qs[0].line, 13)

    def test_bare_line_needs_default(self) -> None:
        self.assertEqual(parse_grep_lines("34:            return None;\n"), [])
        qs = parse_grep_lines("34:            return None;\n", default_file="parse.rs")
        self.assertEqual(qs[0].file, "parse.rs")
        self.assertEqual(qs[0].line, 34)


class CliTests(unittest.TestCase):
    def test_file_line(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main([str(ROOT / "fixtures" / "nested.py:13"), "--tsv"])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        self.assertIn("user.locked", buf.getvalue())

    def test_rg_bare_line_with_file(self) -> None:
        buf = io.StringIO()
        old_out = sys.stdout
        sys.stdout = buf
        try:
            rc = main(
                [str(ROOT / "fixtures" / "nested.py"), "--tsv"],
                stdin=io.StringIO('13:    return "denied"\n'),
            )
        finally:
            sys.stdout = old_out
        self.assertEqual(rc, 0)
        self.assertIn("can_delete", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
