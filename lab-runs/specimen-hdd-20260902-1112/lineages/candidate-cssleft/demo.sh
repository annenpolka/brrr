#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/cssleft"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (diff STATS_JSON names; grep url() in CSS) =="
echo "leftover is url_in_css != png_emitted and/or css_name == prev_css_name"
echo
echo "== cssleft specimen-090 case C leftover =="
python3 "$CLI" "$FIX/090-leftover.rec" || true
echo
echo "== cssleft case A fresh =="
python3 "$CLI" "$FIX/090-fresh.rec" || true
echo
echo "== cssleft case B css moved url ok =="
python3 "$CLI" "$FIX/090-css-only.rec" || true
