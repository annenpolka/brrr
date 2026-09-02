#!/usr/bin/env bash
# Background watchdog. Writes snapshots under the run dir and optional scratch.
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$(cd "$SCRIPTS/.." && pwd)"
SCRATCH_THROUGHPUT="${1:-}"
INTERVAL="${WATCHDOG_INTERVAL_SECONDS:-90}"
export PYTHONPATH="$SCRIPTS${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$RUN_DIR/watchdog"
while true; do
  if [[ -n "$SCRATCH_THROUGHPUT" ]]; then
    python3 "$SCRIPTS/watchdog.py" "$SCRATCH_THROUGHPUT" >>"$RUN_DIR/watchdog/loop.log" 2>&1 || true
  else
    python3 "$SCRIPTS/watchdog.py" >>"$RUN_DIR/watchdog/loop.log" 2>&1 || true
  fi
  sleep "$INTERVAL"
done
