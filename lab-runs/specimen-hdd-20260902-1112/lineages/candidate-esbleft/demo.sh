#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/esbleft"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (diff metafile bytesInOutput vs bytes) =="
echo "leftover is bytes_in_output == uniquekey_len and != substituted_bytes"
echo
echo "== esbleft specimen-093 case B leftover =="
python3 "$CLI" "$FIX/093-leftover.rec" || true
echo
echo "== esbleft case A never-url =="
python3 "$CLI" "$FIX/093-fresh.rec" || true
echo
echo "== esbleft case D long name =="
python3 "$CLI" "$FIX/093-long.rec" || true
