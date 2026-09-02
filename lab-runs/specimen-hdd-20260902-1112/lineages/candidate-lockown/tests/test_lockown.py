#!/usr/bin/env python3
"""Two threads, one lock: owner vs waiter."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "lockown"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("lockown_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


LO = load_mod()


def parse_fields(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("("):
            continue
        key, sep, value = line.partition("  ")
        if not sep:
            continue
        out[key] = value
    return out


def run_cli(args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=os.environ.copy(),
    )


class SnapshotTests(unittest.TestCase):
    def test_unheld_lock_has_no_owner_or_waiter(self):
        lock = LO.OwnedLock("L")
        snap = lock.snapshot()
        self.assertEqual(snap["owner"], "none")
        self.assertEqual(snap["waiter"], "none")
        self.assertEqual(snap["held"], "false")
        self.assertEqual(snap["lock"], "L")

    def test_owner_only_when_held_and_nobody_waiting(self):
        lock = LO.OwnedLock("L")
        seen: dict[str, str] = {}
        done = threading.Event()

        def hold() -> None:
            lock.acquire()
            try:
                seen.update(lock.snapshot())
            finally:
                lock.release()
                done.set()

        t = threading.Thread(target=hold, name="solo")
        t.start()
        self.assertTrue(done.wait(2))
        t.join(2)
        self.assertEqual(seen["owner"], "solo")
        self.assertEqual(seen["waiter"], "none")
        self.assertEqual(seen["held"], "true")
        snap = lock.snapshot()
        self.assertEqual(snap["owner"], "none")
        self.assertEqual(snap["held"], "false")


class SceneTests(unittest.TestCase):
    def test_two_threads_one_lock_names_owner_vs_waiter(self):
        snap = LO.run_scene(
            owner_name="holder",
            waiter_name="blocked",
            lock_name="L",
            release_after=True,
            waiter_timeout=None,
        )
        self.assertEqual(snap["lock"], "L")
        self.assertEqual(snap["owner"], "holder")
        self.assertEqual(snap["waiter"], "blocked")
        self.assertEqual(snap["held"], "true")
        self.assertNotEqual(snap["owner"], snap["waiter"])

    def test_pair_named_before_waiter_timeout_without_release(self):
        snap = LO.run_scene(
            release_after=False,
            waiter_timeout=0.3,
        )
        self.assertEqual(snap["owner"], "holder")
        self.assertEqual(snap["waiter"], "blocked")
        self.assertEqual(snap["held"], "true")

    def test_timeout_probe_does_not_name_owner(self):
        rows = LO.timeout_probe(timeout=0.15)
        self.assertEqual(rows["ok"], "false")
        self.assertEqual(rows["held"], "true")
        self.assertEqual(rows["owner"], "unnamed")
        self.assertEqual(rows["waiter"], "unnamed")
        self.assertIn("does not name the owner", rows["reason"])


class FixtureTests(unittest.TestCase):
    def test_timeout_only_fixture_has_no_owner_field(self):
        proc = subprocess.run(
            [sys.executable, str(FIXTURES / "timeout_only.py")],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["acquire_ok"], "false")
        self.assertEqual(rows["locked"], "true")
        self.assertNotIn("owner", rows)
        self.assertNotIn("waiter", rows)
        self.assertIn("does not name the owner", proc.stdout)


class CliTests(unittest.TestCase):
    def test_cli_two_threads_prints_owner_vs_waiter(self):
        proc = run_cli([])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["lock"], "L")
        self.assertEqual(rows["owner"], "holder")
        self.assertEqual(rows["waiter"], "blocked")
        self.assertEqual(rows["held"], "true")

    def test_cli_contrast_timeout_unnamed(self):
        proc = run_cli(["--contrast"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["ok"], "false")
        self.assertEqual(rows["owner"], "unnamed")
        self.assertEqual(rows["waiter"], "unnamed")
        self.assertEqual(rows["held"], "true")

    def test_cli_python_matches_launcher_path(self):
        proc = run_cli(["--contrast"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("timeout does not name the owner", proc.stdout)

    def test_cli_does_not_wait_out_waiter_timeout(self):
        t0 = time.monotonic()
        proc = run_cli([])
        elapsed = time.monotonic() - t0
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main()
