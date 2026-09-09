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

JST = ZoneInfo("Asia/Tokyo")


def _ledger(*, spent_frac: float, cap: float = 10.0, start_usage: float = 100.0, in_flight: float = 0.0) -> dict:
    spent = cap * spent_frac
    return {
        "hard_cap_usd": 30.0,
        "effective_cap_usd": cap,
        "stop_casual_usd": 0.8 * cap,
        "stop_all_new_r1_usd": cap,
        "day_max_r1_calls": 40,
        "in_flight_reserve_usd": in_flight,
        "openrouter_snapshot_at_start": {
            "at_jst": "2026-09-09 11:30:00 JST",
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
        # remaining 40, reserve 1.50 -> 30 user cap binds
        self.assertEqual(r1_budget.compute_effective_cap(40.0, user_cap=30.0, reserve=1.50), 30.0)
        # remaining 10, reserve 1.50 -> 8.50 binds
        self.assertEqual(r1_budget.compute_effective_cap(10.0, user_cap=30.0, reserve=1.50), 8.50)
        # remaining 1.50 or below -> 0
        self.assertEqual(r1_budget.compute_effective_cap(1.50, user_cap=30.0, reserve=1.50), 0.0)
        self.assertEqual(r1_budget.compute_effective_cap(0.40, user_cap=30.0, reserve=1.50), 0.0)

    def test_no_negative_cap(self):
        self.assertGreaterEqual(r1_budget.compute_effective_cap(-5.0), 0.0)


class R1BudgetTests(unittest.TestCase):
    def test_zero_effective_cap_blocks_r1(self):
        ledger = _ledger(spent_frac=0.0, cap=0.0)
        ledger["calls"] = []
        ledger["estimated_spend_usd"] = 0.0
        ok, reason = r1_budget.can_spend(ledger, "first-turn", now=datetime(2026, 9, 9, 12, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("effective_cap is 0", reason)

    def test_refuses_all_new_r1_at_100_percent_effective_cap(self):
        ledger = _ledger(spent_frac=1.0, cap=9.0)
        ok, reason = r1_budget.can_spend(ledger, "counterexample", now=datetime(2026, 9, 9, 12, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("100%", reason)

    def test_refuses_casual_at_80_percent_but_allows_counterexample(self):
        ledger = _ledger(spent_frac=0.85, cap=10.0)
        now = datetime(2026, 9, 9, 12, 0, tzinfo=JST)
        casual_ok, casual_reason = r1_budget.can_spend(ledger, "cambrian", now=now)
        self.assertFalse(casual_ok)
        self.assertIn("80%", casual_reason)
        hv_ok, hv_reason = r1_budget.can_spend(ledger, "counterexample", now=now)
        self.assertTrue(hv_ok, hv_reason)

    def test_in_flight_reserve_counts_against_cap(self):
        ledger = _ledger(spent_frac=0.5, cap=10.0, in_flight=5.1)
        ok, reason = r1_budget.can_spend(ledger, "first-turn", now=datetime(2026, 9, 9, 12, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("100%", reason)

    def test_freeze_blocks_broad_r1_after_2245(self):
        ledger = _ledger(spent_frac=0.1, cap=10.0)
        now = r1_budget.BROAD_FREEZE + timedelta(minutes=1)
        ok, reason = r1_budget.can_spend(ledger, "cambrian", now=now)
        self.assertFalse(ok)
        self.assertIn("broad R1 frozen", reason)
        jump_ok, jump_reason = r1_budget.can_spend(ledger, "exceptional-jump", now=now)
        self.assertTrue(jump_ok, jump_reason)

    def test_hard_end_blocks_all_r1(self):
        ledger = _ledger(spent_frac=0.1, cap=10.0)
        ok, reason = r1_budget.can_spend(ledger, "exceptional-jump", now=r1_budget.HARD_END)
        self.assertFalse(ok)
        self.assertIn("hard end", reason)

    def test_day_max_calls(self):
        ledger = _ledger(spent_frac=0.1, cap=10.0)
        ledger["calls"] = [{"credits_after": {"total_usage": 100.1}}] * 40
        ok, reason = r1_budget.can_spend(ledger, "first-turn", now=datetime(2026, 9, 9, 12, 0, tzinfo=JST))
        self.assertFalse(ok)
        self.assertIn("day max", reason)


class ClockGateTests(unittest.TestCase):
    def test_named_windows(self):
        g = clock_gate.GATES
        self.assertEqual(clock_gate.phase(g["first_selection"] - timedelta(minutes=1)), "explore_or_select")
        self.assertEqual(clock_gate.phase(g["first_selection"]), "counterexample_window")
        self.assertEqual(clock_gate.phase(g["counterexample"]), "no_broad_already_ended")
        self.assertEqual(clock_gate.phase(g["broad_end"]), "final_jury")
        self.assertEqual(clock_gate.phase(g["save"]), "save")
        self.assertEqual(clock_gate.phase(g["drain"]), "drain")
        self.assertEqual(clock_gate.phase(g["hard_stop"]), "hard_stop")

    def test_due_action_does_not_save_before_2325(self):
        g = clock_gate.GATES
        self.assertEqual(clock_gate.due_action(g["first_selection"]), "checkpoint_1530")
        self.assertEqual(clock_gate.due_action(g["save"]), "save")
        self.assertEqual(clock_gate.due_action(g["hard_stop"]), "hard_stop")

    def test_checkpoint_refuses_before_gate(self):
        with self.assertRaises(SystemExit):
            clock_gate.checkpoint("save", at=clock_gate.GATES["save"] - timedelta(minutes=1))

    def test_save_and_hard_stop_refuse_before_named_clock(self):
        g = clock_gate.GATES
        stop_path = Path(__file__).resolve().parents[1] / "HARD_STOP.md"
        before = (stop_path.read_bytes(), stop_path.stat().st_mtime_ns) if stop_path.exists() else None
        with self.assertRaises(SystemExit) as save_err:
            day_end.save(at=g["save"] - timedelta(minutes=1))
        self.assertIn("refused before", str(save_err.exception))
        with self.assertRaises(SystemExit) as stop_err:
            day_end.hard_stop(at=g["hard_stop"] - timedelta(minutes=1))
        self.assertIn("refused before", str(stop_err.exception))
        # A refused early call must not create or rewrite the live HARD_STOP record.
        if before is None:
            self.assertFalse(stop_path.exists())
        else:
            self.assertEqual(stop_path.read_bytes(), before[0])
            self.assertEqual(stop_path.stat().st_mtime_ns, before[1])

    def test_reschedule_is_not_later_than_original_midnight(self):
        self.assertLessEqual(clock_gate.GATES["hard_stop"], clock_gate.ORIGINAL_HARD_END)


class ChainFilesTests(unittest.TestCase):
    """Structural check that the live first trial actually recorded the required chain."""

    def test_snapshot_hashes_trial_dream_redpen_exist(self):
        run = Path(__file__).resolve().parents[1]
        repo = run.parent.parent
        chain_path = run / "CHAIN-001.json"
        self.assertTrue(chain_path.is_file(), "CHAIN-001.json missing")
        import json

        chain = json.loads(chain_path.read_text(encoding="utf-8"))
        self.assertEqual(
            chain["snapshot_id"],
            "bd49baaa36b6999fdf9e44cf38da470c57c5f9daa6ce291e89c9084c3cce5a81",
        )
        from hash_bundle import hash_tree

        live = hash_tree(run / "inputs" / "case-001")
        self.assertEqual(live, chain["file_hashes"])
        trial = repo / ".hdd-runs" / "corpus-hdd-20260909-1130" / "case-001-a"
        dream = trial / "iterations" / "0001-dreamer.md"
        redpen = trial / "iterations" / "0001-redpen.json"
        self.assertTrue(dream.is_file(), dream)
        self.assertTrue(redpen.is_file(), redpen)
        dream_text = dream.read_text(encoding="utf-8")
        self.assertGreater(len(dream_text), 200)
        self.assertNotIn("docs/execplans/20260909-1130-hdd.md", dream_text)
        patch = json.loads(redpen.read_text(encoding="utf-8"))
        self.assertIn("pressure", patch)


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

    def test_original_text_marker_fails(self):
        hits = self._scan("seed.md", "private source_revision body pasted here\n")
        self.assertTrue(any("private source_revision body" in h for h in hits), hits)

    def test_private_review_fails(self):
        hits = self._scan("seed.md", "see .brrr-corpus/mini-followup/approved-review/review-audit.json\n")
        self.assertTrue(any("approved-review" in h for h in hits), hits)

    def test_past_run_fails(self):
        hits = self._scan("seed.md", "continue lab-runs/specimen-hdd-20260902-1112/lineages\n")
        self.assertTrue(any("specimen-hdd-20260902-1112" in h for h in hits), hits)

    def test_answer_key_fails(self):
        hits = self._scan("seed.md", "The answer-key says the lockfile parser is wrong.\n")
        self.assertTrue(any("answer-key" in h for h in hits), hits)

    def test_old_candidate_anti_steer_fails(self):
        hits = self._scan("seed.md", "Invent something unlike bindname.\n")
        self.assertTrue(any("anti-steer" in h for h in hits), hits)

    def test_collector_root_fails(self):
        hits = self._scan("seed.md", "read .brrr-corpus/mini-followup/objects/ab/cd\n")
        self.assertTrue(any("objects" in h for h in hits), hits)

    def test_git_fails(self):
        hits = self._scan("seed.md", "cat .git/HEAD and dump refs/heads/main\n")
        self.assertTrue(any("git" in h for h in hits), hits)

    def test_this_execplan_fails(self):
        hits = self._scan("seed.md", "follow docs/execplans/20260909-1130-hdd.md exactly\n")
        self.assertTrue(any("20260909-1130-hdd.md" in h for h in hits), hits)

    def test_first_selection_does_not_relax(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            (bundle / "seed.md").write_text("unlike invert please\n", encoding="utf-8")
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
