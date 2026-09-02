#!/usr/bin/env python3
"""Fail if Dreamer-facing materials leak prior-run anti-steer or unsealed answer keys.

Scans only Dreamer-facing surfaces (seeds, outbox prompts, TASK.md / OBSERVED.md /
COMMANDS.md / seed.md). Answer keys stay sealed and are used as a leak oracle.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from paths import FIRST_SELECTION, HDD_ROOT, RUN_DIR, SEEDS, SPECIMENS

FORBIDDEN_PHRASES = (
    "unlike invert",
    "unlike zanei",
    "unlike held",
    "unlike when",
    "unlike whence",
    "unlike envfrom",
    "unlike flowtrace",
    "evolution_report.md",
    "hdd_evolution_report.md",
    "lab/emerging.md",
    "lab/lineages",
    "lab/judges",
    "lab-hdd/lineages",
    "lab-hdd/judges",
    "overnight developer tool evolution lab — master prompt",
    "brrr × hdd loop — overnight",
)

ANTI_STEER_NAMES = (
    "invert",
    "zanei",
    "held",
    "unfmt",
    "wisp",
    "reverb",
    "haunt",
    "whence",
    "envfrom",
    "capdiff",
    "stated",
    "owes",
    "hits",
    "flowtrace",
)

DREAMER_FACING_NAMES = (
    "TASK.md",
    "OBSERVED.md",
    "COMMANDS.md",
    "TREE.txt",
    "seed.md",
    "DREAMER.md",
    "curation.md",
)

ANSWER_KEY_MIN_LEN = 40


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


def _significant_answer_key_spans(text: str) -> list[str]:
    spans = []
    for raw in text.splitlines():
        line = raw.strip()
        if len(line) < ANSWER_KEY_MIN_LEN:
            continue
        if line.startswith("#") or line.startswith("---"):
            continue
        spans.append(line)
    return spans


def collect_answer_key_spans(specimens_dir: Path) -> dict[Path, list[str]]:
    out: dict[Path, list[str]] = {}
    if not specimens_dir.exists():
        return out
    for key_dir in specimens_dir.glob("*/answer-key"):
        spans: list[str] = []
        for path in key_dir.rglob("*"):
            if path.is_file():
                spans.extend(
                    _significant_answer_key_spans(
                        path.read_text(encoding="utf-8", errors="replace")
                    )
                )
        if spans:
            out[key_dir.parent] = spans
    return out


def scan_answer_key_leak(path: Path, text: str, spans: list[str]) -> list[str]:
    hits = []
    for span in spans:
        if span and span in text:
            hits.append(f"{path}: answer-key leak {span[:80]!r}")
    return hits


def dreamer_facing_files(run_dir: Path, hdd_root: Path) -> list[Path]:
    files: list[Path] = []
    seeds = run_dir / "seeds"
    if seeds.exists():
        files.extend(p for p in seeds.rglob("*") if p.is_file())
    specimens = run_dir / "specimens"
    if specimens.exists():
        for spec in specimens.iterdir():
            if not spec.is_dir():
                continue
            for name in DREAMER_FACING_NAMES:
                path = spec / name
                if path.exists():
                    files.append(path)
            files_dir = spec / "files"
            if files_dir.exists():
                files.extend(p for p in files_dir.rglob("*") if p.is_file())
    if hdd_root.exists():
        for trial in hdd_root.iterdir():
            if not trial.is_dir() or trial.name == "current" or trial.is_symlink():
                continue
            for rel in ("seed.md", "human-pressure.md"):
                path = trial / rel
                if path.exists():
                    files.append(path)
            outbox = trial / "outbox"
            if outbox.exists():
                files.extend(outbox.glob("*-dreamer-prompt.md"))
    return files


def check(
    run_dir: Path | None = None,
    hdd_root: Path | None = None,
    first_selection: Path | None = None,
) -> list[str]:
    run_dir = run_dir or RUN_DIR
    hdd_root = hdd_root or HDD_ROOT
    first_selection = first_selection or (run_dir / "FIRST_SELECTION.md")
    if first_selection.exists():
        return []
    hits: list[str] = []
    answer_keys = collect_answer_key_spans(run_dir / "specimens")
    for path in dreamer_facing_files(run_dir, hdd_root):
        text = path.read_text(encoding="utf-8", errors="replace")
        hits.extend(scan_text(path, text))
        # Leak oracle: if this file sits inside a specimen, only that specimen's key.
        specimen_root = None
        try:
            rel = path.relative_to(run_dir / "specimens")
            specimen_root = (run_dir / "specimens" / rel.parts[0]) if rel.parts else None
        except ValueError:
            specimen_root = None
        if specimen_root and specimen_root in answer_keys:
            hits.extend(scan_answer_key_leak(path, text, answer_keys[specimen_root]))
        elif specimen_root is None:
            for spans in answer_keys.values():
                hits.extend(scan_answer_key_leak(path, text, spans))
    return hits


def main() -> None:
    if FIRST_SELECTION.exists():
        print("First Selection on disk; contamination gate relaxed.")
        return
    hits = check()
    if hits:
        print("CONTAMINATION HITS:")
        print("\n".join(hits))
        sys.exit(2)
    print("contamination check: clean (pre-First-Selection)")


if __name__ == "__main__":
    main()
