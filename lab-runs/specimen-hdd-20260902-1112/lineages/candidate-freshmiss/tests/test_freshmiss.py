#!/usr/bin/env python3
"""FRESH-but-missing is an identity miss, not a successful cache hit."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "freshmiss"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CACHE_BUILD = FIXTURES / "cache_build.py"


def load_mod(path: Path, name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


FM = load_mod(CLI, "freshmiss_cli")
CB = load_mod(CACHE_BUILD, "cache_build_fixture")


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        kind, *rest = line.split("\t")
        rows[kind] = rest
    return rows


def write_record(path: Path, **fields) -> Path:
    lines = []
    for key, value in fields.items():
        if isinstance(value, (list, tuple)):
            lines.append(key + "\t" + "\t".join(value))
        else:
            lines.append(f"{key}\t{value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_cli(first: Path, second: Path, extra_args=None):
    cmd = [sys.executable, str(CLI), str(first), str(second)]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=os.environ.copy(),
    )


class Specimen011Tests(unittest.TestCase):
    def test_fixture_key_and_fresh_missing(self):
        cache = set()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            inputs = {"src": "hello"}
            s1, e1, k1 = CB.build(cache, out, inputs, extra=False)
            s2, e2, k2 = CB.build(cache, out, inputs, extra=True)
            self.assertEqual(s1, "BUILT")
            self.assertFalse(e1)
            self.assertEqual(s2, "FRESH")
            self.assertFalse(e2)
            self.assertEqual(k1, k2)
            self.assertEqual(k1, "9280cc7e16e9")
            self.assertTrue((out / "out.bin").is_file())
            self.assertFalse((out / "out.sbom").exists())

    def test_cli_names_sbom_as_identity_miss(self):
        proc = run_cli(
            FIXTURES / "specimen-011-first.rec",
            FIXTURES / "specimen-011-second.rec",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["FRESH-but-missing"])
        self.assertEqual(rows["identity"], ["9280cc7e16e9"])
        self.assertEqual(rows["same_identity"], ["true"])
        self.assertEqual(rows["first_status"], ["BUILT"])
        self.assertEqual(rows["second_status"], ["FRESH"])
        self.assertEqual(rows["requested_extra"], ["out.sbom"])
        self.assertEqual(rows["missing"], ["out.sbom"])
        self.assertEqual(rows["omitted_from_identity"], ["out.sbom"])

    def test_compare_matches_fixture_records(self):
        first = FM.parse_record(FIXTURES / "specimen-011-first.rec")
        second = FM.parse_record(FIXTURES / "specimen-011-second.rec")
        result = FM.compare(first, second)
        self.assertEqual(result["verdict"], "FRESH-but-missing")
        self.assertEqual(result["omitted_from_identity"], ["out.sbom"])


class ContrastTests(unittest.TestCase):
    def test_fresh_with_extra_present_is_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = write_record(
                Path(tmp) / "first.rec",
                status="BUILT",
                identity="abc",
                requested=["out.bin"],
                present=["out.bin"],
            )
            second = write_record(
                Path(tmp) / "second.rec",
                status="FRESH",
                identity="abc",
                requested=["out.bin", "out.sbom"],
                present=["out.bin", "out.sbom"],
            )
            proc = run_cli(first, second)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["FRESH-complete"])
        self.assertEqual(rows["missing"], ["none"])
        self.assertEqual(rows["stub"], ["none"])
        self.assertEqual(rows["omitted_from_identity"], ["none"])
        self.assertEqual(rows["requested_extra"], ["out.sbom"])

    def test_fresh_extra_present_zero_bytes_is_stub(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = write_record(
                Path(tmp) / "first.rec",
                status="BUILT",
                identity="9280cc7e16e9",
                requested=["out.bin"],
                present=["out.bin", "out.sbom"],
            )
            second = Path(tmp) / "second.rec"
            second.write_text(
                "status\tFRESH\n"
                "identity\t9280cc7e16e9\n"
                "requested\tout.bin\tout.sbom\n"
                "present\tout.bin\tout.sbom\n"
                "bytes\tout.sbom\t0\n",
                encoding="utf-8",
            )
            proc = run_cli(first, second)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["FRESH-but-stub"])
        self.assertEqual(rows["missing"], ["none"])
        self.assertEqual(rows["stub"], ["out.sbom"])
        self.assertEqual(rows["omitted_from_identity"], ["out.sbom"])
        self.assertEqual(rows["requested_extra"], ["out.sbom"])

    def test_rebuilt_missing_extra_is_not_identity_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = write_record(
                Path(tmp) / "first.rec",
                status="BUILT",
                identity="abc",
                requested=["out.bin"],
                present=["out.bin"],
            )
            second = write_record(
                Path(tmp) / "second.rec",
                status="BUILT",
                identity="abc",
                requested=["out.bin", "out.sbom"],
                present=["out.bin"],
            )
            proc = run_cli(first, second)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["rebuilt"])
        self.assertEqual(rows["missing"], ["out.sbom"])
        self.assertEqual(rows["omitted_from_identity"], ["none"])

    def test_different_identity_is_not_fresh_but_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = write_record(
                Path(tmp) / "first.rec",
                status="BUILT",
                identity="aaa",
                requested=["out.bin"],
                present=["out.bin"],
            )
            second = write_record(
                Path(tmp) / "second.rec",
                status="FRESH",
                identity="bbb",
                requested=["out.bin", "out.sbom"],
                present=["out.bin"],
            )
            proc = run_cli(first, second)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["identity-changed"])
        self.assertEqual(rows["same_identity"], ["false"])
        self.assertEqual(rows["omitted_from_identity"], ["none"])
        self.assertEqual(rows["missing"], ["out.sbom"])

    def test_ls_missing_without_fresh_is_not_the_verdict(self):
        first = FM.Build(
            status="BUILT",
            identity="k",
            requested=["out.bin"],
            present=["out.bin"],
            source="first",
        )
        second = FM.Build(
            status="BUILT",
            identity="k",
            requested=["out.bin", "out.sbom"],
            present=["out.bin"],
            source="second",
        )
        result = FM.compare(first, second)
        self.assertEqual(result["verdict"], "rebuilt")
        self.assertNotEqual(result["verdict"], "FRESH-but-missing")


class DirObserveTests(unittest.TestCase):
    def test_live_fixture_dir_names_missing_sbom(self):
        cache = set()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            inputs = {"src": "hello"}
            s1, e1, k1 = CB.build(cache, out, inputs, extra=False)
            s2, e2, k2 = CB.build(cache, out, inputs, extra=True)
            first = write_record(
                Path(tmp) / "first.rec",
                status=s1,
                identity=k1,
                requested=["out.bin"],
                dir=str(out),
            )
            second = write_record(
                Path(tmp) / "second.rec",
                status=s2,
                identity=k2,
                requested=["out.bin", "out.sbom"],
                present=["out.sbom"],
                dir=str(out),
            )
            proc = run_cli(first, second)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertFalse(e1)
        self.assertFalse(e2)
        self.assertEqual(rows["verdict"], ["FRESH-but-missing"])
        self.assertEqual(rows["omitted_from_identity"], ["out.sbom"])
        self.assertEqual(rows["missing"], ["out.sbom"])

    def test_dir_flag_overrides_declared_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            (out / "out.bin").write_text("bin:hello", encoding="utf-8")
            first = write_record(
                Path(tmp) / "first.rec",
                status="BUILT",
                identity="k",
                requested=["out.bin"],
                present=["out.bin"],
            )
            second = write_record(
                Path(tmp) / "second.rec",
                status="FRESH",
                identity="k",
                requested=["out.bin", "out.sbom"],
                present=["out.bin", "out.sbom"],
            )
            proc = run_cli(first, second, extra_args=["--dir", str(out)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["FRESH-but-missing"])
        self.assertEqual(rows["omitted_from_identity"], ["out.sbom"])

    def test_dir_not_a_directory_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = write_record(
                Path(tmp) / "first.rec",
                status="BUILT",
                identity="k",
                requested=["out.bin"],
                present=["out.bin"],
            )
            second = write_record(
                Path(tmp) / "second.rec",
                status="FRESH",
                identity="k",
                requested=["out.sbom"],
            )
            proc = run_cli(first, second, extra_args=["--dir", str(Path(tmp) / "nope")])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not a directory", proc.stderr)


class ParseTests(unittest.TestCase):
    def test_repeated_requested_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rec"
            path.write_text(
                "status\tFRESH\nidentity\tk\nrequested\tout.bin\nrequested\tout.sbom\npresent\tout.bin\n",
                encoding="utf-8",
            )
            rec = FM.parse_record(path)
        self.assertEqual(rec.requested, ["out.bin", "out.sbom"])
        self.assertEqual(rec.missing, ["out.sbom"])

    def test_missing_status_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rec"
            path.write_text("identity\tk\nrequested\tout.bin\n", encoding="utf-8")
            proc = run_cli(path, path)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing status", proc.stderr)

    def test_unknown_field_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rec"
            path.write_text(
                "status\tFRESH\nidentity\tk\nmagic\tyes\n",
                encoding="utf-8",
            )
            proc = run_cli(path, path)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("unknown field", proc.stderr)


if __name__ == "__main__":
    unittest.main()
