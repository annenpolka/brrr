#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/refkey"
FIX="$ROOT/fixtures"
echo "== nearest existing operation (diff two cache keys) =="
echo "leftover is keep_git_dir and key_a==key_b and ref_a!=ref_b"
echo
echo "== refkey specimen-097 case B leftover =="
python3 "$CLI" "$FIX/097-leftover.rec" || true
echo
echo "== refkey case A no keep =="
python3 "$CLI" "$FIX/097-nokeep.rec" || true
echo
echo "== refkey case D split =="
python3 "$CLI" "$FIX/097-split.rec" || true
