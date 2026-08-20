#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from graftcore.index import query_file


class PythonLocusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = ROOT / "fixtures" / "nested.py"

    def test_denied_is_under_admin_and_not_can_delete(self) -> None:
        loc = query_file(self.path, 13)
        joined = loc.cond_path
        self.assertIn("user.locked", joined)
        self.assertIn("user.role == 'admin'", joined)
        self.assertIn("not user.can_delete", joined)
        self.assertNotIn("except", joined)

    def test_fallthrough_after_none_guard(self) -> None:
        loc = query_file(self.path, 8)
        kinds = [f.kind for f in loc.frames]
        self.assertIn("given", kinds)
        self.assertTrue(any("is not None" in f.pred or "¬" in f.pred for f in loc.frames))


class BraceLocusTests(unittest.TestCase):
    def test_rust_early_return_given_and_string(self) -> None:
        loc = query_file(ROOT / "fixtures" / "guards.rs", 11)
        self.assertIn("given", loc.cond_path)
        self.assertIn("a/", loc.cond_path)
        self.assertIn("7", loc.cond_path)

    def test_quoted_path_nested_total_becomes_given(self) -> None:
        loc = query_file(ROOT / "fixtures" / "quoted.rs", 32)
        givens = [f.pred for f in loc.frames if f.kind == "given"]
        joined = " ".join(givens)
        # the miss in when/whence: nested-but-total quoted-form if
        self.assertTrue(
            any('\\"a/' in g or '"a/' in g for g in givens),
            f"expected given ¬(quoted form), got {givens!r}",
        )
        self.assertIn("a/", joined)
        self.assertIn("b/", joined)

    def test_swift_after_guard(self) -> None:
        loc = query_file(ROOT / "fixtures" / "sample.swift", 6)
        self.assertTrue(any(f.kind == "guard" for f in loc.frames), loc.cond_path)

    def test_if_let_keeps_let(self) -> None:
        loc = query_file(ROOT / "fixtures" / "sample.rs", 16)
        self.assertTrue(
            any("let" in f.pred for f in loc.frames if f.kind == "if"),
            loc.cond_path,
        )

    def test_swift_init_is_a_function(self) -> None:
        src = """\
public final class PresenceArbiter {
    public init(sensors: [any SensorProtocol], presentThreshold: Double = 0.45) {
        precondition(presentThreshold > 0)
        self.presentThreshold = presentThreshold
    }
}
"""
        from graftcore.index import query_source

        loc = query_source(src, "Arbiter.swift", 3)
        self.assertIsNotNone(loc.function)
        self.assertIn("init", loc.function or "")
        self.assertIn("precondition", loc.here)


if __name__ == "__main__":
    unittest.main()
