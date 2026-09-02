#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/overleft"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep nested override vs lock version) =="
echo "leftover is override_set with lock_version == original"
echo
echo "== overleft specimen-095 leftover =="
python3 "$CLI" "$FIX/095-leftover.rec" || true
echo
echo "== overleft applied =="
python3 "$CLI" "$FIX/095-applied.rec" || true
echo
echo "== overleft never =="
python3 "$CLI" "$FIX/095-never.rec" || true
