#!/usr/bin/env bash
# Compose first; occupy the fold; --emit that covering; git apply the fold.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
HANK="$ROOT/hank"
chmod +x "$HANK"

PASS=0
FAIL=0

ok() { PASS=$((PASS + 1)); echo "  PASS  $1"; }
bad() { FAIL=$((FAIL + 1)); echo "  FAIL  $1" >&2; echo "        $2" >&2; }

assert_eq() {
  local name="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    ok "$name"
  else
    bad "$name" "got=$got want=$want"
  fi
}

assert_contains() {
  local name="$1" hay="$2" needle="$3"
  if [[ "$hay" == *"$needle"* ]]; then
    ok "$name"
  else
    bad "$name" "missing '$needle' in: ${hay:0:240}"
  fi
}

assert_not_contains() {
  local name="$1" hay="$2" needle="$3"
  if [[ "$hay" != *"$needle"* ]]; then
    ok "$name"
  else
    bad "$name" "unexpected '$needle' in: ${hay:0:240}"
  fi
}

jget() {
  python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print(eval(sys.argv[2], {"r": r, "len": len}))' "$1" "$2"
}

echo "======== 1. selftest ========"
if "$HANK" --selftest; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/hank-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

echo "======== 2. gold COMMUTE occupy (one composed, not N rows) ========"
"$HANK" --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/commute.jsonl" > "$DEMO/commute.json"
assert_eq "commute compose" "$(jget "$DEMO/commute.json" 'r["compose"]')" "PARALLEL"
assert_eq "commute occupy" "$(jget "$DEMO/commute.json" 'r["occupy"]')" "PENDING"
assert_eq "commute one composed" "$(jget "$DEMO/commute.json" 'len(r["composed"])')" "1"
assert_eq "commute covering after" "$(jget "$DEMO/commute.json" 'r["composed"][0]["after"]')" "['ALPHA', 'beta', 'GAMMA']"

echo "======== 3. A already applied: SUPERSEDED of the covering ========"
"$HANK" --json -C "$ROOT/fixtures/trees/commute-a-only" "$ROOT/fixtures/commute.jsonl" > "$DEMO/aonly.json"
assert_eq "a-only occupy SUPERSEDED" "$(jget "$DEMO/aonly.json" 'r["occupy"]')" "SUPERSEDED"
"$HANK" --json -C "$ROOT/fixtures/trees/commute-applied" "$ROOT/fixtures/commute.jsonl" > "$DEMO/applied.json"
assert_eq "both-applied occupy APPLIED" "$(jget "$DEMO/applied.json" 'r["occupy"]')" "APPLIED"

echo "======== 4. JAM rc=2, no occupy, no emit ========"
set +e
"$HANK" "$ROOT/fixtures/jam.jsonl" >"$DEMO/jam.out" 2>"$DEMO/jam.err"
jam_rc=$?
"$HANK" --emit "$ROOT/fixtures/jam.jsonl" >"$DEMO/jam.emit" 2>"$DEMO/jam.emit.err"
jam_em=$?
set -e
assert_eq "jam exit 2" "$jam_rc" "2"
assert_eq "jam emit exit 2" "$jam_em" "2"
assert_eq "jam emit empty stdout" "$(cat "$DEMO/jam.emit")" ""
assert_contains "jam emit refused" "$(cat "$DEMO/jam.emit.err")" "not emitting"

echo "======== 5. SPLIT rc=1, replacement not union ========"
set +e
"$HANK" "$ROOT/fixtures/split.jsonl" >/dev/null
split_rc=$?
"$HANK" --emit "$ROOT/fixtures/same-line-overlap-same-after.jsonl" >/dev/null 2>"$DEMO/ov.err"
ov_rc=$?
set -e
assert_eq "split exit 1" "$split_rc" "1"
assert_eq "overlap same-join emit JAM" "$ov_rc" "2"

echo "======== 6. STACK occupy the fold ========"
"$HANK" --json -C "$ROOT/fixtures/trees/stack" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack.json"
assert_eq "stack compose SERIES" "$(jget "$DEMO/stack.json" 'r["compose"]')" "SERIES"
assert_eq "stack fold after" "$(jget "$DEMO/stack.json" 'r["composed"][0]["after"]')" "['beta3']"
"$HANK" --json -C "$ROOT/fixtures/trees/stack-mid" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack-mid.json"
assert_eq "stack mid SUPERSEDED of fold" "$(jget "$DEMO/stack-mid.json" 'r["occupy"]')" "SUPERSEDED"

echo "======== 7. ECHO is a locus; two sites commute ========"
"$HANK" --json -C "$ROOT/fixtures/trees/echo" "$ROOT/fixtures/echo.jsonl" > "$DEMO/echo.json"
assert_eq "echo compose" "$(jget "$DEMO/echo.json" 'r["compose"]')" "ECHO"
"$HANK" --json -C "$ROOT/fixtures/trees/dup-sites" "$ROOT/fixtures/echo-dup-sites.jsonl" > "$DEMO/dup.json"
assert_eq "dup-sites compose PARALLEL" "$(jget "$DEMO/dup.json" 'r["compose"]')" "PARALLEL"
assert_eq "dup-sites two parts" "$(jget "$DEMO/dup.json" 'len(r["composed"][0]["parts"])')" "2"

echo "======== 8. emit COMMUTE covering | git apply (one hunk, not two fences) ========"
mkdir -p "$DEMO/t-commute"
cp "$ROOT/fixtures/trees/commute/app.py" "$DEMO/t-commute/app.py"
"$HANK" --emit -C "$DEMO/t-commute" "$ROOT/fixtures/commute.jsonl" > "$DEMO/t-commute/fold.patch" 2>"$DEMO/t-commute.err"
assert_eq "commute emit hunks" "$(grep -c '^@@' "$DEMO/t-commute/fold.patch")" "1"
assert_contains "commute emit -alpha" "$(cat "$DEMO/t-commute/fold.patch")" "-alpha"
assert_contains "commute emit +ALPHA" "$(cat "$DEMO/t-commute/fold.patch")" "+ALPHA"
assert_contains "commute emit +GAMMA" "$(cat "$DEMO/t-commute/fold.patch")" "+GAMMA"
assert_contains "commute mixed keeps beta as context" "$(cat "$DEMO/t-commute/fold.patch")" $'\n beta\n'
assert_contains "commute occupy stderr" "$(cat "$DEMO/t-commute.err")" "occupy=PENDING"
( cd "$DEMO/t-commute" && git apply fold.patch )
assert_eq "commute applied file" "$(cat "$DEMO/t-commute/app.py")" $'ALPHA\nbeta\nGAMMA'

echo "======== 9. emit STACK fold | git apply (no beta2, not two rounds) ========"
mkdir -p "$DEMO/t-stack"
cp "$ROOT/fixtures/trees/stack/app.py" "$DEMO/t-stack/app.py"
"$HANK" --emit -C "$DEMO/t-stack" "$ROOT/fixtures/stack.jsonl" > "$DEMO/t-stack/fold.patch" 2>"$DEMO/t-stack.err"
assert_eq "stack emit hunks" "$(grep -c '^@@' "$DEMO/t-stack/fold.patch")" "1"
assert_contains "stack emit -beta" "$(cat "$DEMO/t-stack/fold.patch")" "-beta"
assert_contains "stack emit +beta3" "$(cat "$DEMO/t-stack/fold.patch")" "+beta3"
assert_not_contains "stack emit no intermediate" "$(cat "$DEMO/t-stack/fold.patch")" "beta2"
assert_contains "stack pad context alpha" "$(cat "$DEMO/t-stack/fold.patch")" $'\n alpha\n'
( cd "$DEMO/t-stack" && git apply fold.patch )
assert_eq "stack applied fold" "$(cat "$DEMO/t-stack/app.py")" $'alpha\nbeta3\ngamma'

echo "======== 10. emit without -C cannot paint a COMMUTE covering ========"
set +e
"$HANK" --emit "$ROOT/fixtures/commute.jsonl" >"$DEMO/noc.out" 2>"$DEMO/noc.err"
noc_rc=$?
set -e
assert_eq "commute emit without tree rc 3" "$noc_rc" "3"
assert_contains "need -C" "$(cat "$DEMO/noc.err")" "no covering"

echo "======== 11. a-only: emit the origin covering; apply must fail ========"
mkdir -p "$DEMO/t-aonly"
cp "$ROOT/fixtures/trees/commute-a-only/app.py" "$DEMO/t-aonly/app.py"
"$HANK" --emit -C "$DEMO/t-aonly" "$ROOT/fixtures/commute.jsonl" > "$DEMO/t-aonly/fold.patch" 2>"$DEMO/t-aonly.err"
assert_contains "a-only occupy SUPERSEDED" "$(cat "$DEMO/t-aonly.err")" "occupy=SUPERSEDED"
assert_contains "a-only still emits origin covering" "$(cat "$DEMO/t-aonly/fold.patch")" "-alpha"
set +e
( cd "$DEMO/t-aonly" && git apply fold.patch ) >/dev/null 2>&1
aonly_ap=$?
set -e
assert_eq "a-only apply fails (not the fold origin)" "$aonly_ap" "1"

echo "======== 12. subset SERIES fold apply ========"
mkdir -p "$DEMO/t-sub"
cp "$ROOT/fixtures/trees/insert-fn/app.py" "$DEMO/t-sub/app.py"
"$HANK" --emit -C "$DEMO/t-sub" "$ROOT/fixtures/stack-subset.jsonl" > "$DEMO/t-sub/fold.patch" 2>/dev/null
assert_not_contains "subset fold skips return 1" "$(cat "$DEMO/t-sub/fold.patch")" "return 1"
assert_contains "subset fold is return 2" "$(cat "$DEMO/t-sub/fold.patch")" "+    return 2"
( cd "$DEMO/t-sub" && git apply fold.patch )
assert_contains "subset file has return 2" "$(cat "$DEMO/t-sub/app.py")" "return 2"
assert_not_contains "subset file has no return 1" "$(cat "$DEMO/t-sub/app.py")" "return 1"

echo "======== 13. two-site ECHO-that-is-COMMUTE: one covering apply ========"
mkdir -p "$DEMO/t-dup"
cp "$ROOT/fixtures/trees/dup-sites/app.py" "$DEMO/t-dup/app.py"
"$HANK" --emit -C "$DEMO/t-dup" "$ROOT/fixtures/echo-dup-sites.jsonl" > "$DEMO/t-dup/fold.patch" 2>/dev/null
assert_eq "dup emit one file" "$(grep -c '^diff --git' "$DEMO/t-dup/fold.patch")" "1"
assert_contains "dup mixed context keep" "$(cat "$DEMO/t-dup/fold.patch")" $'\n keep\n'
( cd "$DEMO/t-dup" && git apply fold.patch )
assert_eq "dup both sites" "$(grep -c 'return 1' "$DEMO/t-dup/app.py")" "2"
assert_eq "dup no leftover return 0" "$(grep -c 'return 0' "$DEMO/t-dup/app.py" || true)" "0"

echo "======== 14. cli/cli PR #7 covering is one file, applyable ========"
mkdir -p "$DEMO/t-cli"
cp -R "$ROOT/fixtures/trees/cli-orig/." "$DEMO/t-cli/"
"$HANK" --emit -C "$DEMO/t-cli" "$ROOT/fixtures/cli-pr7.json" > "$DEMO/t-cli/fold.patch" 2>"$DEMO/t-cli.err"
assert_eq "cli emit one file (not N strand diffs)" "$(grep -c '^diff --git' "$DEMO/t-cli/fold.patch")" "1"
assert_contains "cli occupy PENDING" "$(cat "$DEMO/t-cli.err")" "occupy=PENDING"
assert_contains "cli minus 347 origin" "$(cat "$DEMO/t-cli/fold.patch")" "return &github.PullRequest{}, err"
assert_contains "cli plus 347 fold" "$(cat "$DEMO/t-cli/fold.patch")" "return nil, err"
assert_contains "cli plus 400 fold" "$(cat "$DEMO/t-cli/fold.patch")" "return nil, nil, nil, err"
( cd "$DEMO/t-cli" && git apply fold.patch )
assert_contains "cli site 347" "$(sed -n '347p' "$DEMO/t-cli/command/pr.go")" "return nil, err"
assert_contains "cli site 400" "$(sed -n '400p' "$DEMO/t-cli/command/pr.go")" "return nil, nil, nil, err"
# leftover identical return nil, err seven lines below must survive (locus slack)
assert_contains "cli locus slack leftover" "$(sed -n '354p' "$DEMO/t-cli/command/pr.go")" "return nil, err"

echo "======== 15. empty / binary / junk / TTY ========"
set +e
printf '' | "$HANK" - >/dev/null
empty_rc=$?
printf '\x00\xff' | "$HANK" - >/dev/null 2>"$DEMO/bin.err"
bin_rc=$?
printf '%s\n' '{"id":"a","path":"app.py","line":1,"before":["alpha"],"after":["ALPHA"]}' 'this is not json' | "$HANK" - >/dev/null 2>"$DEMO/junk.err"
junk_rc=$?
tty_out="$(python3 -c '
import pty, subprocess, sys
master, slave = pty.openpty()
p = subprocess.run([sys.argv[1]], stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(p.returncode)
' "$HANK")"
set -e
assert_eq "empty stdin rc 0" "$empty_rc" "0"
assert_eq "binary stdin rc 3" "$bin_rc" "3"
assert_eq "junk jsonl rc 3" "$junk_rc" "3"
assert_eq "TTY no args rc 3" "$tty_out" "3"

echo "======== 16. cycle JAM, shift covering, md-noquote covering ========"
set +e
"$HANK" --emit "$ROOT/fixtures/stack-cycle.jsonl" >/dev/null 2>"$DEMO/cyc.err"
cyc=$?
set -e
assert_eq "cycle emit exit 2" "$cyc" "2"
mkdir -p "$DEMO/t-shift"
cp "$ROOT/fixtures/trees/shift/app.py" "$DEMO/t-shift/app.py"
"$HANK" --emit -C "$DEMO/t-shift" "$ROOT/fixtures/shift.jsonl" > "$DEMO/t-shift/fold.patch" 2>/dev/null
( cd "$DEMO/t-shift" && git apply fold.patch )
assert_eq "shift applied" "$(cat "$DEMO/t-shift/app.py")" $'a\na2\nb\nc\nD'
"$HANK" --json -C "$ROOT/fixtures/trees/commute" "$ROOT/fixtures/md-commute-noquote.md" > "$DEMO/mdnq.json"
assert_eq "md-noquote occupy PENDING" "$(jget "$DEMO/mdnq.json" 'r["occupy"]')" "PENDING"

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
