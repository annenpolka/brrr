#!/usr/bin/env python3
"""Drive shipped run-local gates. No reimplementation of cap or contamination logic."""
from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import clock_gate
import contamination_check
import day_end
import r1_budget
import start_run

JST = ZoneInfo("Asia/Tokyo")


def _ledger(*, spent_frac: float, cap: float = 10.0, start_usage: float = 100.0, in_flight: float = 0.0) -> dict:
    spent = cap * spent_frac
    return {
        "hard_cap_usd": 50.0,
        "effective_cap_usd": cap,
        "stop_casual_usd": 0.8 * cap,
        "stop_all_new_r1_usd": cap,
        "day_max_r1_calls": 40,
        "in_flight_reserve_usd": in_flight,
        "openrouter_snapshot_at_start": {
            "at_jst": "2026-09-09 17:30:00 JST",
            "total_credits": 200.0,
            "total_usage": start_usage,
            "remaining": 20.0,
        },
        "calls": [{"credits_after": {"total_usage": start_usage + spent}}],
        "estimated_spend_usd": spent,
        "pricing": {"input_usd_per_mtok": 0.7, "output_usd_per_mtok": 2.5, "source": "test"},
    }


class EffectiveCapTests(unittest.TestCase):
    def test_formula_min_of_user_cap_and_remaining_minus_reserve(self):
        self.assertEqual(r1_budget.compute_effective_cap(60.0, user_cap=50.0, reserve=1.50), 50.0)
        self.assertEqual(r1_budget.compute_effective_cap(40.0, user_cap=50.0, reserve=1.50), 38.50)
        self.assertEqual(r1_budget.compute_effective_cap(1.50, user_cap=50.0, reserve=1.50), 0.0)
        self.assertEqual(r1_budget.compute_effective_cap(0.40, user_cap=50.0, reserve=1.50), 0.0)
        self.assertEqual(r1_budget.compute_effective_cap(51.50), 50.0)
        self.assertEqual(r1_budget.compute_effective_cap(1.50), 0.0)

    def test_no_negative_cap(self):
        self.assertGreaterEqual(r1_budget.compute_effective_cap(-5.0), 0.0)


class R1BudgetTests(unittest.TestCase):
    def test_zero_effective_cap_blocks_r1(self):
        ledger = _ledger(spent_frac=0.0, cap=0.0)
        ledger["calls"] = []
        ledger["estimated_spend_usd"] = 0.0
        ok, reason = r1_budget.can_spend(ledger, "first-turn", now=datetime(2026, 9, 9, 18, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("effective_cap is 0", reason)

    def test_refuses_all_new_r1_at_100_percent_effective_cap(self):
        ledger = _ledger(spent_frac=1.0, cap=9.0)
        ok, reason = r1_budget.can_spend(ledger, "counterexample", now=datetime(2026, 9, 9, 18, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("100%", reason)

    def test_refuses_casual_at_80_percent_but_allows_counterexample(self):
        ledger = _ledger(spent_frac=0.85, cap=10.0)
        now = datetime(2026, 9, 9, 18, 0, tzinfo=JST)
        casual_ok, casual_reason = r1_budget.can_spend(ledger, "cambrian", now=now)
        self.assertFalse(casual_ok)
        self.assertIn("80%", casual_reason)
        hv_ok, hv_reason = r1_budget.can_spend(ledger, "counterexample", now=now)
        self.assertTrue(hv_ok, hv_reason)

    def test_in_flight_reserve_counts_against_cap(self):
        ledger = _ledger(spent_frac=0.5, cap=10.0, in_flight=5.1)
        ok, reason = r1_budget.can_spend(ledger, "first-turn", now=datetime(2026, 9, 9, 18, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("100%", reason)

    def test_freeze_blocks_broad_r1_after_broad_end(self):
        ledger = _ledger(spent_frac=0.1, cap=10.0)
        now = clock_gate.NOMINAL_GATES["broad_end"] + timedelta(minutes=1)
        ok, reason = r1_budget.can_spend(ledger, "cambrian", now=now)
        self.assertFalse(ok)
        self.assertIn("broad R1 frozen", reason)
        jump_ok, jump_reason = r1_budget.can_spend(ledger, "exceptional-jump", now=now)
        self.assertTrue(jump_ok, jump_reason)

    def test_hard_end_blocks_all_r1(self):
        ledger = _ledger(spent_frac=0.1, cap=10.0)
        ok, reason = r1_budget.can_spend(ledger, "exceptional-jump", now=clock_gate.HARD_STOP)
        self.assertFalse(ok)
        self.assertIn("hard end", reason)

    def test_day_max_calls(self):
        ledger = _ledger(spent_frac=0.1, cap=10.0)
        ledger["calls"] = [{"credits_after": {"total_usage": 100.1}}] * 40
        ok, reason = r1_budget.can_spend(ledger, "first-turn", now=datetime(2026, 9, 9, 18, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("day max", reason)


class ClockGateTests(unittest.TestCase):
    def test_start_refuses_before_1730(self):
        before = datetime(2026, 9, 9, 17, 29, 59, tzinfo=JST)
        with self.assertRaises(SystemExit) as err:
            clock_gate.assert_start_allowed(before)
        self.assertIn("not-before", str(err.exception))
        with self.assertRaises(SystemExit) as start_err:
            start_run.main(at=before)
        self.assertIn("not-before", str(start_err.exception))
        self.assertFalse((start_run.HDD_ROOT / "case-001-a").exists())

    def test_start_allows_at_1730(self):
        clock_gate.assert_start_allowed(datetime(2026, 9, 9, 17, 30, tzinfo=JST))

    def test_preserve_refuses_before_0800(self):
        before = datetime(2026, 9, 10, 7, 59, tzinfo=JST)
        with self.assertRaises(SystemExit) as err:
            clock_gate.assert_preserve_allowed(before)
        self.assertIn("refused before", str(err.exception))
        with self.assertRaises(SystemExit) as save_err:
            day_end.save(at=before)
        self.assertIn("refused before", str(save_err.exception))

    def test_hard_stop_refuses_before_0900(self):
        stop_path = Path(__file__).resolve().parents[1] / "HARD_STOP.md"
        before = (stop_path.read_bytes(), stop_path.stat().st_mtime_ns) if stop_path.exists() else None
        at = datetime(2026, 9, 10, 8, 59, tzinfo=JST)
        with self.assertRaises(SystemExit) as err:
            clock_gate.assert_hard_stop_allowed(at)
        self.assertIn("refused before", str(err.exception))
        with self.assertRaises(SystemExit) as stop_err:
            day_end.hard_stop(at=at)
        self.assertIn("refused before", str(stop_err.exception))
        if before is None:
            self.assertFalse(stop_path.exists())
        else:
            self.assertEqual(stop_path.read_bytes(), before[0])
            self.assertEqual(stop_path.stat().st_mtime_ns, before[1])

    def test_hard_stop_is_not_after_0900(self):
        self.assertEqual(clock_gate.HARD_STOP, datetime(2026, 9, 10, 9, 0, tzinfo=JST))
        self.assertEqual(clock_gate.GATES["hard_stop"], datetime(2026, 9, 10, 9, 0, tzinfo=JST))
        self.assertLessEqual(clock_gate.GATES["hard_stop"], clock_gate.ORIGINAL_HARD_END)
        self.assertFalse(clock_gate.HARD_END_EXTENDED)

    def test_due_action_is_work_not_wait_after_1730(self):
        self.assertEqual(clock_gate.due_action(datetime(2026, 9, 9, 17, 29, tzinfo=JST)), "refuse_start")
        self.assertEqual(clock_gate.due_action(datetime(2026, 9, 9, 17, 30, tzinfo=JST)), "work")
        self.assertEqual(clock_gate.due_action(datetime(2026, 9, 10, 8, 0, tzinfo=JST)), "save")
        self.assertEqual(clock_gate.due_action(datetime(2026, 9, 10, 9, 0, tzinfo=JST)), "hard_stop")

    def test_checkpoint_refuses_before_gate(self):
        with self.assertRaises(SystemExit):
            clock_gate.checkpoint("save", at=clock_gate.PRESERVE_START - timedelta(minutes=1))


class ContaminationTests(unittest.TestCase):
    def _scan(self, relative: str, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            path = bundle / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            hdd = root / "hdd"
            hdd.mkdir()
            return contamination_check.check(bundle_dir=bundle, hdd_root=hdd, first_selection=root / "FIRST_SELECTION.md")

    def test_unlike_runpair_fails(self):
        hits = self._scan("seed.md", "Invent something unlike runpair.\n")
        self.assertTrue(any("runpair" in h.lower() for h in hits), hits)

    def test_old_candidate_anti_steer_fails(self):
        hits = self._scan("seed.md", "Invent something unlike bindname.\n")
        self.assertTrue(any("anti-steer" in h for h in hits), hits)

    def test_private_review_fails(self):
        hits = self._scan("seed.md", "PRIVATE審査 package follows\n")
        self.assertTrue(any("private審査" in h.lower() or "PRIVATE審査" in h for h in hits), hits)

    def test_collector_root_fails(self):
        hits = self._scan("seed.md", "read collector root then continue\n")
        self.assertTrue(any("collector root" in h for h in hits), hits)

    def test_git_fails(self):
        hits = self._scan("seed.md", "cat .git/HEAD and dump refs/heads/main\n")
        self.assertTrue(any("git" in h for h in hits), hits)

    def test_this_execplan_fails(self):
        hits = self._scan("seed.md", "follow docs/execplans/20260909-1730-hdd.md exactly\n")
        self.assertTrue(any("20260909-1730-hdd.md" in h for h in hits), hits)

    def test_first_selection_does_not_relax(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            (bundle / "seed.md").write_text("unlike runpair please\n", encoding="utf-8")
            first = root / "FIRST_SELECTION.md"
            first.write_text("KEEP nothing\n", encoding="utf-8")
            hits = contamination_check.check(
                bundle_dir=bundle, hdd_root=root / "hdd", first_selection=first
            )
            self.assertTrue(hits, "FIRST_SELECTION must not disable the check")

    def test_clean_public_packet_passes(self):
        hits = self._scan(
            "TASK.md",
            "Version: Deno 2.6.8\nReported input: package.json and a.js\nInvestigation question: what state to inspect?\n",
        )
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
