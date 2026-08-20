#!/usr/bin/env python3
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import onset  # noqa: E402


class ClassifyTests(unittest.TestCase):
    def test_comment_only(self) -> None:
        c = onset.classify_text(
            (ROOT / "fixtures/comment_only.py").read_text(),
            "fixtures/comment_only.py",
        )
        self.assertEqual(c.actual_bound, 0)
        self.assertEqual(c.expected_bound, 0)
        self.assertGreaterEqual(c.silent, 1)
        self.assertEqual(c.status, "OPEN")

    def test_env_assert_is_expected_not_actual(self) -> None:
        c = onset.classify_text(
            (ROOT / "fixtures/env_assert.py").read_text(),
            "fixtures/env_assert.py",
        )
        self.assertEqual(c.actual_bound, 0)
        self.assertEqual(c.expected_bound, 1)
        self.assertEqual(c.status, "EXPECTED-BOUND")

    def test_actual_literal_alice(self) -> None:
        c = onset.classify_text(
            (ROOT / "fixtures/actual_literal.swift").read_text(),
            "fixtures/actual_literal.swift",
        )
        self.assertEqual(c.actual_bound, 1)
        self.assertEqual(c.status, "ACTUAL-BOUND")
        self.assertTrue(any(h.kind == "alice" for h in c.hits))

    def test_title_is_fixture(self) -> None:
        c = onset.classify_text(
            (ROOT / "fixtures/title.swift").read_text(),
            "Tests/WindowTitleParserTests.swift",
        )
        self.assertEqual(c.actual_bound, 0)
        self.assertGreaterEqual(c.fixture, 1)
        self.assertEqual(c.status, "FIXTURE")

    def test_payload_is_spec(self) -> None:
        c = onset.classify_text(
            (ROOT / "fixtures/payload.rs").read_text(),
            "src/init/tests.rs",
        )
        self.assertEqual(c.actual_bound, 0)
        self.assertGreaterEqual(c.spec, 1)

    def test_nested_call_is_not_actual_bound(self) -> None:
        c = onset.classify_text(
            (ROOT / "fixtures/nested.rs").read_text(),
            "src/init.rs",
        )
        self.assertEqual(c.actual_bound, 0)

    def test_xctest_fail_dump(self) -> None:
        c = onset.classify_text(
            (ROOT / "fixtures/xctest_fail.txt").read_text(),
            "fixtures/xctest_fail.txt",
        )
        self.assertEqual(c.actual_bound, 1)
        self.assertEqual(c.expected_bound, 0)


if __name__ == "__main__":
    unittest.main()
