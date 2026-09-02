#!/usr/bin/env python3
"""Drive shipped coordinator functions. No reimplementation of gates."""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import contamination_check
import isolation_hash
import r1_budget
import scheduler
from compile_seed import compile_seed
from paths import HDD_ROOT, LEDGER_JSON, REPO_ROOT, RUN_DIR, RUN_ID

JST = ZoneInfo("Asia/Tokyo")


def _ledger(*, spent_frac: float, cap: float = 10.0, start_usage: float = 100.0) -> dict:
    spent = cap * spent_frac
    return {
        "hard_cap_usd": 50.0,
        "effective_cap_usd": cap,
        "stop_casual_usd": 0.8 * cap,
        "stop_all_new_r1_usd": cap,
        "openrouter_snapshot_at_start": {
            "at_jst": "2026-09-02 11:12:00 JST",
            "total_credits": 200.0,
            "total_usage": start_usage,
            "remaining": 20.0,
        },
        "calls": [
            {
                "credits_after": {"total_usage": start_usage + spent},
            }
        ],
        "pricing": {
            "input_usd_per_mtok": 0.7,
            "output_usd_per_mtok": 2.5,
            "source": "test",
        },
    }


class R1BudgetTests(unittest.TestCase):
    def test_reported_spend_uses_openrouter_delta(self):
        ledger = _ledger(spent_frac=0.5, cap=10.0, start_usage=14.0)
        self.assertAlmostEqual(r1_budget.reported_spend(ledger), 5.0)

    def test_refuses_all_new_r1_at_100_percent_effective_cap(self):
        ledger = _ledger(spent_frac=1.0, cap=9.0)
        now = datetime(2026, 9, 2, 12, 0, tzinfo=JST)
        ok, reason = r1_budget.can_spend(ledger, "counterexample", now=now)
        self.assertFalse(ok)
        self.assertIn("100%", reason)
        self.assertIn("hard stop", reason)

    def test_refuses_casual_first_turn_at_80_percent_but_allows_counterexample(self):
        ledger = _ledger(spent_frac=0.85, cap=10.0)
        now = datetime(2026, 9, 2, 12, 0, tzinfo=JST)
        casual_ok, casual_reason = r1_budget.can_spend(ledger, "cambrian", now=now)
        self.assertFalse(casual_ok)
        self.assertIn("80%", casual_reason)
        hv_ok, hv_reason = r1_budget.can_spend(ledger, "counterexample", now=now)
        self.assertTrue(hv_ok, hv_reason)

    def test_never_exceeds_hard_cap_50(self):
        ledger = _ledger(spent_frac=1.0, cap=50.0)
        ledger["hard_cap_usd"] = 50.0
        ledger["effective_cap_usd"] = 50.0
        ledger["stop_all_new_r1_usd"] = 50.0
        now = datetime(2026, 9, 2, 12, 0, tzinfo=JST)
        ok, reason = r1_budget.can_spend(ledger, "exceptional-jump", now=now)
        self.assertFalse(ok)
        self.assertTrue("hard" in reason.lower() or "stop" in reason.lower())

    def test_freeze_blocks_broad_r1_after_2245(self):
        ledger = _ledger(spent_frac=0.1, cap=10.0)
        now = datetime(2026, 9, 2, 22, 46, tzinfo=JST)
        ok, reason = r1_budget.can_spend(ledger, "cambrian", now=now)
        self.assertFalse(ok)
        self.assertIn("22:45", reason)
        jump_ok, jump_reason = r1_budget.can_spend(ledger, "exceptional-jump", now=now)
        self.assertTrue(jump_ok, jump_reason)


class ContaminationTests(unittest.TestCase):
    def test_anti_steer_phrase_fails_pre_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seeds = root / "seeds"
            seeds.mkdir()
            (seeds / "bad.md").write_text(
                "An unfamiliar CLI exists. Invent something unlike invert.\n",
                encoding="utf-8",
            )
            hdd = root / "hdd"
            hdd.mkdir()
            hits = contamination_check.check(root, hdd, first_selection=root / "FIRST_SELECTION.md")
            self.assertTrue(any("unlike invert" in h for h in hits), hits)

    def test_answer_key_text_in_task_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "specimens" / "specimen-001"
            (spec / "answer-key").mkdir(parents=True)
            secret = "The actual repair was to isolate mutated module-global cache between tests."
            (spec / "answer-key" / "FIX.md").write_text(secret + "\n", encoding="utf-8")
            (spec / "TASK.md").write_text(
                "TASK\nTests fail depending on order.\n" + secret + "\n",
                encoding="utf-8",
            )
            hits = contamination_check.check(root, root / "hdd", first_selection=root / "NOPE.md")
            self.assertTrue(any("answer-key leak" in h for h in hits), hits)

    def test_clean_packet_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = root / "specimens" / "specimen-001"
            spec.mkdir(parents=True)
            (spec / "answer-key").mkdir()
            (spec / "answer-key" / "FIX.md").write_text(
                "The actual repair was to isolate mutated module-global cache between tests.\n",
                encoding="utf-8",
            )
            (spec / "TASK.md").write_text(
                "TASK\nA test fails when run after another test in the same module.\n",
                encoding="utf-8",
            )
            hits = contamination_check.check(root, root / "hdd", first_selection=root / "NOPE.md")
            self.assertEqual(hits, [])


class CompileSeedTests(unittest.TestCase):
    def test_seed_omits_answer_key_and_keeps_failing_world(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / "specimen-002"
            spec.mkdir()
            (spec / "answer-key").mkdir()
            (spec / "answer-key" / "FIX.md").write_text(
                "SECRET_FIX_TOKEN_DO_NOT_LEAK_INTO_SEED_PLEASE_YES\n", encoding="utf-8"
            )
            (spec / "TASK.md").write_text("TASK\nCache returns stale bytes after overwrite.\n", encoding="utf-8")
            (spec / "OBSERVED.md").write_text("OBSERVED\nsecond read != written bytes\n", encoding="utf-8")
            seed = compile_seed(spec)
            self.assertIn("Cache returns stale bytes", seed)
            self.assertNotIn("SECRET_FIX_TOKEN_DO_NOT_LEAK_INTO_SEED_PLEASE_YES", seed)
            self.assertNotIn("answer-key/", seed)
            self.assertIn("unfamiliar developer cli", seed.lower())


class SchedulerTests(unittest.TestCase):
    def test_claim_highest_priority_ready_job(self):
        state = scheduler.empty_state()
        now = datetime(2026, 9, 2, 12, 0, tzinfo=JST)
        scheduler.enqueue(
            state,
            "READY_SPECIMEN_SCOUT",
            input_ref="mine",
            expected_output="packet",
            kill_condition="20m",
            priority_reason="fill corpus",
            now=now,
        )
        scheduler.enqueue(
            state,
            "READY_RED_PEN",
            input_ref="dream-1",
            expected_output="redpen json",
            kill_condition="20m",
            priority_reason="critique ready dream",
            now=now,
        )
        job = scheduler.claim(state, "worker-a", now=now)
        self.assertIsNotNone(job)
        self.assertEqual(job["queue"], "READY_RED_PEN")
        self.assertEqual(job["status"], "CLAIMED")
        scheduler.complete(state, job["id"], result="ok", now=now)
        self.assertEqual(scheduler._find(state, job["id"])["status"], "DONE")

    def test_hard_stop_refuses_new_jobs(self):
        state = scheduler.empty_state()
        state["mode"] = "hard_stop"
        with self.assertRaises(RuntimeError):
            scheduler.enqueue(
                state,
                "READY_SPECIMEN_SCOUT",
                input_ref="x",
                expected_output="y",
                kill_condition="z",
                priority_reason="no",
                now=datetime(2026, 9, 3, 0, 1, tzinfo=JST),
            )


class TransportScriptTests(unittest.TestCase):
    def test_dream_and_redpen_scripts_target_this_run_hdd_root(self):
        dream = (RUN_DIR / "scripts" / "dream.sh").read_text(encoding="utf-8")
        redpen = (RUN_DIR / "scripts" / "record_redpen.sh").read_text(encoding="utf-8")
        budget = (RUN_DIR / "scripts" / "r1_budget.py").read_text(encoding="utf-8")
        self.assertIn(".hdd-runs", dream)
        self.assertIn("--root \"$HDD_ROOT\"", dream)
        self.assertNotIn("--root \"$ROOT/.hdd\"", dream)
        self.assertNotIn("lab-hdd", dream)
        self.assertIn(".hdd-runs", redpen)
        self.assertNotIn("lab-hdd", redpen)
        self.assertIn("stop_all_new_r1", budget)
        self.assertTrue(str(LEDGER_JSON).endswith(f"lab-runs/{RUN_ID}/r1-ledger.json"), LEDGER_JSON)
        self.assertTrue(str(HDD_ROOT).endswith(f".hdd-runs/{RUN_ID}"), HDD_ROOT)
        self.assertNotEqual(HDD_ROOT, REPO_ROOT / ".hdd")


class IsolationHashTests(unittest.TestCase):
    def test_snapshot_and_compare_real_historical_files(self):
        snap = isolation_hash.snapshot(REPO_ROOT)
        self.assertEqual(
            set(snap),
            {
                "EVOLUTION_REPORT.md",
                "HDD_EVOLUTION_REPORT.md",
                "lab/STATE.md",
                "lab-hdd/STATE.md",
                "lab-hdd/SEAL.md",
            },
        )
        for digest in snap.values():
            self.assertEqual(len(digest), 64)
        self.assertEqual(isolation_hash.compare(snap, snap), [])

    def test_compare_detects_drift(self):
        before = {"EVOLUTION_REPORT.md": "a" * 64}
        after = {"EVOLUTION_REPORT.md": "b" * 64}
        diffs = isolation_hash.compare(before, after)
        self.assertTrue(diffs)
        self.assertIn("EVOLUTION_REPORT.md", diffs[0])


if __name__ == "__main__":
    unittest.main()
