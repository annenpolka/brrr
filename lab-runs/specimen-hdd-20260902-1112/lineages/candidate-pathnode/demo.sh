#!/usr/bin/env bash
# Run pathnode on duplicate-path collection events.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/pathnode"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== nearest existing operation (print CLI args plus collect output) =="
echo "pytest dir1 dir2 dir1 --collect-only"
echo "(seeing dir1 twice does not name two node identities or which fixture missed)"
echo

echo "== pathnode specimen-003 owned events (same path, two nodes, fixture miss) =="
python3 "$CLI" "$ROOT/fixtures/003-collect.rec"
echo

echo "== pathnode unseen same-node twice =="
python3 "$CLI" "$ROOT/fixtures/unseen-collect.rec"
echo

echo "== pathnode single path, no dup =="
printf 'collect\tonly\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n' | python3 "$CLI"
