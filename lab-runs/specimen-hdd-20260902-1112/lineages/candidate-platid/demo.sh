#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/platid"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print both gem full names) =="
echo "install nokogiri-1.18.10 ; setup nokogiri-1.18.10-x86_64-linux"
echo "(exit 0 install hides the identity setup will miss)"
echo
echo "== platid specimen-074 owned =="
python3 "$CLI" "$ROOT/fixtures/074-installed.rec" "$ROOT/fixtures/074-lookup.rec"
echo
echo "== platid unseen darwin vs ruby =="
python3 "$CLI" "$ROOT/fixtures/unseen-installed.rec" "$ROOT/fixtures/unseen-lookup.rec"
