#!/usr/bin/env python3
"""Drive the shipped envfrom CLI. No imports of internal helpers."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "envfrom"
FIX = ROOT / "fixtures" / "empty-override"
QUOTED = ROOT / "fixtures" / "quoted-export"


def run(args, cwd=None, extra_env=None):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
    }
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(cwd) if cwd is not None else str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )


class TestEmptyOverrideFixture(unittest.TestCase):
    def test_file_empty_override_vs_inherited(self):
        proc = run(
            ["--dir", str(FIX), "LIBRARY_PATH", "APP_ENV", "NOT_A_REAL_VAR"],
            extra_env={"LIBRARY_PATH": "/usr/local/lib:/usr/lib", "APP_ENV": "from-shell"},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = proc.stdout
        self.assertIn("LIBRARY_PATH\nVALUE=\nSOURCE: file:", out)
        self.assertIn(f"{FIX / '.env'}:2", out)
        self.assertIn("EMPTY_OVERRIDE: yes", out)
        self.assertIn("INHERITED: /usr/local/lib:/usr/lib", out)
        self.assertIn("APP_ENV\nVALUE=dev\nSOURCE: file:", out)
        self.assertIn("INHERITED: from-shell", out)
        self.assertIn("NOT_A_REAL_VAR\nVALUE=\nSOURCE: unset", out)
        self.assertNotIn("NOT_A_REAL_VAR\nVALUE=\nSOURCE: unset\nEMPTY_OVERRIDE", out)

    def test_inherited_env_when_not_in_file(self):
        proc = run(
            ["--dir", str(FIX), "PATH"],
            extra_env={"PATH": "/bin:/usr/bin"},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            proc.stdout,
            "PATH\nVALUE=/bin:/usr/bin\nSOURCE: env\n",
        )

    def test_fail_empty_exits_2(self):
        proc = run(
            ["--dir", str(FIX), "--fail-empty", "LIBRARY_PATH"],
            extra_env={"LIBRARY_PATH": "/already/set"},
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("EMPTY_OVERRIDE: yes", proc.stdout)

    def test_fail_empty_ok_when_not_empty_override(self):
        proc = run(
            ["--dir", str(FIX), "--fail-empty", "APP_ENV"],
            extra_env={"APP_ENV": "from-shell"},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)


class TestDotenvLocalAndRun(unittest.TestCase):
    def test_env_local_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("FOO=from-env\nBAR=keep\n", encoding="utf-8")
            Path(tmp, ".env.local").write_text("FOO=from-local\n", encoding="utf-8")
            proc = run(["--dir", tmp, "FOO", "BAR"], extra_env={"FOO": "from-process"})
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("FOO\nVALUE=from-local\nSOURCE: file:", proc.stdout)
            self.assertIn(f"{Path(tmp, '.env.local')}:1", proc.stdout)
            self.assertIn("INHERITED: from-process", proc.stdout)
            self.assertIn("BAR\nVALUE=keep\nSOURCE: file:", proc.stdout)
            self.assertIn(f"{Path(tmp, '.env')}:2", proc.stdout)

    def test_run_without_load_keeps_inherited(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("LIBRARY_PATH=\nFOO=filefoo\n", encoding="utf-8")
            proc = run(
                [
                    "--dir",
                    tmp,
                    "--run",
                    "--",
                    sys.executable,
                    "-c",
                    "import os; print('CHILD_LP=' + os.environ.get('LIBRARY_PATH', '(unset)'))",
                ],
                extra_env={"LIBRARY_PATH": "/usr/lib"},
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("LIBRARY_PATH\nVALUE=\nSOURCE: file:", proc.stdout)
            self.assertIn("EMPTY_OVERRIDE: yes", proc.stdout)
            self.assertIn("FOO\nVALUE=filefoo", proc.stdout)
            self.assertIn("CHILD_LP=/usr/lib", proc.stdout)

    def test_run_load_applies_empty_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("LIBRARY_PATH=\nFOO=filefoo\n", encoding="utf-8")
            proc = run(
                [
                    "--dir",
                    tmp,
                    "--run",
                    "--load",
                    "--",
                    sys.executable,
                    "-c",
                    "import os; print('CHILD_LP=' + repr(os.environ.get('LIBRARY_PATH'))); print('CHILD_FOO=' + os.environ.get('FOO', '(unset)'))",
                ],
                extra_env={"LIBRARY_PATH": "/usr/lib"},
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("EMPTY_OVERRIDE: yes", proc.stdout)
            self.assertIn("CHILD_LP=''", proc.stdout)
            self.assertIn("CHILD_FOO=filefoo", proc.stdout)

    def test_run_includes_extra_key_args(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("FOO=bar\n", encoding="utf-8")
            proc = run(
                [
                    "--dir",
                    tmp,
                    "ONLY_IN_PROCESS",
                    "--run",
                    "--",
                    sys.executable,
                    "-c",
                    "print('RAN')",
                ],
                extra_env={"ONLY_IN_PROCESS": "yes"},
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("FOO\nVALUE=bar", proc.stdout)
            self.assertIn("ONLY_IN_PROCESS\nVALUE=yes\nSOURCE: env", proc.stdout)
            self.assertIn("RAN", proc.stdout)

    def test_fail_empty_blocks_exec(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("LIBRARY_PATH=\n", encoding="utf-8")
            proc = run(
                [
                    "--dir",
                    tmp,
                    "--fail-empty",
                    "--run",
                    "--",
                    sys.executable,
                    "-c",
                    "print('SHOULD_NOT_RUN')",
                ],
                extra_env={"LIBRARY_PATH": "/usr/lib"},
            )
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertIn("EMPTY_OVERRIDE: yes", proc.stdout)
            self.assertNotIn("SHOULD_NOT_RUN", proc.stdout)

    def test_usage_errors(self):
        proc = run([])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("provide KEY", proc.stderr)
        proc = run(["--load", "FOO"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--load requires --run", proc.stderr)
        proc = run(["--run"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--run requires a command after --", proc.stderr)

    def test_file_empty_when_process_unset(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text("EMPTY_ME=\n", encoding="utf-8")
            proc = run(["--dir", tmp, "EMPTY_ME"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("EMPTY_OVERRIDE: yes", proc.stdout)
            self.assertIn("INHERITED: (unset)", proc.stdout)


class TestQuotedExportComments(unittest.TestCase):
    def test_export_prefix_quotes_and_inline_comments(self):
        proc = run(
            [
                "--dir",
                str(QUOTED),
                "PREFIX",
                "GREETING",
                "NAME",
                "COLOR",
                "EMPTY_QUOTED",
                "HASH_IN_QUOTES",
                "PATH_FRAGMENT",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = proc.stdout
        self.assertIn("PREFIX\nVALUE=app\nSOURCE: file:", out)
        self.assertIn(f"{QUOTED / '.env'}:2", out)
        self.assertIn("GREETING\nVALUE=hello world\nSOURCE: file:", out)
        self.assertIn("NAME\nVALUE=Ada Lovelace\nSOURCE: file:", out)
        self.assertIn("COLOR\nVALUE=red\nSOURCE: file:", out)
        self.assertNotIn("inline comment", out)
        self.assertIn("EMPTY_QUOTED\nVALUE=\nSOURCE: file:", out)
        self.assertIn("EMPTY_OVERRIDE: yes", out)
        self.assertIn("HASH_IN_QUOTES\nVALUE=# not a comment\nSOURCE: file:", out)
        self.assertIn("PATH_FRAGMENT\nVALUE=/usr/bin:/opt/app/bin\nSOURCE: file:", out)

    def test_load_quoted_and_export_into_child(self):
        proc = run(
            [
                "--dir",
                str(QUOTED),
                "--run",
                "--load",
                "--",
                sys.executable,
                "-c",
                "import os; print(os.environ.get('PREFIX')); print(os.environ.get('GREETING')); print(os.environ.get('NAME')); print(repr(os.environ.get('EMPTY_QUOTED')))",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("\napp\nhello world\nAda Lovelace\n''\n", proc.stdout)

    def test_double_quote_escapes(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, ".env").write_text('MSG="say \\"hi\\"\\tnow"\n', encoding="utf-8")
            proc = run(["--dir", tmp, "MSG"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("MSG\nVALUE=say \"hi\"\tnow\nSOURCE: file:", proc.stdout)


if __name__ == "__main__":
    unittest.main()
