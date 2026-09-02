#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/greendep"
chmod +x "$CLI" 2>/dev/null || true

run_cli() {
  local label="$1"
  shift
  echo "== $label =="
  set +e
  python3 "$CLI" "$@" 2>&1
  echo "rc=$?"
  set -e
  echo
}

echo "== nearest existing operation (print two query names) =="
echo "typeck_of(poll) green; type_of(Error) changed"
echo "(two dumps still leave the unrecorded edge as a hand join)"
echo

run_cli "greendep specimen-075 owned" "$ROOT/fixtures/075-green.rec"
run_cli "greendep unrelated green is not false_green" "$ROOT/fixtures/unrelated.rec"
run_cli "greendep recorded-changed is invalidation (not rc=0 silence)" "$ROOT/fixtures/unseen-recorded.rec"
run_cli "greendep both unrecorded and recorded-changed" "$ROOT/fixtures/both.rec"
run_cli "greendep incomplete green without changed (rc=2)" "$ROOT/fixtures/incomplete.rec"
run_cli "greendep arrow names stay TSV query/dep fields" "$ROOT/fixtures/arrows.rec"

echo "== greendep rustc-shaped dump is refused =="
set +e
printf 'typeck_of(S::poll) -> type_of(Error)\n' | python3 "$CLI" - 2>&1
echo "rc=$?"
set -e

echo "== greendep query named '-' is not the empty sentinel =="
set +e
printf 'query\t-\tgreen\nchanged\t-\tD\n' | python3 "$CLI" - 2>&1
echo "rc=$?"
set -e
