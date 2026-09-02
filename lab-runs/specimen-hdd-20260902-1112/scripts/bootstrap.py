#!/usr/bin/env python3
"""Initialize run coordinator state after scripts exist. Does not touch lab-hdd/ or .hdd/."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from credits import fetch_credits, public_snapshot
from isolation_hash import render, snapshot
from paths import (
    BUDGET_MD,
    ENV_FILE,
    HDD_PY,
    HDD_ROOT,
    LEDGER_JSON,
    LEDGER_JSONL,
    REPO_ROOT,
    RUN_DIR,
    RUN_ID,
    SCHEDULER_STATE,
)
from r1_budget import rewrite_budget_md, save_ledger
from scheduler import QUEUES, empty_state, enqueue, now_jst, render_status, save_state

JST = ZoneInfo("Asia/Tokyo")
ACCOUNT_RESERVE_USD = 1.50
R1_HARD_CAP_USD = 50.00

INITIAL_SCOUT_JOBS = [
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: order-dependent tests / leaked global state",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: test-order",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: env/config precedence empty-vs-unset",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: config-precedence",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: cache invalidation / stale fingerprint",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: cache",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: identity move/rename/split/duplicate",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: identity",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: concurrency/race in tests or runtime",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: race",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: merge/history edge / partial hybrid",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: history",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: CI-only or platform-specific failure",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: ci-only",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: generated-code drift or stale docs/tests",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: generated-drift",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: pipeline/process / ambiguous no-result",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: process-semantics",
        "kill": "no public pinned source in 25m",
    },
    {
        "queue": "READY_SPECIMEN_SCOUT",
        "input": "public OSS: serialization/format boundary failure",
        "expected": "pinned source packet with sealed answer-key",
        "reason": "mechanism diversity: format-boundary",
        "kill": "no public pinned source in 25m",
    },
]


def copy_constitution() -> None:
    src = REPO_ROOT / "brrr-hdd-specimen-continuous-master-prompt.md"
    dest = RUN_DIR / "CONSTITUTION.md"
    shutil.copyfile(src, dest)


def write_seal() -> None:
    (RUN_DIR / "SEAL.md").write_text(
        f"""# Previous-brrr / previous-HDD contamination seal

**Status: SEALED {now_jst()}**

Until `{RUN_DIR.relative_to(REPO_ROOT)}/FIRST_SELECTION.md` exists and names multiple
real-embodiment survivors, workers MUST NOT read or quote:

- `EVOLUTION_REPORT.md`
- `HDD_EVOLUTION_REPORT.md`
- `lab/EMERGING.md`
- `lab/lineages/`
- `lab/judges/`
- `lab-hdd/lineages/`
- `lab-hdd/judges/`
- `lab-hdd/FIRST_SELECTION.md`
- `lab-hdd/PRIOR_RUN_COMPARISON.md`
- previous candidate descriptions or Tomorrow-Test binaries
- previous master prompts (except this run's `CONSTITUTION.md`)

Do not steer seeds with phrases such as “invent something unlike <prior name>”.

Independent rediscovery of a similar primitive is allowed. Prior-art comparison
happens only after First Selection.

Coordinator may hash historical files for isolation without using their contents
to steer affordance generation.

Sealed at: {now_jst()}
Unlocks at: First Selection complete (deadline 2026-09-02 15:30 JST, earlier if ready).
""",
        encoding="utf-8",
    )


def write_schedule() -> None:
    (RUN_DIR / "SCHEDULE.md").write_text(
        """# Operator schedule (deadlines, not not-before gates)

Experiment window: **2026-09-02 11:30 JST → 2026-09-03 00:00 JST**
This run started immediately at bootstrap (no 11:30 not-before gate).

| Time | Target | Main activity |
| --- | --- | --- |
| 11:30–12:00 | Bootstrap | Validate HDD/R1 transport, coordinator state, specimen scouts |
| 12:00–14:00 | Specimen-driven Cambrian | Real OSS mining, R1 Dreams, early Red Pen |
| 14:00–15:30 | Deepen + Reality Gate + Embodiment | 2nd–5th turns, counterexamples, Grounders |
| by 15:30 | First Selection | Blind judges on real embodiments; then unseal prior art |
| 15:30–19:00 | Continuous Generation 2 | Mutations, clean-room, hybrids, HDD jumps |
| by 17:00 | Destroyer coverage | Every mature implementation has an adversarial worker |
| 19:00–21:30 | Heavy empirical pressure | Destroyers, transfer, kills, competing implementations |
| 21:30–22:45 | Exploitation | Concentrate on strongest survivors |
| by 22:45 | Broad exploration ends | No new broad Cambrian lineages |
| 22:45–23:25 | Final Jury | Unix / Toolsmith / Heretic / Skeptic / Reality-Stripped + Tomorrow Test |
| 23:25–00:00 | Preservation | Final report, audits, HARD STOP prep |
| 00:00 | HARD STOP | Stop spawning |

Preservation start for this run: **2026-09-02 23:25 JST** (operator table, not HARD_END−60m).
""",
        encoding="utf-8",
    )


def write_worker_rules() -> None:
    (RUN_DIR / "WORKER_RULES.md").write_text(
        f"""# Worker rules (this run)

## Parent tree

The parent working tree is coordinator/reporting-only.

- Do not merge candidate product code onto `main`.
- Do not edit historical `EVOLUTION_REPORT.md`, `HDD_EVOLUTION_REPORT.md`, `lab/`, `lab-hdd/`, `.hdd/`.
- New coordinator state lives under `lab-runs/{RUN_ID}/`.
- Raw HDD trials live under `.hdd-runs/{RUN_ID}/`.
- Candidate implementations live in isolated git worktrees, then are archived under `lineages/`.

## Contamination (until First Selection exists)

Do not read sealed materials listed in `SEAL.md`.
Do not mention previous-run tool names as things to avoid.

## Dreamer channel

```bash
{RUN_DIR}/scripts/dream.sh <trial> <phase>
```

Uses `python3 {HDD_PY} --root {HDD_ROOT}`. Diegetic prompts only.

## Red Pen

Host writes JSON and records it with `scripts/record_redpen.sh`. After every critique choose exactly one:

```
CONTINUE_WITH_TEXT_PRESSURE
CONTINUE_WITH_COUNTEREXAMPLE
HARVEST_NOW
KILL
PARK_WEIRD
```

Do not send THIN_WRAPPER / NO_SURVIVOR back to R1 with “make this more novel”.

## Evidence boundary

Dreamer text is fictional design material. It is never execution evidence.
""",
        encoding="utf-8",
    )


def effective_cap(remaining: float) -> tuple[float, str]:
    usable = max(0.0, remaining - ACCOUNT_RESERVE_USD)
    cap = min(R1_HARD_CAP_USD, usable)
    reason = (
        f"min(${R1_HARD_CAP_USD:.2f} experiment cap, OpenRouter remaining ${remaining:.4f} "
        f"minus ${ACCOUNT_RESERVE_USD:.2f} account reserve)"
    )
    return cap, reason


def init_ledger(snap: dict) -> dict:
    remaining = float(snap["remaining"])
    cap, reason = effective_cap(remaining)
    ledger = {
        "run_id": RUN_ID,
        "hard_cap_usd": R1_HARD_CAP_USD,
        "account_reserve_usd": ACCOUNT_RESERVE_USD,
        "pricing": {
            "input_usd_per_mtok": 0.7,
            "output_usd_per_mtok": 2.5,
            "source": "OpenRouter list price for deepseek/deepseek-r1; used only when generation usage metadata is missing",
        },
        "openrouter_snapshot_at_start": snap,
        "openrouter_snapshot_2": snap,
        "effective_cap_usd": cap,
        "effective_cap_reason": reason,
        "stop_casual_usd": round(0.8 * cap, 4),
        "stop_all_new_r1_usd": cap,
        "calls": [],
        "total_calls": 0,
        "estimated_spend_usd": 0.0,
        "reported_spend_usd": 0.0,
    }
    save_ledger(ledger)
    LEDGER_JSONL.write_text("", encoding="utf-8")
    rewrite_budget_md()
    return ledger


def init_scheduler(ledger: dict) -> dict:
    state = empty_state()
    state["r1_budget"] = {
        "effective_cap_usd": ledger["effective_cap_usd"],
        "hard_cap_usd": ledger["hard_cap_usd"],
        "remaining_at_start": ledger["openrouter_snapshot_at_start"]["remaining"],
    }
    for spec in INITIAL_SCOUT_JOBS:
        enqueue(
            state,
            spec["queue"],
            input_ref=spec["input"],
            expected_output=spec["expected"],
            kill_condition=spec["kill"],
            priority_reason=spec["reason"],
        )
    save_state(state)
    (RUN_DIR / "STATUS.md").write_text(render_status(state), encoding="utf-8")
    (RUN_DIR / "STATE.md").write_text(
        f"""# Experiment state

- Run: `{RUN_ID}`
- Start: {state['start']}
- Hard end: {state['hard_end']}
- Preservation start: {state['preservation_start']}
- Clock: {now_jst()}
- Phase: **RUNNING** (no not-before gates)
- Parent role: coordinator only
- Previous brrr/HDD: **SEALED** (`SEAL.md`) until First Selection
- HDD transport: DeepSeek R1 via OpenRouter through `hdd.py --root {HDD_ROOT}`
- Critic transport: host/manual Red Pen
- Effective R1 cap: **${ledger['effective_cap_usd']:.2f}** ({ledger['effective_cap_reason']})

## Active workers

Bootstrap. Specimen scouts READY.

## Notes

- Do not merge candidate product code onto `main`.
- Do not edit historical reports, `lab/`, `lab-hdd/`, or `.hdd/`.
- Product lives in isolated worktrees; archives under `lineages/`.
""",
        encoding="utf-8",
    )
    (RUN_DIR / "heartbeat.md").write_text(
        f"# Heartbeat\n\n- {now_jst()} bootstrap complete. ready_jobs={len(state['ready_jobs'])}\n",
        encoding="utf-8",
    )
    (RUN_DIR / "INCIDENTS.md").write_text("# Incidents\n\n(none yet)\n", encoding="utf-8")
    (RUN_DIR / "SPECIMEN_INDEX.md").write_text("# Specimen index\n\n(none yet)\n", encoding="utf-8")
    (RUN_DIR / "CONVERGENCE.md").write_text("# Convergence\n\n(none yet; prior art sealed)\n", encoding="utf-8")
    (RUN_DIR / "THROUGHPUT.md").write_text("# Throughput\n\nBootstrap.\n", encoding="utf-8")
    return state


def link_current() -> None:
    current = REPO_ROOT / "lab-runs" / "current"
    if current.is_symlink() or current.exists():
        current.unlink()
    os.symlink(RUN_ID, current)


def run_doctor(log_path: Path) -> str:
    env = os.environ.copy()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env.setdefault(key.strip(), value.strip().strip("'").strip('"'))
    HDD_ROOT.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(HDD_PY), "--root", str(HDD_ROOT), "doctor"]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    header = (
        f"command: {' '.join(cmd)}\n"
        f"HDD_PY={HDD_PY}\n"
        f"HDD_ROOT={HDD_ROOT}\n"
        f"rc={proc.returncode}\n\n"
    )
    text = header + proc.stdout + (("\n" + proc.stderr) if proc.stderr else "")
    log_path.write_text(text, encoding="utf-8")
    if proc.returncode != 0:
        raise SystemExit(f"hdd.py doctor failed rc={proc.returncode}\n{text}")
    return text


def main() -> None:
    scratch = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    copy_constitution()
    write_seal()
    write_schedule()
    write_worker_rules()
    hashes = snapshot()
    isolation_text = render(hashes, "bootstrap")
    (RUN_DIR / "isolation-before.txt").write_text(isolation_text, encoding="utf-8")
    if scratch:
        (scratch / "isolation-before.txt").write_text(
            f"at_jst={now_jst()}\nRUN_ID={RUN_ID}\n"
            + "\n".join(f"{k} {v}" for k, v in hashes.items())
            + "\n",
            encoding="utf-8",
        )
    snap1 = public_snapshot(fetch_credits())
    snap2 = public_snapshot(fetch_credits())
    if scratch:
        (scratch / "credits-1.json").write_text(json.dumps(snap1, indent=2) + "\n", encoding="utf-8")
        (scratch / "credits-2.json").write_text(json.dumps(snap2, indent=2) + "\n", encoding="utf-8")
    (RUN_DIR / "credits-start-1.json").write_text(json.dumps(snap1, indent=2) + "\n", encoding="utf-8")
    (RUN_DIR / "credits-start-2.json").write_text(json.dumps(snap2, indent=2) + "\n", encoding="utf-8")
    ledger = init_ledger(snap1)
    ledger["openrouter_snapshot_2"] = snap2
    save_ledger(ledger)
    rewrite_budget_md()
    doctor1 = run_doctor((scratch / "hdd-doctor-1.log") if scratch else (RUN_DIR / "hdd-doctor-1.log"))
    doctor2 = run_doctor((scratch / "hdd-doctor-2.log") if scratch else (RUN_DIR / "hdd-doctor-2.log"))
    (RUN_DIR / "hdd-doctor-1.log").write_text(doctor1, encoding="utf-8")
    (RUN_DIR / "hdd-doctor-2.log").write_text(doctor2, encoding="utf-8")
    state = init_scheduler(ledger)
    link_current()
    summary = {
        "run_id": RUN_ID,
        "run_dir": str(RUN_DIR),
        "hdd_root": str(HDD_ROOT),
        "effective_cap_usd": ledger["effective_cap_usd"],
        "openrouter_remaining": snap1["remaining"],
        "ready_jobs": len(state["ready_jobs"]),
        "queues": QUEUES,
        "doctor_dreamer_ok": "openrouter" in doctor1.lower() or "deepseek" in doctor1.lower(),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
