#!/usr/bin/env python3
"""Drive the shipped effect CLI. No imports of internal helpers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "effect"
FIXTURES = ROOT / "fixtures"


def run_effect(*args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": os.environ.get("HOME", "/tmp"),
    }
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
    )


def section(text: str, name: str, nxt: str | None) -> str:
    start = text.index(name)
    if nxt is None:
        return text[start:]
    end = text.index(nxt, start + len(name))
    return text[start:end]


class UsageTests(unittest.TestCase):
    def test_missing_key_exits_1(self) -> None:
        proc = run_effect()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing KEY", proc.stderr)

    def test_help_exits_0(self) -> None:
        proc = run_effect("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("usage: effect", proc.stdout)

    def test_unknown_flag_exits_1(self) -> None:
        proc = run_effect("--nope", "timeout")
        self.assertEqual(proc.returncode, 1)

    def test_missing_dir_exits_1(self) -> None:
        proc = run_effect("timeout", str(ROOT / "no-such-dir"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not found", proc.stderr)


class JointRecordTests(unittest.TestCase):
    def test_disagree_exits_2_prints_all_four_and_env(self) -> None:
        proc = run_effect(
            "timeout",
            str(FIXTURES / "disagree"),
            extra_env={"TIMEOUT": "from-shell"},
        )
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        out = proc.stdout
        self.assertIn("KEY: timeout", out)
        self.assertLess(out.index("DECLARED:"), out.index("ASSIGNED:"))
        self.assertLess(out.index("ASSIGNED:"), out.index("ENV_SOURCE:"))
        self.assertLess(out.index("ENV_SOURCE:"), out.index("EFFECTIVE:"))
        decl = section(out, "DECLARED:", "ASSIGNED:")
        assigned = section(out, "ASSIGNED:", "ENV_SOURCE:")
        env = section(out, "ENV_SOURCE:", "EFFECTIVE:")
        effective = section(out, "EFFECTIVE:", None)
        self.assertIn("config.yaml:1", decl)
        self.assertIn("value=5", decl)
        self.assertNotIn("TIMEOUT=30", decl)
        self.assertNotIn(".env", decl)
        self.assertIn("app.py:", assigned)
        self.assertIn("value=10", assigned)
        self.assertIn("TIMEOUT", env)
        self.assertIn("file:", env)
        self.assertIn("value=30", env)
        self.assertIn("why=case-variant", env)
        self.assertIn("INHERITED: from-shell", env)
        self.assertIn("unknown", effective)
        self.assertIn("declared 5 vs assigned 10", effective)

    def test_agree_effective_5(self) -> None:
        proc = run_effect("timeout", str(FIXTURES / "agree"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("value=5", proc.stdout)
        self.assertIn("EFFECTIVE:\n  5\n", proc.stdout)
        self.assertIn("unset", proc.stdout)

    def test_empty_override_deferred_timeout(self) -> None:
        proc = run_effect(
            "timeout",
            str(FIXTURES / "empty-override"),
            extra_env={"TIMEOUT": "/already/set"},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = proc.stdout
        env = section(out, "ENV_SOURCE:", "EFFECTIVE:")
        self.assertIn("TIMEOUT", env)
        self.assertIn("EMPTY_OVERRIDE: yes", env)
        self.assertIn("INHERITED: /already/set", env)
        self.assertIn("why=deferred", env)
        self.assertIn("unknown", section(out, "EFFECTIVE:", None))
        self.assertIn("literal 5 vs env (empty)", section(out, "EFFECTIVE:", None))
        self.assertNotIn(".env", section(out, "DECLARED:", "ASSIGNED:"))
        self.assertIn(
            'os.getenv("TIMEOUT", "5")',
            section(out, "ASSIGNED:", "ENV_SOURCE:"),
        )

    def test_deferred_wait_effective_from_env(self) -> None:
        proc = run_effect(
            "timeout",
            str(FIXTURES / "deferred"),
            extra_env={"WAIT": "from-shell"},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = proc.stdout
        env = section(out, "ENV_SOURCE:", "EFFECTIVE:")
        self.assertIn("WAIT", env)
        self.assertIn("value=10", env)
        self.assertIn("why=deferred", env)
        self.assertIn("INHERITED: from-shell", env)
        self.assertIn("EFFECTIVE:\n  10\n", out)
        assigned = section(out, "ASSIGNED:", "ENV_SOURCE:")
        self.assertIn("not comparable", assigned)
        self.assertIn("os.getenv", assigned)

    def test_unknown_interpolation_unset_env(self) -> None:
        proc = run_effect("timeout", str(FIXTURES / "unknown"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("unknown", section(proc.stdout, "EFFECTIVE:", None))
        self.assertIn("WAIT", section(proc.stdout, "ENV_SOURCE:", "EFFECTIVE:"))
        self.assertIn("unset", section(proc.stdout, "ENV_SOURCE:", "EFFECTIVE:"))
        self.assertIn("${WAIT}", section(proc.stdout, "DECLARED:", "ASSIGNED:"))

    def test_config_only(self) -> None:
        proc = run_effect("timeout", str(FIXTURES / "config_only"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("config.yaml:1", proc.stdout)
        self.assertIn("ASSIGNED:\n  (none)\n", proc.stdout)
        self.assertIn("EFFECTIVE:\n  5\n", proc.stdout)

    def test_comments_not_disagreement(self) -> None:
        proc = run_effect("timeout", str(FIXTURES / "comments"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("EFFECTIVE:\n  5\n", proc.stdout)
        self.assertIn("(comment)", proc.stdout)
        self.assertIn("timeout = 99", proc.stdout)
        self.assertNotIn("declared 5 vs assigned 99", proc.stdout)

    def test_json_is_one_object(self) -> None:
        proc = run_effect(
            "--json",
            "timeout",
            str(FIXTURES / "disagree"),
            extra_env={"TIMEOUT": "from-shell"},
        )
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIsInstance(payload, dict)
        for field in ("declared", "assigned", "env_source", "effective", "disagree", "key"):
            self.assertIn(field, payload)
        self.assertEqual(payload["key"], "timeout")
        self.assertTrue(payload["disagree"])
        self.assertEqual(payload["effective"]["status"], "unknown")
        self.assertEqual(payload["declared"][0]["raw_value"], "5")
        self.assertEqual(payload["assigned"][0]["raw_value"], "10")
        env_keys = {row["key"]: row for row in payload["env_source"]}
        self.assertIn("TIMEOUT", env_keys)
        self.assertEqual(env_keys["TIMEOUT"]["value"], "30")
        self.assertEqual(env_keys["TIMEOUT"]["why"], "case-variant")
        self.assertEqual(env_keys["TIMEOUT"]["inherited"], "from-shell")
        self.assertFalse(any(h["path"].endswith(".env") for h in payload["declared"]))

    def test_json_deferred_join(self) -> None:
        proc = run_effect("--json", "timeout", str(FIXTURES / "deferred"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["effective"]["status"], "value")
        self.assertEqual(payload["effective"]["value"], "10")
        self.assertIn("WAIT", payload["deferred"])
        whys = {row["key"]: row["why"] for row in payload["env_source"]}
        self.assertEqual(whys.get("WAIT"), "deferred")

    def test_no_sites(self) -> None:
        proc = run_effect("no_such_key_zzz", str(FIXTURES / "agree"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("DECLARED:\n  (none)\n", proc.stdout)
        self.assertIn("unknown", proc.stdout)

    def test_environ_get_and_process_env_are_deferred(self) -> None:
        proc = run_effect(
            "timeout",
            str(FIXTURES / "environ-get"),
            extra_env={"WAIT": "from-shell"},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = proc.stdout
        env = section(out, "ENV_SOURCE:", "EFFECTIVE:")
        self.assertIn("WAIT", env)
        self.assertIn("value=10", env)
        self.assertIn("why=deferred", env)
        self.assertIn("INHERITED: from-shell", env)
        self.assertNotIn("EMPTY_OVERRIDE", env)
        effective = section(out, "EFFECTIVE:", None)
        self.assertIn("unknown", effective)
        self.assertIn("literal 5 vs env 10", effective)
        assigned = section(out, "ASSIGNED:", "ENV_SOURCE:")
        self.assertIn("os.environ.get", assigned)
        self.assertIn("process.env.WAIT", assigned)

    def test_compact_json_declaration_is_not_false_effective(self) -> None:
        proc = run_effect("timeout", str(FIXTURES / "compact_json"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        out = proc.stdout
        decl = section(out, "DECLARED:", "ASSIGNED:")
        assigned = section(out, "ASSIGNED:", "ENV_SOURCE:")
        effective = section(out, "EFFECTIVE:", None)
        self.assertIn("config.json:1", decl)
        self.assertIn("value=5", decl)
        self.assertNotIn("(none)", decl)
        self.assertIn("app.py:1", assigned)
        self.assertIn("value=10", assigned)
        self.assertIn("unknown", effective)
        self.assertIn("declared 5 vs assigned 10", effective)
        self.assertNotIn("EFFECTIVE:\n  10\n", out)

    def test_json_compact_json_pair(self) -> None:
        proc = run_effect("--json", "timeout", str(FIXTURES / "compact_json"))
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertTrue(payload["disagree"])
        self.assertEqual(payload["effective"]["status"], "unknown")
        self.assertEqual(payload["effective"]["value"], None)
        self.assertIn("declared 5 vs assigned 10", payload["effective"]["reason"])
        self.assertEqual(payload["declared"][0]["raw_value"], "5")
        self.assertTrue(payload["declared"][0]["path"].endswith("config.json"))
        self.assertEqual(payload["assigned"][0]["raw_value"], "10")

    def test_json_environ_get_deferred(self) -> None:
        proc = run_effect(
            "--json",
            "timeout",
            str(FIXTURES / "environ-get"),
            extra_env={"WAIT": "from-shell"},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("WAIT", payload["deferred"])
        rows = {row["key"]: row for row in payload["env_source"]}
        self.assertEqual(rows["WAIT"]["value"], "10")
        self.assertEqual(rows["WAIT"]["why"], "deferred")
        self.assertEqual(rows["WAIT"]["inherited"], "from-shell")
        self.assertEqual(payload["effective"]["reason"], "literal 5 vs env 10")


if __name__ == "__main__":
    unittest.main()
