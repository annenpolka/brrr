#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from graftcore.overlay import apply_file, overlay_diff, parse_unified_diff, unquote_git_path


class PathTests(unittest.TestCase):
    def test_strips_ab(self) -> None:
        self.assertEqual(unquote_git_path("a/foo.rs"), "foo.rs")
        self.assertEqual(unquote_git_path("b/foo.rs"), "foo.rs")

    def test_quoted_space(self) -> None:
        self.assertEqual(unquote_git_path('"a/foo bar.rs"'), "foo bar.rs")

    def test_quoted_tab_escape(self) -> None:
        self.assertEqual(unquote_git_path('"a/foo\\tbar.rs"'), "foo\tbar.rs")


class ApplyTests(unittest.TestCase):
    def test_insert_middle(self) -> None:
        pre = "a\nb\nc\n"
        diff = """\
--- a/t.txt
+++ b/t.txt
@@ -1,3 +1,4 @@
 a
 b
+x
 c
"""
        patch = parse_unified_diff(diff)[0]
        post, added, err = apply_file(pre, patch)
        self.assertIsNone(err)
        self.assertEqual(post, "a\nb\nx\nc\n")
        self.assertEqual([a.text for a in added], ["x"])
        self.assertEqual(added[0].line, 3)

    def test_new_file(self) -> None:
        diff = (ROOT / "fixtures" / "newfile.diff").read_text()
        images = overlay_diff(diff, root=ROOT, base=":wt")
        self.assertEqual(len(images), 1)
        self.assertIsNone(images[0].error)
        self.assertIn("only_after_apply", images[0].post or "")
        self.assertTrue(any("x > 10" in a.text for a in images[0].added))

    def test_mismatch(self) -> None:
        diff = (ROOT / "fixtures" / "mismatch.diff").read_text()
        images = overlay_diff(diff, root=ROOT, base=":wt")
        self.assertTrue(images[0].error)


class QuotedPathDiffTests(unittest.TestCase):
    def test_git_quoted_paths_parse(self) -> None:
        text = '''diff --git "a/foo bar.rs" "b/foo bar.rs"
--- "a/foo bar.rs"
+++ "b/foo bar.rs"
@@ -1,2 +1,3 @@
 fn f() {
+    let x = 1;
 }
'''
        patches = parse_unified_diff(text)
        self.assertEqual(patches[0].new_path, "foo bar.rs")


if __name__ == "__main__":
    unittest.main()
