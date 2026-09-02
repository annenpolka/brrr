#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/startimer"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print the four duration fields) =="
echo "StartPeriod=2s StartInterval=30s Interval=2s Retries=1"
echo "(the four numbers do not name that the timer is not reset at period end)"
echo
echo "== startimer specimen-066 owned =="
python3 "$CLI" --start-period 2s --start-interval 30s --interval 2s --retries 1
echo
echo "== startimer unseen retries=2 =="
python3 "$CLI" --start-period 5s --start-interval 20s --interval 3s --retries 2
