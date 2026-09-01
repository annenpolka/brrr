#!/usr/bin/env python3
"""Record a coordinator decision for a trial after Red Pen."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
POP = ROOT / "lab-hdd" / "POPULATION.json"
JST = ZoneInfo("Asia/Tokyo")
ALLOWED = {"CONTINUE_DREAMING", "HARVEST_NOW", "KILL", "PARK_WEIRD"}


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: set_decision.py <trial> <DECISION> [note...]")
    trial = sys.argv[1]
    decision = sys.argv[2].strip().upper()
    if decision not in ALLOWED:
        raise SystemExit(f"decision must be one of {sorted(ALLOWED)}")
    note = " ".join(sys.argv[3:])
    pop = json.loads(POP.read_text(encoding="utf-8"))
    found = False
    for row in pop["trials"]:
        if row["trial"] == trial:
            row["decision"] = decision
            row["decision_at_jst"] = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S %Z")
            row["decision_note"] = note
            if decision == "KILL":
                row["stage"] = "killed"
            elif decision == "PARK_WEIRD":
                row["stage"] = "parked"
            elif decision == "HARVEST_NOW":
                row["stage"] = "harvest"
            elif decision == "CONTINUE_DREAMING":
                row["stage"] = "deepen"
            found = True
            break
    if not found:
        pop.setdefault("trials", []).append(
            {
                "trial": trial,
                "seed_file": f"lab-hdd/seeds/{trial}.md",
                "workspace": f".hdd/{trial}",
                "initialized_before": False,
                "stage": "seeded",
                "decision": None,
                "dreams": 0,
            }
        )
        for row in pop["trials"]:
            if row["trial"] == trial:
                row["decision"] = decision
                row["decision_at_jst"] = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S %Z")
                row["decision_note"] = note
                if decision == "KILL":
                    row["stage"] = "killed"
                elif decision == "PARK_WEIRD":
                    row["stage"] = "parked"
                elif decision == "HARVEST_NOW":
                    row["stage"] = "harvest"
                elif decision == "CONTINUE_DREAMING":
                    row["stage"] = "deepen"
                found = True
                break
    POP.write_text(json.dumps(pop, indent=2) + "\n", encoding="utf-8")
    dest = ROOT / "lab-hdd" / "lineages" / trial
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "DECISION.md").write_text(
        f"# {trial}\n\nDECISION: {decision}\n\n{note}\n\nAt: {datetime.now(JST)}\n",
        encoding="utf-8",
    )
    print(f"{trial}: {decision}")


if __name__ == "__main__":
    main()
