#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/platident"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest: print both gem full names =="
echo "install nokogiri-1.18.10  setup nokogiri-1.18.10-x86_64-linux  install exit 0"
echo
echo "== platident specimen-074 owned =="
python3 "$CLI" "$ROOT/fixtures/074-nokogiri.rec"
echo
echo "== platident unseen sorbet-static =="
python3 "$CLI" "$ROOT/fixtures/unseen-sorbet.rec"
echo
echo "== platident agree same identity =="
python3 "$CLI" "$ROOT/fixtures/agree.rec"
