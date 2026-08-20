#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from likenpkg.index import query_file, query_source


class PythonLocusTests(unittest.TestCase):
    def test_denied_is_under_admin_and_not_can_delete(self) -> None:
        loc = query_file(ROOT / "fixtures" / "nested.py", 13)
        joined = loc.cond_path
        self.assertIn("user.locked", joined)
        self.assertIn("user.role == 'admin'", joined)
        self.assertIn("not user.can_delete", joined)

    def test_fallthrough_after_none_guard(self) -> None:
        loc = query_file(ROOT / "fixtures" / "nested.py", 8)
        kinds = [f.kind for f in loc.frames]
        self.assertIn("given", kinds)
        self.assertTrue(any("is not None" in f.pred or "¬" in f.pred for f in loc.frames), loc.cond_path)


class BraceLocusTests(unittest.TestCase):
    def test_rust_early_return_given_and_string(self) -> None:
        loc = query_file(ROOT / "fixtures" / "guards.rs", 11)
        self.assertIn("given", loc.cond_path, loc.cond_path)
        self.assertIn("a/", loc.cond_path)
        self.assertIn("7", loc.cond_path)

    def test_quoted_path_nested_total_becomes_given(self) -> None:
        loc = query_file(ROOT / "fixtures" / "quoted.rs", 32)
        givens = [f.pred for f in loc.frames if f.kind == "given"]
        joined = " ".join(givens)
        self.assertTrue(
            any('\\"a/' in g or '"a/' in g for g in givens),
            "expected given ¬(quoted form), got {!r}".format(givens),
        )
        self.assertIn("a/", joined)
        self.assertIn("b/", joined)

    def test_two_survivors_share_a_slash_given(self) -> None:
        a_side = query_file(ROOT / "fixtures" / "quoted.rs", 27)
        b_side = query_file(ROOT / "fixtures" / "quoted.rs", 32)
        self.assertTrue(
            any(f.kind == "given" and "starts_with" in f.pred and "a/" in f.pred for f in a_side.frames),
            a_side.cond_path,
        )
        self.assertTrue(
            any(f.kind == "given" and "starts_with" in f.pred and "a/" in f.pred for f in b_side.frames),
            b_side.cond_path,
        )

    def test_quoted_if_is_not_the_unquoted_given(self) -> None:
        loc = query_file(ROOT / "fixtures" / "quoted.rs", 12)
        givens = [f for f in loc.frames if f.kind == "given"]
        self.assertFalse(
            any("starts_with" in f.pred and 'b"a/"' in f.pred.replace(" ", "") for f in givens),
            loc.cond_path,
        )
        self.assertTrue(any(f.kind == "if" and '"a/' in f.pred for f in loc.frames), loc.cond_path)

    def test_swift_after_guard(self) -> None:
        loc = query_file(ROOT / "fixtures" / "sample.swift", 6)
        self.assertTrue(any(f.kind == "guard" for f in loc.frames), loc.cond_path)

    def test_swift_init_is_a_function(self) -> None:
        src = """\
public final class PresenceArbiter {
    public init(sensors: [any SensorProtocol], presentThreshold: Double = 0.45) {
        precondition(presentThreshold > 0)
        self.presentThreshold = presentThreshold
    }
}
"""
        loc = query_source(src, "Arbiter.swift", 3)
        self.assertIsNotNone(loc.function)
        self.assertIn("init", loc.function or "")
        self.assertIn("precondition", loc.here)


if __name__ == "__main__":
    unittest.main()
