#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import lees as L  # noqa: E402

FIX = ROOT / "fixtures"
PY = sys.executable
LEES = [PY, str(ROOT / "lees.py")]
FACTS = [
    "--clean-dict",
    "--dict-json",
    str(FIX / "facts.json"),
]


def run(args, stdin=None, env=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(
        LEES + args,
        input=stdin,
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        env=e,
    )
    return p


class StainTests(unittest.TestCase):
    def test_self_test(self):
        p = run(["--self-test"])
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)

    def test_local_tainted_under_fixture_dict(self):
        p = run(FACTS + ["--check", "--json", str(FIX / "local.snap")])
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["files"][0]["status"], "TAINTED")
        names = {h["name"] for h in data["files"][0]["hits"]}
        self.assertTrue({"HOME", "USER", "HOST"} <= names)

    def test_spec_only_clean(self):
        p = run(FACTS + ["--check", "--json", str(FIX / "spec_only.snap")])
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertEqual(json.loads(p.stdout)["files"][0]["status"], "CLEAN")

    def test_holes_rewrite(self):
        p = run(FACTS + ["--holes", str(FIX / "local.snap")])
        self.assertEqual(p.returncode, 0)
        self.assertNotIn("/Users/alice", p.stdout)
        self.assertIn("{HOME}", p.stdout)
        self.assertIn("timeout: 30", p.stdout)

    def test_boundary_malice(self):
        facts = L.facts_from_json(json.dumps([{"name": "USER", "value": "alice", "kind": "env"}]))
        self.assertEqual(L.stain("malice\n", facts), [])

    def test_user_not_inside_home(self):
        facts = L.facts_from_json(
            json.dumps(
                [
                    {"name": "HOME", "value": "/Users/alice", "kind": "env"},
                    {"name": "USER", "value": "alice", "kind": "env"},
                ]
            )
        )
        hits = L.stain("/Users/alice/secret\n", facts)
        self.assertTrue(any(h.name == "HOME" for h in hits))
        self.assertFalse(any(h.name == "USER" for h in hits))

    def test_user_in_github_url_is_fixture(self):
        facts = L.facts_from_json(
            json.dumps([{"name": "USER", "value": "annenpolka", "kind": "env"}])
        )
        hits = L.stain('url = "https://github.com/annenpolka/sitbone"\n', facts)
        self.assertTrue(hits)
        self.assertTrue(all(h.kind == "fixture" for h in hits))
        self.assertEqual(L.current_machine_hits(hits), [])

    def test_standalone_user_stays_env(self):
        facts = L.facts_from_json(
            json.dumps([{"name": "USER", "value": "annenpolka", "kind": "env"}])
        )
        hits = L.stain("user: annenpolka\n", facts)
        self.assertTrue(any(h.kind == "env" and h.name == "USER" for h in hits))

    def test_ugly_unicode_spaces(self):
        p = run(
            FACTS
            + ["--json", str(FIX / "ugly" / "dir with spaces" / "snap.txt")]
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        hits = json.loads(p.stdout)["files"][0]["hits"]
        self.assertTrue(any(h["name"] == "HOME" for h in hits))


class ParTests(unittest.TestCase):
    def test_local_vs_ci_is_machine(self):
        p = run(
            FACTS
            + ["--json", "--check", "--par", str(FIX / "local.snap"), str(FIX / "ci.snap")]
        )
        data = json.loads(p.stdout)
        self.assertEqual(data["verdict"], "MACHINE", p.stdout)
        self.assertEqual(p.returncode, 0)
        self.assertEqual(data["residue"], [])

    def test_mixed_timeout(self):
        p = run(
            FACTS
            + ["--json", "--check", "--par", str(FIX / "local.snap"), str(FIX / "mixed.snap")]
        )
        data = json.loads(p.stdout)
        self.assertIn(data["verdict"], ("MIXED", "SPEC"))
        self.assertEqual(p.returncode, 1)
        blob = "\n".join(data["residue"])
        self.assertTrue("30" in blob and "60" in blob, blob)

    def test_spec_numeric(self):
        p = run(
            FACTS
            + [
                "--json",
                "--check",
                "--par",
                str(FIX / "spec_only.snap"),
                str(FIX / "spec_only_60.snap"),
            ]
        )
        data = json.loads(p.stdout)
        self.assertEqual(data["verdict"], "SPEC")
        self.assertEqual(p.returncode, 1)

    def test_identical_clean(self):
        p = run(
            FACTS
            + ["--json", "--check", "--par", str(FIX / "spec_only.snap"), str(FIX / "spec_only.snap")]
        )
        self.assertEqual(json.loads(p.stdout)["verdict"], "CLEAN")
        self.assertEqual(p.returncode, 0)


class FromFailTests(unittest.TestCase):
    def test_pytest_log_is_machine(self):
        log = (FIX / "pytest_fail.txt").read_text()
        p = run(FACTS + ["--from-fail", "--json", "--check"], stdin=log)
        data = json.loads(p.stdout)
        self.assertEqual(len(data["pairs"]), 1, p.stdout)
        self.assertTrue(
            all(row["verdict"] in {"MACHINE", "ENV"} for row in data["pairs"]),
            p.stdout,
        )
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_cargo_log_is_machine(self):
        log = (FIX / "cargo_fail.txt").read_text()
        p = run(FACTS + ["--from-fail", "--json"], stdin=log)
        data = json.loads(p.stdout)
        self.assertEqual(data["pairs"][0]["verdict"], "MACHINE", p.stdout)

    def test_spec_fail_is_spec(self):
        log = (FIX / "spec_fail.txt").read_text()
        p = run(FACTS + ["--from-fail", "--json", "--check"], stdin=log)
        data = json.loads(p.stdout)
        self.assertTrue(data["pairs"])
        self.assertTrue(any(row["verdict"] == "SPEC" for row in data["pairs"]), p.stdout)
        self.assertEqual(p.returncode, 1)


class ProbeTests(unittest.TestCase):
    def test_echo_world_is_env_tied(self):
        p = run(
            ["--probe", "--json", "--", PY, str(FIX / "echo_world.py")],
        )
        self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        data = json.loads(p.stdout)
        self.assertEqual(data["verdict"], "ENV-TIED", p.stdout)
        axes = {row["axis"]: row for row in data["axes"]}
        self.assertEqual(axes["env:HOME"]["raw"], "FLIP")
        self.assertEqual(axes["env:HOME"]["spec"], "STABLE")
        self.assertEqual(axes["env:TZ"]["raw"], "FLIP")
        self.assertEqual(axes["env:TZ"]["spec"], "STABLE")

    def test_echo_spec_is_stable(self):
        p = run(["--probe", "--json", "--", PY, str(FIX / "echo_spec.py")])
        data = json.loads(p.stdout)
        self.assertEqual(data["verdict"], "STABLE", p.stdout)
        for row in data["axes"]:
            self.assertEqual(row["raw"], "SAME", row)
            self.assertEqual(row["spec"], "STABLE", row)


class DictTests(unittest.TestCase):
    def test_dump_dict_has_home(self):
        p = run(["--dump-dict", "--json"])
        self.assertEqual(p.returncode, 0, p.stderr)
        rows = json.loads(p.stdout)
        names = {r["name"] for r in rows}
        self.assertIn("HOME", names)


if __name__ == "__main__":
    unittest.main()
