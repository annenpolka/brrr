#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/narleftover"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (diff lock narHash vs cache value for that rev) =="
echo "leftover is cache_nar != lock_nar for the same rev fingerprint"
echo
echo "== narleftover specimen-092 poison =="
python3 "$CLI" "$FIX/092-poison.rec" || true
echo
echo "== narleftover fresh consistent =="
python3 "$CLI" "$FIX/092-fresh.rec" || true
