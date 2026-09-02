#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$ROOT/armtimer" 2>/dev/null || true
echo "== nearest: read StartPeriod and StartInterval =="
echo "starting, elapsed 0, start_interval 30 vs interval 2 after period 2"
echo
echo "== armtimer specimen-066 =="
python3 "$ROOT/armtimer" "$ROOT/fixtures/066-starting.rec"
echo
echo "== armtimer unseen after period =="
python3 "$ROOT/armtimer" "$ROOT/fixtures/unseen-after.rec"
