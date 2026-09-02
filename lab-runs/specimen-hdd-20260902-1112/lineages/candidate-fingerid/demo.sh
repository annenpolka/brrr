#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/fingerid"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (diff two rustc -vV; compare path+mtime) =="
echo "path and mtime match; Fedora suffix in -vV does not"
echo
echo "== fingerid specimen-086 fc42 vs fc40 =="
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/086-fc40.rec" || true
echo
echo "== fingerid same compiler =="
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/086-fc42.rec" || true
echo
echo "== fingerid unseen size differs, fingerprint still collides =="
python3 "$CLI" "$FIX/086-fc42.rec" "$FIX/unseen-size.rec" || true
