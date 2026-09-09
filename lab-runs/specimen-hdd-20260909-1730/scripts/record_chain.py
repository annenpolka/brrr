#!/usr/bin/env python3
"""Record snapshot -> hashes -> trial -> dream -> redpen chain. HTTP success is not tool success."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from hash_bundle import hash_tree
from paths import HDD_ROOT, INPUTS_JSON, PUBLIC_BUNDLE, RUN_DIR, SNAPSHOT_ID


def main() -> None:
    trial = sys.argv[1] if len(sys.argv) > 1 else "case-001-a"
    iteration = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    inputs = json.loads(INPUTS_JSON.read_text(encoding="utf-8"))
    hashes = hash_tree(PUBLIC_BUNDLE)
    ws = HDD_ROOT / trial
    dream = ws / "iterations" / f"{iteration:04d}-dreamer.md"
    redpen = ws / "iterations" / f"{iteration:04d}-redpen.json"
    host_redpen = RUN_DIR / "redpen" / f"{trial}-{iteration:04d}.json"
    ledger = json.loads((RUN_DIR / "r1-ledger.json").read_text(encoding="utf-8"))
    call = None
    for row in reversed(ledger.get("calls") or []):
        if row.get("trial") == trial and row.get("iteration") == iteration:
            call = row
            break
    http_success = bool(call and call.get("http_success"))
    tool_success = False
    chain = {
        "chain": "snapshot_id -> file_hashes -> public_bundle_copy -> trial -> dream -> redpen",
        "snapshot_id": SNAPSHOT_ID,
        "file_hashes": hashes,
        "public_bundle_copy": str(PUBLIC_BUNDLE.relative_to(PUBLIC_BUNDLE.parents[2])),
        "trial": trial,
        "hdd_workspace": str(ws.relative_to(ws.parents[2])),
        "dream": {
            "iteration": iteration,
            "model": "deepseek/deepseek-r1",
            "transport": "openrouter",
            "path": str(dream) if dream.is_file() else None,
            "exists": dream.is_file(),
            "bytes": dream.stat().st_size if dream.is_file() else 0,
            "started_jst": (call or {}).get("at_jst"),
            "ended_jst": (call or {}).get("ended_jst"),
            "http_success": http_success,
            "tool_success": tool_success,
            "note": "R1 HTTP success is design material, not tool success.",
        },
        "redpen": {
            "host": True,
            "path": str(host_redpen) if host_redpen.is_file() else None,
            "recorded": str(redpen) if redpen.is_file() else None,
        },
        "consumer_did_not_receive": inputs.get("not_passed_to_consumer"),
        "scale": inputs.get("scale"),
        "unknown_holdout": False,
    }
    out = RUN_DIR / f"CHAIN-{iteration:03d}.json"
    out.write_text(json.dumps(chain, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
