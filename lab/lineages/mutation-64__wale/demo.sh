#!/usr/bin/env bash
# End-to-end: gold COMMUTE/JAM/PR#7, locus-aware ECHO, markdown empty-before.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WALE="$ROOT/wale"
ANC="${ANC:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b56-ac5a-7b03-a99f-437a44b4b3bf}"
PLAIT="${PLAIT:-$ANC/plait}"
chmod +x "$WALE"

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

unanimous_of() {
  python3 -c 'import json,sys; print(json.load(sys.stdin)["unanimous"])'
}

pair_verdicts() {
  python3 -c 'import json,sys; print(" ".join(sorted({p["verdict"] for p in json.load(sys.stdin)["pairs"]})))'
}

echo "======== 1. selftest ========"
if "$WALE" --selftest; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/wale-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

echo "======== 2. gold: re-run ancestor, then match ========"
if [[ -x "$PLAIT" ]]; then
  set +e
  "$PLAIT" "$ROOT/fixtures/commute.jsonl" >/dev/null
  a_com=$?
  "$PLAIT" "$ROOT/fixtures/jam.jsonl" >/dev/null
  a_jam=$?
  "$PLAIT" "$ROOT/fixtures/cli-pr7.json" >/dev/null
  a_pr7=$?
  set -e
  assert_eq "ancestor commute rc=0" "$a_com" "0"
  assert_eq "ancestor jam rc=2" "$a_jam" "2"
  assert_eq "ancestor pr7 rc=0" "$a_pr7" "0"
else
  echo "  SKIP  ancestor plait not at $PLAIT"
fi

set +e
"$WALE" "$ROOT/fixtures/commute.jsonl" >/dev/null
w_com=$?
"$WALE" "$ROOT/fixtures/jam.jsonl" >/dev/null
w_jam=$?
"$WALE" "$ROOT/fixtures/cli-pr7.json" >/dev/null
w_pr7=$?
set -e
assert_eq "wale commute rc=0" "$w_com" "0"
assert_eq "wale jam rc=2" "$w_jam" "2"
assert_eq "wale pr7 rc=0" "$w_pr7" "0"

got="$("$WALE" --json --report-only "$ROOT/fixtures/commute.jsonl")"
assert_eq "commute unanimous" "$(printf '%s\n' "$got" | unanimous_of)" "PARALLEL"
assert_eq "commute pair" "$(printf '%s\n' "$got" | pair_verdicts)" "COMMUTE"
pretty="$("$WALE" --report-only "$ROOT/fixtures/commute.jsonl")"
assert_contains "commute pretty both ids" "$pretty" "#alice,#bob"

got="$("$WALE" --json --report-only "$ROOT/fixtures/jam.jsonl")"
assert_eq "jam unanimous" "$(printf '%s\n' "$got" | unanimous_of)" "JAMMED"
pretty="$("$WALE" --report-only "$ROOT/fixtures/cli-pr7.json")"
assert_contains "pr7 both comment ids" "$pretty" "#333030758,#333031216"
assert_contains "pr7 COMMUTE" "$pretty" "COMMUTE"

echo "======== 3. stack / split / echo-at-one-locus still replacement-algebra ========"
mkdir -p "$DEMO/stack"
printf 'alpha\nbeta\ngamma\n' > "$DEMO/stack/app.py"
set +e
"$WALE" --json -C "$DEMO/stack" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack.json"
st=$?
"$WALE" "$ROOT/fixtures/split.jsonl" >/dev/null
s_split=$?
"$WALE" "$ROOT/fixtures/echo.jsonl" >/dev/null
s_echo=$?
set -e
assert_eq "stack exit 0" "$st" "0"
assert_eq "stack SERIES" "$(unanimous_of < "$DEMO/stack.json")" "SERIES"
assert_eq "split exit 1" "$s_split" "1"
assert_eq "echo-same-locus exit 0" "$s_echo" "0"
assert_eq "echo unanimous" "$("$WALE" --json --report-only "$ROOT/fixtures/echo.jsonl" | unanimous_of)" "ECHO"

echo "======== 4. destroyer: duplicate-site same image is NOT ECHO-collapse ========"
mkdir -p "$DEMO/dup"
printf 'return 0\nkeep\nkeep\nkeep\nkeep\nkeep\nkeep\nkeep\nkeep\nreturn 0\n' > "$DEMO/dup/app.py"
"$WALE" --json -C "$DEMO/dup" "$ROOT/fixtures/echo-dup-sites.jsonl" > "$DEMO/dup.json"
python3 - "$DEMO/dup.json" << 'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["unanimous"] == "MULTI", r
assert r["pairs"][0]["verdict"] == "MULTI", r["pairs"]
assert "distinct loci" in r["pairs"][0]["reason"], r["pairs"][0]
c = r["components"][0]
for name, sch in c["schedules"].items():
    assert sch["ok"] is True, (name, sch)
    assert set(sch["order"]) == {"site1", "site2"}, (name, sch["order"])
# both sites rewritten: not ancestor leftover 4fad3e4d4674
assert c["schedules"]["line"]["digest"] == "8ebc1b8f61f9", c["schedules"]["line"]
print("  PASS  dup-sites MULTI apply-each digest=8ebc1b8f61f9")
PY
PASS=$((PASS + 1))

echo "======== 5. destroyer: markdown empty before is not SPLIT of disjoint ALPHA/GAMMA ========"
got="$("$WALE" --json --report-only "$ROOT/fixtures/md-commute-noquote.md")"
assert_eq "md-noquote unanimous" "$(printf '%s\n' "$got" | unanimous_of)" "PARALLEL"
assert_eq "md-noquote pair" "$(printf '%s\n' "$got" | pair_verdicts)" "COMMUTE"
gotj="$("$WALE" --json --report-only "$ROOT/fixtures/json-commute.jsonl")"
assert_eq "json-commute pair" "$(printf '%s\n' "$gotj" | pair_verdicts)" "COMMUTE"
gotq="$("$WALE" --json --report-only "$ROOT/fixtures/md-commute-quoted.md")"
assert_eq "md-quoted pair" "$(printf '%s\n' "$gotq" | pair_verdicts)" "COMMUTE"
set +e
"$WALE" "$ROOT/fixtures/md-split.md" >/dev/null
s_mdsplit=$?
set -e
assert_eq "md-split same-locus still exit 1" "$s_mdsplit" "1"
mkdir -p "$DEMO/mdnq"
printf 'alpha\nbeta\ngamma\n' > "$DEMO/mdnq/app.py"
"$WALE" --json -C "$DEMO/mdnq" "$ROOT/fixtures/md-commute-noquote.md" > "$DEMO/mdnq.json"
python3 - "$DEMO/mdnq.json" << 'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert r["unanimous"] == "PARALLEL", r
assert r["strands"][0]["recon"] == "none" and r["strands"][0]["before"] == []
c = r["components"][0]
assert c["same_tree"] is True
assert all(s["ok"] for s in c["schedules"].values())
print("  PASS  md-noquote apply same-tree (JSON of these edits is COMMUTE)")
PY
PASS=$((PASS + 1))
pretty="$("$WALE" --report-only -C "$DEMO/dup" "$ROOT/fixtures/echo-dup-sites.jsonl")"
assert_contains "dup-sites pretty MULTI" "$pretty" "MULTI"
assert_contains "dup-sites pretty applied both" "$pretty" "applied=["
assert_contains "dup-sites pretty site1" "$pretty" "site1"
assert_contains "dup-sites pretty site2" "$pretty" "site2"

echo "======== 6. real GitHub 100-comment stream still one PARALLEL of 3 ========"
got="$("$WALE" --json --report-only "$ROOT/fixtures/cli-cli-comments.json")"
assert_eq "100-stream 3 suggestions 1 plait" "$(printf '%s\n' "$got" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["n"], r["unanimous"], len(r["components"]))')" "3 PARALLEL 1"

echo
echo "======== summary ======== "
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
