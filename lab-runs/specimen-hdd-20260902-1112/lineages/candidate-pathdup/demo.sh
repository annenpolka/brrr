#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/pathdup"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (normpath the two warning lines) =="
echo "leftover is lexical dup that collapses to the same directory"
echo
echo "== pathdup specimen-091 case B leftover .. =="
python3 "$CLI" "$FIX/091-dotdot.rec" || true
echo
echo "== pathdup case A one spelling =="
python3 "$CLI" "$FIX/091-clean.rec" || true
echo
echo "== pathdup case C true clash =="
python3 "$CLI" "$FIX/091-clash.rec" || true
