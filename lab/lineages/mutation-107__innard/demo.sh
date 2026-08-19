#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/innard"
INNARD="$ROOT/innard"

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

TMP="$(mktemp -d "${TMPDIR:-/tmp}/innard-demo.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "======== 0. selftest ========"
"$INNARD" --selftest

echo "======== 1. gold: unpiped stderr vs naive tee | grep ========"
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

"$INNARD" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status | cat | cat' >"$TMP/stderr.json"
echo "--- innard ---"
"$INNARD" --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat | cat'
jtrue "stderr producer path 0" "$TMP/stderr.json" "r['producer']['path']=='0'"
jtrue "stderr stream is stderr" "$TMP/stderr.json" "r['producer']['stream']=='stderr'"
jtrue "stderr kind mint" "$TMP/stderr.json" "r['producer']['kind']=='mint'"
jtrue "stderr nest is outer" "$TMP/stderr.json" "r['producer']['nest'] is None"
jtrue "stderr disagrees with tee" "$TMP/stderr.json" "r['disagrees_with_tee'] is True"
jtrue "stderr tee_sim miss" "$TMP/stderr.json" "r['tee_sim'] is None"
jtrue "stderr piped_bytes 0" "$TMP/stderr.json" "r['stages'][0]['piped_bytes']==0"

echo "======== 2. inner \$() ≠ outer wrap lie ========"
"$INNARD" --quiet --json --needle 'Kizu' \
  --sh 'echo $(printf kizu | tr k K) | cat' >"$TMP/dollar.json"
echo "--- innard Kizu ---"
"$INNARD" --quiet --needle 'Kizu' --sh 'echo $(printf kizu | tr k K) | cat'
jtrue "\$() nest" "$TMP/dollar.json" "r['producer']['nest']=='\$()'"
jtrue "\$() producer is tr" "$TMP/dollar.json" "'tr' in r['producer']['argv']"
jtrue "\$() path is inner" "$TMP/dollar.json" "r['producer']['path'].startswith('0.')"
jtrue "\$() not the echo wrap" "$TMP/dollar.json" "'echo' not in r['producer']['argv']"
jtrue "\$() tee names echo" "$TMP/dollar.json" "r['tee_sim'] is not None and 'echo' in r['tee_sim']['argv'] and r['tee_sim']['nest'] is None"
jtrue "\$() disagrees with tee" "$TMP/dollar.json" "r['disagrees_with_tee'] is True"

"$INNARD" --quiet --json --needle 'kizu' \
  --sh 'echo $(printf kizu | tr k K) | cat' >"$TMP/dollar-k.json"
echo "--- innard kizu ---"
"$INNARD" --quiet --needle 'kizu' --sh 'echo $(printf kizu | tr k K) | cat'
jtrue "\$() kizu is printf" "$TMP/dollar-k.json" "r['producer']['nest']=='\$()' and 'printf' in r['producer']['argv']"

echo "======== 3. mid-command 2>&1 is stderr merge at that stage ========"
"$INNARD" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp 2>&1 status | cat' >"$TMP/mid.json"
echo "--- innard mid 2>&1 ---"
"$INNARD" --quiet --needle 'fatal: not a git repository' --sh 'git -C /tmp 2>&1 status | cat'
jtrue "mid 2>&1 stream stderr" "$TMP/mid.json" "r['producer']['stream']=='stderr'"
jtrue "mid 2>&1 merge" "$TMP/mid.json" "any(s['merge_stderr'] and 'git' in s['argv'] for s in r['stages'] if s['nest'] is None)"
jtrue "mid 2>&1 tee sees pipe" "$TMP/mid.json" "r['tee_sim'] is not None"
jtrue "mid 2>&1 argv has no leftover 2>&1" "$TMP/mid.json" "'2>&1' not in r['producer']['argv']"

echo "======== 4. trailing 2>&1 still names stderr ========"
"$INNARD" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status 2>&1 | cat' >"$TMP/trail.json"
jtrue "trailing 2>&1 producer stderr" "$TMP/trail.json" "r['producer']['stage']==0 and r['producer']['stream']=='stderr' or r['producer']['stream']=='stderr'"
jtrue "trailing 2>&1 tee sees piped" "$TMP/trail.json" "r['tee_sim'] is not None"

echo "======== 5. bash -c and <() inner ========"
"$INNARD" --quiet --json --needle b --sh "bash -c 'printf a | sed s/a/b/' | cat" >"$TMP/bashc.json"
echo "--- innard bash -c ---"
"$INNARD" --quiet --needle b --sh "bash -c 'printf a | sed s/a/b/' | cat"
jtrue "bash -c nest" "$TMP/bashc.json" "r['producer']['nest']=='bash -c' and 'sed' in r['producer']['argv']"

"$INNARD" --quiet --json --needle b --sh 'cat <(printf a | tr a b) | cat' >"$TMP/proc.json"
echo "--- innard <() ---"
"$INNARD" --quiet --needle b --sh 'cat <(printf a | tr a b) | cat'
jtrue "<() nest tr" "$TMP/proc.json" "r['producer']['nest']=='<()' and r['producer']['argv'].startswith('tr')"

echo "======== 6. wrap: sed prefix vs tee exact ========"
"$INNARD" --quiet --json --needle 'fatal: not a git repository' \
  --sh "printf '%s\n' 'not a git repository' | sed 's/^/fatal: /' | cat" >"$TMP/wrap.json"
echo "--- innard sed wrap ---"
"$INNARD" --quiet --needle 'fatal: not a git repository' \
  --sh "printf '%s\n' 'not a git repository' | sed 's/^/fatal: /' | cat"
jtrue "wrap kind wrap" "$TMP/wrap.json" "r['producer']['kind']=='wrap' and 'sed' in r['producer']['argv']"
jtrue "wrap pieces include payload" "$TMP/wrap.json" "any(p['text']=='not a git repository' for p in r['pieces'] if p['kind']=='from')"
jtrue "wrap glue has fatal:" "$TMP/wrap.json" "any('fatal:' in p['text'] for p in r['pieces'] if p['kind']=='glue')"

echo "======== 7. jq concat pieces ========"
"$INNARD" --quiet --json --line 1 --sh \
  'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"' \
  >"$TMP/jq.json"
echo "--- innard ---"
"$INNARD" --quiet --line 1 --sh \
  'printf "%s\n" "{\"name\":\"kizu\",\"version\":\"0.7.0\"}" | jq -r ".name + \"@\" + .version"'
jtrue "jq wrap" "$TMP/jq.json" "r['producer']['kind']=='wrap' and 'jq' in r['producer']['argv']"
jtrue "jq piece kizu" "$TMP/jq.json" "any(p['text']=='kizu' and p['kind']=='from' for p in r['pieces'])"
jtrue "jq glue @" "$TMP/jq.json" "any(p['text']=='@' and p['kind']=='glue' for p in r['pieces'])"

echo "======== 8. trace save / replay ========"
"$INNARD" --quiet --save "$TMP/run.json" --needle 'fatal: not a git repository' \
  --sh 'git -C /tmp status | cat' >"$TMP/live.txt"
"$INNARD" --quiet --needle 'fatal: not a git repository' --trace "$TMP/run.json" >"$TMP/replay.txt"
assert "trace replay matches live" cmp -s "$TMP/live.txt" "$TMP/replay.txt"

echo "======== 9. kizu git log | rg | head ========"
if [[ -d "$KIZU/.git" ]]; then
  "$INNARD" --quiet --cwd "$KIZU" --json --needle 'release: v0.7.0' \
    --sh 'git log --oneline | rg release | head -5' >"$TMP/kizu-log.json"
  echo "--- innard ---"
  "$INNARD" --quiet --cwd "$KIZU" --needle 'release: v0.7.0' \
    --sh 'git log --oneline | rg release | head -5'
  jtrue "kizu log mint git" "$TMP/kizu-log.json" "r['producer']['kind']=='mint' and 'git log' in r['producer']['argv']"
  jtrue "kizu log later rg carry" "$TMP/kizu-log.json" "any(x['kind']=='carry' and 'rg' in x['argv'] for x in r['later'])"
  "$INNARD" --quiet --cwd "$KIZU" --json --needle 'release: v0.7.0' \
    --sh 'echo "$(git log --oneline | rg release | head -1)"' >"$TMP/kizu-dollar.json"
  echo "--- innard kizu inside \$() ---"
  "$INNARD" --quiet --cwd "$KIZU" --needle 'release: v0.7.0' \
    --sh 'echo "$(git log --oneline | rg release | head -1)"'
  jtrue "kizu \$() mint git not echo" "$TMP/kizu-dollar.json" "r['producer']['nest']=='\$()' and 'git log' in r['producer']['argv']"
else
  echo "  skip kizu (missing $KIZU)"
fi

echo "======== 10. sitbone git log | rg ========"
if [[ -d "$SITBONE/.git" ]]; then
  "$INNARD" --quiet --cwd "$SITBONE" --json --needle 'dual-threshold hysteresis' \
    --sh 'git log --oneline | rg hysteresis | cat' >"$TMP/sit.json"
  echo "--- innard ---"
  "$INNARD" --quiet --cwd "$SITBONE" --needle 'dual-threshold hysteresis' \
    --sh 'git log --oneline | rg hysteresis | cat'
  jtrue "sitbone mint git log" "$TMP/sit.json" "'git log' in r['producer']['argv'] and r['producer']['kind']=='mint'"
else
  echo "  skip sitbone (missing $SITBONE)"
fi

echo "======== 11. \$() git fatal is inner stderr leak, not remint ========"
"$INNARD" --quiet --json --needle 'fatal: not a git repository' \
  --sh 'echo $(git -C /tmp status) | cat' >"$TMP/dollar-fatal.json"
echo "--- innard \$() git fatal ---"
"$INNARD" --quiet --needle 'fatal: not a git repository' \
  --sh 'echo $(git -C /tmp status) | cat'
jtrue "\$() fatal nest git" "$TMP/dollar-fatal.json" "r['producer']['nest']=='\$()' and 'git' in r['producer']['argv'] and r['producer']['stream']=='stderr'"
jtrue "\$() fatal tee miss" "$TMP/dollar-fatal.json" "r['tee_sim'] is None"
jtrue "\$() fatal later leak not remint" "$TMP/dollar-fatal.json" "any(x['kind']=='leak' and x['stream']=='stderr' and 'echo' in x['argv'] for x in r['later']) and not any(x['kind']=='remint' and x['stream']=='stderr' for x in r['later'])"

echo "======== 12. stdin carry ========"
printf 'hello-from-outside\n' | "$INNARD" --quiet --json --stdin --needle 'hello-from-outside' \
  --sh 'cat | cat' >"$TMP/stdin.json"
jtrue "stdin carry stage 0" "$TMP/stdin.json" "r['producer']['kind']=='carry' and r['from_stdin'] is True"

echo
echo "passed $PASS  failed $FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
