#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/staleid"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest: print cache key =="
echo "first BUILT key 55e3acdd667f buildid-aaa"
echo "second FRESH same key buildid-bbb cached_buildid-aaa"
echo
echo "== staleid owned analog =="
python3 "$CLI" "$ROOT/fixtures/075-first.rec" "$ROOT/fixtures/075-second.rec" || true
echo
echo "== staleid unseen same-key new buildid =="
python3 "$CLI" "$ROOT/fixtures/unseen-first.rec" "$ROOT/fixtures/unseen-second.rec" || true
echo
echo "== staleid key changed with buildid =="
python3 "$CLI" "$ROOT/fixtures/075-first.rec" "$ROOT/fixtures/includes-second.rec" || true
