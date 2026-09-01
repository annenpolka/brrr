#!/usr/bin/env bash
# Launch up to N Dreamer turns in parallel. Usage: launch_dreams.sh <phase> [trial ...]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PHASE="${1:?phase}"
shift
if [[ $# -eq 0 ]]; then
  echo "usage: launch_dreams.sh <phase> <trial> [trial...]" >&2
  exit 2
fi
PIDS=()
for trial in "$@"; do
  echo "launching dream trial=$trial phase=$PHASE"
  "$ROOT/lab-hdd/scripts/dream.sh" "$trial" "$PHASE" \
    >"$ROOT/lab-hdd/dream-logs/${trial}-wrapper.out" \
    2>"$ROOT/lab-hdd/dream-logs/${trial}-wrapper.err" &
  PIDS+=("$!")
  echo "$trial pid=${PIDS[-1]}"
done
printf '%s\n' "${PIDS[@]}" > "$ROOT/lab-hdd/dream-logs/wave.pids"
echo "launched ${#PIDS[@]} dreams; pids in lab-hdd/dream-logs/wave.pids"
