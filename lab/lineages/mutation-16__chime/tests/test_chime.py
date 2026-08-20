#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from chimeline.cli import main
from chimeline.query import query_file
from chimeline.rhyme import relation
from chimeline.scan import collapse_hits, drop_noise, hits_in_file


class NestedRhymeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = ROOT / "fixtures" / "nested.py"
        self.seed13 = query_file(self.path, 13)
        self.seed8 = query_file(self.path, 8)
        self.seed10 = query_file(self.path, 10)

    def test_denied_is_exact_only_itself(self) -> None:
        hits = hits_in_file(self.path, self.seed13, exact=True)
        lines = {h.loc.line for h in hits}
        self.assertEqual(lines, {13})
        self.assertTrue(all(h.relation == "same" for h in hits))

    def test_denied_does_not_chime_with_drained(self) -> None:
        hits = hits_in_file(self.path, self.seed13)
        lines = {h.loc.line for h in hits}
        self.assertIn(13, lines)
        self.assertNotIn(34, lines)
        self.assertNotIn(6, lines)

    def test_after_none_guard_is_superset_of_locked_and_pending(self) -> None:
        hits = hits_in_file(self.path, self.seed8)
        lines = {h.loc.line for h in hits}
        self.assertIn(8, lines)
        self.assertIn(13, lines)  # deeper: locked + admin + can_delete
        self.assertIn(34, lines)  # deeper: pending + for-else
        self.assertNotIn(6, lines)  # the None arm is the opposite polarity
        self.assertNotIn(45, lines)  # fallthrough lost the given (engine hole)

    def test_try_body_does_not_include_except(self) -> None:
        hits = hits_in_file(self.path, self.seed10)
        lines = {h.loc.line for h in hits}
        self.assertIn(10, lines)  # db.flush
        self.assertIn(13, lines)  # deeper admin
        self.assertNotIn(17, lines)  # except body
        self.assertNotIn(19, lines)
        exact = hits_in_file(self.path, self.seed10, exact=True)
        exact_lines = {h.loc.line for h in exact}
        self.assertIn(10, lines)
        self.assertNotIn(13, exact_lines)  # nested admin is deeper, not same

    def test_relation_prefix(self) -> None:
        loc8 = query_file(self.path, 8)
        loc13 = query_file(self.path, 13)
        loc6 = query_file(self.path, 6)
        self.assertEqual(relation(loc8, loc13), "deeper")
        self.assertEqual(relation(loc13, loc13), "same")
        self.assertIsNone(relation(loc13, loc8))  # subset, not super
        self.assertIsNone(relation(loc8, loc6))


class BraceRhymeTests(unittest.TestCase):
    def test_rust_fallthrough_not_early_return(self) -> None:
        path = ROOT / "fixtures" / "guards.rs"
        seed = query_file(path, 11)
        hits = hits_in_file(path, seed)
        lines = {h.loc.line for h in hits}
        self.assertIn(11, lines)
        self.assertNotIn(3, lines)  # quoted-form early return
        self.assertNotIn(6, lines)  # len<7 early return
        self.assertNotIn(9, lines)  # !starts_with early return

    def test_swift_guard_body_not_else(self) -> None:
        path = ROOT / "fixtures" / "sample.swift"
        seed = query_file(path, 6)
        hits = hits_in_file(path, seed)
        lines = {h.loc.line for h in hits}
        self.assertIn(6, lines)
        self.assertNotIn(3, lines)  # guard-else return
        # second-guard else still has isEnabled in force
        self.assertIn(10, lines)


class CollapseTests(unittest.TestCase):
    def test_collapse_contiguous(self) -> None:
        path = ROOT / "fixtures" / "nested.py"
        seed = query_file(path, 8)
        raw = hits_in_file(path, seed)
        collapsed = collapse_hits(raw)
        self.assertLess(len(collapsed), len(raw))

    def test_noise_drop_prefers_let_not_brace(self) -> None:
        path = ROOT / "fixtures" / "guards.rs"
        seed = query_file(path, 11)
        raw = hits_in_file(path, seed, exact=True)
        cleaned = drop_noise(raw)
        collapsed = collapse_hits(cleaned)
        self.assertTrue(collapsed)
        heres = {h.loc.here.strip() for h in collapsed}
        self.assertTrue(any("let p" in h or "Some(p)" in h for h in heres))
        self.assertNotIn("}", heres)


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

    def test_explain_denied_exact(self) -> None:
        rc, out = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:13", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_try_exact_is_flush_and_return_not_except(self) -> None:
        rc, out = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:10", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("db.flush()", out)
        self.assertIn("return None", out)
        self.assertNotIn("except", out)
        self.assertNotIn("denied", out)

    def test_same_as_flag(self) -> None:
        rc, out = self._run(
            [
                "--same-as",
                f"{ROOT / 'fixtures' / 'nested.py'}:13",
                "--exact",
                "--tsv",
            ]
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)

    def test_missing_locus(self) -> None:
        buf = io.StringIO()
        old = sys.stderr
        sys.stderr = buf
        try:
            rc = main([], stdin=io.StringIO(""))
        finally:
            sys.stderr = old
        self.assertEqual(rc, 2)

    def test_guards_here_is_payload(self) -> None:
        rc, out = self._run(
            [f"{ROOT / 'fixtures' / 'guards.rs'}:11", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("let p", out)
        self.assertNotIn("here   }", out)

    def test_grep_filter(self) -> None:
        rc, out = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:8", "--tsv"],
            stdin='13:    return "denied"\n6:        audit.warn("missing")\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn(":13", out)
        self.assertNotIn(":6", out)


if __name__ == "__main__":
    unittest.main()
