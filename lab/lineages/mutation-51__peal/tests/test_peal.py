#!/usr/bin/env python3
from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pealline.cli import main
from pealline.diffio import parse_locator_line
from pealline.query import query_file
from pealline.rhyme import relation
from pealline.scan import collapse_hits, drop_noise, hits_in_file


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

    def test_denied_does_not_peal_with_drained(self) -> None:
        hits = hits_in_file(self.path, self.seed13)
        lines = {h.loc.line for h in hits}
        self.assertIn(13, lines)
        self.assertNotIn(34, lines)
        self.assertNotIn(6, lines)

    def test_after_none_guard_is_superset_of_locked_and_pending(self) -> None:
        hits = hits_in_file(self.path, self.seed8)
        lines = {h.loc.line for h in hits}
        self.assertIn(8, lines)
        self.assertIn(13, lines)
        self.assertIn(34, lines)
        self.assertNotIn(6, lines)
        self.assertNotIn(45, lines)

    def test_try_body_does_not_include_except(self) -> None:
        hits = hits_in_file(self.path, self.seed10)
        lines = {h.loc.line for h in hits}
        self.assertIn(10, lines)
        self.assertIn(13, lines)
        self.assertNotIn(17, lines)
        self.assertNotIn(19, lines)
        exact = hits_in_file(self.path, self.seed10, exact=True)
        exact_lines = {h.loc.line for h in exact}
        self.assertNotIn(13, exact_lines)

    def test_relation_prefix(self) -> None:
        loc8 = query_file(self.path, 8)
        loc13 = query_file(self.path, 13)
        loc6 = query_file(self.path, 6)
        self.assertEqual(relation(loc8, loc13), "deeper")
        self.assertEqual(relation(loc13, loc13), "same")
        self.assertIsNone(relation(loc13, loc8))
        self.assertIsNone(relation(loc8, loc6))


class BraceRhymeTests(unittest.TestCase):
    def test_rust_fallthrough_not_early_return(self) -> None:
        path = ROOT / "fixtures" / "guards.rs"
        seed = query_file(path, 11)
        hits = hits_in_file(path, seed)
        lines = {h.loc.line for h in hits}
        self.assertIn(11, lines)
        self.assertNotIn(3, lines)
        self.assertNotIn(6, lines)
        self.assertNotIn(9, lines)

    def test_swift_guard_body_not_else(self) -> None:
        path = ROOT / "fixtures" / "sample.swift"
        seed = query_file(path, 6)
        hits = hits_in_file(path, seed)
        lines = {h.loc.line for h in hits}
        self.assertIn(6, lines)
        self.assertNotIn(3, lines)
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


class LocatorParseTests(unittest.TestCase):
    def test_rg_nh(self) -> None:
        loc = parse_locator_line(
            'fixtures/guards.rs:8:        if !bytes.starts_with(b"a/") {'
        )
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

    def test_explain_denied_exact(self) -> None:
        rc, out, _ = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:13", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_try_exact_is_flush_and_return_not_except(self) -> None:
        rc, out, _ = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:10", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("db.flush()", out)
        self.assertIn("return None", out)
        self.assertNotIn("except", out)
        self.assertNotIn("denied", out)

    def test_same_as_flag(self) -> None:
        rc, out, _ = self._run(
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
        rc, _, err = self._run([])
        self.assertEqual(rc, 2)
        self.assertIn("No cwd walk", err)

    def test_refuses_dir_walk(self) -> None:
        rc, _, err = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:13", str(ROOT / "fixtures")]
        )
        self.assertEqual(rc, 2)
        self.assertIn("will not walk", err)

    def test_guards_here_is_payload(self) -> None:
        rc, out, _ = self._run(
            [f"{ROOT / 'fixtures' / 'guards.rs'}:11", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("let p", out)
        self.assertNotIn("here   }", out)

    def test_stdin_locators_scan_the_file_not_the_lines(self) -> None:
        # rg hit is the inverted `!starts_with` arm. Scanning still finds `let p`.
        guards = ROOT / "fixtures" / "guards.rs"
        stdin = f"{guards}:11:    let p = (bytes.len() - 5) / 2;\n"
        rc, out, err = self._run(["--tsv"], stdin=stdin)
        self.assertEqual(rc, 0, err)
        self.assertIn("let p", out)
        # scan, not filter: contiguous same-stack includes the next statement
        self.assertIn("11-12", out)
        self.assertNotIn("return None", out)

    def test_rg_l_needs_a_seed(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, _, err = self._run(["--tsv"], stdin=f"{nested}\n")
        self.assertEqual(rc, 2)
        self.assertIn("locus", err)

    def test_rg_l_plus_same_as_scans_named_file(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            ["--same-as", f"{nested}:13", "--exact", "--tsv"],
            stdin=f"{nested}\n",
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_hits_filters_locator_lines(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            [f"{nested}:8", "--hits", "--tsv"],
            stdin='13:    return "denied"\n6:        audit.warn("missing")\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn(":13", out)
        self.assertNotIn(":6", out)

    def test_bare_line_recovers_unique_git_file(self) -> None:
        # single-file rg omits the filename; (line, text) pins name nested.py
        rc, out, err = self._run(
            ["--exact", "--tsv"],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_bare_line_unknown_pins_refuse(self) -> None:
        rc, _, err = self._run(
            ["--tsv"],
            stdin="9999:    this-line-does-not-exist-xyzzy\n",
        )
        self.assertEqual(rc, 2)
        self.assertIn("LINE:text", err)

    def test_bare_line_plus_file_operand_scans(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            ["--tsv", str(nested)],
            stdin='13:    return "denied"\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)
        # locator file and FILE operand are the same path — scan once
        self.assertEqual(out.count("denied"), 1)


if __name__ == "__main__":
    unittest.main()
