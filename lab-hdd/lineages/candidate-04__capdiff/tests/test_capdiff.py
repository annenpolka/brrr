#!/usr/bin/env python3
"""Tests drive the shipped capdiff CLI via subprocess."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CLI = os.path.join(ROOT, "capdiff")
FIX_A = os.path.join(ROOT, "fixtures", "env-a")
FIX_B = os.path.join(ROOT, "fixtures", "env-b")
PRINT_KEY = os.path.join(ROOT, "fixtures", "print_key.py")


def run_cli(args, cwd):
    env = os.environ.copy()
    env["PATH"] = os.path.dirname(sys.executable) + os.pathsep + env.get("PATH", "")
    return subprocess.run(
        [CLI] + list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        env=env,
    )


class CapdiffCLITests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp(prefix="capdiff-test-")
        if not os.access(CLI, os.X_OK):
            os.chmod(CLI, 0o755)

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def test_help(self):
        r = run_cli(["-h"], cwd=self.td)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("capture NAME DIR", r.stdout)
        self.assertIn("replay", r.stdout)

    def test_no_args_is_usage(self):
        r = run_cli([], cwd=self.td)
        self.assertEqual(r.returncode, 1)
        self.assertIn("usage", r.stdout.lower() + r.stderr.lower())

    def test_capture_diff_shows_api_key_and_extra_file(self):
        r = run_cli(["capture", "a", FIX_A], cwd=self.td)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run_cli(["capture", "b", FIX_B], cwd=self.td)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run_cli(["diff", "a", "b"], cwd=self.td)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("ENV modified:", out)
        self.assertIn("API_KEY", out)
        self.assertIn("local-ci-key", out)
        self.assertIn("remote-ci-key", out)
        self.assertIn("FILES extra:", out)
        self.assertIn("extra.txt", out)
        self.assertIn("FILES missing:", out)
        self.assertIn("(none)", out)
        self.assertTrue(os.path.isfile(os.path.join(self.td, ".capdiff", "a", ".env")))
        self.assertTrue(
            os.path.isfile(os.path.join(self.td, ".capdiff", "a", "manifest.json"))
        )

    def test_identical_captures_exit_0(self):
        self.assertEqual(run_cli(["capture", "a", FIX_A], cwd=self.td).returncode, 0)
        self.assertEqual(run_cli(["capture", "a2", FIX_A], cwd=self.td).returncode, 0)
        r = run_cli(["diff", "a", "a2"], cwd=self.td)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("(none)", r.stdout)

    def test_replay_env_only_prints_api_key(self):
        self.assertEqual(run_cli(["capture", "a", FIX_A], cwd=self.td).returncode, 0)
        r = run_cli(
            ["replay", "a", "--", FIX_A, sys.executable, PRINT_KEY],
            cwd=self.td,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "local-ci-key")

    def test_replay_remote_key(self):
        self.assertEqual(run_cli(["capture", "b", FIX_B], cwd=self.td).returncode, 0)
        r = run_cli(
            ["replay", "b", "--", FIX_B, sys.executable, PRINT_KEY],
            cwd=self.td,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "remote-ci-key")

    def test_replay_does_not_require_host_env(self):
        self.assertEqual(run_cli(["capture", "a", FIX_A], cwd=self.td).returncode, 0)
        dest = os.path.join(self.td, "empty-cwd")
        os.mkdir(dest)
        r = run_cli(
            [
                "replay",
                "a",
                "--",
                dest,
                sys.executable,
                "-c",
                "import os; print(os.environ['API_KEY'])",
            ],
            cwd=self.td,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "local-ci-key")

    def test_files_flag_writes_dotenv(self):
        self.assertEqual(run_cli(["capture", "a", FIX_A], cwd=self.td).returncode, 0)
        dest = os.path.join(self.td, "restore")
        os.mkdir(dest)
        r = run_cli(
            [
                "replay",
                "a",
                "--files",
                "--",
                dest,
                sys.executable,
                "-c",
                "print(open('.env').read())",
            ],
            cwd=self.td,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("API_KEY=local-ci-key", r.stdout)

    def test_missing_env_is_empty_not_crash(self):
        empty = os.path.join(self.td, "no-env")
        os.mkdir(empty)
        with open(os.path.join(empty, "readme.txt"), "w") as fh:
            fh.write("no dotenv\n")
        r = run_cli(["capture", "x", empty], cwd=self.td)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0 env vars", r.stdout)
        self.assertFalse(
            os.path.isfile(os.path.join(self.td, ".capdiff", "x", ".env"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(self.td, ".capdiff", "x", "manifest.json"))
        )
        r = run_cli(["capture", "a", FIX_A], cwd=self.td)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = run_cli(["diff", "a", "x"], cwd=self.td)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("API_KEY=local-ci-key", r.stdout)
        self.assertIn("ENV missing:", r.stdout)
        dest = os.path.join(self.td, "replay-empty")
        os.mkdir(dest)
        r = run_cli(
            [
                "replay",
                "x",
                "--files",
                "--",
                dest,
                sys.executable,
                "-c",
                "print('ok')",
            ],
            cwd=self.td,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "ok")
        self.assertFalse(os.path.isfile(os.path.join(dest, ".env")))

    def test_missing_capture_diff(self):
        r = run_cli(["diff", "nope", "also"], cwd=self.td)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not found", r.stderr)

    def test_bad_name(self):
        r = run_cli(["capture", "../x", FIX_A], cwd=self.td)
        self.assertEqual(r.returncode, 1)
        self.assertIn("NAME", r.stderr)

    def test_dot_name_rejected(self):
        r = run_cli(["capture", ".", FIX_A], cwd=self.td)
        self.assertEqual(r.returncode, 1)
        self.assertIn("NAME", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_dotdot_name_rejected(self):
        nest = os.path.join(self.td, "nest")
        os.mkdir(nest)
        r = run_cli(["capture", "..", FIX_A], cwd=nest)
        self.assertEqual(r.returncode, 1)
        self.assertIn("NAME", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertTrue(os.path.isdir(self.td))

    def test_corrupt_manifest_no_traceback(self):
        self.assertEqual(run_cli(["capture", "good", FIX_A], cwd=self.td).returncode, 0)
        bad = os.path.join(self.td, ".capdiff", "bad")
        os.makedirs(bad)
        with open(os.path.join(bad, "manifest.json"), "w") as fh:
            fh.write("{not json")
        r = run_cli(["diff", "good", "bad"], cwd=self.td)
        self.assertEqual(r.returncode, 1)
        self.assertIn("corrupt capture", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_truncated_captures_are_not_identical(self):
        store = os.path.join(self.td, ".capdiff")
        for name in ("a", "b"):
            dest = os.path.join(store, name)
            os.makedirs(dest)
            with open(os.path.join(dest, "manifest.json"), "w") as fh:
                json.dump(
                    {
                        "name": name,
                        "env": {},
                        "files": {"app.txt": "abc"},
                        "truncated": True,
                    },
                    fh,
                )
        r = run_cli(["diff", "a", "b"], cwd=self.td)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("truncated", r.stdout.lower())
        self.assertNotIn("Traceback", r.stderr)


if __name__ == "__main__":
    unittest.main()
