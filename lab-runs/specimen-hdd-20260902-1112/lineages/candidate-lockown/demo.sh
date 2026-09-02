#!/usr/bin/env bash
# Two threads, one lock: print owner vs waiter. Contrast acquire timeout.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/lockown"
FIX="$ROOT/fixtures/timeout_only.py"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== nearest existing operation (threading.Lock.acquire timeout) =="
python3 "$FIX"
echo

echo "== lockown two threads one lock =="
python3 "$CLI"
