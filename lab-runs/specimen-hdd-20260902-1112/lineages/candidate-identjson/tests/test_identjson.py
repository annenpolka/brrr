#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "identjson"
FIX = ROOT / "fixtures"


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run_record(name: str) -> tuple[int, dict[str, list[str]], str]:
    proc = subprocess.run(
        [sys.executable, str(CLI), str(FIX / name)],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, parse_rows(proc.stdout), proc.stderr


class IdentJsonTests(unittest.TestCase):
    def test_nil_schema_leftover_json_errors(self):
        rc, rows, err = run_record("081-nil-leftover.rec")
        self.assertEqual(rc, 1, err)
        self.assertEqual(rows["schema"], ["nil"])
        self.assertEqual(rows["json"], ["present"])
        self.assertEqual(rows["decode"], ["error"])
        self.assertEqual(rows["error_class"], ["unsupported-attribute"])

    def test_present_schema_decodes_object(self):
        rc, rows, err = run_record("081-schema-present.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["decode"], ["object"])
        self.assertEqual(rows["error_class"], ["-"])

    def test_nil_json_omitted(self):
        rc, rows, err = run_record("081-nil-json.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["json"], ["omitted"])
        self.assertEqual(rows["decode"], ["omitted"])

    def test_mismatch_arn_vs_id(self):
        rc, rows, err = run_record("081-mismatch.rec")
        self.assertEqual(rc, 1, err)
        self.assertEqual(rows["decode"], ["error"])
        self.assertEqual(rows["error_class"], ["unsupported-attribute"])

    def test_json_null_nil_schema_is_typed_null(self):
        rc, rows, err = run_record("081-typed-null.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["schema"], ["nil"])
        self.assertEqual(rows["json"], ["null"])
        self.assertEqual(rows["decode"], ["typed-null"])
        self.assertEqual(rows["error_class"], ["-"])

    def test_json_null_present_schema_is_typed_null(self):
        rc, rows, err = run_record("081-typed-null-present.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["schema"], ["present"])
        self.assertEqual(rows["json"], ["null"])
        self.assertEqual(rows["decode"], ["typed-null"])

    def test_present_schema_omitted_json_is_omitted_not_typed_null(self):
        rc, rows, err = run_record("081-present-omitted.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["schema"], ["present"])
        self.assertEqual(rows["json"], ["omitted"])
        self.assertEqual(rows["decode"], ["omitted"])
        self.assertNotEqual(rows["decode"], ["typed-null"])

    def test_empty_json_object_vs_nil_schema(self):
        rc, rows, err = run_record("081-empty-object.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["schema"], ["nil"])
        self.assertEqual(rows["json"], ["empty-object"])
        self.assertEqual(rows["decode"], ["empty-object"])
        self.assertEqual(rows["error_class"], ["-"])

    def test_schema_list_with_spaces(self):
        rc, rows, err = run_record("081-schema-spaces.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["schema"], ["present"])
        self.assertEqual(rows["json"], ["present"])
        self.assertEqual(rows["decode"], ["object"])
        self.assertEqual(rows["error_class"], ["-"])

    def test_schema_list_with_comma_spaces(self):
        rc, rows, err = run_record("081-schema-comma-spaces.rec")
        self.assertEqual(rc, 0, err)
        self.assertEqual(rows["decode"], ["object"])


if __name__ == "__main__":
    unittest.main()
