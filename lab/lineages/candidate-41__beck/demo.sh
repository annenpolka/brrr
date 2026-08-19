#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/beck"
BECK="$ROOT/beck"

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"

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

TMP="$(mktemp -d "${TMPDIR:-/tmp}/beck-demo.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "======== 0. selftest ========"
"$BECK" --selftest

echo "======== 1. unpiped stderr vs naive tee | grep ========"
# What tee on the pipe actually sees:
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
echo "--- beck ---"
"$BECK" --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat | cat'
jtrue "stderr producer stage 0" "$TMP/stderr.json" "r['producer']['stage']==0"
jtrue "stderr stream is stderr" "$TMP/stderr.json" "r['producer']['stream']=='stderr'"
jtrue "stderr kind mint" "$TMP/stderr.json" "r['producer']['kind']=='mint'"
jtrue "stderr disagrees with tee" "$TMP/stderr.json" "r['disagrees_with_tee'] is True"
jtrue "stderr tee_sim miss" "$TMP/stderr.json" "r['tee_sim'] is None"

echo "======== 2. wrap: sed prefix vs tee exact ========"
printf '%s\n' 'not a git repository' | tee "$TMP/w0.out" | sed 's/^/fatal: /' | tee "$TMP/w1.out" | cat >"$TMP/w2.out"
if grep -q 'fatal: not a git repository' "$TMP/w0.out"; then
  echo "  FAIL tee dump 0 already has exact needle" >&2
  FAIL=$((FAIL + 1))
else
  PASS=$((PASS + 1))
  echo "  ok  tee dump 0 lacks exact needle"
fi
assert "tee dump 1 has exact needle (would name sed)" grep -q 'fatal: not a git repository' "$TMP/w1.out"

"$BECK" --quiet --json --needle 'fatal: not a git repository' \
  --sh "printf '%s\n' 'not a git repository' | sed 's/^/fatal: /' | cat" >"$TMP/wrap.json"
echo "--- beck ---"
"$BECK" --quiet --needle 'fatal: not a git repository' \
  --sh "printf '%s\n' 'not a git repository' | sed 's/^/fatal: /' | cat"
jtrue "wrap producer stage 1" "$TMP/wrap.json" "r['producer']['stage']==1"
jtrue "wrap kind wrap" "$TMP/wrap.json" "r['producer']['kind']=='wrap'"
jtrue "wrap disagrees with tee" "$TMP/wrap.json" "r['disagrees_with_tee'] is True"
jtrue "wrap pieces include payload" "$TMP/wrap.json" "any(p['text']=='not a git repository' for p in r['pieces'] if p['kind']=='from')"
jtrue "wrap glue has fatal:" "$TMP/wrap.json" "any('fatal:' in p['text'] for p in r['pieces'] if p['kind']=='glue')"

echo "======== 3. quoted pipe is not a stage cut ========"
"$BECK" --quiet --json --needle 'a|b' --sh 'awk '"'"'BEGIN{print "a|b"}'"'"' | cat' >"$TMP/quote.json"
jtrue "quoted pipe two stages" "$TMP/quote.json" "len(r['stages'])==2"
jtrue "quoted pipe mint awk" "$TMP/quote.json" "r['producer']['stage']==0 and 'awk' in r['producer']['argv']"

echo "======== 4. jq concat pieces (the object tee cannot name) ========"
"$BECK" --quiet --json --line 1 --sh \
  'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"' \
  >"$TMP/jq.json"
echo "--- beck ---"
"$BECK" --quiet --line 1 --sh \
  'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"'
jtrue "jq wrap" "$TMP/jq.json" "r['producer']['kind']=='wrap' and r['producer']['stage']==1"
jtrue "jq piece kizu" "$TMP/jq.json" "any(p['text']=='kizu' and p['kind']=='from' for p in r['pieces'])"
jtrue "jq piece 0.7.0" "$TMP/jq.json" "any(p['text']=='0.7.0' and p['kind']=='from' for p in r['pieces'])"
jtrue "jq glue @" "$TMP/jq.json" "any(p['text']=='@' and p['kind']=='glue' for p in r['pieces'])"
jtrue "jq disagrees with tee" "$TMP/jq.json" "r['disagrees_with_tee'] is True"

echo "======== 5. 2>&1 still names stderr origin ========"
"$BECK" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status 2>&1 | cat' >"$TMP/merge.json"
jtrue "2>&1 producer stderr" "$TMP/merge.json" "r['producer']['stage']==0 and r['producer']['stream']=='stderr'"
jtrue "2>&1 tee sees piped" "$TMP/merge.json" "r['tee_sim'] is not None and r['tee_sim']['stage']==0"

echo "======== 6. trace save / replay ========"
"$BECK" --quiet --save "$TMP/run.json" --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status | cat' >"$TMP/live.txt"
"$BECK" --quiet --needle 'fatal: not a git repository' --trace "$TMP/run.json" >"$TMP/replay.txt"
assert "trace replay matches live" cmp -s "$TMP/live.txt" "$TMP/replay.txt"

echo "======== 7. kizu git log | rg | head ========"
if [[ -d "$KIZU/.git" ]]; then
  "$BECK" --quiet --cwd "$KIZU" --json --needle 'release: v0.7.0' \
    --sh 'git log --oneline | rg release | head -5' >"$TMP/kizu-log.json"
  echo "--- beck ---"
  "$BECK" --quiet --cwd "$KIZU" --needle 'release: v0.7.0' \
    --sh 'git log --oneline | rg release | head -5'
  jtrue "kizu log mint git" "$TMP/kizu-log.json" "r['producer']['stage']==0 and r['producer']['kind']=='mint'"
  jtrue "kizu log later rg carry" "$TMP/kizu-log.json" "any(x['kind']=='carry' and 'rg' in x['argv'] for x in r['later'])"
  "$BECK" --quiet --cwd "$KIZU" --json --line 1 \
    --sh 'git log --oneline | rg "^9349dc5"' >"$TMP/kizu-line.json"
  jtrue "kizu --line 1 from git" "$TMP/kizu-line.json" "r['producer']['stage']==0 and '9349dc5' in r['needle']"
else
  echo "  skip kizu (missing $KIZU)"
fi

echo "======== 8. kizu cargo metadata | jq ========"
if [[ -d "$KIZU" ]] && command -v cargo >/dev/null && command -v jq >/dev/null; then
  "$BECK" --quiet --cwd "$KIZU" --timeout 30 --json --needle '0.7.0' \
    --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | .version"' \
    >"$TMP/kizu-ver.json"
  echo "--- extract version ---"
  "$BECK" --quiet --cwd "$KIZU" --timeout 30 --needle '0.7.0' \
    --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | .version"'
  jtrue "version first in cargo JSON" "$TMP/kizu-ver.json" "r['producer']['stage']==0 and 'cargo' in r['producer']['argv']"

  echo "--- construct kizu@0.7.0 ---"
  "$BECK" --quiet --cwd "$KIZU" --timeout 30 --json --needle 'kizu@0.7.0' \
    --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | \"kizu@\" + .version"' \
    >"$TMP/kizu-at.json"
  "$BECK" --quiet --cwd "$KIZU" --timeout 30 --needle 'kizu@0.7.0' \
    --sh 'cargo metadata --format-version 1 --offline | jq -r ".packages[] | select(.name==\"kizu\") | \"kizu@\" + .version"'
  jtrue "construct wrap at jq" "$TMP/kizu-at.json" "r['producer']['kind']=='wrap' and r['producer']['stage']==1"
  jtrue "construct piece kizu from cargo" "$TMP/kizu-at.json" "any(p['kind']=='from' and p['text']=='kizu' and p['stage']==0 for p in r['pieces'])"
  jtrue "construct disagrees with tee" "$TMP/kizu-at.json" "r['disagrees_with_tee'] is True"
else
  echo "  skip cargo/jq dogfood"
fi

echo "======== 9. sitbone git log | rg ========"
if [[ -d "$SITBONE/.git" ]]; then
  "$BECK" --quiet --cwd "$SITBONE" --json --needle 'dual-threshold hysteresis' \
    --sh 'git log --oneline | rg hysteresis | cat' >"$TMP/sit.json"
  echo "--- beck ---"
  "$BECK" --quiet --cwd "$SITBONE" --needle 'dual-threshold hysteresis' \
    --sh 'git log --oneline | rg hysteresis | cat'
  jtrue "sitbone mint git log" "$TMP/sit.json" "r['producer']['stage']==0 and 'git log' in r['producer']['argv']"
  jtrue "sitbone rg carry" "$TMP/sit.json" "any(x['kind']=='carry' and 'rg' in x['argv'] for x in r['later'])"
else
  echo "  skip sitbone (missing $SITBONE)"
fi

echo "======== 10. stdin carry (outside the pipeline) ========"
printf 'hello-from-outside\n' | "$BECK" --quiet --json --stdin --needle 'hello-from-outside' \
  --sh 'cat | cat' >"$TMP/stdin.json"
jtrue "stdin carry stage 0" "$TMP/stdin.json" "r['producer']['kind']=='carry' and r['from_stdin'] is True"

echo
echo "passed $PASS  failed $FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
