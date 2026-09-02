#!/usr/bin/env bash
# Run waitoneshot on the three timeout-0 flag cases (specimen-056 / harvest).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/waitoneshot"

candidate_roots() {
  local top common abs parent
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && printf '%s\n' "$top"
  common="$(git -C "$1" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    case "$common" in
      /*) abs="$common" ;;
      *) abs="$(cd "$1" && cd "$common" && pwd)" ;;
    esac
    parent="$(cd "$abs/.." && pwd)"
    printf '%s\n' "$parent"
  fi
}

find_run() {
  if [ -n "${RUN_DIR:-}" ] && [ -d "$RUN_DIR/specimens/specimen-056" ]; then
    printf '%s\n' "$RUN_DIR"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112"
    if [ -d "$cand/specimens/specimen-056" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

RUN="$(find_run || true)"
S056="${RUN:+$RUN/specimens/specimen-056}"
S044="${RUN:+$RUN/specimens/specimen-044}"
FLAGS="${S056:+$S056/files/flags.txt}"
if [ ! -f "${FLAGS:-}" ]; then
  FLAGS="$ROOT/fixtures/flags.txt"
fi

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== fixture ${FLAGS} =="
cat "$FLAGS"
echo

echo "== nearest existing operation (help text plus error string) =="
echo "timeout help: Zero means check once and don't wait"
echo "wait-for-creation default: true; ignored in --for=delete"
echo "error: --wait-for-creation requires a timeout value greater than 0"
echo "(the error does not name abort-before-visit vs one-shot check)"
if [ -f "${S044:-}/files/staging/src/k8s.io/kubectl/pkg/cmd/wait/wait.go.excerpt" ]; then
  echo
  echo "== specimen-044 wait.go abort (origin excerpt, not executed) =="
  grep -n -A2 "WaitForCreation && o.Timeout" \
    "$S044/files/staging/src/k8s.io/kubectl/pkg/cmd/wait/wait.go.excerpt" \
    | head -n 6
fi
echo

echo "== waitoneshot timeout 0 wait-for-creation true (abort before visit) =="
"$CLI" --timeout 0 --wait-for-creation true --for jsonpath --object-exists true
echo

echo "== waitoneshot timeout 0 wait-for-creation false (oneshot visit) =="
"$CLI" --timeout 0 --wait-for-creation false --for jsonpath --object-exists true
echo

echo "== waitoneshot timeout 0 for=delete (oneshot) =="
"$CLI" --timeout 0 --wait-for-creation true --for delete --object-exists true
