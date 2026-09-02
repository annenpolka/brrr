#!/usr/bin/env python3
"""Exclusive why for a lying zero; not concatenated parent stdout."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "zerowhy"


def load_mod(path: Path, name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


ZW = load_mod(CLI, "zerowhy_cli")


def parse_fields(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
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


def find_lineage(name: str) -> Path | None:
    env = os.environ.get("RUN_DIR")
    roots = []
    if env:
        roots.append(Path(env))
    here = ROOT
    for parent in [here, *here.parents]:
        roots.append(parent / "lab-runs/specimen-hdd-20260902-1112")
        roots.append(parent)
    seen: set[Path] = set()
    for run in roots:
        cand = run / "lineages" / name
        if cand in seen:
            continue
        seen.add(cand)
        if cand.is_dir():
            return cand
    return None


def find_swallowecho() -> Path | None:
    env = os.environ.get("SWALLOWECHO")
    if env and Path(env).is_file():
        return Path(env)
    home = Path.home() / ".grok/worktrees/annenpolka-brrr/candidate-swallowecho-swallowecho/swallowecho/swallowecho"
    if home.is_file():
        return home
    lin = find_lineage("candidate-swallowecho")
    if lin is not None and (lin / "swallowecho").is_file():
        return lin / "swallowecho"
    return None


def find_waitoneshot() -> Path | None:
    env = os.environ.get("WAITONESHOT")
    if env and Path(env).is_file():
        return Path(env)
    home = Path.home() / ".grok/worktrees/annenpolka-brrr/waitoneshot-waitoneshot/waitoneshot/waitoneshot.py"
    if home.is_file():
        return home
    lin = find_lineage("candidate-waitoneshot")
    if lin is None:
        return None
    if (lin / "waitoneshot").is_file():
        return lin / "waitoneshot"
    if (lin / "waitoneshot.py").is_file():
        return lin / "waitoneshot.py"
    return None


class DecideShellTests(unittest.TestCase):
    def test_false_or_echo_swallows(self):
        ev = ZW.decide_shell(src="false || echo ok")
        self.assertTrue(ev.swallow)
        self.assertEqual(ev.step_status, 0)
        self.assertFalse(ev.all_ok)

    def test_true_and_echo_all_ok(self):
        ev = ZW.decide_shell(src="true && echo ok")
        self.assertFalse(ev.swallow)
        self.assertEqual(ev.step_status, 0)
        self.assertTrue(ev.all_ok)

    def test_false_or_false_step_nonzero(self):
        ev = ZW.decide_shell(src="false || false")
        self.assertFalse(ev.swallow)
        self.assertEqual(ev.step_status, 1)

    def test_semicolon_last_status_is_not_swallow(self):
        ev = ZW.decide_shell(src="false; echo ok")
        self.assertFalse(ev.swallow)
        self.assertEqual(ev.step_status, 0)
        self.assertFalse(ev.all_ok)

    def test_pipe_last_status_is_not_swallow(self):
        ev = ZW.decide_shell(src="false | echo ok")
        self.assertFalse(ev.swallow)
        self.assertEqual(ev.step_status, 0)
        self.assertFalse(ev.all_ok)


class DecideWaitTests(unittest.TestCase):
    def test_timeout0_creation_wait_aborts(self):
        ev = ZW.decide_wait(0, True, "jsonpath", True)
        self.assertFalse(ev.visited)
        self.assertFalse(ev.oneshot)
        self.assertEqual(ev.abort, "wait-for-creation-requires-timeout")

    def test_timeout0_no_creation_wait_visits_existing(self):
        ev = ZW.decide_wait(0, False, "jsonpath", True)
        self.assertTrue(ev.visited)
        self.assertTrue(ev.oneshot)
        self.assertEqual(ev.abort, "none")

    def test_timeout0_no_creation_wait_missing_not_visited(self):
        ev = ZW.decide_wait(0, False, "jsonpath", False)
        self.assertFalse(ev.visited)
        self.assertTrue(ev.oneshot)
        self.assertEqual(ev.abort, "none")

    def test_for_delete_oneshot_even_with_creation_wait(self):
        ev = ZW.decide_wait(0, True, "delete", True)
        self.assertTrue(ev.visited)
        self.assertTrue(ev.oneshot)
        self.assertEqual(ev.abort, "none")

    def test_positive_timeout_missing_is_not_abort(self):
        ev = ZW.decide_wait(5, True, "jsonpath", False)
        self.assertFalse(ev.visited)
        self.assertEqual(ev.abort, "none")


class ClassifyTests(unittest.TestCase):
    def test_false_or_echo_is_swallowed_nonzero(self):
        v = ZW.classify(ZW.decide_shell(src="false || echo ok"), None)
        self.assertEqual(v.why, "swallowed-nonzero")
        self.assertEqual(v.claims, ("swallowed-nonzero",))

    def test_abort_before_visit(self):
        v = ZW.classify(None, ZW.decide_wait(0, True, "jsonpath", True))
        self.assertEqual(v.why, "abort-before-visit")
        self.assertEqual(v.claims, ("abort-before-visit",))

    def test_oneshot_existing_is_observed_ok(self):
        v = ZW.classify(None, ZW.decide_wait(0, False, "jsonpath", True))
        self.assertEqual(v.why, "observed-ok")
        self.assertEqual(v.claims, ("observed-ok",))

    def test_true_and_echo_is_observed_ok(self):
        v = ZW.classify(ZW.decide_shell(src="true && echo ok"), None)
        self.assertEqual(v.why, "observed-ok")

    def test_semicolon_lie_is_unknown(self):
        v = ZW.classify(ZW.decide_shell(src="false; echo ok"), None)
        self.assertEqual(v.why, "unknown")
        self.assertEqual(v.claims, ())

    def test_false_or_false_is_unknown(self):
        v = ZW.classify(ZW.decide_shell(src="false || false"), None)
        self.assertEqual(v.why, "unknown")

    def test_oneshot_missing_is_unknown(self):
        v = ZW.classify(None, ZW.decide_wait(0, False, "jsonpath", False))
        self.assertEqual(v.why, "unknown")
        self.assertEqual(v.claims, ())

    def test_swallow_and_abort_conflict_is_unknown(self):
        v = ZW.classify(
            ZW.decide_shell(src="false || echo ok"),
            ZW.decide_wait(0, True, "jsonpath", True),
        )
        self.assertEqual(v.why, "unknown")
        self.assertEqual(
            v.claims, ("swallowed-nonzero", "abort-before-visit")
        )
        self.assertIn("exclusive", v.detail)

    def test_both_observed_ok_stays_observed_ok(self):
        v = ZW.classify(
            ZW.decide_shell(src="true && echo ok"),
            ZW.decide_wait(0, False, "jsonpath", True),
        )
        self.assertEqual(v.why, "observed-ok")
        self.assertEqual(v.claims, ("observed-ok",))

    def test_swallow_vs_visit_conflict_is_unknown(self):
        v = ZW.classify(
            ZW.decide_shell(src="false || echo ok"),
            ZW.decide_wait(0, False, "jsonpath", True),
        )
        self.assertEqual(v.why, "unknown")
        self.assertEqual(v.claims, ("swallowed-nonzero", "observed-ok"))

    def test_exactly_one_of_four(self):
        cases = [
            ZW.classify(ZW.decide_shell(src="false || echo ok"), None),
            ZW.classify(None, ZW.decide_wait(0, True, "jsonpath", True)),
            ZW.classify(None, ZW.decide_wait(0, False, "jsonpath", True)),
            ZW.classify(ZW.decide_shell(src="false; echo ok"), None),
        ]
        whys = [c.why for c in cases]
        self.assertEqual(
            whys,
            [
                "swallowed-nonzero",
                "abort-before-visit",
                "observed-ok",
                "unknown",
            ],
        )
        for why in whys:
            self.assertIn(why, ZW.WHYS)


class CliTests(unittest.TestCase):
    def test_cli_false_or_echo(self):
        proc = run_cli(["false || echo ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["why"], "swallowed-nonzero")
        self.assertEqual(rows["claims"], "swallowed-nonzero")

    def test_cli_abort_before_visit(self):
        proc = run_cli(
            ["--timeout", "0", "--wait-for-creation", "true"]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["why"], "abort-before-visit")

    def test_cli_oneshot_exists_observed_ok(self):
        proc = run_cli(
            [
                "--timeout",
                "0",
                "--wait-for-creation",
                "false",
                "--object-exists",
                "true",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["why"], "observed-ok")

    def test_cli_argv_list(self):
        proc = run_cli(["--", "false", "||", "echo", "ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["why"], "swallowed-nonzero")

    def test_cli_join_conflict(self):
        proc = run_cli(
            [
                "--timeout",
                "0",
                "--wait-for-creation",
                "true",
                "false || echo ok",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["why"], "unknown")
        self.assertEqual(rows["claims"], "swallowed-nonzero abort-before-visit")

    def test_cli_not_parent_concatenation(self):
        proc = run_cli(["false || echo ok"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("why  swallowed-nonzero", proc.stdout)
        self.assertNotIn("swallow\tyes", proc.stdout)
        self.assertNotIn("step_status", proc.stdout)
        self.assertNotIn("visited  ", proc.stdout)
        self.assertNotIn("hid_by", proc.stdout)
        abort = run_cli(["--timeout", "0", "--wait-for-creation", "true"])
        self.assertNotIn("wait_for_creation", abort.stdout)
        self.assertNotIn("wait-for-creation-requires-timeout", abort.stdout)
        self.assertNotIn("visited  ", abort.stdout)

    def test_cli_usage_without_evidence(self):
        proc = run_cli([])
        self.assertEqual(proc.returncode, 2)
        self.assertIn("need a snippet", proc.stderr)

    def test_cli_wait_flags_need_timeout(self):
        proc = run_cli(["--wait-for-creation", "true"])
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--timeout", proc.stderr)

    def test_cli_unmodeled_command(self):
        proc = run_cli(["make test || true"])
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unmodeled", proc.stderr)

    def test_cli_default_wait_for_creation_is_true(self):
        proc = run_cli(["--timeout", "0"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["why"], "abort-before-visit")

    def test_cli_for_delete_observed_ok(self):
        proc = run_cli(
            [
                "--timeout",
                "0",
                "--wait-for-creation",
                "true",
                "--for",
                "delete",
                "--object-exists",
                "true",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_fields(proc.stdout)
        self.assertEqual(rows["why"], "observed-ok")


class ParentOracleTests(unittest.TestCase):
    def test_swallowecho_oracle_false_or_echo(self):
        parent = find_swallowecho()
        if parent is None:
            self.skipTest("swallowecho parent not found")
        parent_proc = subprocess.run(
            [sys.executable, str(parent), "false || echo ok"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(parent_proc.returncode, 0, parent_proc.stderr)
        self.assertIn("swallow\tyes", parent_proc.stdout)
        ours = run_cli(["false || echo ok"])
        self.assertEqual(ours.returncode, 0, ours.stderr)
        self.assertEqual(parse_fields(ours.stdout)["why"], "swallowed-nonzero")
        self.assertNotEqual(ours.stdout, parent_proc.stdout)

    def test_waitoneshot_oracle_abort(self):
        parent = find_waitoneshot()
        if parent is None:
            self.skipTest("waitoneshot parent not found")
        cmd = [sys.executable, str(parent)] if parent.suffix == ".py" else [str(parent)]
        parent_proc = subprocess.run(
            cmd
            + [
                "--timeout",
                "0",
                "--wait-for-creation",
                "true",
                "--object-exists",
                "true",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(parent_proc.returncode, 0, parent_proc.stderr)
        self.assertIn("visited  false", parent_proc.stdout)
        self.assertIn("abort  wait-for-creation-requires-timeout", parent_proc.stdout)
        ours = run_cli(["--timeout", "0", "--wait-for-creation", "true", "--object-exists", "true"])
        self.assertEqual(ours.returncode, 0, ours.stderr)
        self.assertEqual(parse_fields(ours.stdout)["why"], "abort-before-visit")
        self.assertNotEqual(ours.stdout, parent_proc.stdout)

    def test_waitoneshot_oracle_oneshot_visit(self):
        parent = find_waitoneshot()
        if parent is None:
            self.skipTest("waitoneshot parent not found")
        cmd = [sys.executable, str(parent)] if parent.suffix == ".py" else [str(parent)]
        parent_proc = subprocess.run(
            cmd
            + [
                "--timeout",
                "0",
                "--wait-for-creation",
                "false",
                "--object-exists",
                "true",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(parent_proc.returncode, 0, parent_proc.stderr)
        self.assertIn("visited  true", parent_proc.stdout)
        ours = run_cli(
            [
                "--timeout",
                "0",
                "--wait-for-creation",
                "false",
                "--object-exists",
                "true",
            ]
        )
        self.assertEqual(parse_fields(ours.stdout)["why"], "observed-ok")

    def test_concatenated_parents_are_not_the_object(self):
        swallow = find_swallowecho()
        wait = find_waitoneshot()
        if swallow is None or wait is None:
            self.skipTest("both parents not found")
        s = subprocess.run(
            [sys.executable, str(swallow), "false || echo ok"],
            check=False,
            capture_output=True,
            text=True,
        )
        wcmd = [sys.executable, str(wait)] if wait.suffix == ".py" else [str(wait)]
        w = subprocess.run(
            wcmd
            + [
                "--timeout",
                "0",
                "--wait-for-creation",
                "true",
                "--object-exists",
                "true",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        concat = s.stdout + w.stdout
        ours = run_cli(
            ["--timeout", "0", "--wait-for-creation", "true", "false || echo ok"]
        )
        self.assertEqual(ours.returncode, 0, ours.stderr)
        self.assertNotEqual(ours.stdout, concat)
        self.assertEqual(parse_fields(ours.stdout)["why"], "unknown")
        self.assertNotIn("why  ", concat)


if __name__ == "__main__":
    unittest.main()
