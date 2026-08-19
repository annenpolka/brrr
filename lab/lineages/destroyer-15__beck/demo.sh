#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
BECK="${BECK:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-1108ac34ccbe/beck}"
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
FACET="${FACET:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7d8a55cd1699/facet}"
DEST="${DESTROY_ROOT:-/tmp/destroy-beck}"
mkdir -p "$DEST/fixtures"

PASS=0
FAIL=0
assert() {
  local name="$1"
  shift
  if "$@"; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name" >&2
  fi
}

jtrue() {
  local name="$1" file="$2" expr="$3"
  if python3 -c "import json,sys; r=json.load(open(sys.argv[1])); assert $expr, r" "$file"; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name ($expr)" >&2
  fi
}

TMP="$(mktemp -d "${TMPDIR:-/tmp}/destroy-beck-demo.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "======== 0. victim selftest (unpatched) ========"
"$BECK" --selftest

echo "======== 1. git fatal vs naive tee (gold) ========"
set +e
git -C /tmp status | tee "$TMP/tee0.out" | cat >"$TMP/tee1.out"
set -e
if grep -q 'fatal: not a git repository' "$TMP/tee0.out" "$TMP/tee1.out" 2>/dev/null; then
  echo "  FAIL naive tee unexpectedly saw the needle" >&2
  FAIL=$((FAIL + 1))
else
  PASS=$((PASS + 1))
  echo "  ok  naive tee | grep misses unpiped git stderr ($(wc -c < "$TMP/tee0.out") piped bytes)"
fi
"$BECK" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status | cat | cat' >"$TMP/stderr.json"
"$BECK" --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat | cat'
jtrue "stderr producer stage 0" "$TMP/stderr.json" "r['producer']['stage']==0"
jtrue "stderr stream is stderr" "$TMP/stderr.json" "r['producer']['stream']=='stderr'"
jtrue "stderr kind mint" "$TMP/stderr.json" "r['producer']['kind']=='mint'"
jtrue "stderr disagrees with tee" "$TMP/stderr.json" "r['disagrees_with_tee'] is True"
jtrue "stderr tee_sim miss" "$TMP/stderr.json" "r['tee_sim'] is None"

echo "======== 2. tiny JSON wrap glue @ (gold) ========"
"$BECK" --quiet --json --line 1 --sh \
  'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"' \
  >"$TMP/jq.json"
"$BECK" --quiet --line 1 --sh \
  'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"'
jtrue "jq wrap" "$TMP/jq.json" "r['producer']['kind']=='wrap' and r['producer']['stage']==1"
jtrue "jq glue @" "$TMP/jq.json" "any(p['text']=='@' and p['kind']=='glue' for p in r['pieces'])"

echo "======== 3. facet hole: kizu@0.7.0 vs notify-debouncer ========"
CARGO="$DEST/fixtures/kizu-cargo.json"
if [[ ! -s "$CARGO" ]] && [[ -f "$KIZU/Cargo.toml" ]] && command -v cargo >/dev/null; then
  cargo metadata --format-version 1 --offline --manifest-path "$KIZU/Cargo.toml" >"$CARGO"
fi
if [[ -s "$CARGO" ]] && command -v jq >/dev/null; then
  "$BECK" --quiet --timeout 30 --json --needle 'kizu@0.7.0' --sh \
    "cat $CARGO | jq -r '.packages[] | select(.name==\"kizu\") | .name + \"@\" + .version'" \
    >"$TMP/kizu-at.json"
  "$BECK" --quiet --timeout 30 --needle 'kizu@0.7.0' --sh \
    "cat $CARGO | jq -r '.packages[] | select(.name==\"kizu\") | .name + \"@\" + .version'"
  jtrue "construct wrap at jq" "$TMP/kizu-at.json" "r['producer']['kind']=='wrap'"
  jtrue "stolen @0.7.0 at 448982" "$TMP/kizu-at.json" \
    "any(p['text']=='@0.7.0' and p['byte']==448982 for p in r['pieces'])"
  if [[ -x "$FACET" ]]; then
    "$FACET" --quiet -n 'kizu@0.7.0' <"$CARGO" | tee "$TMP/facet.txt"
    assert "facet names glue @" grep -q "glue   '@'" "$TMP/facet.txt"
  else
    echo "  skip facet (missing $FACET)"
  fi
else
  echo "  skip cargo fixture"
fi

echo "======== 4. { } split (CANDIDATE claimed one outer stage) ========"
"$BECK" --quiet --json --needle Kizu --sh '{ printf kizu | tr k K; } | cat' >"$TMP/brace.json" || true
jtrue "brace miss" "$TMP/brace.json" "r['producer'] is None"
jtrue "brace three stages" "$TMP/brace.json" "len(r['stages'])==3"

echo "======== 5. --run + strips quotes vs --sh ========"
"$BECK" --quiet --json --needle 'hello world' --run -- printf '%s\n' 'hello world' + cat >"$TMP/run.json" || true
"$BECK" --quiet --json --needle 'hello world' --sh "printf '%s\n' 'hello world' | cat" >"$TMP/sh.json"
jtrue "--run + miss" "$TMP/run.json" "r['producer'] is None"
jtrue "--sh hit" "$TMP/sh.json" "r['producer'] is not None and r['producer']['kind']=='mint'"

echo "======== 6. overlapping remint classified carry ========"
"$BECK" --quiet --json --needle hi --sh 'printf hi | echo hi' >"$TMP/echo.json"
jtrue "echo later carry" "$TMP/echo.json" "any(x['kind']=='carry' and 'echo' in x['argv'] for x in r['later'])"

echo "======== 7. JSON trace round-trip ========"
"$BECK" --quiet --save "$TMP/fatal.json" --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status | cat' >"$TMP/live.txt"
"$BECK" --quiet --needle 'fatal: not a git repository' --trace "$TMP/fatal.json" >"$TMP/replay.txt"
assert "trace replay matches live" cmp -s "$TMP/live.txt" "$TMP/replay.txt"

echo "======== 8. empty mid-stage vs trailing pipe ========"
set +e
"$BECK" --quiet --needle x --sh 'echo a | | cat' >"$TMP/empty.out" 2>"$TMP/empty.err"
empty_rc=$?
set -e
assert "empty mid rc=2" test "$empty_rc" -eq 2
"$BECK" --quiet --json --needle hi --sh 'printf hi |' >"$TMP/trail.json"
jtrue "trailing pipe one stage" "$TMP/trail.json" "len(r['stages'])==1 and r['producer'] is not None"

echo "======== 9. mid-command 2>&1 loses stderr fd ========"
"$BECK" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp 2>&1 status | cat' >"$TMP/mid.json"
jtrue "mid 2>&1 reports stdout" "$TMP/mid.json" "r['producer']['stream']=='stdout'"
"$BECK" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status 2>&1 | cat' >"$TMP/trail2.json"
jtrue "trailing 2>&1 reports stderr" "$TMP/trail2.json" "r['producer']['stream']=='stderr'"

echo
echo "passed $PASS  failed $FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
