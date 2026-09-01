#!/usr/bin/env python3
"""Print HDD trial slot status for the heartbeat."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HDD = ROOT / ".hdd"


def ledger(trial: Path) -> dict:
    path = trial / "ledger.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    rows = []
    for trial in sorted(p for p in HDD.iterdir() if p.is_dir() and not p.is_symlink()):
        led = ledger(trial)
        pending = led.get("pending") or {}
        dreams = list((trial / "iterations").glob("*-dreamer.md")) if (trial / "iterations").exists() else []
        redpens = list((trial / "iterations").glob("*-redpen.json")) if (trial / "iterations").exists() else []
        assessment = (led.get("affordance_assessment") or {}).get("classification")
        rows.append(
            {
                "trial": trial.name,
                "iteration": led.get("iteration", 0),
                "pending_stage": pending.get("stage"),
                "dreams": len(dreams),
                "redpens": len(redpens),
                "assessment": assessment,
            }
        )
    print(json.dumps(rows, indent=2))
    pending_redpen = [r["trial"] for r in rows if r["pending_stage"] == "redpen"]
    ready_dream = [r["trial"] for r in rows if not r["pending_stage"] and r["dreams"] == 0]
    print("\n# pending Red Pen:", ", ".join(pending_redpen) or "(none)")
    print("# never dreamed:", ", ".join(ready_dream) or "(none)")


if __name__ == "__main__":
    main()
