#!/usr/bin/env python3
"""Tests that import and subprocess the shipped ./whence CLI (not a reimplementation)."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "whence"
FIXTURES = ROOT / "fixtures"


def load_whence():
    loader = importlib.machinery.SourceFileLoader("whence_cli", str(CLI))
    spec = importlib.util.spec_from_loader("whence_cli", loader)
    if spec is None:
        raise RuntimeError(f"cannot import shipped CLI at {CLI}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["whence_cli"] = mod
    loader.exec_module(mod)
    return mod


WHENCE = load_whence()


def run_cli(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(ROOT),
        input=stdin,
        text=True,
        capture_output=True,
    )


class WhenceCLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="whence-test-")
        self.addCleanup(shutil.rmtree, self.tmp)

    def copy(self, name: str) -> Path:
        dest = Path(self.tmp) / name
        shutil.copy(FIXTURES / name, dest)
        return dest

    def test_report_lists_region(self) -> None:
        proc = run_cli("report", str(FIXTURES / "simple.conflict"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("conflicts: 1", proc.stdout)
        self.assertIn("HEAD vs feature", proc.stdout)
        self.assertIn("color = red", proc.stdout)
        self.assertIn("color = blue", proc.stdout)

    def test_ours_keeps_ours_and_writes_prov(self) -> None:
        path = self.copy("simple.conflict")
        proc = run_cli("resolve", str(path), "--ours")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text, "# palette\ncolor = red\nsize = 1\n# end\n")
        self.assertNotIn("<<<<<<<", text)
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["region_count"], 1)
        self.assertEqual(doc["regions"][0]["mode"], "ours")
        self.assertEqual(doc["regions"][0]["spans"][0]["parent"], "ours")
        self.assertNotIn("hybrid", doc)
        self.assertTrue((path.with_name(path.name + ".prov")).exists() or Path(str(path) + ".prov").exists())
        prov_path = Path(str(path) + ".prov")
        self.assertTrue(prov_path.is_file())
        self.assertEqual(json.loads(prov_path.read_text(encoding="utf-8")), doc)

    def test_theirs_keeps_theirs(self) -> None:
        path = self.copy("simple.conflict")
        proc = run_cli("resolve", str(path), "--theirs")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# palette\ncolor = blue\nsize = 2\n# end\n",
        )
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["regions"][0]["mode"], "theirs")
        self.assertEqual(doc["regions"][0]["spans"][0]["parent"], "theirs")

    def test_hybrid_tagged_success(self) -> None:
        path = self.copy("simple.conflict")
        sidecar = str(FIXTURES / "hybrid-tagged.txt")
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            sidecar,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# palette\ncolor = red\nsize = 2\n# end\n",
        )
        doc = json.loads(proc.stdout)
        parents = [s["parent"] for s in doc["regions"][0]["spans"]]
        self.assertEqual(parents, ["ours", "theirs"])
        self.assertEqual(doc["regions"][0]["spans"][0]["text"], "color = red")
        self.assertEqual(doc["regions"][0]["spans"][1]["text"], "2")
        self.assertEqual(doc["hybrid"], {"source": "file", "path": sidecar})

    def test_hybrid_stdin_matches_file_sidecar(self) -> None:
        tagged = (FIXTURES / "hybrid-tagged.txt").read_text(encoding="utf-8")
        path_file = self.copy("simple.conflict")
        path_stdin = Path(self.tmp) / "simple-stdin.conflict"
        shutil.copy(FIXTURES / "simple.conflict", path_stdin)
        sidecar = str(FIXTURES / "hybrid-tagged.txt")
        file_proc = run_cli("resolve", str(path_file), "--hybrid", sidecar)
        stdin_proc = run_cli(
            "resolve",
            str(path_stdin),
            "--hybrid",
            "-",
            stdin=tagged,
        )
        self.assertEqual(file_proc.returncode, 0, file_proc.stderr)
        self.assertEqual(stdin_proc.returncode, 0, stdin_proc.stderr + stdin_proc.stdout)
        self.assertEqual(
            path_file.read_text(encoding="utf-8"),
            path_stdin.read_text(encoding="utf-8"),
        )
        file_doc = json.loads(file_proc.stdout)
        stdin_doc = json.loads(stdin_proc.stdout)
        self.assertEqual(file_doc["regions"][0]["spans"], stdin_doc["regions"][0]["spans"])
        self.assertEqual(file_doc["hybrid"], {"source": "file", "path": sidecar})
        self.assertEqual(stdin_doc["hybrid"], {"source": "stdin"})
        self.assertTrue(Path(str(path_stdin) + ".prov").is_file())

    def test_hybrid_stdin_messy_matches_file(self) -> None:
        tagged = (FIXTURES / "messy-hybrid.txt").read_text(encoding="utf-8")
        path = self.copy("messy.conflict")
        proc = run_cli("resolve", str(path), "--hybrid", "-", stdin=tagged)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(
            path.read_bytes(),
            b'title = "app"\n'
            b'name = "Alice \\"lead\\""\n'
            b'role = "editor"\n'
            b"timeout = 90\n"
            b"debug = true\n"
            b"# eof",
        )
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["hybrid"], {"source": "stdin"})
        self.assertEqual(doc["region_count"], 3)

    def test_hybrid_empty_stdin_refused(self) -> None:
        path = self.copy("simple.conflict")
        original = path.read_text(encoding="utf-8")
        for payload in ("", "\n", "  \n\n"):
            with self.subTest(payload=payload):
                proc = run_cli("resolve", str(path), "--hybrid", "-", stdin=payload)
                self.assertEqual(proc.returncode, 3, proc.stderr)
                self.assertIn("empty stdin", proc.stderr)
                self.assertIn("<<<<<<< HEAD", path.read_text(encoding="utf-8"))
                self.assertEqual(path.read_text(encoding="utf-8"), original)
                self.assertFalse(Path(str(path) + ".prov").exists())

    def test_hybrid_and_file_both_stdin_refused(self) -> None:
        dash = Path(self.tmp) / "cwd" / "-"
        dash.parent.mkdir()
        proc = subprocess.run(
            [sys.executable, str(CLI), "resolve", "-", "--hybrid", "-"],
            cwd=str(dash.parent),
            input="<<<<<<< HEAD\nx\n=======\ny\n>>>>>>> feature\n",
            text=True,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 3, proc.stdout)
        self.assertIn("both FILE and --hybrid", proc.stderr)
        self.assertFalse(dash.exists())

    def test_hybrid_crlf_stdin_matches_lf_sidecar(self) -> None:
        tagged = (FIXTURES / "hybrid-tagged.txt").read_bytes().replace(b"\n", b"\r\n")
        self.assertIn(b"\r\n", tagged)
        path = self.copy("simple.conflict")
        proc = subprocess.run(
            [sys.executable, str(CLI), "resolve", str(path), "--hybrid", "-"],
            cwd=str(ROOT),
            input=tagged,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode() + proc.stdout.decode())
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# palette\ncolor = red\nsize = 2\n# end\n",
        )
        doc = json.loads(proc.stdout.decode())
        self.assertEqual(doc["hybrid"], {"source": "stdin"})

    def test_hybrid_bom_stdin_matches_file_sidecar(self) -> None:
        tagged = (FIXTURES / "hybrid-tagged.txt").read_bytes()
        path = self.copy("simple.conflict")
        proc = subprocess.run(
            [sys.executable, str(CLI), "resolve", str(path), "--hybrid", "-"],
            cwd=str(ROOT),
            input=b"\xef\xbb\xbf" + tagged,
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr.decode() + proc.stdout.decode())
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# palette\ncolor = red\nsize = 2\n# end\n",
        )
        doc = json.loads(proc.stdout.decode())
        self.assertEqual(doc["hybrid"], {"source": "stdin"})

    def test_hybrid_bom_file_sidecar_still_works(self) -> None:
        sidecar = Path(self.tmp) / "bom-hybrid.txt"
        sidecar.write_bytes(b"\xef\xbb\xbf" + (FIXTURES / "hybrid-tagged.txt").read_bytes())
        path = self.copy("simple.conflict")
        proc = run_cli("resolve", str(path), "--hybrid", str(sidecar))
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# palette\ncolor = red\nsize = 2\n# end\n",
        )
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["hybrid"]["source"], "file")

    def test_hybrid_stdin_without_trailing_newline_is_literal(self) -> None:
        path = self.copy("simple.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            "-",
            stdin="[ours:color = red]\nsize = [theirs:2]",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# palette\ncolor = red\nsize = 2# end\n",
        )

    def test_hybrid_generated_tags_on_stdin(self) -> None:
        path = self.copy("simple.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            "-",
            stdin="[ours:color = red]\nsize = [theirs:2]\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            "# palette\ncolor = red\nsize = 2\n# end\n",
        )

    def test_hybrid_tty_stdin_refused(self) -> None:
        path = self.copy("simple.conflict")
        original = path.read_text(encoding="utf-8")
        master, slave = os.openpty()
        try:
            proc = subprocess.run(
                [sys.executable, str(CLI), "resolve", str(path), "--hybrid", "-"],
                cwd=str(ROOT),
                stdin=slave,
                capture_output=True,
                text=True,
                timeout=5,
            )
        finally:
            os.close(master)
            os.close(slave)
        self.assertEqual(proc.returncode, 3, proc.stderr)
        self.assertIn("terminal", proc.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_untagged_hybrid_mix_refused(self) -> None:
        path = self.copy("simple.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            str(FIXTURES / "untagged-mix.txt"),
        )
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("untagged", proc.stderr.lower())
        self.assertIn("<<<<<<<", path.read_text(encoding="utf-8"))
        self.assertFalse(Path(str(path) + ".prov").exists())

    def test_untagged_ours_copy_refused(self) -> None:
        path = self.copy("simple.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            str(FIXTURES / "untagged-ours.txt"),
        )
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("ours", proc.stderr.lower())
        self.assertIn("<<<<<<< HEAD", path.read_text(encoding="utf-8"))

    def test_wrong_parent_tag_refused(self) -> None:
        path = self.copy("simple.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            "-",
            stdin="[ours:color = blue]\n",
        )
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("not in ours", proc.stderr)
        self.assertIn("theirs", proc.stderr)

    def test_choice_per_region(self) -> None:
        path = self.copy("two.conflict")
        proc = run_cli("resolve", str(path), "--choice", "ours,theirs")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "alpha\none\nbeta\nTWO\ngamma\n")
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["regions"][0]["mode"], "ours")
        self.assertEqual(doc["regions"][1]["mode"], "theirs")

    def test_choice_length_mismatch(self) -> None:
        path = self.copy("two.conflict")
        proc = run_cli("resolve", str(path), "--choice", "ours")
        self.assertEqual(proc.returncode, 3, proc.stdout)
        self.assertIn("2 conflict region", proc.stderr)

    def test_no_markers(self) -> None:
        path = Path(self.tmp) / "clean.txt"
        path.write_text("just text\n", encoding="utf-8")
        proc = run_cli("resolve", str(path), "--ours")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("no conflict markers", proc.stderr)

    def test_malformed_markers(self) -> None:
        proc = run_cli("resolve", str(FIXTURES / "malformed.conflict"), "--ours")
        self.assertEqual(proc.returncode, 2)
        self.assertIn(">>>>>>> before =======", proc.stderr)

    def test_diff3_ancestor_refused(self) -> None:
        proc = run_cli("resolve", str(FIXTURES / "diff3.conflict"), "--ours")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("|||||||", proc.stderr)
        self.assertIn("two parents", proc.stderr)

    def test_usage_without_command(self) -> None:
        proc = run_cli()
        self.assertEqual(proc.returncode, 3)
        self.assertIn("usage:", proc.stdout.lower() + proc.stderr.lower())

    def test_messy_three_region_hybrid_and_missing_newline(self) -> None:
        path = self.copy("messy.conflict")
        self.assertFalse(path.read_bytes().endswith(b"\n"))
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            str(FIXTURES / "messy-hybrid.txt"),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        resolved = path.read_bytes()
        self.assertEqual(
            resolved.decode("utf-8"),
            'title = "app"\n'
            'name = "Alice \\"lead\\""\n'
            'role = "editor"\n'
            "timeout = 90\n"
            "debug = true\n"
            "# eof",
        )
        self.assertFalse(resolved.endswith(b"\n"))
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["region_count"], 3)
        self.assertFalse(doc["input_trailing_newline"])
        self.assertFalse(doc["trailing_newline"])
        self.assertEqual(doc["regions"][0]["mode"], "hybrid")
        self.assertEqual(
            [s["parent"] for s in doc["regions"][0]["spans"]],
            ["ours", "theirs"],
        )
        self.assertIn("Alice", doc["regions"][0]["spans"][0]["text"])
        self.assertEqual(doc["regions"][1]["spans"][0]["parent"], "theirs")
        self.assertEqual(doc["regions"][2]["spans"][0]["parent"], "ours")

    def test_messy_hybrid_block_mismatch_lists_regions(self) -> None:
        path = self.copy("messy.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--hybrid",
            "-",
            stdin='[ours:name = "Alice \\"lead\\""]\nrole = [theirs:"editor"]\n',
        )
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("MISSING tagged block", proc.stderr)
        self.assertIn("region 2/3", proc.stderr)
        self.assertIn("region 3/3", proc.stderr)
        self.assertIn("<<<<<<<", path.read_text(encoding="utf-8"))

    def test_messy_wrong_parent_quoted_name(self) -> None:
        path = self.copy("messy.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--choice",
            "hybrid,theirs,ours",
            "--hybrid",
            "-",
            stdin='[ours:name = "Bob \\"staff\\""]\nrole = "owner"\n',
        )
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("not in ours", proc.stderr)
        self.assertIn("did you mean [theirs:...]", proc.stderr)
        self.assertIn('Bob \\"staff\\"', proc.stderr)
        self.assertNotIn("\\\\\"lead\\\\\"", proc.stderr)

    def test_messy_untagged_mix_shows_parent_bodies(self) -> None:
        path = self.copy("messy.conflict")
        proc = run_cli(
            "resolve",
            str(path),
            "--choice",
            "hybrid,theirs,ours",
            "--hybrid",
            "-",
            stdin='name = "Alice \\"lead\\""\nrole = "editor"\n',
        )
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("unmarked mix", proc.stderr)
        self.assertIn("region 1/3", proc.stderr)
        self.assertIn('role = "owner"', proc.stderr)
        self.assertIn('role = "editor"', proc.stderr)
        # one JSON escaping pass, not snippet-then-repr
        self.assertNotIn("\\\\n", proc.stderr)

    def test_imported_parser_matches_cli(self) -> None:
        text = (FIXTURES / "simple.conflict").read_text(encoding="utf-8")
        parts = WHENCE.parse_conflicts(text, "simple.conflict")
        regs = WHENCE.regions_of(parts)
        self.assertEqual(len(regs), 1)
        self.assertEqual(regs[0].ours_label, "HEAD")
        self.assertEqual(regs[0].theirs_label, "feature")
        self.assertIn("color = red", regs[0].ours)
        proc = run_cli("report", str(FIXTURES / "simple.conflict"))
        self.assertIn("HEAD vs feature", proc.stdout)


if __name__ == "__main__":
    unittest.main()
