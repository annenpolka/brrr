#!/usr/bin/env python3
"""Run-local path resolution for corpus-hdd-20260909-1130. Defaults follow this script."""
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
        Path.home() / ".codex/skills/hdd-loop/scripts/hdd.py",
    )
)
ENV_FILE = REPO_ROOT / ".env.hdd"
LEDGER_JSON = RUN_DIR / "r1-ledger.json"
LEDGER_JSONL = RUN_DIR / "r1-ledger.jsonl"
BUDGET_MD = RUN_DIR / "R1_BUDGET.md"
JOBS_JSONL = RUN_DIR / "jobs.jsonl"
INPUTS_JSON = RUN_DIR / "INPUTS.json"
PUBLIC_BUNDLE = RUN_DIR / "inputs" / "case-001"
SNAPSHOT_ID = "bd49baaa36b6999fdf9e44cf38da470c57c5f9daa6ce291e89c9084c3cce5a81"
EXPORT_REL = Path(".brrr-corpus/mini-followup/exports/reported-discovery-v1")
CORPUS_ROOT = REPO_ROOT / ".brrr-corpus" / "mini-followup"
USER_CAP_USD = 30.00
ACCOUNT_RESERVE_USD = 1.50
DAY_MAX_R1_CALLS = 40
R1_CONCURRENCY_INITIAL = 1
R1_CONCURRENCY_MAX = 2
