#!/usr/bin/env python3
"""Independent replica of keptfp: caller fingerprint membership. Does not import keptfp."""

from __future__ import annotations

KNOWN = ("current", "entry")


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def parse(text: str, *, source: str = "<stdin>") -> tuple[str, list[tuple[str, str, str, str]]]:
    current: str | None = None
    entries: list[tuple[str, str, str, str]] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError(f"{source}:{lineno}: expected key<TAB>value")
        key, rest = line.split("\t", 1)
        key, rest = key.strip(), rest.strip()
        if key not in KNOWN:
            raise ValueError(f"{source}:{lineno}: unknown field {key!r}")
        if key == "current":
            if not rest:
                raise ValueError(f"{source}:{lineno}: empty current")
            if current is not None and current != rest:
                raise ValueError(f"{source}:{lineno}: conflicting current hash")
            current = rest
        else:
            parts = [p for p in rest.split("\t") if p]
            if len(parts) < 3:
                raise ValueError(
                    f"{source}:{lineno}: entry needs id, member, lockfile_hash"
                )
            ident, member, lock_hash = parts[0], parts[1], parts[2]
            size = parts[3] if len(parts) > 3 else "-"
            entries.append((ident, member, lock_hash, size))
    if current is None:
        raise ValueError(f"{source}: missing current")
    return current, entries


def report(current: str, entries: list[tuple[str, str, str, str]]) -> str:
    live = [e for e in entries if e[2] == current]
    leftover = [e for e in entries if e[2] != current]
    leftover_members = unique([e[1] for e in leftover])
    lines = [f"current\t{current}"]
    if live:
        for e in live:
            lines.append(f"live\t{e[0]}\t{e[1]}\t{e[2]}\t{e[3]}")
    else:
        lines.append("live\tnone")
    if leftover:
        for e in leftover:
            lines.append(f"leftover\t{e[0]}\t{e[1]}\t{e[2]}\t{e[3]}")
    else:
        lines.append("leftover\tnone")
    lines.append(f"live_n\t{len(live)}")
    lines.append(f"leftover_n\t{len(leftover)}")
    lines.append(
        "leftover_members\t"
        + ("\t".join(leftover_members) if leftover_members else "none")
    )
    return "\n".join(lines) + "\n"


def run(text: str, *, source: str = "<stdin>") -> tuple[int, str, str]:
    try:
        current, entries = parse(text, source=source)
        return 0, report(current, entries), ""
    except ValueError as err:
        return 1, "", f"keptfp: {err}\n"
