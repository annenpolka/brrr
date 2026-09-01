#!/usr/bin/env python3
"""Initialize independent HDD trials from lab-hdd/seeds without overwriting existing ones."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
HDD = ROOT / ".hdd"
SEEDS = ROOT / "lab-hdd" / "seeds"
HDD_PY = Path.home() / "ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py"
JST = ZoneInfo("Asia/Tokyo")

# Keep unfamiliar-cli as the already-initialized canonical trial.
TRIALS = [
    ("unfamiliar-cli", "unfamiliar-cli.md"),
    ("hdd-debug", "hdd-debug.md"),
    ("hdd-test", "hdd-test.md"),
    ("hdd-review", "hdd-review.md"),
    ("hdd-history", "hdd-history.md"),
    ("hdd-build", "hdd-build.md"),
    ("hdd-log", "hdd-log.md"),
    ("hdd-config", "hdd-config.md"),
    ("hdd-merge", "hdd-merge.md"),
    ("hdd-perf", "hdd-perf.md"),
    ("hdd-type", "hdd-type.md"),
    ("hdd-ci", "hdd-ci.md"),
    ("hdd-docs", "hdd-docs.md"),
    ("hdd-patch", "hdd-patch.md"),
    ("hdd-env", "hdd-env.md"),
    ("hdd-agent", "hdd-agent.md"),
]


def main() -> None:
    created = []
    skipped = []
    for trial, seed_name in TRIALS:
        seed = SEEDS / seed_name
        if not seed.exists():
            raise SystemExit(f"missing seed {seed}")
        ws = HDD / trial
        if ws.exists() and any(ws.iterdir()):
            skipped.append(trial)
            continue
        subprocess.run(
            [
                sys.executable,
                str(HDD_PY),
                "--root",
                str(HDD),
                "init",
                "--trial",
                trial,
                "--seed-file",
                str(seed),
            ],
            check=True,
        )
        created.append(trial)

    pop = {
        "at_jst": datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "trials": [
            {
                "trial": trial,
                "seed_file": f"lab-hdd/seeds/{seed}",
                "workspace": f".hdd/{trial}",
                "initialized_before": trial in skipped,
                "stage": "seeded",
                "decision": None,
                "dreams": 0,
            }
            for trial, seed in TRIALS
        ],
        "created_this_run": created,
        "already_present": skipped,
    }
    out = ROOT / "lab-hdd" / "POPULATION.json"
    out.write_text(json.dumps(pop, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"created": created, "skipped": skipped, "population": str(out)}, indent=2))


if __name__ == "__main__":
    main()
