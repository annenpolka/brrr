#!/usr/bin/env python3
"""Fail if Dreamer-facing materials leak private corpus, past runs, answers, or this execplan.

Scans only the public-bundle copy, trial seed.md / human-pressure.md, and outbox
Dreamer prompts. FIRST_SELECTION.md does not disable this check.
"""
from __future__ import annotations

import sys
from pathlib import Path

from paths import HDD_ROOT, PUBLIC_BUNDLE, RUN_DIR

PATH_LEAKS = (
    ".brrr-corpus/mini-followup/approved-review",
    ".brrr-corpus/mini-followup/pilot",
    ".brrr-corpus/mini-followup/objects",
    ".brrr-corpus/mini-followup/quarantine",
    ".brrr-corpus/mini-followup/staging",
    ".brrr-corpus/mini-followup/corpus.sqlite",
    "docs/execplans/20260909-1730-hdd.md",
    "docs/execplans/20260909-1130-hdd.md",
    "docs/execution/20260909-1730-start.md",
    "docs/execution/20260909-1130-start.md",
    "lab-runs/specimen-hdd-20260902-1112",
    "lab-runs/corpus-hdd-20260909-1130",
    "lab-hdd/lineages",
    "lab-hdd/judges",
    "lab/lineages",
    "lab/judges",
    "lab/emerging.md",
    ".hdd-runs/specimen-hdd-20260902-1112",
    ".hdd-runs/corpus-hdd-20260909-1130",
)

PHRASE_LEAKS = (
    "private審査",
    "PRIVATE審査",
    "private review package",
    "approved-review",
    "review-audit.json",
    "answer-key",
    "正解をconsumer",
    "旧候補",
    "evolution_report.md",
    "hdd_evolution_report.md",
    "overnight developer tool evolution lab — master prompt",
    "brrr × hdd loop — overnight",
    "unlike invert",
    "unlike zanei",
    "unlike held",
    "unlike when",
    "unlike whence",
    "unlike envfrom",
    "unlike flowtrace",
    "unlike bindname",
    "unlike runpair",
    "collector root",
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
    "bindname",
    "runpair",
)

COLLECTOR_ROOT_MARKERS = (
    ".brrr-corpus/mini-followup/objects",
    ".brrr-corpus/mini-followup/corpus.sqlite",
    "collector root",
)

GIT_MARKERS = (
    "/.git/",
    ".git/config",
    ".git/HEAD",
    "refs/heads/",
)

ORIGINAL_TEXT_MARKERS = (
    "原文パス",
    "原文ディレクトリ",
    "full original issue body follows",
    "private source_revision body",
)


def scan_text(path: Path, text: str) -> list[str]:
    hits: list[str] = []
    lower = text.lower()
    for phrase in PATH_LEAKS + PHRASE_LEAKS + COLLECTOR_ROOT_MARKERS + ORIGINAL_TEXT_MARKERS:
        if phrase.lower() in lower:
            hits.append(f"{path}: phrase {phrase!r}")
    for marker in GIT_MARKERS:
        if marker.lower() in lower:
            hits.append(f"{path}: git {marker!r}")
    for name in ANTI_STEER_NAMES:
        if f"unlike {name}" in lower or f"not like {name}" in lower:
            hits.append(f"{path}: anti-steer {name!r}")
    return hits


def dreamer_facing_files(
    bundle_dir: Path | None,
    hdd_root: Path | None,
    extra_files: list[Path] | None = None,
) -> list[Path]:
    files: list[Path] = []
    if bundle_dir and bundle_dir.exists():
        files.extend(p for p in bundle_dir.rglob("*") if p.is_file())
    if hdd_root and hdd_root.exists():
        for trial in sorted(hdd_root.iterdir()):
            if not trial.is_dir() or trial.name == "current" or trial.is_symlink():
                continue
            for rel in ("seed.md", "human-pressure.md"):
                path = trial / rel
                if path.exists():
                    files.append(path)
            outbox = trial / "outbox"
            if outbox.exists():
                files.extend(outbox.glob("*-dreamer-prompt.md"))
    if extra_files:
        files.extend(extra_files)
    seen: set[Path] = set()
    out: list[Path] = []
    for path in files:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            out.append(resolved)
    return out


def check(
    bundle_dir: Path | None = None,
    hdd_root: Path | None = None,
    extra_files: list[Path] | None = None,
    first_selection: Path | None = None,
) -> list[str]:
    """Return leak descriptions. first_selection is ignored; the gate never auto-relaxes."""
    del first_selection
    hits: list[str] = []
    for path in dreamer_facing_files(bundle_dir, hdd_root, extra_files):
        text = path.read_text(encoding="utf-8", errors="replace")
        hits.extend(scan_text(path, text))
    return hits


def check_live() -> list[str]:
    extra: list[Path] = []
    seed_copy = RUN_DIR / "seeds" / "case-001-a.md"
    if seed_copy.exists():
        extra.append(seed_copy)
    return check(bundle_dir=PUBLIC_BUNDLE, hdd_root=HDD_ROOT, extra_files=extra)


def main() -> None:
    hits = check_live()
    if hits:
        print("CONTAMINATION HITS:")
        print("\n".join(hits))
        sys.exit(2)
    print("contamination check: clean (public-bundle + seed + outbox; FIRST_SELECTION does not relax)")


if __name__ == "__main__":
    main()
