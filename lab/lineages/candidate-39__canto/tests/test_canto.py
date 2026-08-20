#!/usr/bin/env python3
"""Unit tests for canto — import the CLI file as a module."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_loader = importlib.machinery.SourceFileLoader("canto", str(ROOT / "canto"))
_spec = importlib.util.spec_from_loader("canto", _loader)
canto = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["canto"] = canto
_spec.loader.exec_module(canto)


class ParseDiff(unittest.TestCase):
    def test_new_file_and_hunk(self):
        files = canto.parse_diff(canto.MIXED_PY)
        self.assertEqual(len(files), 5)
        self.assertEqual(files[0].path, "pkg/lexer.py")
        self.assertEqual(files[0].status, "add")
        self.assertTrue(files[0].hunks)
        self.assertTrue(any(k == "+" and "class Lexer" in t for k, t in files[0].hunks[0].lines))

    def test_rename(self):
        text = """diff --git a/old.py b/new.py
similarity index 90%
rename from old.py
rename to new.py
--- a/old.py
+++ b/new.py
@@ -1,1 +1,1 @@
-x
+y
"""
        files = canto.parse_diff(text)
        self.assertEqual(files[0].status, "rename")
        self.assertEqual(files[0].path, "new.py")
        self.assertEqual(files[0].old_path, "old.py")


class Names(unittest.TestCase):
    def test_defs(self):
        self.assertIn("Lexer", canto.defs_in_line("class Lexer:"))
        self.assertIn("Alpha", canto.defs_in_line("pub struct Alpha {"))
        self.assertIn("Arbiter", canto.defs_in_line("public final class Arbiter {"))
        self.assertIn("PresenceArbiter", canto.defs_in_line(
            "public final class PresenceArbiter: PresenceDetectorProtocol, @unchecked Sendable {"
        ))

    def test_stopwords_not_uses(self):
        self.assertFalse(canto.idents_in("return true"))
        self.assertFalse(canto.idents_in("    pass"))


class PlotMixed(unittest.TestCase):
    def test_reading_order(self):
        plot = canto.build_plot(canto.parse_diff(canto.MIXED_PY), grain="hunk")
        idx = {}
        for a in plot.acts:
            for f in a.files:
                idx.setdefault(f, a.index)
        self.assertLess(idx["pkg/lexer.py"], idx["pkg/parse.py"])
        self.assertLess(idx["pkg/parse.py"], idx["tests/test_parse.py"])
        payoff = [a for a in plot.acts if "tests/test_parse.py" in a.files]
        self.assertEqual(payoff[0].kind, "PAYOFF")
        self.assertEqual(plot.spoil, 0)
        self.assertEqual(plot.tangle, 0)

    def test_readme_aside(self):
        plot = canto.build_plot(canto.parse_diff(canto.MIXED_PY), grain="file")
        readme = [a for a in plot.acts if "README.md" in a.files]
        self.assertTrue(readme)
        self.assertEqual(readme[0].kind, "ASIDE")

    def test_util_uncoupled_track(self):
        plot = canto.build_plot(canto.parse_diff(canto.MIXED_PY), grain="file")
        util_t = next(a.track for a in plot.acts if "pkg/util.py" in a.files)
        parse_t = next(a.track for a in plot.acts if "pkg/parse.py" in a.files)
        self.assertNotEqual(util_t, parse_t)

    def test_two_tracks(self):
        plot = canto.build_plot(canto.parse_diff(canto.TWO_TRACKS), grain="file")
        files_by_track = {}
        for a in plot.acts:
            files_by_track.setdefault(a.track, set()).update(a.files)
        alpha = next(t for t, fs in files_by_track.items() if "src/alpha.rs" in fs)
        beta = next(t for t, fs in files_by_track.items() if "src/beta.rs" in fs)
        self.assertNotEqual(alpha, beta)
        self.assertIn("tests/alpha.rs", files_by_track[alpha])
        self.assertIn("tests/beta.rs", files_by_track[beta])

    def test_spoil_same_hunk(self):
        plot = canto.build_plot(canto.parse_diff(canto.SPOIL_DIFF), grain="hunk")
        self.assertGreaterEqual(plot.spoil, 1)

    def test_touched_class_payoff(self):
        plot = canto.build_plot(canto.parse_diff(canto.TOUCHED_CLASS), grain="hunk")
        kinds = {tuple(a.files): a.kind for a in plot.acts}
        self.assertIn("PAYOFF", [a.kind for a in plot.acts])
        prod = next(a for a in plot.acts if a.files == ["Sources/Arbiter.swift"])
        tests = next(a for a in plot.acts if a.files == ["Tests/ArbiterTests.swift"])
        self.assertLess(prod.index, tests.index)
        self.assertEqual(tests.kind, "PAYOFF")
        self.assertTrue({"presentThreshold", "absentThreshold"} & (prod.natal | prod.defs))

    def test_check_exit(self):
        import io
        buf = io.StringIO(canto.SPOIL_DIFF)
        old_in, old_out = sys.stdin, sys.stdout
        sys.stdin = buf
        sys.stdout = io.StringIO()
        try:
            rc = canto.main(["--stdin", "--check"])
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        self.assertEqual(rc, 1)

    def test_json_shape(self):
        plot = canto.build_plot(canto.parse_diff(canto.MIXED_PY), grain="file")
        js = plot.to_json()
        json.dumps(js)
        self.assertIn("acts", js)
        self.assertTrue(js["acts"])

    def test_porcelain_header(self):
        plot = canto.build_plot(canto.parse_diff(canto.MIXED_PY), grain="file")
        text = canto.format_porcelain(plot)
        self.assertTrue(text.startswith("canto "))
        self.assertIn("TRACK", text)
        self.assertIn("PAYOFF", text)


class SplitVerify(unittest.TestCase):
    def test_file_first_act_disjoint(self):
        plot = canto.build_plot(canto.parse_diff(canto.MIXED_PY), grain="file")
        first = canto.files_first_act(plot)
        self.assertEqual(len(first), len(set(first)))
        self.assertIn("pkg/lexer.py", first)
        self.assertIn("tests/test_parse.py", first)
        self.assertLess(first["pkg/lexer.py"], first["tests/test_parse.py"])


if __name__ == "__main__":
    unittest.main()
