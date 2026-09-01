#!/usr/bin/env bash
# Joint record: DECLARED + ASSIGNED + ENV_SOURCE + EFFECTIVE. Not two CLIs concatenated.
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
EFFECT="$ROOT/effect"
PY="${PYTHON:-python3}"

run() {
  local title="$1"
  shift
  echo "======== $title ========"
  echo "+ $PY effect $*"
  set +e
  env -u TIMEOUT -u WAIT -u timeout "$PY" "$EFFECT" "$@"
  local code=$?
  set -e
  echo "exit: $code"
  echo
}

run_env() {
  local title="$1"
  shift
  echo "======== $title ========"
  echo "+ $*"
  set +e
  env -u timeout "$@"
  local code=$?
  set -e
  echo "exit: $code"
  echo
}

run "disagree (config 5 vs source 10; .env TIMEOUT=30 still in ENV_SOURCE)" \
  timeout "$ROOT/fixtures/disagree"

run_env "disagree with inherited TIMEOUT=from-shell" \
  env TIMEOUT=from-shell "$PY" "$EFFECT" timeout "$ROOT/fixtures/disagree"

run "agree (both 5, env unset)" \
  timeout "$ROOT/fixtures/agree"

run "config only" \
  timeout "$ROOT/fixtures/config_only"

run_env "empty override (declared 5, getenv TIMEOUT, file TIMEOUT=)" \
  env TIMEOUT=/already/set "$PY" "$EFFECT" timeout "$ROOT/fixtures/empty-override"

run_env "deferred WAIT (config \${WAIT} and os.getenv WAIT; file WAIT=10)" \
  env WAIT=from-shell "$PY" "$EFFECT" timeout "$ROOT/fixtures/deferred"

run "unknown (interpolation vs getenv, WAIT unset)" \
  timeout "$ROOT/fixtures/unknown"

run "comments ignored for comparison" \
  timeout "$ROOT/fixtures/comments"

run_env "environ.get / process.env WAIT (declared 5, file WAIT=10)" \
  env WAIT=from-shell "$PY" "$EFFECT" timeout "$ROOT/fixtures/environ-get"

run "json joint object (disagree)" \
  --json timeout "$ROOT/fixtures/disagree"

run "compact JSON object member (one-line {\"timeout\": 5} vs timeout = 10)" \
  timeout "$ROOT/fixtures/compact_json"
