#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/treeid"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print files= list and cache hit) =="
echo "fileTree dir+pattern identity omits member names; named files() does not"
echo
echo "== treeid specimen-088 fileTree =="
python3 "$CLI" "$FIX/088-filetree.rec" || true
echo
echo "== treeid specimen-088 named files =="
python3 "$CLI" "$FIX/088-named.rec" || true
