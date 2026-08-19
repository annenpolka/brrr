#!/usr/bin/env bash
# Exercise spar: compose review suggestions, never occupy a tree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SPAR="$ROOT/spar"
chmod +x "$SPAR"
FIX="$ROOT/fixtures"

pass=0
fail=0

ok() {
  pass=$((pass + 1))
  echo "  PASS  $1"
}

bad() {
  fail=$((fail + 1))
  echo "  FAIL  $1"
  echo "        $2"
}

assert_eq() {
  local name="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    ok "$name"
  else
    bad "$name" "got=$got want=$want"
  fi
}

status_of() {
  "$SPAR" --porcelain --report-only "$@" | awk '/^status /{print $2; exit}'
}

json_status() {
  "$SPAR" --json --report-only "$@" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])'
}

echo "== selftest =="
if "$SPAR" --selftest; then
  ok "selftest"
else
  bad "selftest" "spar --selftest exited $?"
fi

echo "== fixture algebra (no tree) =="
assert_eq "commute jsonl" "$(status_of "$FIX/commute.jsonl")" "COMMUTE"
assert_eq "conflict jsonl" "$(status_of "$FIX/conflict.jsonl")" "CONFLICT"
assert_eq "absorb jsonl" "$(status_of "$FIX/absorb.jsonl")" "ABSORB"
assert_eq "ordered jsonl" "$(status_of "$FIX/ordered.jsonl")" "ORDERED"

echo "== two patches, not a commit =="
assert_eq "twain-halves COMMUTE" "$(status_of --patch "$FIX/oracle.patch" "$FIX/prod.patch")" "COMMUTE"
assert_eq "suffix-cut same file COMMUTE" "$(status_of --patch "$FIX/cut-prod.patch" "$FIX/cut-oracle.patch")" "COMMUTE"

echo "== emit composed patch =="
em="$("$SPAR" --emit --report-only --patch "$FIX/oracle.patch" "$FIX/prod.patch")"
if echo "$em" | grep -q 'tests/test_add.py' && echo "$em" | grep -q 'app.py'; then
  ok "emit concatenates oracle and prod"
else
  bad "emit concatenates oracle and prod" "$em"
fi
em2="$("$SPAR" --emit --report-only "$FIX/absorb.jsonl")"
if echo "$em2" | grep -q 'bias()' && ! echo "$em2" | grep -q 'tiny'; then
  ok "emit absorb is the outer rewrite"
else
  bad "emit absorb is the outer rewrite" "$em2"
fi

echo "== markdown stream =="
assert_eq "markdown two suggestions" "$(status_of "$FIX/stream.md")" "COMMUTE"

echo "== real GitHub comments =="
assert_eq "cli/cli PR7 pairwise" "$(status_of "$FIX/cli-pr7.json")" "COMMUTE"
assert_eq "golang iotest pair COMMUTE" "$(status_of "$FIX/iotest-pair.json")" "COMMUTE"

# iotest: same commit, lines 71 and 91 — the money shot GitHub will batch
note="$("$SPAR" --json --report-only "$FIX/iotest-pair.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["verdicts"][0]["note"])')"
assert_eq "iotest note is same-snapshot compose" "$note" "either-order"

# zip multiline reconstruction still a suggestion (single; pairwise EMPTY)
assert_eq "zip single is EMPTY pairwise" "$(status_of "$FIX/go-zip.json")" "EMPTY"

echo "== v0.2: pairwise stays inside original_commit_id =="
cli_pairs="$("$SPAR" --porcelain --report-only "$FIX/cli-pr7.json" | awk '/^pairs /{print $2}')"
assert_eq "cli-pr7 default pairs=1 (PR#24 dropped)" "$cli_pairs" "1"
cli_skip="$("$SPAR" --porcelain --report-only "$FIX/cli-pr7.json" | awk '/^skipped /{print $2}')"
assert_eq "cli-pr7 skipped 2 cross-commit" "$cli_skip" "2"
cli_all="$("$SPAR" --porcelain --report-only --all-commits "$FIX/cli-pr7.json" | awk '/^pairs /{print $2}')"
assert_eq "--all-commits restores 3" "$cli_all" "3"
# the remaining pair is the two PR#7 nil-return suggestions
cli_note="$("$SPAR" --json --report-only "$FIX/cli-pr7.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["verdicts"][0]["note"])')"
assert_eq "cli-pr7 remaining pair is either-order" "$cli_note" "either-order"

echo "== go-suggestions harvest (mixed PRs) =="
assert_eq "go-suggestions status" "$(status_of "$FIX/go-suggestions.json")" "COMMUTE"
go_pairs="$("$SPAR" --porcelain --report-only "$FIX/go-suggestions.json" | awk '/^pairs /{print $2}')"
assert_eq "go-suggestions grouped pairs=6" "$go_pairs" "6"
go_all="$("$SPAR" --porcelain --report-only --all-commits "$FIX/go-suggestions.json" | awk '/^pairs /{print $2}')"
assert_eq "go-suggestions --all-commits 120" "$go_all" "120"

echo "== exit codes =="
set +e
"$SPAR" "$FIX/commute.jsonl" >/dev/null
rc=$?
set -e
assert_eq "COMMUTE exit 0" "$rc" "0"
set +e
"$SPAR" "$FIX/ordered.jsonl" >/dev/null
rc=$?
set -e
assert_eq "ORDERED exit 1" "$rc" "1"
set +e
"$SPAR" "$FIX/conflict.jsonl" >/dev/null
rc=$?
set -e
assert_eq "CONFLICT exit 2" "$rc" "2"
set +e
"$SPAR" --report-only "$FIX/conflict.jsonl" >/dev/null
rc=$?
set -e
assert_eq "--report-only forces 0" "$rc" "0"
set +e
"$SPAR" "$FIX/absorb.jsonl" >/dev/null
rc=$?
set -e
assert_eq "nested ABSORB exit 1" "$rc" "1"

echo "== ugly unicode via jsonl =="
ugly="$FIX/ugly.jsonl"
cat > "$ugly" <<'EOF'
{"id":"a","path":"src/file with spaces.rs","start_line":2,"line":2,"before":["pub fn 加算(a: i32, b: i32) -> i32 { a + b }"],"after":["pub fn 加算(a: i32, b: i32) -> i32 { a + b + 1 }"]}
{"id":"b","path":"tests/加算_test.rs","start_line":1,"line":1,"before":["fn 加算_works() { assert_eq!(加算(1,1), 2); }"],"after":["fn 加算_works() { assert_eq!(加算(1,1), 3); }"]}
EOF
assert_eq "unicode paths COMMUTE" "$(status_of "$ugly")" "COMMUTE"

echo
echo "demo: $pass passed, $fail failed"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
