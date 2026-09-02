#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/nilkeep"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print both maps) =="
echo 'default {} + user baz:~ → map[foo:bar]'
echo 'default ~ + user baz:~ → map[baz:<nil> foo:bar]'
echo "(two quoted maps still leave the default-shape join as a hand comparison)"
echo
echo "== nilkeep specimen-079 empty-map default =="
python3 "$CLI" "$ROOT/fixtures/079-empty-map.rec" || true
echo
echo "== nilkeep specimen-079 null default =="
python3 "$CLI" "$ROOT/fixtures/079-null-default.rec" || true
echo
echo "== nilkeep unseen =="
python3 "$CLI" "$ROOT/fixtures/unseen.rec" || true
