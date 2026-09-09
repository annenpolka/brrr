"""Drive the shipped runpair CLI and functions. No reimplementation of the delta logic."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runpair import file_delta, runpair, snapshot_files  # noqa: E402

RUN_BUNDLE = Path(__file__).resolve().parents[3] / "inputs" / "case-001" / "discovery" / "input-001" / "files"


class SnapshotTests(unittest.TestCase):
    def test_snapshot_lists_regular_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "a.txt").write_text("hi")
            (cwd / "sub").mkdir()
            (cwd / "sub" / "nested.txt").write_text("no")
            snap = snapshot_files(cwd)
            self.assertEqual(snap, {"a.txt": 2})


class DeltaTests(unittest.TestCase):
    def test_added_removed_changed(self):
        delta = file_delta({"keep": 1, "gone": 2, "edit": 3}, {"keep": 1, "new": 4, "edit": 9})
        self.assertEqual(delta["added"], [{"name": "new", "size": 4}])
        self.assertEqual(delta["removed"], [{"name": "gone", "size": 2}])
        self.assertEqual(delta["changed"], [{"name": "edit", "before": 3, "after": 9}])


class RunpairFunctionTests(unittest.TestCase):
    def test_true_creates_no_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "seed.txt").write_text("x")
            result = runpair(["true"], cwd)
            self.assertEqual(result["first"]["rc"], 0)
            self.assertEqual(result["second"]["rc"], 0)
            self.assertEqual(result["first"]["delta"]["added"], [])
            self.assertEqual(result["second"]["delta"]["added"], [])

    def test_first_failure_still_runs_second(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            result = runpair(["false"], cwd)
            self.assertEqual(result["first"]["rc"], 1)
            self.assertEqual(result["second"]["rc"], 1)
            self.assertEqual(result["first"]["delta"]["added"], [])

    def test_writer_then_same_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            script = cwd / "write.py"
            script.write_text("from pathlib import Path\nPath('out.bin').write_bytes(b'abc')\n")
            result = runpair([sys.executable, str(script.name)], cwd)
            self.assertEqual(result["first"]["rc"], 0)
            self.assertEqual(result["first"]["delta"]["added"], [{"name": "out.bin", "size": 3}])
            # second run overwrites same size -> no added/changed
            self.assertEqual(result["second"]["rc"], 0)
            self.assertEqual(result["second"]["delta"]["added"], [])


class RunpairCliTests(unittest.TestCase):
    def test_cli_json_on_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, "-m", "runpair", "--cwd", tmp, "--", "true"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["command"], ["true"])
            self.assertEqual(payload["first"]["rc"], 0)
            self.assertEqual(payload["second"]["rc"], 0)


class DenoReportedInputTests(unittest.TestCase):
    def test_two_deno_run_on_public_bundle_copy(self):
        if shutil.which("deno") is None:
            self.skipTest("deno not installed")
        self.assertTrue(RUN_BUNDLE.is_dir(), RUN_BUNDLE)
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            shutil.copy(RUN_BUNDLE / "a.js", cwd / "a.js")
            shutil.copy(RUN_BUNDLE / "package.json", cwd / "package.json")
            result = runpair(["deno", "run", "a.js"], cwd)
            self.assertEqual(result["first"]["rc"], 0, result["first"])
            self.assertEqual(result["first"]["stdout"], "foo\n")
            added_names = [row["name"] for row in result["first"]["delta"]["added"]]
            self.assertIn("deno.lock", added_names)
            self.assertEqual(result["second"]["rc"], 1, result["second"])
            self.assertIn("Invalid package requirement '@.'", result["second"]["stderr"])
            # Tool does not interpret lockfile contents; it only reports the name/size.
            lock = next(row for row in result["first"]["delta"]["added"] if row["name"] == "deno.lock")
            self.assertGreater(lock["size"], 0)


if __name__ == "__main__":
    unittest.main()
