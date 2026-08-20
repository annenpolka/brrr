#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import veil  # noqa: E402


class PathRoles(unittest.TestCase):
    def test_test_paths(self):
        self.assertTrue(veil.is_test_path("tests/test_add.py"))
        self.assertTrue(veil.is_test_path("tests/test add.py"))
        self.assertTrue(veil.is_test_path("src/composer.test.ts"))
        self.assertTrue(veil.is_test_path("packages/kernel/src/evaluate.test.ts"))
        self.assertTrue(veil.is_test_path("conftest.py"))
        self.assertTrue(veil.is_test_path("Engine/Tests/TenaoshiEngineTests/OraclesGenerated.swift"))
        self.assertTrue(veil.is_test_path("Sources/SitboneUITests/NotchOverlayTests.swift"))
        self.assertFalse(veil.is_test_path("src/loader.ts"))
        self.assertFalse(veil.is_test_path("shop.py"))
        self.assertFalse(veil.is_production_path("Engine/Tests/TenaoshiEngineTests/OraclesGenerated.swift"))

    def test_production_skips_markdown_and_tests(self):
        self.assertTrue(veil.is_production_path("shop.py"))
        self.assertTrue(veil.is_production_path("src/loader.ts"))
        self.assertFalse(veil.is_production_path("README.md"))
        self.assertFalse(veil.is_production_path("tests/test_add.py"))
        self.assertFalse(veil.is_production_path("src/composer.test.ts"))
        self.assertFalse(veil.is_production_path("node_modules/foo.py"))


class PyDefs(unittest.TestCase):
    def test_body_change_and_new_fn(self):
        old = "def add(a, b):\n    return 0\n\ndef checkout(c):\n    return 0\n"
        new = "def add(a, b):\n    return a + b\n\ndef checkout(c):\n    return 0\n\ndef charge(c):\n    return 1\n"
        ch = veil.changed_names_in_file("shop.py", old, new)
        names = {c.qualname for c in ch}
        self.assertIn("add", names)
        self.assertIn("charge", names)
        self.assertNotIn("checkout", names)

    def test_skips_private_and_test_fns(self):
        src = "def _hidden():\n    return 1\n\ndef test_foo():\n    return 1\n\ndef visible():\n    return 1\n"
        defs = veil.py_defs(src)
        self.assertIn("visible", defs)
        self.assertNotIn("test_foo", defs)
        ch = veil.changed_names_in_file("m.py", None, src)
        self.assertEqual([c.qualname for c in ch], ["visible"])


class PatchSpecs(unittest.TestCase):
    def test_decorator_and_object(self):
        src = (
            "from unittest.mock import patch\n"
            "@patch('shop.checkout')\n"
            "def test_ok(m):\n"
            "    pass\n\n"
            "def test_obj():\n"
            "    with patch.object(Shop, 'charge'):\n"
            "        pass\n"
        )
        facts = veil.py_test_facts(src, "tests/test_checkout.py")
        specs = [s for s, _ in facts.mocks]
        self.assertIn("shop.checkout", specs)
        self.assertIn("Shop.charge", specs)


class UglyRepo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="veil-test-"))
        self.repo = veil.build_ugly_fixture(self.tmp)
        self.parent = veil.git_text(self.repo, "rev-parse", "HEAD~1").strip()

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, onerror=veil._chmod_and_retry)

    def test_python_cover_types(self):
        rep = veil.analyze(self.repo, self.parent, "HEAD")
        by = {n.name.qualname: n for n in rep.names}
        self.assertEqual(by["add"].status, veil.LIVE)
        self.assertEqual(by["checkout"].status, veil.VEIL)
        self.assertEqual(by["retry_budget"].status, veil.BARE)
        self.assertEqual(by["charge"].status, veil.BARE)

    def test_js_module_mock_is_veil(self):
        rep = veil.analyze(self.repo, self.parent, "HEAD")
        by = {n.name.qualname: n for n in rep.names}
        self.assertEqual(by["loadTemplate"].status, veil.VEIL)
        self.assertEqual(by["parseFrontmatter"].status, veil.VEIL)
        self.assertEqual(by["compose"].status, veil.LIVE)

    def test_rollup_open_and_clean(self):
        rep = veil.analyze(self.repo, self.parent, "HEAD")
        self.assertEqual(rep.status, veil.OPEN)
        clean = veil.analyze(self.repo, "HEAD", None)
        self.assertEqual(clean.status, veil.CLEAN)

    def test_cli_json_and_check(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "veil.py"),
                "-C",
                str(self.repo),
                "--from",
                self.parent,
                "--to",
                "HEAD",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "OPEN")
        statuses = {n["qualname"]: n["status"] for n in data["names"]}
        self.assertEqual(statuses["checkout"], "VEIL")
        chk = subprocess.run(
            [
                sys.executable,
                str(ROOT / "veil.py"),
                "-C",
                str(self.repo),
                "--from",
                self.parent,
                "--to",
                "HEAD",
                "--check",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(chk.returncode, 1)

    def test_spaces_and_unicode_are_test_paths(self):
        self.assertTrue(veil.is_test_path("tests/test add.py"))
        listed = veil.list_test_files(self.repo, "HEAD")
        self.assertTrue(any(p.endswith("test add.py") for p in listed))

    def test_porcelain_dedupes_patch_decorator(self):
        parent = self.parent
        porc = veil.fmt_porcelain(veil.analyze(self.repo, parent, "HEAD"))
        rows = [ln for ln in porc.splitlines() if ln.startswith("VEIL\tcheckout\t")]
        self.assertEqual(len(rows), 1, porc)


class BraceSpans(unittest.TestCase):
    def test_only_the_edited_fn_is_changed(self):
        old = (
            "export function keep(x: number): number {\n  return x + 1\n}\n"
            "export function touch(x: number): number {\n  return x\n}\n"
            "function hidden(x: number): number {\n  return x * 2\n}\n"
        )
        new = (
            "export function keep(x: number): number {\n  return x + 1\n}\n"
            "export function touch(x: number): number {\n  return x + 99\n}\n"
            "function hidden(x: number): number {\n  return x * 3\n}\n"
        )
        ch = veil.changed_names_in_file("src/mod.ts", old, new)
        names = {c.qualname: c for c in ch}
        self.assertIn("touch", names)
        self.assertNotIn("keep", names)
        self.assertIn("hidden", names)
        self.assertFalse(names["hidden"].public)
        self.assertTrue(names["touch"].public)

    def test_private_bare_dropped_private_veil_kept(self):
        pub = veil.ChangedName("keep", "keep", "a.ts", "fn", "h", public=True)
        hid = veil.ChangedName("hid", "hid", "a.ts", "fn", "h", public=False)
        reports = [
            veil.NameReport(pub, veil.BARE),
            veil.NameReport(hid, veil.BARE),
            veil.NameReport(
                veil.ChangedName("fmt", "fmt", "a.ts", "fn", "h", public=False),
                veil.VEIL,
            ),
        ]
        kept = veil.drop_private_bare(reports)
        statuses = {(n.name.qualname, n.status) for n in kept}
        self.assertIn(("keep", "BARE"), statuses)
        self.assertNotIn(("hid", "BARE"), statuses)
        self.assertIn(("fmt", "VEIL"), statuses)


if __name__ == "__main__":
    unittest.main()
