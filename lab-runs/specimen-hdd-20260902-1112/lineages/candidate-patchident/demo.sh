#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/patchident"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep the selector) =="
echo "grep express@4.18.1 hits object and hash-only lock excerpts"
echo "(the leftover is which identity, and that .hash on a string is empty)"
echo
echo "== patchident specimen-085 object =="
python3 "$CLI" "$ROOT/fixtures/patcheddeps.object.yaml" --selector express@4.18.1 || true
echo
echo "== patchident specimen-085 hash-only =="
python3 "$CLI" "$ROOT/fixtures/patcheddeps.hash.yaml" --selector express@4.18.1 || true
echo
echo "== patchident empty hash =="
python3 "$CLI" "$ROOT/fixtures/patcheddeps.empty.yaml" --selector express@4.18.1 || true
echo
echo "== patchident omitted selector =="
python3 "$CLI" "$ROOT/fixtures/patcheddeps.hash.yaml" --selector missing-package@1.0.0 || true
