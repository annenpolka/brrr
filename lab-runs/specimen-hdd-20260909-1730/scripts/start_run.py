#!/usr/bin/env python3
"""Initialize specimen-hdd-20260909-1730 after the 17:30 JST gate. No Dreamer call.

A second invocation resumes via hdd.py status and does not re-init the trial.
Does not re-init corpus-hdd-20260909-1130 or specimen-hdd-20260902-1112.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from clock_gate import HARD_END_EXTENDED, HARD_STOP, NOT_BEFORE, PRESERVE_START, apply_compressed_gates, assert_start_allowed, now
from credits import fetch_credits, fetch_r1_pricing, load_env, public_snapshot
from hash_bundle import hash_tree, sha256_file
from jobs import append_job
from paths import (
    ACCOUNT_RESERVE_USD,
    CORPUS_ROOT,
    DAY_MAX_R1_CALLS,
    ENV_FILE,
    EXPORT_REL,
    HDD_PY,
    HDD_ROOT,
    INPUTS_JSON,
    OTHER_RUN_IDS,
    PUBLIC_BUNDLE,
    REPO_ROOT,
    RUN_DIR,
    RUN_ID,
    SNAPSHOT_ID,
    USER_CAP_USD,
)
from r1_budget import compute_effective_cap, rewrite_budget_md, save_ledger

JST = ZoneInfo("Asia/Tokyo")
RECEIPT = REPO_ROOT / "docs/preparation/evidence-pilot-receipt.json"
TRIAL = "case-001-a"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=REPO_ROOT, check=True, text=True, **kwargs)


def already_initialized() -> bool:
    trial = HDD_ROOT / TRIAL
    summary = RUN_DIR / "bootstrap-summary.json"
    return summary.is_file() and trial.is_dir() and (trial / "seed.md").is_file()


def record_slots() -> dict:
    ncpu = os.cpu_count() or 0
    try:
        loadavg = list(os.getloadavg())
    except OSError:
        loadavg = None
    return {
        "recorded_at_jst": now().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "parent_included": True,
        "coordinator_slots": 1,
        "worker_slots_max_plan": 3,
        "r1_concurrency_initial": 1,
        "r1_concurrency_max": 2,
        "day_max_r1_calls": DAY_MAX_R1_CALLS,
        "hw_ncpu": ncpu,
        "loadavg": loadavg,
        "copied_previous_12_worker_floor": False,
        "started_previous_scheduler": False,
        "reinit_1130": False,
        "reinit_20260902": False,
        "note": "Slots observed in this parent session (guide: parent 1 + work 3, R1 concurrent 1). Empty slots are not filled with fabricated cases.",
    }


def write_schedule(started: datetime) -> None:
    compressed = apply_compressed_gates(started)
    write(
        RUN_DIR / "compressed-deadlines.json",
        json.dumps({k: v.strftime("%Y-%m-%d %H:%M:%S %Z") for k, v in compressed.items()}, indent=2) + "\n",
    )
    write(
        RUN_DIR / "SCHEDULE.md",
        f"""# Operator schedule (deadlines, not wait-to-start)

Experiment window: **2026-09-09 17:30 JST → 2026-09-10 09:00 JST**
Start is a not-before gate. Hard end is not extended if start is late.
Actual start: **{started.strftime("%Y-%m-%d %H:%M:%S %Z")}**

| Time (JST) | Target | Main activity |
| --- | --- | --- |
| {compressed["first_packet_dream"].strftime("%H:%M")} | First packet + first Dream | Public bundle → trial → Dream → Red Pen |
| {compressed["redpen_harvest"].strftime("%H:%M")} | Persistent Red Pen + harvest | Same world, not a reset |
| {compressed["first_selection"].strftime("%H:%M")} | First selection | KEEP/MUTATE/KILL when materials exist; may be earlier |
| {compressed["counterexample"].strftime("%H:%M")} | Counterexample | Mature candidates get a 反証 pass |
| {compressed["broad_end"].strftime("%H:%M")} | Broad exploration ends | No new 広い探索 after this deadline |
| {compressed["final_jury"].strftime("%H:%M")} | Final jury materials | 0–2 items allowed |
| 08:00 | 保全 | No new wide exploration. Save 採否/費用/hash/再実行 |
| 09:00 | HARD STOP | This run's hdd.py/dream.sh only. Not 9/2, not lab-hdd/, not 1130 |

Preservation start: **{PRESERVE_START.strftime("%Y-%m-%d %H:%M:%S %Z")}**. Hard end: **{HARD_STOP.strftime("%Y-%m-%d %H:%M:%S %Z")}**. hard_end_extended: no.

Vacant inference slots take the next ready collect/review/reconstitute/refute/implement job. Do not sleep on a clock milestone after 17:30.
""",
    )


def write_seal() -> None:
    write(
        RUN_DIR / "SEAL.md",
        f"""# Contamination seal (this run)

**Status: SEALED {now().strftime("%Y-%m-%d %H:%M:%S %Z")}**

Dreamer-facing materials may receive only the public-bundle copy of snapshot
`{SNAPSHOT_ID}`. Do not pass 原文, PRIVATE審査, 過去run, 正解, 旧候補, collector root,
`.git`, or `docs/execplans/20260909-1730-hdd.md`. Do not pass `unlike runpair` or old candidate names.

`FIRST_SELECTION.md` does **not** disable `scripts/contamination_check.py`.

Host Red Pen and quality/leakage review stay off the Dreamer prompt.
""",
    )


def resume() -> None:
    print(f"already initialized; resume via hdd.py status; not re-initing {TRIAL}", flush=True)
    print("not touching corpus-hdd-20260909-1130", flush=True)
    print("not touching specimen-hdd-20260902-1112", flush=True)
    env = {**os.environ, "HDD_DREAMER_MODEL": "deepseek/deepseek-r1", "HDD_DREAMER_TRANSPORT": "openrouter"}
    status = subprocess.run(
        [sys.executable, str(HDD_PY), "--root", str(HDD_ROOT), "status", "--trial", TRIAL],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        env=env,
    )
    write(RUN_DIR / "resume-status.log", status.stdout + status.stderr)
    print(status.stdout, end="")
    if status.returncode != 0:
        raise SystemExit(f"hdd.py status failed: {status.stderr}")
    summary = {
        "run_id": RUN_ID,
        "resumed": True,
        "reinit_trial": False,
        "reinit_1130": False,
        "reinit_20260902": False,
        "trial": TRIAL,
        "hard_end_jst": HARD_STOP.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_extended": "no",
    }
    print(json.dumps(summary, indent=2), flush=True)


def main(at: datetime | None = None) -> None:
    if already_initialized():
        resume()
        return
    started = assert_start_allowed(at)
    # Create run bookkeeping only after the not-before gate.
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    HDD_ROOT.mkdir(parents=True, exist_ok=True)
    for name in ("dream-logs", "redpen", "seeds", "jobs", "lineages", "inputs"):
        (RUN_DIR / name).mkdir(exist_ok=True)
    (RUN_DIR / "jobs.jsonl").touch(exist_ok=True)
    # Do not create worktrees/ inside the run directory.

    load_env(ENV_FILE)
    os.environ.setdefault("HDD_DREAMER_TRANSPORT", "openrouter")
    os.environ["HDD_DREAMER_MODEL"] = "deepseek/deepseek-r1"

    credits = public_snapshot(fetch_credits())
    available = float(credits["remaining"])
    cap = compute_effective_cap(available, user_cap=USER_CAP_USD, reserve=ACCOUNT_RESERVE_USD)
    pricing = fetch_r1_pricing()
    slots = record_slots()
    apply_compressed_gates(started)

    ledger = {
        "run_id": RUN_ID,
        "hard_cap_usd": USER_CAP_USD,
        "account_reserve_usd": ACCOUNT_RESERVE_USD,
        "user_cap_usd": USER_CAP_USD,
        "day_max_r1_calls": DAY_MAX_R1_CALLS,
        "pricing": {
            "input_usd_per_mtok": pricing["input_usd_per_mtok"],
            "output_usd_per_mtok": pricing["output_usd_per_mtok"],
            "source": pricing["source"],
        },
        "openrouter_snapshot_at_start": credits,
        "effective_cap_usd": cap,
        "effective_cap_reason": (
            f"max(0, min({USER_CAP_USD:.2f} USD user cap, "
            f"available_credit {available:.4f} − {ACCOUNT_RESERVE_USD:.2f} reserve))"
        ),
        "stop_casual_usd": round(0.8 * cap, 6),
        "stop_all_new_r1_usd": cap,
        "in_flight_reserve_usd": 0.0,
        "calls": [],
        "total_calls": 0,
        "estimated_spend_usd": 0.0,
        "observed_spend_usd": 0.0,
        "hard_end_jst": HARD_STOP.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_extended": "no",
        "not_before_jst": NOT_BEFORE.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "preserve_start_jst": PRESERVE_START.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "started_jst": started.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "dreamer_model": "deepseek/deepseek-r1",
        "no_auto_topup": True,
    }
    save_ledger(ledger)
    rewrite_budget_md()
    write(RUN_DIR / "credits-start.json", json.dumps(credits, indent=2) + "\n")
    write(RUN_DIR / "pricing-start.json", json.dumps(pricing, indent=2) + "\n")
    write(RUN_DIR / "slots.json", json.dumps(slots, indent=2) + "\n")
    write_schedule(started)
    write_seal()
    write(
        RUN_DIR / "clock-start.txt",
        "\n".join(
            [
                f"started_jst: {started.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                f"not_before: {NOT_BEFORE.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                f"hard_end: {HARD_STOP.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                "hard_end_extended: no",
                f"effective_cap_usd: {cap}",
                f"remaining_at_start: {available}",
                f"run_id: {RUN_ID}",
            ]
        )
        + "\n",
    )
    write(
        RUN_DIR / "STATE.md",
        f"""# Experiment state

- Run: `{RUN_ID}`
- Start: {started.strftime("%Y-%m-%d %H:%M:%S %Z")}
- Not-before: 2026-09-09 17:30:00 JST
- Hard end: 2026-09-10 09:00:00 JST (not extended)
- Preservation start: 2026-09-10 08:00:00 JST
- Phase: bootstrap (cap and hard stop recorded; no Dream yet)
- Parent role: coordinator only (no candidate product merge onto main)
- Dreamer: `deepseek/deepseek-r1` via OpenRouter through `{HDD_PY}` `--root {HDD_ROOT}`
- Critic: host Red Pen
- Effective R1 cap: **${cap:.4f}** (available ${available:.4f} − $1.50 reserve, user cap $50)
- Isolation: `static_bundle_only` (not OS/network isolation; not 未知性)
- Input scale: starting with 1 discovery case; if still 1 after collect window, this is 小規模試行 and the case is not 未知holdout
- Previous 9/2 wrapper/scheduler: not started
- corpus-hdd-20260909-1130: not re-inited
""",
    )
    write(
        RUN_DIR / "STATUS.md",
        f"""# Status

- run_id: `{RUN_ID}`
- started: {started.strftime("%Y-%m-%d %H:%M:%S %Z")}
- hard_end: 2026-09-10 09:00:00 JST
- hard_end_extended: no
- effective_cap_usd: {cap}
- trial: {TRIAL} (pending init)
- other runs re-inited: no
""",
    )
    write(
        RUN_DIR / "heartbeat.md",
        f"# Heartbeat\n\n- {started.strftime('%Y-%m-%d %H:%M:%S %Z')} bootstrap started\n",
    )
    write(
        RUN_DIR / "scheduler-state.json",
        json.dumps(
            {
                "run_id": RUN_ID,
                "mode": "vacancy",
                "started_jst": started.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "hard_end_jst": HARD_STOP.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "hard_end_extended": False,
                "copied_12_worker_floor": False,
                "idle_sleep_on_clock": False,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        RUN_DIR / "SPECIMEN_INDEX.md",
        f"""# Specimen index

1. snapshot `{SNAPSHOT_ID}` — Deno 32113 public packet. Role: discovery. Not 未知holdout. Scale: 小規模試行 until more PASS inputs exist.
""",
    )

    print("=== check_corpus ===", flush=True)
    check = run([sys.executable, "scripts/check_corpus.py"], capture_output=True)
    write(RUN_DIR / "corpus-check.txt", check.stdout + check.stderr)
    print(check.stdout, end="")

    print("=== corpus audit ===", flush=True)
    audit = run(
        [sys.executable, "scripts/corpus.py", "--root", str(CORPUS_ROOT), "audit"],
        capture_output=True,
    )
    write(RUN_DIR / "corpus-audit.json", audit.stdout)
    if audit.stderr:
        write(RUN_DIR / "corpus-audit.err", audit.stderr)
    print(audit.stdout, end="")
    audit_payload = json.loads(audit.stdout)
    if audit_payload.get("ok") is not True:
        raise SystemExit(f"corpus audit not ok: {audit_payload}")

    print("=== hdd doctor ===", flush=True)
    doctor_env = {**os.environ, "HDD_DREAMER_MODEL": "deepseek/deepseek-r1", "HDD_DREAMER_TRANSPORT": "openrouter"}
    doctor = run([sys.executable, str(HDD_PY), "doctor"], capture_output=True, env=doctor_env)
    write(RUN_DIR / "hdd-doctor.log", doctor.stdout + doctor.stderr)
    print(doctor.stdout, end="")
    if "OPENROUTER_API_KEY: set" not in doctor.stdout:
        raise SystemExit("hdd doctor did not see OPENROUTER_API_KEY")
    if "deepseek/deepseek-r1" not in doctor.stdout:
        raise SystemExit("hdd doctor did not resolve deepseek/deepseek-r1")

    export_dir = REPO_ROOT / EXPORT_REL
    export_dir.parent.mkdir(parents=True, exist_ok=True)
    print("=== corpus export ===", flush=True)
    export_proc = run(
        [
            sys.executable,
            "scripts/corpus.py",
            "--root",
            str(CORPUS_ROOT),
            "export",
            SNAPSHOT_ID,
            "--output",
            str(export_dir),
        ],
        capture_output=True,
    )
    write(RUN_DIR / "export.log", export_proc.stdout + export_proc.stderr)
    print(export_proc.stdout, end="")

    expected = json.loads(RECEIPT.read_text(encoding="utf-8"))["export"]["files"]
    exported_hashes = hash_tree(export_dir)
    if exported_hashes != expected:
        raise SystemExit(
            "export hashes do not match docs/preparation/evidence-pilot-receipt.json; "
            "do not reuse old View reviews. "
            f"expected={expected} got={exported_hashes}"
        )

    if PUBLIC_BUNDLE.exists():
        shutil.rmtree(PUBLIC_BUNDLE)
    shutil.copytree(export_dir, PUBLIC_BUNDLE)
    copy_hashes = hash_tree(PUBLIC_BUNDLE)
    if copy_hashes != exported_hashes:
        raise SystemExit("public-bundle copy hashes drifted from export")

    seed_src = PUBLIC_BUNDLE / "discovery/input-001/seed.md"
    seed_copy = RUN_DIR / "seeds" / "case-001-a.md"
    shutil.copyfile(seed_src, seed_copy)

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    inputs = {
        "run_id": RUN_ID,
        "snapshot_id": SNAPSHOT_ID,
        "case_count": 1,
        "scale": "小規模試行",
        "unknown_holdout_forbidden_for_this_case": True,
        "consumer_receives": "public-bundle copy only",
        "export_dir": str(export_dir),
        "public_bundle_copy": str(PUBLIC_BUNDLE),
        "file_hashes": copy_hashes,
        "tree_hash_receipt": receipt["export"]["tree_hash"],
        "quality_leakage": {
            "view_id": receipt["review"]["view_id"],
            "quality": receipt["review"]["quality"],
            "leakage": receipt["review"]["leakage"],
            "reviewer_type": receipt["review"]["reviewer_type"],
            "human_reviews_created": receipt["review"]["human_reviews_created"],
            "agent_reconfirmed_at_start": False,
        },
        "not_passed_to_consumer": [
            "原文",
            "PRIVATE審査",
            "過去run",
            "正解",
            "旧候補",
            "collector root",
            ".git",
            "docs/execplans/20260909-1730-hdd.md",
            "unlike runpair",
        ],
    }
    write(INPUTS_JSON, json.dumps(inputs, indent=2, ensure_ascii=False) + "\n")

    if not HDD_PY.is_file():
        raise SystemExit(f"hdd.py missing: {HDD_PY}")

    print("=== hdd init case-001-a from public-bundle copy ===", flush=True)
    init = run(
        [
            sys.executable,
            str(HDD_PY),
            "--root",
            str(HDD_ROOT),
            "init",
            "--trial",
            TRIAL,
            "--seed-file",
            str(seed_src),
        ],
        capture_output=True,
        env={**os.environ, "HDD_DREAMER_MODEL": "deepseek/deepseek-r1"},
    )
    write(RUN_DIR / "init-case-001-a.log", init.stdout + init.stderr)
    print(init.stdout, end="")

    trial_bundle = HDD_ROOT / TRIAL / "bundle"
    if trial_bundle.exists():
        shutil.rmtree(trial_bundle)
    shutil.copytree(PUBLIC_BUNDLE / "discovery/input-001", trial_bundle)
    trial_files = {
        "seed.md": trial_bundle / "seed.md",
        "TASK.md": trial_bundle / "TASK.md",
        "OBSERVED.md": trial_bundle / "OBSERVED.md",
        "COMMANDS.md": trial_bundle / "COMMANDS.md",
        "files/a.js": trial_bundle / "files/a.js",
        "files/package.json": trial_bundle / "files/package.json",
    }
    trial_hashes = {rel: sha256_file(path) for rel, path in trial_files.items()}
    expected_short = {
        "seed.md": copy_hashes["discovery/input-001/seed.md"],
        "TASK.md": copy_hashes["discovery/input-001/TASK.md"],
        "OBSERVED.md": copy_hashes["discovery/input-001/OBSERVED.md"],
        "COMMANDS.md": copy_hashes["discovery/input-001/COMMANDS.md"],
        "files/a.js": copy_hashes["discovery/input-001/files/a.js"],
        "files/package.json": copy_hashes["discovery/input-001/files/package.json"],
    }
    if trial_hashes != expected_short:
        raise SystemExit(f"trial bundle hash mismatch: {trial_hashes} vs {expected_short}")

    print("=== preview-dream --check-meta ===", flush=True)
    preview = subprocess.run(
        [
            sys.executable,
            str(HDD_PY),
            "--root",
            str(HDD_ROOT),
            "preview-dream",
            "--trial",
            TRIAL,
            "--check-meta",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        env={**os.environ, "HDD_DREAMER_MODEL": "deepseek/deepseek-r1"},
    )
    write(RUN_DIR / "preview-dream.txt", preview.stdout)
    if preview.returncode != 0:
        write(RUN_DIR / "preview-dream.err", preview.stderr)
        raise SystemExit("preview-dream --check-meta failed")

    print("=== contamination ===", flush=True)
    cont = subprocess.run(
        [sys.executable, str(RUN_DIR / "scripts" / "contamination_check.py")],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    write(RUN_DIR / "contamination-init.txt", cont.stdout + cont.stderr)
    if cont.returncode != 0:
        raise SystemExit(f"contamination hits after init:\n{cont.stdout}\n{cont.stderr}")

    current_link = REPO_ROOT / "lab-runs" / "current"
    if current_link.exists() or current_link.is_symlink():
        if current_link.is_symlink() or current_link.is_file():
            current_link.unlink()
        else:
            raise SystemExit(f"lab-runs/current is a directory, not a symlink: {current_link}")
    current_link.symlink_to(RUN_ID, target_is_directory=True)

    summary = {
        "run_id": RUN_ID,
        "started_jst": started.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_jst": HARD_STOP.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "hard_end_extended": "no",
        "available_credit": available,
        "account_reserve_usd": ACCOUNT_RESERVE_USD,
        "user_cap_usd": USER_CAP_USD,
        "effective_cap_usd": cap,
        "snapshot_id": SNAPSHOT_ID,
        "file_hashes": copy_hashes,
        "trial": TRIAL,
        "preview_dream_check_meta_exit": 0,
        "contamination_hits": 0,
        "slots": slots,
        "dreamer_model": "deepseek/deepseek-r1",
        "r1_available_in_model_list": pricing.get("available"),
        "dream_started": False,
        "reinit_1130": False,
        "reinit_20260902": False,
        "lab_runs_current": RUN_ID,
    }
    write(RUN_DIR / "bootstrap-summary.json", json.dumps(summary, indent=2) + "\n")
    append_job(
        {
            "job": "bootstrap",
            "trial": TRIAL,
            "status": "completed",
            "slot": "coordinator",
            "note": "init+export+preview-dream; no Dream yet; 1130/9/2 not re-inited",
            "intentional_idle": False,
        }
    )
    print(json.dumps(summary, indent=2))
    print("bootstrap complete; cap and hard stop recorded; no Dream yet", flush=True)
    print(f"other runs not re-inited: {OTHER_RUN_IDS}", flush=True)


if __name__ == "__main__":
    main()
