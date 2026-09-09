#!/usr/bin/env python3
"""SHA-256 the public 6-file bundle. Drive real files; do not hard-code live hashes as inputs."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

BUNDLE_RELATIVE = (
    "discovery/input-001/COMMANDS.md",
    "discovery/input-001/OBSERVED.md",
    "discovery/input-001/TASK.md",
    "discovery/input-001/files/a.js",
    "discovery/input-001/files/package.json",
    "discovery/input-001/seed.md",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_tree(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in BUNDLE_RELATIVE:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"missing bundle file: {path}")
        out[rel] = sha256_file(path)
    return out


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: hash_bundle.py BUNDLE_ROOT")
    root = Path(sys.argv[1])
    json.dump(hash_tree(root), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
