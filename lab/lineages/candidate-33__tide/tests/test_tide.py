#!/usr/bin/env python3
"""Unit tests for tide: extractors, classifier, and a tiny git walk."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_tide():
    path = ROOT / "tide"
    spec = importlib.util.spec_from_file_location("tide_mod", path)
    if spec is not None and spec.loader is not None:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    import types
    mod = types.ModuleType("tide_mod")
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), mod.__dict__)
    return mod


tide = load_tide()


def git(cwd: str, *args: str) -> None:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "tide",
            "GIT_AUTHOR_EMAIL": "tide@demo",
            "GIT_COMMITTER_NAME": "tide",
            "GIT_COMMITTER_EMAIL": "tide@demo",
            "GIT_AUTHOR_DATE": env.get("GIT_AUTHOR_DATE", "2026-01-01T00:00:00 +0000"),
            "GIT_COMMITTER_DATE": env.get("GIT_COMMITTER_DATE", "2026-01-01T00:00:00 +0000"),
        }
    )
    subprocess.check_call(
        ["git", *args],
        cwd=cwd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class ExtractInline(unittest.TestCase):
    def test_rust_message(self):
        src = """
#[test]
fn scan_scars() {
    assert_eq!(hits[0].message, "real scar outside fence -->");
}
"""
        os_ = tide.extract_inline(src, "src/hook/tests.rs")
        by = {o["lhs"]: o["raw"] for o in os_}
        self.assertEqual(by.get("hits[0].message"), "real scar outside fence -->")
        self.assertEqual(os_[0]["test"], "scan_scars")

    def test_jest_version_and_skip_idents(self):
        src = """
it("v", () => {
  expect(outcome.result.fingerprint.engineVersion).toBe("0.21.0");
  expect(first).toEqual(second);
});
"""
        os_ = tide.extract_inline(src, "evaluate.test.ts")
        lhs = {o["lhs"] for o in os_}
        self.assertIn("outcome.result.fingerprint.engineVersion", lhs)
        self.assertNotIn("first", lhs)

    def test_swift_expect(self):
        src = """
    func formatTimeSecondsOnly() {
        #expect(formatTime(45) == "0:45")
    }
"""
        os_ = tide.extract_inline(src, "UILogicTests.swift")
        self.assertEqual(os_[0]["raw"], "0:45")


class ExtractJson(unittest.TestCase):
    def test_naive_tracks_input(self):
        raw = json.dumps(
            {
                "id": "CTR-008",
                "input": "hello",
                "expected_properties": {"max_length_ratio": 0.95},
            }
        )
        os_ = tide.extract_json(raw, "contracts/testcases/CTR-008.json", oracle_roots_only=False)
        lhs = {o["lhs"] for o in os_}
        self.assertTrue(any(x.endswith("input") for x in lhs))
        self.assertTrue(any("max_length_ratio" in x for x in lhs))

    def test_roots_hides_input(self):
        raw = json.dumps(
            {
                "id": "CTR-008",
                "input": "hello",
                "expected_properties": {"max_length_ratio": 0.95, "contains": ["a", "b"]},
            }
        )
        os_ = tide.extract_json(raw, "contracts/testcases/CTR-008.json", oracle_roots_only=True)
        lhs = {o["lhs"]: o["raw"] for o in os_}
        self.assertFalse(any(x.endswith("input") for x in lhs))
        self.assertIn(0.95, lhs.values())
        self.assertTrue(any(v == ["a", "b"] for v in lhs.values()))


class Classify(unittest.TestCase):
    def _ev(self, values, events, prods):
        return [
            {
                "event": e,
                "value": v,
                "prod": p,
                "commit": str(i),
                "ts": i,
                "date": "2026-01-01",
                "subject": "",
            }
            for i, (v, e, p) in enumerate(zip(values, events, prods))
        ]

    def test_ratchet(self):
        info = tide.classify(self._ev(["1", "2", "4"], ["BORN", "SET", "SET"], ["COUPLED"] * 3))
        self.assertEqual(info["class"], "RATCHET")

    def test_version_ratchet(self):
        info = tide.classify(
            self._ev(['"0.19.0"', '"0.20.0"', '"0.21.0"'], ["BORN", "SET", "SET"], ["COUPLED"] * 3)
        )
        self.assertEqual(info["class"], "RATCHET")

    def test_flipflop_bless(self):
        info = tide.classify(
            self._ev(["3", "5", "3"], ["BORN", "SET", "SET"], ["COUPLED", "BLESS", "COUPLED"])
        )
        self.assertEqual(info["class"], "FLIPFLOP")
        self.assertTrue(info["bless"])


class WalkRepo(unittest.TestCase):
    def test_bless_and_flipflop(self):
        with tempfile.TemporaryDirectory() as td:
            git(td, "init", "-b", "main")
            git(td, "config", "user.email", "tide@demo")
            git(td, "config", "user.name", "tide")
            git(td, "config", "commit.gpgsign", "false")
            os.makedirs(os.path.join(td, "src"))
            os.makedirs(os.path.join(td, "tests"))
            Path(td, "src", "app.py").write_text("TIMEOUT = 30\nRETRIES = 3\n", encoding="utf-8")
            Path(td, "tests", "test_app.py").write_text(
                "import app\n"
                "def test_t():\n"
                "    assert app.TIMEOUT == 30\n"
                "    assert app.RETRIES == 3\n",
                encoding="utf-8",
            )
            git(td, "add", "-A")
            env_date = {"GIT_AUTHOR_DATE": "2026-01-01T00:00:00 +0000", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00 +0000"}
            os.environ.update(env_date)
            git(td, "commit", "-m", "t0")

            Path(td, "tests", "test_app.py").write_text(
                "import app\n"
                "def test_t():\n"
                "    assert app.TIMEOUT == 60\n"
                "    assert app.RETRIES == 3\n",
                encoding="utf-8",
            )
            git(td, "add", "-A")
            os.environ["GIT_AUTHOR_DATE"] = "2026-01-02T00:00:00 +0000"
            os.environ["GIT_COMMITTER_DATE"] = "2026-01-02T00:00:00 +0000"
            git(td, "commit", "-m", "bless timeout")

            Path(td, "tests", "test_app.py").write_text(
                "import app\n"
                "def test_t():\n"
                "    assert app.TIMEOUT == 60\n"
                "    assert app.RETRIES == 5\n",
                encoding="utf-8",
            )
            Path(td, "src", "app.py").write_text("TIMEOUT = 60\nRETRIES = 5\n", encoding="utf-8")
            git(td, "add", "-A")
            os.environ["GIT_AUTHOR_DATE"] = "2026-01-03T00:00:00 +0000"
            os.environ["GIT_COMMITTER_DATE"] = "2026-01-03T00:00:00 +0000"
            git(td, "commit", "-m", "retries 5")

            Path(td, "tests", "test_app.py").write_text(
                "import app\n"
                "def test_t():\n"
                "    assert app.TIMEOUT == 60\n"
                "    assert app.RETRIES == 3\n",
                encoding="utf-8",
            )
            Path(td, "src", "app.py").write_text("TIMEOUT = 60\nRETRIES = 3\n", encoding="utf-8")
            git(td, "add", "-A")
            os.environ["GIT_AUTHOR_DATE"] = "2026-01-04T00:00:00 +0000"
            os.environ["GIT_COMMITTER_DATE"] = "2026-01-04T00:00:00 +0000"
            git(td, "commit", "-m", "retries back to 3")

            series = tide.walk_oracles(td, 20, False, [], "naive")
            infos = {rec["lhs"]: tide.classify(rec["events"]) for rec in series.values()}
            self.assertEqual(infos["app.TIMEOUT"]["class"], "RATCHET")
            self.assertTrue(infos["app.TIMEOUT"]["bless"])
            self.assertEqual(infos["app.RETRIES"]["class"], "FLIPFLOP")


if __name__ == "__main__":
    unittest.main()
