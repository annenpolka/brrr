#!/usr/bin/env python3
"""Unit + process tests for coast. No third-party deps."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COAST = ROOT / "coast.py"
FIXTURES = ROOT / "fixtures"


def run_coast(
    tmp: Path,
    fixture: str,
    *extra: str,
    max_coast_ms: int = 2500,
    quiet_ms: int = 180,
) -> dict:
    store = tmp / "store"
    watched = tmp / "tree"
    watched.mkdir(parents=True, exist_ok=True)
    json_out = tmp / "report.json"
    cmd = [
        sys.executable,
        str(COAST),
        "run",
        "--root",
        str(watched),
        "--cwd",
        str(ROOT),
        "--store",
        str(store),
        "--json-out",
        str(json_out),
        "--no-passthrough",
        "--interval-ms",
        "12",
        "--quiet-ms",
        str(quiet_ms),
        "--max-coast-ms",
        str(max_coast_ms),
        *extra,
        "--",
        "bash",
        str(FIXTURES / fixture),
        str(watched),
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    if not json_out.is_file():
        raise AssertionError(
            f"no report\nexit={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return json.loads(json_out.read_text())


class CoastTests(unittest.TestCase):
    def test_clean_command_has_zero_coast(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            report = run_coast(tmp, "clean.sh", max_coast_ms=800)
            self.assertEqual(report["exit_code"], 0)
            self.assertTrue(report["settled"])
            self.assertEqual(report["late_writes"], [])
            self.assertEqual(report["stragglers"], [])
            self.assertLess(report["coast_s"], 0.15)
            self.assertIn("out.txt", report["layers"])

    def test_late_write_is_coast(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            report = run_coast(tmp, "late_write.sh", max_coast_ms=2500)
            self.assertEqual(report["exit_code"], 0)
            self.assertTrue(report["settled"])
            late_paths = {e["path"] for e in report["late_writes"]}
            self.assertIn("late.txt", late_paths)
            self.assertGreaterEqual(report["coast_s"], 0.25)
            late = next(e for e in report["late_writes"] if e["path"] == "late.txt")
            self.assertEqual(late["kind"], "artifact")
            self.assertEqual(late["op"], "create")

    def test_straggler_unsettled_then_kill(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            report = run_coast(
                tmp,
                "straggler.sh",
                "--kill-stragglers",
                max_coast_ms=700,
                quiet_ms=120,
            )
            self.assertTrue(report["stragglers"], msg=json.dumps(report["processes"], indent=2))
            commands = " ".join(p["command"] for p in report["stragglers"])
            self.assertIn("sleep", commands)
            # After kill, leftover should be gone.
            self.assertEqual(report["leftover"], [])

    def test_rewrite_records_layers(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            report = run_coast(tmp, "rewrite.sh", max_coast_ms=800)
            self.assertIn("bundle.js", report["rewritten"])
            layers = report["layers"]["bundle.js"]
            self.assertGreaterEqual(len(layers), 2)
            hashes = [layer.get("sha256") for layer in layers if layer.get("sha256")]
            self.assertGreaterEqual(len(set(hashes)), 2)

    def test_wait_returns_124_when_unsettled(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            watched = tmp / "tree"
            watched.mkdir()
            proc = subprocess.run(
                [
                    sys.executable,
                    str(COAST),
                    "wait",
                    "--root",
                    str(watched),
                    "--store",
                    str(tmp / "store"),
                    "--no-passthrough",
                    "--max-coast-ms",
                    "400",
                    "--quiet-ms",
                    "80",
                    "--",
                    "bash",
                    str(FIXTURES / "straggler.sh"),
                    str(watched),
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 124)
            # Clean leaked sleep from the command's process group via leftover pids.
            report = json.loads((tmp / "store" / "last.json").read_text())
            for p in report.get("leftover", []):
                try:
                    os.kill(p["pid"], 9)
                except OSError:
                    pass

    def test_isolate_tmp_sees_private_tmp_late_write(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            watched = tmp / "tree"
            watched.mkdir()
            store = tmp / "store"
            json_out = tmp / "report.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(COAST),
                    "run",
                    "--root",
                    str(watched),
                    "--store",
                    str(store),
                    "--json-out",
                    str(json_out),
                    "--no-passthrough",
                    "--isolate-tmp",
                    "--interval-ms",
                    "12",
                    "--quiet-ms",
                    "180",
                    "--max-coast-ms",
                    "2500",
                    "--",
                    sys.executable,
                    str(FIXTURES / "tmp_late.py"),
                ],
                cwd=str(ROOT),
                text=True,
                capture_output=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = json.loads(json_out.read_text())
            late_paths = {e["path"] for e in report["late_writes"]}
            self.assertTrue(
                any(p.endswith("secret.bin") for p in late_paths),
                msg=json.dumps(report["late_writes"], indent=2),
            )
            self.assertTrue(report["hazards"])
            self.assertGreaterEqual(report["coast_s"], 0.25)
            self.assertTrue(
                any(e.get("hazard") for e in report["late_writes"] if e["path"].endswith("secret.bin"))
            )

    def test_late_artifact_is_hazard(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            report = run_coast(tmp, "late_write.sh", max_coast_ms=2500)
            hazards = {e["path"] for e in report["hazards"]}
            self.assertIn("late.txt", hazards)


if __name__ == "__main__":
    unittest.main(verbosity=2)
