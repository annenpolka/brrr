#!/usr/bin/env python3
"""Independent replica of requeue inspect: filter caller-labeled TSV rows."""
from __future__ import annotations


def replica(text: str) -> str:
    units: dict[str, bool] = {}
    requeued: list[str] = []
    seen: set[str] = set()
    assigned: list[tuple[str, str]] = []
    nunit = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError("expected key<TAB>value")
        key, rest = line.split("\t", 1)
        parts = [p for p in rest.split("\t") if p != ""]
        if key == "unit":
            tok = parts[2].strip().lower()
            if tok in {"yes", "true", "done"}:
                units[parts[0]] = True
            elif tok in {"no", "false", "open"}:
                units[parts[0]] = False
            else:
                raise ValueError(tok)
            nunit += 1
        elif key == "requeued":
            if parts[0] not in seen:
                seen.add(parts[0])
                requeued.append(parts[0])
        elif key == "assigned":
            assigned.append((parts[0], parts[1]))
        else:
            raise ValueError(key)
    if nunit == 0:
        raise ValueError("missing unit")
    already = [n for n in requeued if units.get(n) is True]
    unfinished = [n for n in requeued if units.get(n) is False]
    unknown = [n for n in requeued if n not in units]
    by: dict[str, list[str]] = {}
    for worker, name in assigned:
        by.setdefault(worker, []).append(name)
    empty: list[str] = []
    for worker, names in by.items():
        open_names = [n for n in names if not units.get(n)]
        if names and not open_names:
            empty.append(worker)

    def fmt(items: list[str]) -> str:
        return "\t".join(items) if items else "none"

    lines = [
        f"requeued\t{fmt(requeued)}",
        f"already_done\t{fmt(already)}",
        f"unfinished\t{fmt(unfinished)}",
        f"empty_assign\t{fmt(empty)}",
    ]
    if unknown:
        lines.append(f"unknown\t{fmt(unknown)}")
    return "\n".join(lines) + "\n"
