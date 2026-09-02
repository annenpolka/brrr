#!/usr/bin/env python3
"""Write a sealed specimen packet. Answer-key files are never mixed into TASK/OBSERVED."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from paths import RUN_DIR, SPECIMENS


def emit(packet: dict) -> Path:
    spec_id = packet["id"]
    dest = SPECIMENS / spec_id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "answer-key").mkdir(exist_ok=True)
    (dest / "files").mkdir(exist_ok=True)
    (dest / "raw-sources").mkdir(exist_ok=True)
    (dest / "manifest.yaml").write_text(packet["manifest"].rstrip() + "\n", encoding="utf-8")
    (dest / "TASK.md").write_text(packet["task"].rstrip() + "\n", encoding="utf-8")
    (dest / "OBSERVED.md").write_text(packet["observed"].rstrip() + "\n", encoding="utf-8")
    (dest / "COMMANDS.md").write_text(packet["commands"].rstrip() + "\n", encoding="utf-8")
    (dest / "TREE.txt").write_text(packet.get("tree", "").rstrip() + "\n", encoding="utf-8")
    (dest / "curation.md").write_text(packet.get("curation", "ACCEPT_R1\n").rstrip() + "\n", encoding="utf-8")
    (dest / "answer-key" / "FIX.md").write_text(packet["answer_key"].rstrip() + "\n", encoding="utf-8")
    (dest / "raw-sources" / "SOURCE.md").write_text(packet["source"].rstrip() + "\n", encoding="utf-8")
    for rel, content in (packet.get("files") or {}).items():
        path = dest / "files" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
    (dest / "packet.json").write_text(
        json.dumps({k: v for k, v in packet.items() if k != "files"}, indent=2) + "\n",
        encoding="utf-8",
    )
    return dest


def main() -> None:
    raise SystemExit("import emit() from a driver")


if __name__ == "__main__":
    main()
