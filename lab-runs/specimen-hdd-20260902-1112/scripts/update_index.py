#!/usr/bin/env python3
"""Rebuild SPECIMEN_INDEX.md from packet manifests."""
from __future__ import annotations

from pathlib import Path

from paths import RUN_DIR, SPECIMENS


def _field(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip()
    return ""


def main() -> None:
    rows = []
    for spec in sorted(SPECIMENS.glob("specimen-*")):
        man = (spec / "manifest.yaml").read_text(encoding="utf-8") if (spec / "manifest.yaml").exists() else ""
        sealed = (spec / "answer-key" / "FIX.md").exists()
        rows.append(
            {
                "id": spec.name,
                "kind": _field(man, "kind"),
                "repo": _field(man, "repository"),
                "failing": _field(man, "failing_ref"),
                "fixed": _field(man, "fixed_ref"),
                "sealed": sealed,
            }
        )
    lines = [
        "# Specimen index",
        "",
        f"Count: {len(rows)}",
        "",
        "| id | kind | repository | failing_ref | fixed_ref | answer_key_sealed |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['kind']} | {r['repo']} | `{r['failing']}` | `{r['fixed']}` | {r['sealed']} |"
        )
    lines.append("")
    (RUN_DIR / "SPECIMEN_INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"indexed {len(rows)}")


if __name__ == "__main__":
    main()
