#!/usr/bin/env python3
"""Run-local path resolution. Defaults follow this script's location."""
from __future__ import annotations

import os
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
RUN_DIR = Path(os.environ.get("BRRR_RUN_DIR", SCRIPTS_DIR.parent)).resolve()
RUN_ID = os.environ.get("BRRR_RUN_ID", RUN_DIR.name)
REPO_ROOT = Path(os.environ.get("BRRR_REPO_ROOT", RUN_DIR.parent.parent)).resolve()
HDD_ROOT = Path(os.environ.get("BRRR_HDD_ROOT", REPO_ROOT / ".hdd-runs" / RUN_ID)).resolve()
HDD_PY = Path(
    os.environ.get(
        "HDD_PY",
        Path.home() / "ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py",
    )
)
ENV_FILE = REPO_ROOT / ".env.hdd"
LEDGER_JSON = RUN_DIR / "r1-ledger.json"
LEDGER_JSONL = RUN_DIR / "r1-ledger.jsonl"
BUDGET_MD = RUN_DIR / "R1_BUDGET.md"
SCHEDULER_STATE = RUN_DIR / "scheduler-state.json"
JOBS_JSONL = RUN_DIR / "jobs.jsonl"
SEAL = RUN_DIR / "SEAL.md"
FIRST_SELECTION = RUN_DIR / "FIRST_SELECTION.md"
SPECIMENS = RUN_DIR / "specimens"
SEEDS = RUN_DIR / "seeds"
WATCHDOG_DIR = RUN_DIR / "watchdog"

QUEUES = (
    "READY_SPECIMEN_SCOUT",
    "READY_SPECIMEN_REPRODUCE",
    "READY_SPECIMEN_COMPRESS",
    "READY_SPECIMEN_MUTATE",
    "READY_SPECIMEN_CURATE",
    "READY_R1_DREAM",
    "READY_RED_PEN",
    "READY_COUNTEREXAMPLE",
    "READY_HARVEST",
    "READY_GROUND",
    "READY_IMPLEMENT",
    "READY_DOGFOOD",
    "READY_DESTROY",
    "READY_MUTATE",
    "READY_REIMPLEMENT",
    "READY_HYBRID",
    "READY_JUDGE",
    "READY_PRESERVE",
)

HISTORICAL_ISOLATION_FILES = (
    "EVOLUTION_REPORT.md",
    "HDD_EVOLUTION_REPORT.md",
    "lab/STATE.md",
    "lab-hdd/STATE.md",
    "lab-hdd/SEAL.md",
)
