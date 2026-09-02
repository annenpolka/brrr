#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$ROOT/requeue" 2>/dev/null || true
echo "== nearest: read the hang log =="
echo "requeued test_1 (done) and test_2 (open) to gw1"
echo
echo "== requeue specimen-063 =="
python3 "$ROOT/requeue" "$ROOT/fixtures/063-crash.rec"
echo
echo "== requeue unseen all-done empty assign =="
python3 "$ROOT/requeue" "$ROOT/fixtures/unseen-alldone.rec"
