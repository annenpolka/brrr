#!/usr/bin/env bash
# Run the shipped CLI against the three required fixtures (plus unknown).
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
STATED="$ROOT/stated"
PY="${PYTHON:-python3}"

run() {
  local title="$1"
  shift
  echo "======== $title ========"
  echo "+ $PY stated $*"
  set +e
  "$PY" "$STATED" "$@"
  local code=$?
  set -e
  echo "exit: $code"
  echo
}

run "disagree (config.yaml timeout: 5 vs app.py timeout = 10)" \
  timeout "$ROOT/fixtures/disagree"

run "agree (both 5)" \
  timeout "$ROOT/fixtures/agree"

run "config only" \
  timeout "$ROOT/fixtures/config_only"

run "unknown (interpolation vs getenv) — honest non-comparison" \
  timeout "$ROOT/fixtures/unknown"

run "comments vs real assignment (docstring/block-comment 99 ignored)" \
  timeout "$ROOT/fixtures/comments"

run "json disagreement pair" \
  --json timeout "$ROOT/fixtures/disagree"
