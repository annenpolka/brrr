#!/usr/bin/env python3
"""Save / HARD_STOP for this run only. Never kill 9/2 or lab-hdd PIDs. Never fabricate early."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from clock_gate import GATES, HARD_STOP, ORIGINAL_HARD_END, PRESERVE_START, assert_hard_stop_allowed, assert_preserve_allowed
from credits import fetch_credits, public_snapshot
from hash_bundle import hash_tree
from paths import CORPUS_ROOT, HDD_ROOT, REPO_ROOT, RUN_DIR, RUN_ID, SNAPSHOT_ID
from r1_budget import conservative_spend, load_ledger, remaining_usd, reported_spend, rewrite_budget_md

JST = ZoneInfo("Asia/Tokyo")
RECEIPT = REPO_ROOT / "docs/preparation/evidence-pilot-receipt.json"
SCRATCH = Path(os.environ.get("GOAL_SCRATCH", "")).resolve() if os.environ.get("GOAL_SCRATCH") else None


def now() -> datetime:
    return datetime.now(JST)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def this_run_pids() -> list[dict]:
    """Only this run's Dreamer/hdd.py/dream.sh workers. Never 9/2 PIDs or lab-hdd/."""
    out = subprocess.run(["ps", "-ax", "-o", "pid=,command="], capture_output=True, text=True, check=True)
    hits = []
    markers = (
        str(HDD_ROOT),
        f"{RUN_ID}/scripts/dream.sh",
        f"hdd.py --root {HDD_ROOT}",
    )
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        pid_s, _, cmd = line.partition(" ")
        if "specimen-hdd-20260902" in cmd or "lab-hdd/" in cmd:
            continue
        if "corpus-hdd-20260909-1130" in cmd:
            continue
        if any(m in cmd for m in markers) and ("hdd.py" in cmd or "dream.sh" in cmd):
            hits.append({"pid": int(pid_s), "command": cmd})
    return hits


def cmd(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=REPO_ROOT, check=True, text=True, capture_output=True)


def save(at: datetime | None = None) -> None:
    at = at or now()
    assert_preserve_allowed(at)
    credits = public_snapshot(fetch_credits())
    write(RUN_DIR / "credits-end.json", json.dumps(credits, indent=2) + "\n")
    if (RUN_DIR / "r1-ledger.json").exists():
        rewrite_budget_md()
        ledger = load_ledger()
    else:
        ledger = {
            "effective_cap_usd": 0.0,
            "total_calls": 0,
            "openrouter_snapshot_at_start": {"total_usage": 0, "remaining": 0, "total_credits": 0},
        }
    export_dir = CORPUS_ROOT / "exports" / "reported-discovery-v1-day-end-1730"
    if export_dir.exists():
        shutil.rmtree(export_dir)
    exported = cmd(
        [
            sys.executable,
            "scripts/corpus.py",
            "--root",
            str(CORPUS_ROOT),
            "export",
            SNAPSHOT_ID,
            "--output",
            str(export_dir),
        ]
    )
    write(RUN_DIR / "export-day-end.log", exported.stdout + exported.stderr)
    hashes = hash_tree(export_dir)
    expected = json.loads(RECEIPT.read_text(encoding="utf-8"))["export"]["files"]
    if hashes != expected:
        raise SystemExit(f"day-end export hash mismatch: {hashes} vs {expected}")
    bk = REPO_ROOT / ".brrr-corpus-backups" / "mini-followup-20260909-1730-hdd-day-end"
    rst = REPO_ROOT / ".brrr-corpus-restored" / "mini-followup-20260909-1730-hdd-day-end"
    if bk.exists():
        shutil.rmtree(bk)
    if rst.exists():
        shutil.rmtree(rst)
    cmd([sys.executable, "scripts/corpus.py", "--root", str(CORPUS_ROOT), "backup", "--output", str(bk)])
    cmd([sys.executable, "scripts/corpus.py", "restore", "--backup", str(bk), "--output", str(rst)])
    rst_export = rst / "exports" / "reported-discovery-v1"
    cmd(
        [
            sys.executable,
            "scripts/corpus.py",
            "--root",
            str(rst),
            "export",
            SNAPSHOT_ID,
            "--output",
            str(rst_export),
        ]
    )
    restored = hash_tree(rst_export)
    write(
        RUN_DIR / "restore-hashes-day-end.txt",
        json.dumps({"expected": expected, "restored": restored, "identical": restored == expected}, indent=2) + "\n",
    )
    if restored != expected:
        raise SystemExit("day-end restore hashes drifted")
    saiyo = RUN_DIR / "採否.md"
    if not saiyo.exists():
        write(
            saiyo,
            f"""# 採否理由

Host only. Not human. Recorded {at.strftime("%Y-%m-%d %H:%M:%S %Z")}.

HOLD/FAIL rows were not rewritten to PASS for the clock.

If no KEEP product: 0 products is allowed. See FIRST_SELECTION.md / FINAL_JURY.md if present.

Observed spend ${reported_spend(ledger):.6f}; conservative ${conservative_spend(ledger):.6f}; remaining ${remaining_usd(ledger):.6f}.
""",
        )
    if not (RUN_DIR / "RERUN.md").exists():
        write(
            RUN_DIR / "RERUN.md",
            f"""# 再実行方法

cwd: repository root `{REPO_ROOT}`

1. Do not start before 17:30 JST on 2026-09-09 without this run id.
2. Export the same snapshot:

       python3 scripts/corpus.py --root .brrr-corpus/mini-followup export {SNAPSHOT_ID} --output .brrr-corpus/mini-followup/exports/reported-discovery-v1

3. Copy only the public 6 files. Do not pass collector root, PRIVATE reviews, past runs, or the execplan to the Dreamer.
4. HDD:

       python3 /Users/annenpolka/.codex/skills/hdd-loop/scripts/hdd.py --root .hdd-runs/{RUN_ID} status --trial case-001-a

   Resume with `status`, not `init`, for the same trial.
5. Dreamer remains `deepseek/deepseek-r1`. No silent substitute.
6. Candidate worktrees go outside the run directory and are removed before HARD_STOP.
""",
        )
    if not (RUN_DIR / "TOMORROW.md").exists():
        write(RUN_DIR / "TOMORROW.md", "# Tomorrow Test (0–2)\n\n0 products is allowed.\n")
    if not (RUN_DIR / "FINAL_JURY.md").exists():
        write(
            RUN_DIR / "FINAL_JURY.md",
            f"""# Final jury

Host only. Not human.

Observed spend ${reported_spend(ledger):.6f}; conservative ${conservative_spend(ledger):.6f}; remaining ${remaining_usd(ledger):.6f}.
Input remains discovery (not 未知holdout) if still the 32113 public packet.
""",
        )
    if not (RUN_DIR / "EVOLUTION_REPORT.md").exists():
        write(
            RUN_DIR / "EVOLUTION_REPORT.md",
            f"""# Evolution report (this run only)

Run `{RUN_ID}` hard end 2026-09-10 09:00 JST not extended.

- Snapshot `{SNAPSHOT_ID}` public 6 hashes recorded in INPUTS.json.
- Cost: observed ${reported_spend(ledger):.6f}, conservative ${conservative_spend(ledger):.6f}, cap ${ledger.get('effective_cap_usd', 0):.4f}, calls {ledger.get('total_calls', 0)}.
- Coordinator main was not given candidate product during the experiment.
""",
        )
    print("save complete")


def hard_stop(at: datetime | None = None) -> None:
    at = at or now()
    assert_hard_stop_allowed(at)
    pids = this_run_pids()
    live = [
        p
        for p in pids
        if "day_end.py" not in p["command"] and "clock_gate.py" not in p["command"]
    ]
    write(
        RUN_DIR / "HARD_STOP.md",
        f"""HARD STOP at {at.strftime("%Y-%m-%d %H:%M:%S %Z")}
Run: {RUN_ID}
Matched dirs: {RUN_DIR}, {HDD_ROOT}
Live processes for this run (excluding this stopper): {len(live)}
{json.dumps(live, indent=2)}
Old 9/2 PIDs were not killed.
lab-hdd/ PIDs were not killed.
corpus-hdd-20260909-1130 PIDs were not killed.
hard_end_extended: no
""",
    )
    ps_text = subprocess.run(["ps", "-ax", "-o", "pid=,command="], capture_output=True, text=True, check=True).stdout
    write(RUN_DIR / "hard-stop-ps.txt", ps_text)
    write(
        RUN_DIR / "clock-stop.txt",
        "\n".join(
            [
                "phase: hard_stop",
                f"captured_at_jst: {at.isoformat()}",
                f"human: {at.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                f"hard_end: {GATES['hard_stop'].isoformat()}",
                f"original_hard_end: {ORIGINAL_HARD_END.isoformat()}",
                "hard_end_extended: no",
                f"this_run_live_pids: {len(live)}",
                f"run_id: {RUN_ID}",
            ]
        )
        + "\n",
    )
    leftover_wt = list((RUN_DIR / "worktrees").glob("*")) if (RUN_DIR / "worktrees").exists() else []
    if leftover_wt:
        raise SystemExit(f"worktrees left inside the run directory: {leftover_wt}")
    if live:
        raise SystemExit(f"this run still has live processes: {live}")
    print("HARD_STOP recorded; live=0")


def copy_scratch() -> None:
    if not SCRATCH:
        return
    for name in (
        "credits-end.json",
        "restore-hashes-day-end.txt",
        "HARD_STOP.md",
        "hard-stop-ps.txt",
        "R1_BUDGET.md",
        "TOMORROW.md",
        "FINAL_JURY.md",
        "EVOLUTION_REPORT.md",
        "RERUN.md",
        "clock-stop.txt",
        "採否.md",
        "THROUGHPUT.md",
    ):
        src = RUN_DIR / name
        if src.exists():
            shutil.copy(src, SCRATCH / name)


def main() -> None:
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    if action == "save":
        save()
    elif action == "hard-stop":
        hard_stop()
        copy_scratch()
    else:
        raise SystemExit("usage: day_end.py save|hard-stop")


if __name__ == "__main__":
    main()
