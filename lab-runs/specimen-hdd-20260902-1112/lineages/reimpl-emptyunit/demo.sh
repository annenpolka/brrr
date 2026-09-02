#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/emptyunit"
chmod +x "$CLI" 2>/dev/null || true
echo "== nearest existing operation (print the workqueue dict) =="
echo "scope testing/test_timeout.py items test_1=done test_2=done"
echo "(the hang is empty send after completed-only requeue, not the crash)"
echo
echo "== emptyunit specimen-063 owned hang =="
python3 "$CLI" "$ROOT/fixtures/063-hang.rec"
echo
echo "== emptyunit unseen mixed incomplete =="
python3 "$CLI" "$ROOT/fixtures/unseen-mixed.rec"
echo
echo "== emptyunit unseen two scopes =="
python3 "$CLI" "$ROOT/fixtures/unseen-two-scopes.rec"
echo
echo "== emptyunit specimen-063 jsonl events =="
python3 "$CLI" "$ROOT/fixtures/063-hang.jsonl"
