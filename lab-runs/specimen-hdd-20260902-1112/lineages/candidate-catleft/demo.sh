#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/catleft"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep catalog: vs catalog object) =="
echo "leftover is member_spec != catalog: and member_spec != catalog_range"
echo
echo "== catleft specimen-100 case B leftover =="
python3 "$CLI" "$FIX/100-leftover.rec" || true
echo
echo "== catleft case A still catalog: =="
python3 "$CLI" "$FIX/100-joined.rec" || true
echo
echo "== catleft both moved =="
python3 "$CLI" "$FIX/100-moved.rec" || true
