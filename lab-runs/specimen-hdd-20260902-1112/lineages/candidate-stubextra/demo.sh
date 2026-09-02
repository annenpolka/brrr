#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/stubextra"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest: print cache key and extra_exists =="
echo "first BUILT extra_requested no extra_bytes 0"
echo "second FRESH extra_requested yes extra_bytes 0 same key"
echo
echo "== stubextra specimen-071 owned =="
python3 "$CLI" "$ROOT/fixtures/071-first.rec" "$ROOT/fixtures/071-second.rec"
echo
echo "== stubextra unseen leftover cyclonedx =="
python3 "$CLI" "$ROOT/fixtures/unseen-first.rec" "$ROOT/fixtures/unseen-second.rec"
