#!/usr/bin/env bash
# Run ordleak on specimen-009 plus helper / class / import-noise / unseen probes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/ordleak"

candidate_roots() {
  local top common parent
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && printf '%s\n' "$top"
  common="$(git -C "$1" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    parent="$(cd "$common/.." && pwd)"
    printf '%s\n' "$parent"
  fi
}

find_specimen() {
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/test_order.py" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-009"
    if [ -f "$cand/files/test_order.py" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

SPECIMEN="$(find_specimen || true)"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi
if [ ! -f "${SPECIMEN:-}/files/test_order.py" ]; then
  echo "demo.sh: specimen-009 fixture not found at $SPECIMEN" >&2
  echo "demo.sh: set SPECIMEN to the specimen-009 directory" >&2
  exit 1
fi

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

echo "== fixture $SPECIMEN/files/test_order.py =="
python3 "$SPECIMEN/files/run_orders.py"
echo

run_cli "ordleak test_a test_b (both orders)" \
  "$SPECIMEN/files/test_order.py" test_a test_b
run_cli "class-attribute Box.items" \
  "$ROOT/tests/fixtures/test_class_attr.py" test_a test_b
run_cli "helper-module from helper import bucket" \
  "$ROOT/tests/fixtures/helper/test_order.py" test_a test_b
run_cli "class-method TestOrder.test_a" \
  "$ROOT/tests/fixtures/test_class_method.py" TestOrder.test_a TestOrder.test_b
run_cli "import-time time_ns is not a leak" \
  "$ROOT/tests/fixtures/test_stamp.py" test_a test_b
run_cli "env split is unseen, not none" \
  "$ROOT/tests/fixtures/test_env.py" test_a test_b
run_cli "function-local holder.acc" \
  "$ROOT/tests/fixtures/test_fnattr.py" test_a test_b
run_cli "private _acc is named" \
  "$ROOT/tests/fixtures/test_private.py" test_a test_b
run_cli "package from pkg.helper import bucket" \
  "$ROOT/tests/fixtures/pkg/test_from_pkg.py" test_a test_b
run_cli "relative from .helper import bucket" \
  "$ROOT/tests/fixtures/pkg/test_relative.py" test_a test_b
run_cli "slots box.n" \
  "$ROOT/tests/fixtures/test_slots.py" test_a test_b

rm -f /tmp/ordleak-demo-smear.marker
run_cli "dual-FAIL /tmp smear is unseen not none" \
  "$ROOT/tests/fixtures/test_smear.py" test_a test_b
rm -f /tmp/ordleak-demo-smear.marker

run_cli "binary stdout is not a utf-8 crash" \
  "$ROOT/tests/fixtures/test_binary.py" test_a test_b
