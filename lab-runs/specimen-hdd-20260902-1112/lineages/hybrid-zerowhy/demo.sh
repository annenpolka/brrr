#!/usr/bin/env bash
# Exclusive why for a lying zero. Not swallowecho stdout plus waitoneshot stdout.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/zerowhy"

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
  if [ -n "${RUN_DIR:-}" ] && [ -d "$RUN_DIR/lineages" ]; then
    printf '%s\n' "$RUN_DIR"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112"
    if [ -d "$cand/lineages" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

find_swallowecho() {
  if [ -n "${SWALLOWECHO:-}" ] && [ -f "$SWALLOWECHO" ]; then
    printf '%s\n' "$SWALLOWECHO"
    return 0
  fi
  local home run
  home="${HOME}/.grok/worktrees/annenpolka-brrr/candidate-swallowecho-swallowecho/swallowecho/swallowecho"
  if [ -f "$home" ]; then
    printf '%s\n' "$home"
    return 0
  fi
  run="$(find_run || true)"
  if [ -n "$run" ] && [ -f "$run/lineages/candidate-swallowecho/swallowecho" ]; then
    printf '%s\n' "$run/lineages/candidate-swallowecho/swallowecho"
    return 0
  fi
  return 1
}

find_waitoneshot() {
  if [ -n "${WAITONESHOT:-}" ] && [ -f "$WAITONESHOT" ]; then
    printf '%s\n' "$WAITONESHOT"
    return 0
  fi
  local home run py
  home="${HOME}/.grok/worktrees/annenpolka-brrr/waitoneshot-waitoneshot/waitoneshot/waitoneshot.py"
  if [ -f "$home" ]; then
    printf '%s\n' "$home"
    return 0
  fi
  run="$(find_run || true)"
  if [ -n "$run" ] && [ -f "$run/lineages/candidate-waitoneshot/waitoneshot" ]; then
    printf '%s\n' "$run/lineages/candidate-waitoneshot/waitoneshot"
    return 0
  fi
  py="${HOME}/.grok/worktrees/annenpolka-brrr/waitoneshot-waitoneshot/waitoneshot/waitoneshot.py"
  if [ -f "$py" ]; then
    printf '%s\n' "$py"
    return 0
  fi
  return 1
}

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

SW="$(find_swallowecho || true)"
WO="$(find_waitoneshot || true)"

echo "== nearest existing: concatenate parent stdout =="
if [ -n "$SW" ] && [ -n "$WO" ]; then
  echo "+ swallowecho 'false || echo ok'"
  python3 "$SW" 'false || echo ok'
  echo
  echo "+ waitoneshot --timeout 0 --wait-for-creation true --object-exists true"
  if [ "${WO##*.}" = "py" ]; then
    python3 "$WO" --timeout 0 --wait-for-creation true --object-exists true
  else
    "$WO" --timeout 0 --wait-for-creation true --object-exists true
  fi
  echo
  echo "(two reports; no exclusive why)"
else
  echo "swallowecho names swallow yes + step 0"
  echo "waitoneshot names visited false + abort wait-for-creation-requires-timeout"
  echo "concatenating those still does not pick exactly one of"
  echo "swallowed-nonzero | abort-before-visit | observed-ok | unknown"
fi
echo

echo "== zerowhy 'false || echo ok' =="
python3 "$CLI" 'false || echo ok'
echo

echo "== zerowhy --timeout 0 --wait-for-creation true =="
python3 "$CLI" --timeout 0 --wait-for-creation true
echo

echo "== zerowhy --timeout 0 --wait-for-creation false --object-exists true =="
python3 "$CLI" --timeout 0 --wait-for-creation false --object-exists true
echo

echo "== zerowhy both swallow and abort (exclusive refuses) =="
python3 "$CLI" --timeout 0 --wait-for-creation true 'false || echo ok'
