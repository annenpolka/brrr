#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/patchid"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep the selector) =="
echo "grep express@4.18.1 hits object path+hash and hash-only string"
echo
echo "== patchid specimen-085 object =="
python3 "$CLI" "$FIX/patcheddeps.object.yaml" --selector "express@4.18.1" || true
echo
echo "== patchid specimen-085 hash-only =="
python3 "$CLI" "$FIX/patcheddeps.hash.yaml" --selector "express@4.18.1" || true
echo
echo "== patchid unseen omitted =="
python3 "$CLI" "$FIX/patcheddeps.hash.yaml" --selector "missing@1.0.0" || true
echo
echo "== patchid empty string =="
printf 'patchedDependencies:\n  express@4.18.1: ""\n' | python3 "$CLI" - --selector "express@4.18.1" || true
