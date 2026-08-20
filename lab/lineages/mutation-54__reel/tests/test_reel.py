#!/usr/bin/env python3
"""Unit tests for reel — import the CLI file as a module."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_loader = importlib.machinery.SourceFileLoader("reel", str(ROOT / "reel"))
_spec = importlib.util.spec_from_loader("reel", _loader)
reel = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["reel"] = reel
_spec.loader.exec_module(reel)


class ParseDiff(unittest.TestCase):
    def test_new_file_and_hunk(self):
        files = reel.parse_diff(reel.MIXED_PY)
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
        files = reel.parse_diff(text)
        self.assertEqual(files[0].status, "rename")
        self.assertEqual(files[0].path, "new.py")
        self.assertEqual(files[0].old_path, "old.py")


class Names(unittest.TestCase):
    def test_defs(self):
        self.assertIn("Lexer", reel.defs_in_line("class Lexer:"))
        self.assertIn("Alpha", reel.defs_in_line("pub struct Alpha {"))
        self.assertIn("Arbiter", reel.defs_in_line("public final class Arbiter {"))
        self.assertIn("PresenceArbiter", reel.defs_in_line(
            "public final class PresenceArbiter: PresenceDetectorProtocol, @unchecked Sendable {"
        ))

    def test_stopwords_not_uses(self):
        self.assertFalse(reel.idents_in("return true"))
        self.assertFalse(reel.idents_in("    pass"))


class PlotMixed(unittest.TestCase):
    def test_reading_order(self):
        plot = reel.build_plot(reel.parse_diff(reel.MIXED_PY), grain="hunk")
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
        plot = reel.build_plot(reel.parse_diff(reel.MIXED_PY), grain="file")
        readme = [a for a in plot.acts if "README.md" in a.files]
        self.assertTrue(readme)
        self.assertEqual(readme[0].kind, "ASIDE")

    def test_util_uncoupled_track(self):
        plot = reel.build_plot(reel.parse_diff(reel.MIXED_PY), grain="file")
        util_t = next(a.track for a in plot.acts if "pkg/util.py" in a.files)
        parse_t = next(a.track for a in plot.acts if "pkg/parse.py" in a.files)
        self.assertNotEqual(util_t, parse_t)

    def test_two_tracks(self):
        plot = reel.build_plot(reel.parse_diff(reel.TWO_TRACKS), grain="file")
        files_by_track = {}
        for a in plot.acts:
            files_by_track.setdefault(a.track, set()).update(a.files)
        alpha = next(t for t, fs in files_by_track.items() if "src/alpha.rs" in fs)
        beta = next(t for t, fs in files_by_track.items() if "src/beta.rs" in fs)
        self.assertNotEqual(alpha, beta)
        self.assertIn("tests/alpha.rs", files_by_track[alpha])
        self.assertIn("tests/beta.rs", files_by_track[beta])

    def test_spoil_same_hunk(self):
        plot = reel.build_plot(reel.parse_diff(reel.SPOIL_DIFF), grain="hunk")
        self.assertGreaterEqual(plot.spoil, 1)

    def test_touched_class_payoff(self):
        plot = reel.build_plot(reel.parse_diff(reel.TOUCHED_CLASS), grain="hunk")
        self.assertIn("PAYOFF", [a.kind for a in plot.acts])
        prod = next(a for a in plot.acts if a.files == ["Sources/Arbiter.swift"])
        tests = next(a for a in plot.acts if a.files == ["Tests/ArbiterTests.swift"])
        self.assertLess(prod.index, tests.index)
        self.assertEqual(tests.kind, "PAYOFF")
        self.assertTrue({"presentThreshold", "absentThreshold"} & (prod.natal | prod.defs))

    def test_check_exit(self):
        import io
        buf = io.StringIO(reel.SPOIL_DIFF)
        old_in, old_out = sys.stdin, sys.stdout
        sys.stdin = buf
        sys.stdout = io.StringIO()
        try:
            rc = reel.main(["--stdin", "--check"])
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        self.assertEqual(rc, 1)

    def test_stdin_default_refuses_mailbox(self):
        import io
        buf = io.StringIO(reel.MIXED_PY)
        old_in, old_out, old_err = sys.stdin, sys.stdout, sys.stderr
        sys.stdin = buf
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            rc = reel.main(["--stdin"])
        finally:
            sys.stdin, sys.stdout, sys.stderr = old_in, old_out, old_err
        self.assertEqual(rc, 2)

    def test_json_shape(self):
        plot = reel.build_plot(reel.parse_diff(reel.MIXED_PY), grain="file")
        js = plot.to_json()
        json.dumps(js)
        self.assertIn("acts", js)
        self.assertTrue(js["acts"])

    def test_report_header(self):
        plot = reel.build_plot(reel.parse_diff(reel.MIXED_PY), grain="file")
        text = reel.format_porcelain(plot)
        self.assertTrue(text.startswith("reel "))
        self.assertIn("TRACK", text)
        self.assertIn("PAYOFF", text)


class Mailbox(unittest.TestCase):
    def test_format_mbox_git_am_headers(self):
        msg = reel.format_mbox_message(
            n=1,
            total=3,
            kind="PRELUDE",
            files=["Sources/SitboneCore/PresenceArbiter.swift"],
            body="reel act #1 PRELUDE track=1\n",
            diff="diff --git a/x b/x\nnew file mode 100644\n",
            author="Annenpolka",
            email="x@y.z",
            date="Fri, 10 Apr 2026 11:28:37 +0900",
        )
        self.assertTrue(msg.startswith("From "))
        self.assertIn("From: Annenpolka <x@y.z>", msg)
        self.assertIn("Subject: [PATCH 1/3] PRELUDE: PresenceArbiter.swift", msg)
        self.assertIn("\n---\n", msg)
        self.assertIn("diff --git", msg)
        self.assertIn("-- \nreel ", msg)

    def test_aside_last_order(self):
        plot = reel.build_plot(reel.parse_diff(reel.MIXED_PY), grain="file")
        inline = [a.kind for a in reel.series_acts(plot, aside="inline")]
        last = [a.kind for a in reel.series_acts(plot, aside="last")]
        default = [a.kind for a in reel.series_acts(plot)]
        self.assertEqual(sorted(inline), sorted(last))
        self.assertEqual(last[-1], "ASIDE")
        self.assertEqual(default, last)
        self.assertIn("PAYOFF", last)
        self.assertLess(last.index("PAYOFF"), last.index("ASIDE"))

    def test_patch_filename(self):
        self.assertEqual(
            reel.patch_filename(3, "PAYOFF", ["tests/test_parse.py"]),
            "0003-PAYOFF-test_parse.py.patch",
        )

    def test_file_first_act_disjoint(self):
        plot = reel.build_plot(reel.parse_diff(reel.MIXED_PY), grain="file")
        first = reel.files_first_act(plot)
        self.assertEqual(len(first), len(set(first)))
        self.assertIn("pkg/lexer.py", first)
        self.assertIn("tests/test_parse.py", first)
        self.assertLess(first["pkg/lexer.py"], first["tests/test_parse.py"])


if __name__ == "__main__":
    unittest.main()
