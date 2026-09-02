#!/usr/bin/env bash
# Run keptfp on leftover vs live lockfile fingerprints.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/keptfp"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== nearest existing operation (ls plus grep of fingerprint dirs) =="
echo "current lockfile hash: f0e1d2c3b4"
echo "entries: fm_7a1b2c3d project_a a1b2c3d4e5; fm_8e9f0a1b project_a f0e1d2c3b4; fm_5c6d7e8f project_b a1b2c3d4e5"
echo "(listing dirs does not name leftover vs live without a hand join)"
echo

echo "== keptfp specimen-006 owned record (leftover hashes beside live) =="
python3 "$CLI" "$ROOT/fixtures/006-cache.rec"
echo

echo "== keptfp unseen mixed members =="
python3 "$CLI" "$ROOT/fixtures/unseen-cache.rec"
echo

echo "== keptfp all-live (no leftover) =="
printf 'current\tabc\nentry\te1\tm\tabc\t1\n' | python3 "$CLI"
