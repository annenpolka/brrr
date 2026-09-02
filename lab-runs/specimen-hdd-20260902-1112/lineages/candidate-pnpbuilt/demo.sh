#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/pnpbuilt"
FIX="$ROOT/fixtures"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (grep locator in build-state; ls unplugged .ready) =="
echo "leftover is stored hash with no .ready after unplugged delete"
echo
echo "== pnpbuilt specimen-089 leftover =="
python3 "$CLI" "$FIX/089-leftover.rec" || true
echo
echo "== pnpbuilt intact built =="
python3 "$CLI" "$FIX/089-built.rec" || true
echo
echo "== pnpbuilt never =="
python3 "$CLI" "$FIX/089-never.rec" || true
