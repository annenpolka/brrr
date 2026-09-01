#!/usr/bin/env bash
# Run the three core fixtures against the shipped owes CLI.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
OWES="$ROOT/owes"
fail=0

run_case() {
  local name="$1"
  local expected="$2"
  shift 2
  echo
  echo "=== $name (expect exit $expected) ==="
  set +e
  python3 "$OWES" "$@"
  local code=$?
  set -e
  echo "exit: $code"
  if [[ "$code" -ne "$expected" ]]; then
    echo "FAIL: expected exit $expected, got $code"
    fail=1
  else
    echo "ok"
  fi
}

run_case "1 deleted function still mentioned in README.md" 2 \
  "$ROOT/fixtures/deleted-fn"

run_case "2 remaining doc names absent SECURITY.decision.md" 2 \
  "$ROOT/fixtures/missing-companion"

run_case "3 clean change with no leftover mentions" 0 \
  "$ROOT/fixtures/clean"

echo
if [[ "$fail" -ne 0 ]]; then
  echo "demo: FAILED"
  exit 1
fi
echo "demo: all three fixtures behaved as expected"
exit 0
