#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from whencecore.cli import main
from whencecore.diffio import parse_grep_lines, parse_unified_diff
from whencecore.model import engine_for
from whencecore.python_eng import query_python
from whencecore.brace_eng import query_braces


def _query(path: Path, line: int):
    src = path.read_text(encoding="utf-8")
    if engine_for(path) == "python-ast":
        return query_python(str(path), src, line)
    return query_braces(str(path), src, line)


class PythonLocusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = ROOT / "fixtures" / "nested.py"

    def test_denied_stack(self) -> None:
        loc = _query(self.path, 13)
        self.assertIn("user.locked", loc.path)
        self.assertIn("user.role == 'admin'", loc.path)
        self.assertIn("not user.can_delete", loc.path)
        self.assertIn("given", [f.kind for f in loc.frames])
        self.assertNotIn("except", loc.path)

    def test_none_guard_given(self) -> None:
        loc = _query(self.path, 8)
        self.assertIn("given", [f.kind for f in loc.frames])
        self.assertTrue(any("is not None" in f.pred for f in loc.frames))

    def test_for_else(self) -> None:
        loc = _query(self.path, 34)
        self.assertIn("for-else", loc.path)

    def test_match_case_guard(self) -> None:
        loc = _query(self.path, 38)
        self.assertIn("match", loc.path)
        self.assertIn("case", loc.path)
        self.assertIn("age", loc.path)

    def test_decorator(self) -> None:
        loc = _query(self.path, 52)
        self.assertIn("decorating", loc.path)

    def test_comprehension(self) -> None:
        loc = _query(self.path, 54)
        self.assertTrue(any("comp" in f.kind for f in loc.frames))


class BraceLocusTests(unittest.TestCase):
    def test_rust_early_return_given(self) -> None:
        loc = _query(ROOT / "fixtures" / "guards.rs", 11)
        self.assertEqual(
            [f.kind for f in loc.frames],
            ["fn", "given", "given", "given"],
        )
        self.assertIn("a/", loc.path)
        self.assertIn("7", loc.path)
        self.assertIn("¬(", loc.path)

    def test_swift_after_guard(self) -> None:
        loc = _query(ROOT / "fixtures" / "sample.swift", 6)
        self.assertIn("guard", [f.kind for f in loc.frames])
        self.assertIn("isEnabled", loc.path)
        self.assertNotIn("guard-else", loc.path)

    def test_swift_guard_else_body(self) -> None:
        loc = _query(ROOT / "fixtures" / "sample.swift", 3)
        self.assertIn("guard-else", [f.kind for f in loc.frames])

    def test_if_let_and_arm(self) -> None:
        loc = _query(ROOT / "fixtures" / "sample.rs", 16)
        self.assertIn("arm", loc.path)
        self.assertIn("Kind::Untracked", loc.path)
        self.assertIn("let Ok(text)=", loc.path)


class GrepDiffTests(unittest.TestCase):
    def test_file_line_colon(self) -> None:
        qs = parse_grep_lines("fixtures/nested.py:13:return denied\n")
        self.assertEqual(qs[0].file, "fixtures/nested.py")
        self.assertEqual(qs[0].line, 13)

    def test_bare_line_needs_default(self) -> None:
        self.assertEqual(parse_grep_lines("34:            return None;\n"), [])
        qs = parse_grep_lines("34:            return None;\n", default_file="parse.rs")
        self.assertEqual(qs[0].file, "parse.rs")
        self.assertEqual(qs[0].line, 34)

    def test_diff_plus_line(self) -> None:
        text = (ROOT / "fixtures" / "sample.diff").read_text()
        hits = parse_unified_diff(text)
        self.assertTrue(hits)
        self.assertEqual(hits[0].side, "+")
        loc = _query(ROOT / hits[0].path, hits[0].line)
        self.assertIn("can_delete", loc.path)


class CliTests(unittest.TestCase):
    def test_file_line_tsv(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main([str(ROOT / "fixtures" / "nested.py") + ":13", "--tsv"])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        self.assertIn("user.locked", buf.getvalue())

    def test_rg_bare_line_with_file(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main(
                [str(ROOT / "fixtures" / "nested.py"), "--tsv"],
                stdin=io.StringIO('13:    return "denied"\n'),
            )
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        self.assertIn("can_delete", buf.getvalue())

    def test_json_depth(self) -> None:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            rc = main([str(ROOT / "fixtures" / "guards.rs") + ":11", "--json"])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        rec = json.loads(buf.getvalue())
        self.assertEqual(rec["depth"], 4)
        self.assertEqual(sum(1 for f in rec["frames"] if f["kind"] == "given"), 3)


class FourGivenTests(unittest.TestCase):
    def test_kizu_parse_rs_60(self) -> None:
        path = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu/src/git/parse.rs")
        if not path.is_file():
            self.skipTest("kizu parse.rs not present")
        loc = _query(path, 60)
        givens = [f.pred for f in loc.frames if f.kind == "given"]
        self.assertEqual(len(givens), 4, givens)
        self.assertEqual(givens[0], "¬(len<5+ 2)")
        self.assertEqual(givens[1], "inner.is_multiple_of(2)")
        self.assertIn('starts_with(b"a/")', givens[2])
        self.assertIn('b" b/"', givens[3])
        self.assertIn("b_side", loc.here)


if __name__ == "__main__":
    unittest.main()
