#!/usr/bin/env bash
# Exercise unfmt against fixtures and prove inversion + exit codes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
UNFMT="$ROOT/unfmt"
FIX="$ROOT/fixtures"
fail=0

run() {
  local name="$1" expected="$2"
  shift 2
  local out
  if ! out="$("$UNFMT" "$@" 2>&1)"; then
    echo "FAIL $name: unfmt exited $?"
    echo "$out"
    fail=1
    return
  fi
  if ! grep -F -q -- "$expected" <<<"$out"; then
    echo "FAIL $name: expected to see: $expected"
    echo "$out"
    fail=1
    return
  fi
  echo "ok  $name"
}

chmod +x "$UNFMT"

set +e
"$UNFMT" -C "$FIX" "this string is not a template anywhere" >/dev/null 2>&1
ec=$?
set -e
if [[ "$ec" -ne 1 ]]; then
  echo "FAIL miss-exit: wanted 1 got $ec"
  fail=1
else
  echo "ok  miss-exit"
fi

run static "repo/mod.py:6:11: static" \
  -C "$FIX" "static exact message from fixtures"
run rust-brace "{1} = patch: **** malformed ****" \
  -C "$FIX" '`git apply --reverse` failed: patch: **** malformed ****'
run rust-static "app.rs:8:17: static" \
  -C "$FIX/repo" 'failed to spawn `git apply --reverse`'
run rust-named "{rest} = a/foo b/bar" \
  -C "$FIX" 'unparseable `diff --git` header: a/foo b/bar'
run swift "{presentThreshold} = 0.3" \
  -C "$FIX" 'presentThreshold must be greater than absentThreshold (got 0.3 vs 0.9)'
run python-f "{n} = 12" \
  -C "$FIX" "unknown dialect 'rust' at line 12"
run go-printf "{1} = @@ -1 +1 @@" \
  -C "$FIX" 'malformed hunk header missing old range: @@ -1 +1 @@'
run ts-tmpl "{path} = foo/bar.ts" \
  -C "$FIX" "cannot read 'foo/bar.ts' (code 2)"
run spaces-dir "ugly/dir with spaces/t.rs" \
  -C "$FIX" 'weird filename said hello to world'
run shell "{HOST} = api.internal" \
  -C "$FIX" 'deploy failed for api.internal at prod'

json="$("$UNFMT" --json -C "$FIX" 'synthesizing untracked snapshot src/app.rs')"
if grep -q '"name": "1"' <<<"$json" && grep -q 'src/app.rs' <<<"$json"; then
  echo "ok  json"
else
  echo "FAIL json"
  echo "$json"
  fail=1
fi

# v0.2: prefixed logs, nested Swift quotes, joined multiline templates
run prefixed "prefix: 2026-08-19T23:50:01Z ERROR " \
  -C "$FIX" '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
run nested-swift "{enabled} = enabled" \
  -C "$FIX" 'camera presence enabled'
run multiline-join "{reason} = timeout" \
  -C "$FIX" 'transition focused → idle reason=timeout idle=12s'

set +e
"$UNFMT" --exact -C "$FIX" '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`' >/dev/null 2>&1
ec=$?
set -e
if [[ "$ec" -ne 1 ]]; then
  echo "FAIL exact-rejects-prefix: wanted 1 got $ec"
  fail=1
else
  echo "ok  exact-rejects-prefix"
fi

if [[ "$fail" -ne 0 ]]; then
  echo "demo failed"
  exit 1
fi
echo "demo ok"
exit 0
