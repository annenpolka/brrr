#!/usr/bin/env python3
"""Two-pass ImpliedType then unmarshal over schema+state objects."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "identjson"
FIX = ROOT / "fixtures"


def load_cli():
    loader = importlib.machinery.SourceFileLoader("identjson2_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


MOD = load_cli()


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class ImpliedTypeThenUnmarshalTests(unittest.TestCase):
    def test_nil_object_implied_type_is_empty_object(self):
        ty = MOD.implied_type(None)
        self.assertTrue(ty.is_empty())
        self.assertEqual(ty.names(), frozenset())

    def test_present_object_implied_type_keeps_attribute_names(self):
        ident = MOD.Object((("id", "string"),))
        ty = MOD.implied_type(ident)
        self.assertFalse(ty.is_empty())
        self.assertEqual(ty.names(), frozenset({"id"}))

    def test_unmarshal_extra_key_against_empty_object(self):
        with self.assertRaises(MOD.UnsupportedAttribute) as ctx:
            MOD.unmarshal(b'{"id":"foo"}', MOD.implied_type(None))
        self.assertEqual(ctx.exception.name, "id")

    def test_unmarshal_matching_id_succeeds(self):
        ty = MOD.implied_type(MOD.Object((("id", "string"),)))
        self.assertEqual(MOD.unmarshal(b'{"id":"foo"}', ty), {"id": "foo"})

    def test_decode_leftover_json_against_nil_schema_is_unsupported(self):
        src = MOD.InstanceObjectSrc(identity_json=b'{"id":"foo"}')
        schema = MOD.Schema(identity=None)
        report = MOD.decode(src, schema)
        self.assertEqual(report.schema, "nil")
        self.assertEqual(report.json, "present")
        self.assertEqual(report.decode, "error")
        self.assertEqual(report.error_class, "unsupported-attribute")

    def test_decode_present_schema_is_object(self):
        src = MOD.InstanceObjectSrc(identity_json=b'{"id":"foo"}')
        schema = MOD.Schema(identity=MOD.Object((("id", "string"),)))
        report = MOD.decode(src, schema)
        self.assertEqual(report.decode, "object")
        self.assertEqual(report.error_class, "-")

    def test_decode_omitted_json_nil_schema(self):
        report = MOD.decode(MOD.InstanceObjectSrc(), MOD.Schema())
        self.assertEqual(report.decode, "omitted")
        self.assertEqual(report.json, "omitted")

    def test_decode_omitted_json_present_schema_is_typed_null(self):
        schema = MOD.Schema(identity=MOD.Object((("id", "string"),)))
        report = MOD.decode(MOD.InstanceObjectSrc(), schema)
        self.assertEqual(report.schema, "present")
        self.assertEqual(report.decode, "typed-null")

    def test_decode_empty_object_json_against_nil_schema(self):
        src = MOD.InstanceObjectSrc(identity_json=b"{}")
        report = MOD.decode(src, MOD.Schema())
        self.assertEqual(report.json, "empty-object")
        self.assertEqual(report.decode, "empty-object")

    def test_tsv_compiles_to_schema_state_objects(self):
        doc = MOD.compile_tsv(
            "schema\tnil\nidentity_json\t{\"id\": \"foo\"}\n",
            source="mem",
        )
        self.assertIsNone(doc["schema"]["identity"])
        self.assertEqual(doc["state"]["identity_json"], '{"id": "foo"}')


class FixtureCliTests(unittest.TestCase):
    def test_nil_schema_leftover_json_errors(self):
        proc = run_cli(str(FIX / "081-nil-leftover.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["schema"], ["nil"])
        self.assertEqual(rows["decode"], ["error"])
        self.assertEqual(rows["error_class"], ["unsupported-attribute"])

    def test_present_schema_decodes_object(self):
        proc = run_cli(str(FIX / "081-schema-present.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["decode"], ["object"])
        self.assertEqual(rows["error_class"], ["-"])

    def test_nil_json_omitted(self):
        proc = run_cli(str(FIX / "081-nil-json.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["decode"], ["omitted"])

    def test_mismatch_arn_vs_id(self):
        proc = run_cli(str(FIX / "081-mismatch.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["decode"], ["error"])
        self.assertEqual(rows["error_class"], ["unsupported-attribute"])

    def test_json_documents_match_tsv_delta(self):
        pairs = [
            "081-nil-leftover",
            "081-schema-present",
            "081-nil-json",
            "081-mismatch",
        ]
        for stem in pairs:
            tsv = run_cli(str(FIX / f"{stem}.rec"))
            js = run_cli(str(FIX / f"{stem}.json"))
            self.assertEqual(tsv.returncode, js.returncode, stem)
            self.assertEqual(tsv.stdout, js.stdout, stem)

    def test_typed_null_when_schema_present_and_json_omitted(self):
        proc = run_cli(str(FIX / "081-typed-null.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["schema"], ["present"])
        self.assertEqual(rows["json"], ["omitted"])
        self.assertEqual(rows["decode"], ["typed-null"])

    def test_json_stdin_leftover_errors(self):
        payload = (FIX / "081-nil-leftover.json").read_text()
        proc = run_cli("-", stdin=payload)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("decode\terror", proc.stdout)
        self.assertIn("error_class\tunsupported-attribute", proc.stdout)

    def test_missing_file(self):
        proc = run_cli("/no/such/identjson.rec")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("identjson:", proc.stderr)


if __name__ == "__main__":
    unittest.main()
