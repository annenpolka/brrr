#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/extraedge"
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

echo "== nearest existing operation (read pyproject and the lock) =="
echo "declared extra postgresql maps to extra-edge psycopg2; edit-lock resolved empty; add-lock resolved psycopg2"
echo "(without an extras table, extra names and extra-edge package names are different vocabularies)"
echo

run_cli "extraedge specimen-021 owned pair" \
  "$ROOT/fixtures/021-edit.rec" "$ROOT/fixtures/021-add.rec"

run_cli "extraedge add-lock as FIRST (mapped extra-edge present; not a miss)" \
  "$ROOT/fixtures/021-add.rec" "$ROOT/fixtures/021-add.rec"

run_cli "extraedge unseen mapped attach" \
  "$ROOT/fixtures/unseen-edit.rec" "$ROOT/fixtures/unseen-add.rec"

run_cli "extraedge specimen-021 json attach graph" \
  "$ROOT/fixtures/021-edit.json" "$ROOT/fixtures/021-add.json"
