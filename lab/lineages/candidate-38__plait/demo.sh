#!/usr/bin/env bash
# End-to-end: algebra fixtures, apply witnesses, real GitHub streams, kizu file.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
PLAIT="$ROOT/plait"
chmod +x "$PLAIT"

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
    bad "$name" "missing '$needle' in: ${hay:0:200}"
  fi
}

unanimous_of() {
  python3 -c 'import json,sys; print(json.load(sys.stdin)["unanimous"])'
}

comp_n() {
  python3 -c 'import json,sys; print(len(json.load(sys.stdin)["components"]))'
}

pair_verdicts() {
  python3 -c 'import json,sys; print(" ".join(sorted({p["verdict"] for p in json.load(sys.stdin)["pairs"]})))'
}

sched_ok() {
  python3 -c 'import json,sys; r=json.load(sys.stdin); c=r["components"][0]["schedules"]; print(" ".join(k+(":"+"ok" if v["ok"] else ":fail") for k,v in c.items()))'
}

same_tree() {
  python3 -c 'import json,sys; print(json.load(sys.stdin)["components"][0]["same_tree"])'
}

echo "======== 1. selftest ========"
if "$PLAIT" --selftest; then
  ok "selftest"
else
  bad "selftest" "exit $?"
fi

DEMO="$(mktemp -d "${TMPDIR:-/tmp}/plait-demo.XXXXXX")"
cleanup() { rm -rf "$DEMO"; }
trap cleanup EXIT

echo "======== 2. commute: two suggestions, one PARALLEL plait ========"
mkdir -p "$DEMO/commute"
printf 'alpha\nbeta\ngamma\n' > "$DEMO/commute/app.py"
"$PLAIT" --json --report-only -C "$DEMO/commute" "$ROOT/fixtures/commute.jsonl" > "$DEMO/commute.json"
assert_eq "commute unanimous" "$(unanimous_of < "$DEMO/commute.json")" "PARALLEL"
assert_eq "commute one plait" "$(comp_n < "$DEMO/commute.json")" "1"
assert_eq "commute pair" "$(pair_verdicts < "$DEMO/commute.json")" "COMMUTE"
assert_eq "commute same-tree" "$(same_tree < "$DEMO/commute.json")" "True"
assert_contains "commute time+line ok" "$(sched_ok < "$DEMO/commute.json")" "line:ok"
assert_contains "commute topo ok" "$(sched_ok < "$DEMO/commute.json")" "topo:ok"
got="$("$PLAIT" --report-only "$ROOT/fixtures/commute.jsonl")"
assert_contains "commute pretty both ids" "$got" "#alice,#bob"

echo "======== 3. stack: topo applies; inverted time does not ========"
mkdir -p "$DEMO/stack"
printf 'alpha\nbeta\ngamma\n' > "$DEMO/stack/app.py"
set +e
"$PLAIT" --json -C "$DEMO/stack" "$ROOT/fixtures/stack.jsonl" > "$DEMO/stack.json"
st=$?
set -e
assert_eq "stack exit 0 (SERIES is composable)" "$st" "0"
assert_eq "stack unanimous" "$(unanimous_of < "$DEMO/stack.json")" "SERIES"
python3 - "$DEMO/stack.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
c=r["components"][0]
assert c["verdict"]=="SERIES", c
assert c["schedules"]["topo"]["ok"] is True
assert c["schedules"]["time"]["ok"] is False, c["schedules"]["time"]
assert c["same_tree"] is False
print("  PASS  stack topo-ok time-fail different-trees")
PY
PASS=$((PASS + 1))

echo "======== 4. split / jam / echo / subsume exits ========"
set +e
"$PLAIT" --report-only "$ROOT/fixtures/split.jsonl" >/dev/null
# report-only forces 0; without it:
"$PLAIT" "$ROOT/fixtures/split.jsonl" >/dev/null
s_split=$?
"$PLAIT" "$ROOT/fixtures/jam.jsonl" >/dev/null
s_jam=$?
"$PLAIT" "$ROOT/fixtures/echo.jsonl" >/dev/null
s_echo=$?
"$PLAIT" "$ROOT/fixtures/subsume.jsonl" >/dev/null
s_sub=$?
"$PLAIT" "$ROOT/fixtures/commute.jsonl" >/dev/null
s_com=$?
set -e
assert_eq "split exit 1" "$s_split" "1"
assert_eq "jam exit 2" "$s_jam" "2"
assert_eq "echo exit 0" "$s_echo" "0"
assert_eq "subsume exit 0" "$s_sub" "0"
assert_eq "commute exit 0" "$s_com" "0"
assert_eq "echo verdict" "$("$PLAIT" --json --report-only "$ROOT/fixtures/echo.jsonl" | unanimous_of)" "ECHO"
assert_eq "jam verdict" "$("$PLAIT" --json --report-only "$ROOT/fixtures/jam.jsonl" | unanimous_of)" "JAMMED"
assert_eq "split verdict" "$("$PLAIT" --json --report-only "$ROOT/fixtures/split.jsonl" | unanimous_of)" "SPLIT"
assert_eq "subsume verdict" "$("$PLAIT" --json --report-only "$ROOT/fixtures/subsume.jsonl" | unanimous_of)" "SUBSUME"

echo "======== 5. time-order must shift lower spans ========"
mkdir -p "$DEMO/shift"
printf 'a\nb\nc\nd\n' > "$DEMO/shift/app.py"
"$PLAIT" --json --report-only -C "$DEMO/shift" "$ROOT/fixtures/shift.jsonl" > "$DEMO/shift.json"
assert_eq "shift same-tree" "$(same_tree < "$DEMO/shift.json")" "True"
python3 - "$DEMO/shift.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
# reconstruct is in schedules; digest equality is same_tree
c=r["components"][0]
assert c["schedules"]["time"]["ok"] and c["schedules"]["line"]["ok"]
assert c["schedules"]["time"]["digest"]==c["schedules"]["line"]["digest"]
print("  PASS  shift time digest == line digest")
PY
PASS=$((PASS + 1))

echo "======== 6. markdown stream ========"
got="$("$PLAIT" --json --report-only "$ROOT/fixtures/stream.md")"
assert_eq "md commute" "$(printf '%s\n' "$got" | unanimous_of)" "PARALLEL"
assert_eq "md n=2" "$(printf '%s\n' "$got" | python3 -c 'import json,sys; print(json.load(sys.stdin)["n"])')" "2"

echo "======== 7. real GitHub: cli/cli PR #7 ========"
got="$("$PLAIT" --json --report-only "$ROOT/fixtures/cli-pr7.json")"
assert_eq "pr7 n=2 suggestions" "$(printf '%s\n' "$got" | python3 -c 'import json,sys; print(json.load(sys.stdin)["n"])')" "2"
assert_eq "pr7 one PARALLEL plait" "$(printf '%s\n' "$got" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["unanimous"], len(r["components"]))')" "PARALLEL 1"
pretty="$("$PLAIT" --report-only "$ROOT/fixtures/cli-pr7.json")"
assert_contains "pr7 both comment ids" "$pretty" "#333030758,#333031216"

echo "======== 8. real GitHub: 100 recent cli/cli review comments ========"
got="$("$PLAIT" --json --report-only "$ROOT/fixtures/cli-cli-comments.json")"
assert_eq "100-stream 3 suggestions 1 plait" "$(printf '%s\n' "$got" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["n"], r["unanimous"], len(r["components"]))')" "3 PARALLEL 1"

echo "======== 9. --remarks: threads, not O(n^2) COVER/DISJOINT ========"
pretty="$("$PLAIT" --remarks --report-only "$ROOT/fixtures/cli-pr7.json")"
assert_contains "pr7 remarks THREAD" "$pretty" "THREAD"
assert_contains "pr7 remarks hide disjoint" "$pretty" "DISJOINT hidden"
json="$("$PLAIT" --remarks --json --report-only "$ROOT/fixtures/cli-cli-comments.json")"
python3 - "$json" << 'PY'
import json,sys
r=json.loads(sys.argv[1]) if sys.argv[1].startswith("{") else json.load(open(sys.argv[1]))
# argv is the json string
PY
printf '%s\n' "$json" > "$DEMO/remarks100.json"
python3 - "$DEMO/remarks100.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r["n"]==100, r["n"]
assert r["component_counts"].get("THREAD"), r["component_counts"]
assert "COVER" not in r["component_counts"], r["component_counts"]
# DISJOINT stripped from pair listing
assert all(p["verdict"]!="DISJOINT" for p in r["pairs"]), "disjoint leaked"
# suggestions still one PARALLEL plait
pars=[c for c in r["components"] if c["verdict"]=="PARALLEL" and len(c["strands"])==3]
assert pars, r["components"]
print("  PASS  remarks-100 THREAD clusters, no COVER-on-replies, 3-sug PARALLEL intact")
PY
PASS=$((PASS + 1))

echo "======== 10. kizu git.rs: real file, overlapping vs commuting review ========"
KIZU_SRC="${KIZU_SRC:-$HOME/ghq/github.com/annenpolka/kizu/src/git.rs}"
if [[ -f "$KIZU_SRC" ]]; then
  mkdir -p "$DEMO/kizu/src"
  cp "$KIZU_SRC" "$DEMO/kizu/src/git.rs"
  python3 - "$DEMO/kizu/src/git.rs" "$DEMO/kizu/comments.jsonl" << 'PY'
import json,sys
path="src/git.rs"
lines=open(sys.argv[1]).read().splitlines()
# two commuting nits on distant exports
a,b=8,19  # 0-based: pub use diff / pub use types
out=open(sys.argv[2],"w")
json.dump({"id":"nit-diff","path":path,"start_line":a+1,"line":a+1,"before":[lines[a]],"after":[lines[a].replace("compute_diff,","")]}, out); out.write("\n")
json.dump({"id":"nit-types","path":path,"start_line":b+1,"line":b+1,"before":[lines[b]],"after":[lines[b].replace("DiffContent, ","")]}, out); out.write("\n")
# overlapping jam: rewrite the same pub use types block plus the next line
json.dump({"id":"wide-types","path":path,"start_line":b+1,"line":b+2,"before":lines[b:b+2],"after":["pub use types::{FileDiff, Hunk};"]}, out); out.write("\n")
PY
  "$PLAIT" --json --report-only -C "$DEMO/kizu" "$DEMO/kizu/comments.jsonl" > "$DEMO/kizu.json"
  python3 - "$DEMO/kizu.json" << 'PY'
import json,sys
r=json.load(open(sys.argv[1]))
verdicts=sorted({p["verdict"] for p in r["pairs"]})
assert "JAM" in verdicts, verdicts
assert "COMMUTE" in verdicts, verdicts
assert r["unanimous"]=="JAMMED", r
# apply of the whole file fails
sch=r["components"][0]["schedules"]
assert sch["line"]["ok"] is False
print("  PASS  kizu git.rs commute+jam → JAMMED, apply fails")
PY
  PASS=$((PASS + 1))
  # drop the overlapping third: remaining pair COMMUTES and applies
  python3 - "$DEMO/kizu/comments.jsonl" "$DEMO/kizu/two.jsonl" << 'PY'
import sys
src=open(sys.argv[1]).read().splitlines()
open(sys.argv[2],"w").write(src[0]+"\n"+src[1]+"\n")
PY
  "$PLAIT" --json --report-only -C "$DEMO/kizu" "$DEMO/kizu/two.jsonl" > "$DEMO/kizu2.json"
  assert_eq "kizu two nits PARALLEL" "$(unanimous_of < "$DEMO/kizu2.json")" "PARALLEL"
  assert_eq "kizu two nits apply" "$(same_tree < "$DEMO/kizu2.json")" "True"
else
  echo "  SKIP  kizu git.rs not at $KIZU_SRC"
fi

echo "======== 11. stdin pipe ========"
got="$(cat "$ROOT/fixtures/commute.jsonl" | "$PLAIT" --json --report-only)"
assert_eq "stdin commute" "$(printf '%s\n' "$got" | unanimous_of)" "PARALLEL"

echo
echo "======== summary ======== "
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
