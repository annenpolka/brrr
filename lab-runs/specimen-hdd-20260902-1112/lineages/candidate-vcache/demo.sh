#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/vcache"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep memory write vs fs empty) =="
echo "leftover is a minted key with externalize yes and disk_write no"
echo
echo "== vcache specimen-094 externalize leftover =="
python3 "$CLI" "$FIX/094-ext.rec" || true
echo
echo "== vcache inlined written =="
python3 "$CLI" "$FIX/094-inline.rec" || true
