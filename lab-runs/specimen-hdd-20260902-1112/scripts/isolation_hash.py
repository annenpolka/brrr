#!/usr/bin/env python3
"""Hash historical experiment files. Must not mutate them."""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from paths import HISTORICAL_ISOLATION_FILES, REPO_ROOT

JST = ZoneInfo("Asia/Tokyo")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(repo_root: Path | None = None) -> dict[str, str]:
    root = repo_root or REPO_ROOT
    out: dict[str, str] = {}
    for rel in HISTORICAL_ISOLATION_FILES:
        path = root / rel
        if not path.exists():
            raise FileNotFoundError(rel)
        out[rel] = sha256_file(path)
    return out


def render(snap: dict[str, str], label: str) -> str:
    lines = [
        f"label={label}",
        f"at_jst={datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S %Z')}",
    ]
    for rel, digest in snap.items():
        lines.append(f"{rel} {digest}")
    lines.append("")
    return "\n".join(lines)


def compare(before: dict[str, str], after: dict[str, str]) -> list[str]:
    diffs = []
    for rel in HISTORICAL_ISOLATION_FILES:
        if before.get(rel) != after.get(rel):
            diffs.append(f"{rel}: {before.get(rel)} -> {after.get(rel)}")
    return diffs


def parse_snapshot(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if " " not in line or line.startswith("at_jst=") or line.startswith("label=") or line.startswith("RUN_ID="):
            continue
        rel, digest = line.rsplit(" ", 1)
        if len(digest) == 64:
            out[rel] = digest
    return out


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
    if cmd == "snapshot":
        label = sys.argv[2] if len(sys.argv) > 2 else "live"
        sys.stdout.write(render(snapshot(), label))
        return
    if cmd == "compare":
        before_path = Path(sys.argv[2])
        after_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
        before = parse_snapshot(before_path.read_text(encoding="utf-8"))
        after = parse_snapshot(after_path.read_text(encoding="utf-8")) if after_path else snapshot()
        diffs = compare(before, after)
        if diffs:
            print("ISOLATION DRIFT:")
            print("\n".join(diffs))
            sys.exit(2)
        print("isolation: historical hashes unchanged")
        return
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
