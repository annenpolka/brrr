#!/usr/bin/env python3
"""Fail if pre-selection Dreamer materials paste previous-brrr reports or anti-steering."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HDD = ROOT / ".hdd"
SEAL = ROOT / "lab-hdd" / "SEAL.md"

FORBIDDEN_PHRASES = (
    "unlike invert",
    "unlike zanei",
    "unlike held",
    "unlike when",
    "evolution_report.md",
    "lab/emerging.md",
    "lab/lineages",
    "lab/judges",
    "overnight developer tool evolution lab — master prompt",
)

# Strong previous-run names only as contamination if used as "don't invent X"
ANTI_STEER_NAMES = (
    "invert",
    "zanei",
    "held",
    "unfmt",
    "wisp",
    "reverb",
    "haunt",
)


def scan_text(path: Path, text: str) -> list[str]:
    hits = []
    lower = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lower:
            hits.append(f"{path}: phrase {phrase!r}")
    for name in ANTI_STEER_NAMES:
        if f"unlike {name}" in lower or f"not like {name}" in lower:
            hits.append(f"{path}: anti-steer {name!r}")
    return hits


def main() -> None:
    hits: list[str] = []
    first_sel = ROOT / "lab-hdd" / "FIRST_SELECTION.md"
    if first_sel.exists():
        print("First Selection on disk; contamination gate relaxed.")
        return
    for trial in sorted(p for p in HDD.iterdir() if p.is_dir() and p.name != "current"):
        for rel in ("seed.md", "human-pressure.md"):
            path = trial / rel
            if path.exists():
                hits.extend(scan_text(path, path.read_text(encoding="utf-8", errors="replace")))
        outbox = trial / "outbox"
        if outbox.exists():
            for path in outbox.glob("*-dreamer-prompt.md"):
                hits.extend(scan_text(path, path.read_text(encoding="utf-8", errors="replace")))
    seeds = ROOT / "lab-hdd" / "seeds"
    if seeds.exists():
        for path in seeds.glob("*.md"):
            hits.extend(scan_text(path, path.read_text(encoding="utf-8", errors="replace")))
    if hits:
        print("CONTAMINATION HITS:")
        print("\n".join(hits))
        sys.exit(2)
    print("contamination check: clean (pre-First-Selection)")


if __name__ == "__main__":
    main()
