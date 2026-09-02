#!/usr/bin/env bash
# Run visitid on pointer vs value visit sets (specimen-070 analog).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/visitid"

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
  if [ -n "${RUN_DIR:-}" ] && [ -d "$RUN_DIR/specimens/specimen-070" ]; then
    printf '%s\n' "$RUN_DIR"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112"
    if [ -d "$cand/specimens/specimen-070" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

run_visit() {
  local rc=0
  python3 "$CLI" "$@" || rc=$?
  echo "rc=$rc"
  case "$rc" in
    0|1) return 0 ;;
    *) return "$rc" ;;
  esac
}

RUN="$(find_run || true)"
S070="${RUN:+$RUN/specimens/specimen-070}"
CC="${S070:+$S070/files/prefetch_failing.cc}"
COUNTS="${S070:+$S070/files/observed_counts.txt}"
if [ ! -f "${CC:-}" ]; then
  CC="$ROOT/fixtures/prefetch_failing.cc"
fi
if [ ! -f "${COUNTS:-}" ]; then
  COUNTS="$ROOT/fixtures/observed_counts.txt"
fi

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== nearest existing operation (print object ids) =="
python3 -c "print('id(object())==id(object())', id(object())==id(object()))"
echo "(equal ids after the first object dies still do not name skipped-because-pointer vs distinct-value)"
echo

echo "== fixture counts ${COUNTS} =="
cat "$COUNTS"
echo "(origin counts; visitid walks a caller-complete (node, addr) list and does not encode 232/170/150)"
echo

if [ -f "$CC" ]; then
  echo "== specimen-070 prefetch_failing.cc done-set (origin excerpt, not executed) =="
  grep -n "done.insert" "$CC" | head -n 4
  echo
fi

echo "== visitid specimen-070 owned addr/name events (address reuse skips distinct node) =="
run_visit "$ROOT/fixtures/070-reuse.rec"
echo

echo "== visitid unseen unique addrs =="
run_visit "$ROOT/fixtures/unseen-unique.rec"
echo

echo "== visitid unseen same-name different-addr (value skip) =="
run_visit "$ROOT/fixtures/unseen-same-value.rec"
echo

echo "== visitid same input name, later node reuses earlier addr =="
run_visit "$ROOT/fixtures/reuse-same-name.rec"
