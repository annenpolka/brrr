#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/nilkeep"
chmod +x "$CLI" 2>/dev/null || true

run_cli() {
  local title="$1"
  shift
  echo "== $title =="
  set +e
  python3 "$CLI" "$@"
  local code=$?
  set -e
  echo "exit: $code"
  echo
}

echo "== nearest existing operation (print both maps) =="
echo 'default {} + user baz:~ → map[foo:bar]'
echo 'default ~ + user baz:~ → map[baz:<nil> foo:bar]'
echo "(two quoted maps still leave the default-shape join as a hand comparison)"
echo

run_cli "nilkeep specimen-079 empty-map default" \
  "$ROOT/fixtures/079-empty-map.rec"

run_cli "nilkeep specimen-079 null default" \
  "$ROOT/fixtures/079-null-default.rec"

run_cli "nilkeep unseen" \
  "$ROOT/fixtures/unseen.rec"

run_cli "nilkeep specimen-079 json values maps (empty-map)" \
  "$ROOT/fixtures/079-empty-map.json"

run_cli "nilkeep specimen-079 json values maps (null default)" \
  "$ROOT/fixtures/079-null-default.json"
