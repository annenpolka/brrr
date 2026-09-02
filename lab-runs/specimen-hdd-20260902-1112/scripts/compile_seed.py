#!/usr/bin/env python3
"""Compile a Dreamer-facing seed from a sealed specimen packet. Never reads answer-key/."""
from __future__ import annotations

import sys
from pathlib import Path

from contamination_check import check
from paths import HDD_ROOT, RUN_DIR, SEEDS, SPECIMENS

ANSWER_KEY_DIRNAME = "answer-key"

OPERATOR_REQUEST = """OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
"""


def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").rstrip() + "\n"


def compile_seed(specimen_dir: Path) -> str:
    if not specimen_dir.is_dir():
        raise FileNotFoundError(specimen_dir)
    parts = [
        "CURRENT SITUATION",
        "A real checkout or reduced fixture exists. The following material is what is known.",
        "",
        _read(specimen_dir / "TASK.md") or "TASK\n(unknown)\n",
        _read(specimen_dir / "OBSERVED.md"),
        _read(specimen_dir / "COMMANDS.md"),
        _read(specimen_dir / "TREE.txt"),
    ]
    files_dir = specimen_dir / "files"
    if files_dir.exists():
        parts.append("RELEVANT MATERIAL")
        parts.append("")
        for path in sorted(p for p in files_dir.rglob("*") if p.is_file()):
            rel = path.relative_to(files_dir)
            parts.append(f"### {rel}")
            parts.append("")
            parts.append(_read(path))
    parts.append("KNOWN FACTS")
    parts.append("Only the observations above are established. Do not assume a root cause.")
    parts.append("")
    parts.append("UNKNOWN")
    parts.append("What relation, provenance, or question would make this failure smaller to investigate?")
    parts.append("")
    parts.append(OPERATOR_REQUEST)
    text = "\n".join(parts)
    if ANSWER_KEY_DIRNAME in text.lower() and "answer-key/" in text.lower():
        raise RuntimeError("compile_seed attempted to mention answer-key path")
    return text


def write_seed(specimen_dir: Path, dest: Path | None = None) -> Path:
    dest = dest or (SEEDS / f"{specimen_dir.name}.md")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(compile_seed(specimen_dir), encoding="utf-8")
    hits = check(RUN_DIR, HDD_ROOT)
    seed_hits = [h for h in hits if str(dest) in h or dest.name in h]
    if seed_hits:
        dest.unlink(missing_ok=True)
        raise SystemExit("contamination in compiled seed:\n" + "\n".join(seed_hits))
    return dest


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: compile_seed.py <specimen-id>")
    spec = SPECIMENS / sys.argv[1]
    path = write_seed(spec)
    print(path)


if __name__ == "__main__":
    main()
