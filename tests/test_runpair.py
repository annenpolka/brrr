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
sys.path.insert(0, str(ROOT / "src"))

from runpair import file_delta, runpair, snapshot_files  # noqa: E402

# Public reported 32113 files (not the collector root). Same bytes as the HDD public bundle.
RUN_BUNDLE = ROOT / "tests" / "fixtures" / "runpair-reported-input"


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

    def test_missing_binary_is_rc_127_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            result = runpair(["runpair-definitely-not-installed-xyz"], cwd)
            self.assertEqual(result["first"]["rc"], 127)
            self.assertEqual(result["second"]["rc"], 127)
            self.assertEqual(result["first"]["delta"]["added"], [])

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

    def test_second_run_grows_existing_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "grow.py").write_text(
                "from pathlib import Path\n"
                "p = Path('log.bin')\n"
                "p.write_bytes(p.read_bytes() + b'xx' if p.exists() else b'x')\n"
            )
            result = runpair([sys.executable, "grow.py"], cwd)
            self.assertEqual(result["first"]["delta"]["added"], [{"name": "log.bin", "size": 1}])
            self.assertEqual(result["second"]["delta"]["changed"], [{"name": "log.bin", "before": 1, "after": 3}])

    def test_first_run_removes_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "gone.txt").write_text("bye")
            (cwd / "rm.py").write_text("from pathlib import Path\nPath('gone.txt').unlink(missing_ok=True)\n")
            result = runpair([sys.executable, "rm.py"], cwd)
            self.assertEqual(result["first"]["delta"]["removed"], [{"name": "gone.txt", "size": 3}])
            self.assertEqual(result["second"]["delta"]["removed"], [])

    def test_unicode_and_binary_sidecars(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "w.py").write_text(
                "from pathlib import Path\n"
                "Path('日本語.txt').write_text('あ')\n"
                "Path('nul.bin').write_bytes(b'a\\x00b')\n"
            )
            result = runpair([sys.executable, "w.py"], cwd)
            names = {row["name"]: row["size"] for row in result["first"]["delta"]["added"]}
            self.assertIn("日本語.txt", names)
            self.assertEqual(names["nul.bin"], 3)

    def test_transfer_stamp_not_deno_bundle(self):
        """Tool contract on a different command: first write, second fail. Not issue 32113."""
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            (cwd / "stamp.py").write_text(
                "from pathlib import Path\n"
                "p = Path('stamp.dat')\n"
                "if p.exists():\n"
                "    raise SystemExit(2)\n"
                "p.write_bytes(b'STAMP')\n"
            )
            result = runpair([sys.executable, "stamp.py"], cwd)
            self.assertEqual(result["first"]["rc"], 0)
            self.assertEqual(result["first"]["delta"]["added"], [{"name": "stamp.dat", "size": 5}])
            self.assertEqual(result["second"]["rc"], 2)
            self.assertEqual(result["second"]["delta"]["added"], [])


class RunpairCliTests(unittest.TestCase):
    def test_cli_json_on_true(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "runpair.py"), "--cwd", tmp, "--", "true"],
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
