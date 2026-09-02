#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/emptyunit"
chmod +x "$CLI" 2>/dev/null || true

run_cli() {
  local label="$1"
  local file="$2"
  echo "== $label =="
  set +e
  python3 "$CLI" "$file" 2>&1
  local rc=$?
  set -e
  echo "rc:$rc"
  echo
}

run_stdin() {
  local label="$1"
  local payload="$2"
  echo "== $label =="
  set +e
  printf '%s\n' "$payload" | python3 "$CLI" - 2>&1
  local rc=$?
  set -e
  echo "rc:$rc"
  echo
}

echo "== nearest existing operation (print the workqueue dict) =="
cat "$ROOT/fixtures/063-hang.dump"
echo
echo "(indexes still a hand join; emptyunit groups by dist then names assign-burst send () vs hang_risk)"
echo

run_cli "emptyunit ingest of that dump (loadgroup crash after test_1)" "$ROOT/fixtures/063-hang.dump"
run_cli "emptyunit print(workqueue) OrderedDict" "$ROOT/fixtures/063-hang.wq"
run_cli "emptyunit unseen mixed incomplete (loadscope)" "$ROOT/fixtures/unseen-mixed.rec"
run_cli "emptyunit two scopes done-first (first assign is empty send)" "$ROOT/fixtures/unseen-two-scopes.rec"
run_cli "emptyunit two scopes live-first (reschedule second is empty send)" "$ROOT/fixtures/unseen-live-first.rec"
run_cli "emptyunit pending=2 then completed-only (watermark assigns second)" "$ROOT/fixtures/unseen-pending2.rec"
run_cli "emptyunit pending=3 then completed-only (watermark holds second)" "$ROOT/fixtures/unseen-pending3.rec"
run_cli "emptyunit handwritten module-both-done rec (regrouped, not the hang)" "$ROOT/fixtures/063-hang.rec"
run_cli "emptyunit hang log (refused)" "$ROOT/fixtures/hang_log.txt"
run_cli "emptyunit loadscope both done (not requeued)" "$ROOT/fixtures/loadscope-alldone.rec"

run_stdin "same tests loadgroup (no caller regroup)" '{"collection":["mod.py::a","mod.py::b"],"dist":"loadgroup","workqueue":{"mod.py::a":{"mod.py::a":true},"mod.py::b":{"mod.py::b":false}}}'
run_stdin "same tests loadscope (no caller regroup)" '{"collection":["mod.py::a","mod.py::b"],"dist":"loadscope","workqueue":{"mod.py::a":{"mod.py::a":true},"mod.py::b":{"mod.py::b":false}}}'
