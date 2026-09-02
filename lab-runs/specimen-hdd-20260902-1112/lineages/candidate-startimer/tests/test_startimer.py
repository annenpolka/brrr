#!/usr/bin/env python3
"""start-interval timer armed during starting is not reset at period end."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "startimer"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("startimer_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


ST = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class Specimen066Tests(unittest.TestCase):
    def test_owned_timer_numbers(self):
        result = ST.inspect(2.0, 30.0, 2.0, 1)
        self.assertEqual(result["armed_kind"], "start-interval")
        self.assertEqual(result["armed"], 30.0)
        self.assertEqual(result["period_end"], 2.0)
        self.assertEqual(result["remaining_at_period_end"], 28.0)
        self.assertFalse(result["reset_at_period_end"])
        self.assertEqual(result["first_probe"], 30.0)
        self.assertEqual(result["unhealthy_at"], 30.0)
        self.assertEqual(result["expected_unhealthy"], 4.0)
        self.assertEqual(result["gap"], 26.0)

    def test_cli_owned(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--start-period",
                "2s",
                "--start-interval",
                "30s",
                "--interval",
                "2s",
                "--retries",
                "1",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["armed"], ["start-interval", "30s"])
        self.assertEqual(rows["period_end"], ["2s"])
        self.assertEqual(rows["remaining_at_period_end"], ["28s"])
        self.assertEqual(rows["reset_at_period_end"], ["no"])
        self.assertEqual(rows["unhealthy_at"], ["30s"])
        self.assertEqual(rows["expected_unhealthy"], ["4s"])
        self.assertEqual(rows["gap"], ["26s"])

    def test_unseen_retries_two(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--start-period",
                "5s",
                "--start-interval",
                "20s",
                "--interval",
                "3s",
                "--retries",
                "2",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["armed"], ["start-interval", "20s"])
        self.assertEqual(rows["remaining_at_period_end"], ["15s"])
        self.assertEqual(rows["unhealthy_at"], ["23s"])
        self.assertEqual(rows["expected_unhealthy"], ["11s"])

    def test_bad_retries(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--start-period",
                "2s",
                "--start-interval",
                "30s",
                "--interval",
                "2s",
                "--retries",
                "0",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
