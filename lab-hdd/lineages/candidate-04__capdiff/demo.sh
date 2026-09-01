#!/usr/bin/env bash
# Capture two fixture environments, diff them, replay env-only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
CLI="$ROOT/capdiff"
chmod +x "$CLI"
rm -rf .capdiff

echo "== capture a (local) =="
"$CLI" capture a "$ROOT/fixtures/env-a"
echo "== capture b (remote) =="
"$CLI" capture b "$ROOT/fixtures/env-b"

echo "== diff a b (expect exit 2) =="
set +e
"$CLI" diff a b
DIFF_EC=$?
set -e
echo "diff exit: $DIFF_EC"
if [ "$DIFF_EC" -ne 2 ]; then
  echo "expected diff exit 2, got $DIFF_EC" >&2
  exit 1
fi

echo "== replay a (env-only) =="
"$CLI" replay a -- "$ROOT/fixtures/env-a" python3 "$ROOT/fixtures/print_key.py"
echo "== replay b (env-only) =="
"$CLI" replay b -- "$ROOT/fixtures/env-b" python3 "$ROOT/fixtures/print_key.py"

echo "== capture none (no .env) =="
"$CLI" capture none "$ROOT/fixtures/env-empty"
echo "== diff a none (expect exit 2, API_KEY missing on none) =="
set +e
"$CLI" diff a none
NONE_EC=$?
set -e
echo "diff exit: $NONE_EC"
if [ "$NONE_EC" -ne 2 ]; then
  echo "expected diff exit 2, got $NONE_EC" >&2
  exit 1
fi

echo "demo ok"
