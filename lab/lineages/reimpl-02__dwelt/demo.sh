#!/usr/bin/env bash
# Exercise dwelt against a synthetic ugly fixture and the real repos held was judged on.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DWELT="$ROOT/dwelt"
chmod +x "$DWELT"
ORIG="${ORIG:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-796f-76d0-988f-5c2c16399eaa/held}"

if [[ ! -x "$DWELT" ]]; then
  echo "demo: dwelt is not executable" >&2
  exit 2
fi

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

assert_eq() {
  local name="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name" >&2
    echo "       got:  $got" >&2
    echo "       want: $want" >&2
  fi
}

echo "== fixture: oscillating path, rename, weird names, nested git =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/dwelt-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "dwelt-demo"
git -C "$FIX" config user.email "dwelt@example.test"

mkdir -p "$FIX/nested/deep"
printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'born\n' > "$FIX/oscillate.txt"
printf 'ghost\n' > "$FIX/old name.txt"
printf 'hello\n' > "$FIX/nested/deep/weird (1).txt"
git -C "$FIX" add keep.txt oscillate.txt "old name.txt" "nested/deep/weird (1).txt"
git -C "$FIX" commit -q -m "t0: birth"

rm "$FIX/oscillate.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t1: kill oscillate"

printf 'reborn\n' > "$FIX/oscillate.txt"
printf 'keep\n' > "$FIX/keep.txt"
printf '計画\n' > "$FIX/計画.md"
git -C "$FIX" add oscillate.txt keep.txt "計画.md"
git -C "$FIX" commit -q -m "t2: revive oscillate, drop TOKEN_A"

git -C "$FIX" mv "old name.txt" "new name.txt"
git -C "$FIX" commit -q -m "t3: rename with spaces"

rm "$FIX/oscillate.txt"
printf 'other\nTOKEN_A\n' > "$FIX/other.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t4: kill oscillate, TOKEN_A reincarnates"

mkdir -p "$FIX/vendor/nested"
git -C "$FIX/vendor/nested" init -q -b inner
git -C "$FIX/vendor/nested" config user.name "dwelt-demo"
git -C "$FIX/vendor/nested" config user.email "dwelt@example.test"
echo inner > "$FIX/vendor/nested/inner.txt"
git -C "$FIX/vendor/nested" add inner.txt
git -C "$FIX/vendor/nested" commit -q -m "inner commit"
echo 'vendor-marker' > "$FIX/vendor/marker.txt"
git -C "$FIX" add vendor/marker.txt
git -C "$FIX" commit -q -m "t5: nested git + marker"

printf 'keep\n' > "$FIX/other.txt"
git -C "$FIX" add other.txt
git -C "$FIX" commit -q -m "t6: TOKEN_A gone again"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "7"

echo "-- exists oscillate.txt (should flip T F T F)"
OSC_JSON="$("$DWELT" -C "$FIX" --color never --json exists oscillate.txt || true)"
OSC_NOW="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(int(r["holds_now"]))' <<<"$OSC_JSON")"
OSC_TRUE="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["true_commits"])' <<<"$OSC_JSON")"
OSC_PATTERN="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$OSC_JSON")"
assert_eq "oscillate holds_now" "$OSC_NOW" "0"
assert_eq "oscillate true_commits" "$OSC_TRUE" "3"
assert_eq "oscillate era pattern" "$OSC_PATTERN" "TFTF"

echo "-- exists 'old name.txt' vs 'new name.txt' (rename is a path death)"
OLD_PAT="$("$DWELT" -C "$FIX" --oneline exists "old name.txt" || true)"
NEW_PAT="$("$DWELT" -C "$FIX" --oneline exists "new name.txt" || true)"
OLD_TF="$(awk '{printf $1}' <<<"$OLD_PAT" | tr -d '\n')"
NEW_TF="$(awk '{printf $1}' <<<"$NEW_PAT" | tr -d '\n')"
assert_eq "old name eras" "$OLD_TF" "TF"
assert_eq "new name eras" "$NEW_TF" "FT"

echo "-- exists Japanese path"
"$DWELT" -C "$FIX" -q exists "計画.md"
assert "計画.md holds now" true

echo "-- glob exists 'nested/deep/*'"
if "$DWELT" -C "$FIX" -q exists 'nested/deep/*'; then
  assert "glob exists now" true
else
  assert "glob exists now" false
fi

echo "-- grep TOKEN_A reincarnation (T F T F)"
TOK_JSON="$("$DWELT" -C "$FIX" --json grep TOKEN_A || true)"
TOK_PAT="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$TOK_JSON")"
assert_eq "TOKEN_A era pattern" "$TOK_PAT" "TFTF"

echo "-- grep witnesses move from keep.txt to other.txt"
WIT_START="$(python3 -c 'import json,sys; r=json.load(sys.stdin); trues=[e for e in r["eras"] if e["value"]]; print(trues[0]["witnesses_start"][0])' <<<"$TOK_JSON")"
WIT_LAST="$(python3 -c 'import json,sys; r=json.load(sys.stdin); trues=[e for e in r["eras"] if e["value"]]; print(trues[-1]["witnesses_end"][0])' <<<"$TOK_JSON")"
assert_eq "first TOKEN_A witness" "$WIT_START" "keep.txt"
assert_eq "last TOKEN_A witness" "$WIT_LAST" "other.txt"

echo "-- exec: wc -l keep.txt is 2 only while TOKEN_A lived there (t0-t1)"
EXEC_JSON="$("$DWELT" -C "$FIX" --json --timeout 5 exec -- sh -c 'test "$(wc -l < keep.txt)" -eq 2' || true)"
EXEC_PAT="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$EXEC_JSON")"
assert_eq "exec two-line keep.txt pattern" "$EXEC_PAT" "TF"

echo "-- --revs / --bounds / exit codes"
set +e
"$DWELT" -C "$FIX" -q exists oscillate.txt
OSC_RC=$?
"$DWELT" -C "$FIX" -q exists keep.txt
KEEP_RC=$?
"$DWELT" -C "$FIX" -q exists 'does-not-exist.xyz'
MISS_RC=$?
set -e
assert_eq "exists oscillate exit" "$OSC_RC" "1"
assert_eq "exists keep exit" "$KEEP_RC" "0"
assert_eq "exists missing exit" "$MISS_RC" "1"

REVS="$("$DWELT" -C "$FIX" --revs exists keep.txt)"
REVS_N="$(printf '%s\n' "$REVS" | grep -c .)"
assert_eq "keep.txt true revs == all commits" "$REVS_N" "7"

BOUNDS_N="$("$DWELT" -C "$FIX" --true-bounds exists oscillate.txt | grep -c . || true)"
assert_eq "oscillate true-bounds rows" "$BOUNDS_N" "2"

echo "-- --now sees an uncommitted resurrection"
printf 'dirty\n' > "$FIX/oscillate.txt"
NOW_JSON="$("$DWELT" -C "$FIX" --now --json exists oscillate.txt || true)"
NOW_HOLD="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(int(r["holds_now"]), r["eras"][-1]["end"]["kind"])' <<<"$NOW_JSON")"
assert_eq "uncommitted oscillate via --now" "$NOW_HOLD" "1 worktree"

echo "-- dead pathspec warns instead of silent never-held"
DEAD_JSON="$("$DWELT" -C "$FIX" --json grep TOKEN_A definitely-not-a-file || true)"
DEAD_WARN="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["warnings"][0] if r["warnings"] else "")' <<<"$DEAD_JSON")"
assert "dead pathspec warning" grep -q "definitely-not-a-file" <<<"$DEAD_WARN"
assert "dead pathspec suggests quoting" grep -q "dwelt grep 'TOKEN_A definitely-not-a-file'" <<<"$DEAD_WARN"

echo "-- wrong case hints -i"
CASE_JSON="$("$DWELT" -C "$FIX" --json grep token_a || true)"
CASE_HINT="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print((r["hints"] or [r["hint"] or ""])[0])' <<<"$CASE_JSON")"
assert "case-fold hint mentions -i" grep -q -- "-i" <<<"$CASE_HINT"

echo "-- first-parent TRUE starting at a merge names the off-mainline birth"
MERGE="$(mktemp -d "${TMPDIR:-/tmp}/dwelt-merge.XXXXXX")"
git -C "$MERGE" init -q -b main
git -C "$MERGE" config user.name "dwelt-demo"
git -C "$MERGE" config user.email "dwelt@example.test"
echo base > "$MERGE/base.txt"
git -C "$MERGE" add base.txt
git -C "$MERGE" commit -q -m "t0: skeleton"
git -C "$MERGE" checkout -q -b topic
echo secret > "$MERGE/secret.txt"
git -C "$MERGE" add secret.txt
git -C "$MERGE" commit -q -m "t1: birth on topic"
echo more >> "$MERGE/secret.txt"
git -C "$MERGE" add secret.txt
git -C "$MERGE" commit -q -m "t2: still on topic"
git -C "$MERGE" checkout -q main
git -C "$MERGE" merge -q --no-ff topic -m "t3: merge topic"
BIRTH="$(git -C "$MERGE" rev-list --reverse HEAD -- secret.txt | head -1 | cut -c1-7)"
MERGE_JSON="$("$DWELT" -C "$MERGE" --json exists secret.txt || true)"
MERGE_START="$(python3 -c 'import json,sys; r=json.load(sys.stdin); t=[e for e in r["eras"] if e["value"]][0]; print(t["start"]["subject"])' <<<"$MERGE_JSON")"
MERGE_ORIGIN="$(python3 -c 'import json,sys; r=json.load(sys.stdin); t=[e for e in r["eras"] if e["value"]][0]; print(t.get("origin",{}).get("short",""))' <<<"$MERGE_JSON")"
assert "merge-start subject is a merge" grep -q "merge topic" <<<"$MERGE_START"
assert_eq "merge origin is topic birth" "$MERGE_ORIGIN" "$BIRTH"
rm -rf "$MERGE"

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/dwelt-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$DWELT" -C "$EMPTY" exists README.md 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -q "empty" <<<"$EMPTY_ERR"

compare_json() {
  local name="$1" a="$2" b="$3"
  python3 - "$name" "$a" "$b" <<'PY'
import json, sys
name, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
A, B = json.loads(a), json.loads(b)
keys = ["holds_now", "never_held", "always_held", "commits_scanned", "reachable", "true_commits"]
bad = []
for k in keys:
    if A.get(k) != B.get(k):
        bad.append(f"{k}: orig={A.get(k)!r} dwelt={B.get(k)!r}")
def pat(r):
    return "".join("T" if e["value"] else "F" for e in r["eras"]), [e["count"] for e in r["eras"]]
pa, ca = pat(A)
pb, cb = pat(B)
if pa != pb:
    bad.append(f"era pattern: orig={pa} dwelt={pb}")
if ca != cb:
    bad.append(f"era counts: orig={ca} dwelt={cb}")
def bounds(r):
    out = []
    for e in r["eras"]:
        out.append((e["value"], e["count"], e["start"]["short"], e["end"]["short"]))
    return out
if bounds(A) != bounds(B):
    bad.append(f"era bounds: orig={bounds(A)} dwelt={bounds(B)}")
if bad:
    print("FAIL", name)
    for line in bad:
        print("      ", line)
    sys.exit(1)
print("ok", name)
sys.exit(0)
PY
}

echo
echo "== real repo: sitbone FocusRiverView (git log -- path is empty) =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- git log -- path (the footgun dwelt exists to replace)"
  LOG_N="$(git -C "$SITBONE" log --oneline -- Sources/SitboneUI/FocusRiverView.swift | grep -c . || true)"
  assert_eq "git log -- deleted-path is empty" "$LOG_N" "0"

  echo "-- first-parent exists (mainline never shipped the file)"
  FP_JSON="$("$DWELT" -C "$SITBONE" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  FP_NEVER="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(int(r["never_held"]))' <<<"$FP_JSON")"
  FP_HINT="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["hint"] or "")' <<<"$FP_JSON")"
  assert_eq "first-parent never_held" "$FP_NEVER" "1"
  assert "first-parent hint mentions --full" grep -q -- "--full" <<<"$FP_HINT"

  echo "-- first-parent grep also hints --full"
  GR_JSON="$("$DWELT" -C "$SITBONE" --json grep FocusRiverView || true)"
  GR_HINT="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(" ".join(r.get("hints") or ([r["hint"]] if r.get("hint") else [])))' <<<"$GR_JSON")"
  assert "first-parent grep hint mentions --full" grep -q -- "--full" <<<"$GR_HINT"

  echo "-- --full exists (side-history island)"
  FULL_JSON="$("$DWELT" -C "$SITBONE" --full --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  FULL_TRUE="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["true_commits"])' <<<"$FULL_JSON")"
  FULL_NOW="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(int(r["holds_now"]))' <<<"$FULL_JSON")"
  test "$FULL_TRUE" -ge 1
  assert "full history found true commits" true
  assert_eq "full history holds_now" "$FULL_NOW" "0"

  echo
  echo "---- sitbone first-parent (human) ----"
  "$DWELT" -C "$SITBONE" --color never exists Sources/SitboneUI/FocusRiverView.swift || true
  echo "---- sitbone --full (human) ----"
  "$DWELT" -C "$SITBONE" --full --color never exists Sources/SitboneUI/FocusRiverView.swift || true

  if [[ -x "$ORIG" ]]; then
    echo "-- empirical match vs original held"
    ORIG_FP="$("$ORIG" -C "$SITBONE" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
    ORIG_FULL="$("$ORIG" -C "$SITBONE" --full --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
    if compare_json "sitbone first-parent vs held" "$ORIG_FP" "$FP_JSON"; then
      assert "sitbone first-parent matches held" true
    else
      assert "sitbone first-parent matches held" false
    fi
    if compare_json "sitbone --full vs held" "$ORIG_FULL" "$FULL_JSON"; then
      assert "sitbone --full matches held" true
    else
      assert "sitbone --full matches held" false
    fi
  fi
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: skills circuit-breaker plugin life =="
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  CB_JSON="$("$DWELT" -C "$SKILLS" --json exists circuit-breaker/scripts/detect.sh || true)"
  CB_PAT="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$CB_JSON")"
  python3 -c 'import sys; p=sys.argv[1]; sys.exit(0 if ("T" in p and p.endswith("F")) else 1)' "$CB_PAT"
  assert "circuit-breaker lived then died ($CB_PAT)" true
  echo "---- skills circuit-breaker ----"
  "$DWELT" -C "$SKILLS" --color never exists circuit-breaker/scripts/detect.sh || true
  if [[ -x "$ORIG" ]]; then
    ORIG_CB="$("$ORIG" -C "$SKILLS" --json exists circuit-breaker/scripts/detect.sh || true)"
    if compare_json "skills circuit-breaker vs held" "$ORIG_CB" "$CB_JSON"; then
      assert "skills circuit-breaker matches held" true
    else
      assert "skills circuit-breaker matches held" false
    fi
  fi
else
  echo "skip skills (not present)"
fi

echo
echo "== real repo: kizu first-parent compression is visible =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  KZ_JSON="$("$DWELT" -C "$KIZU" --json exists CLAUDE.md || true)"
  KZ_SCAN="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["commits_scanned"], r["reachable"])' <<<"$KZ_JSON")"
  python3 -c 'import sys; s,r=map(int,sys.argv[1].split()); sys.exit(0 if r>s else 1)' "$KZ_SCAN"
  assert "kizu reachable > first-parent scanned ($KZ_SCAN)" true
  KZ_ORIGIN="$(python3 -c 'import json,sys; r=json.load(sys.stdin); ts=[e for e in r["eras"] if e["value"]]; print((ts[0].get("origin") or {}).get("short",""))' <<<"$KZ_JSON")"
  assert_eq "kizu first-parent origin is e1098c8" "$KZ_ORIGIN" "e1098c8"
  echo "---- kizu CLAUDE.md (first-parent, with origin) ----"
  "$DWELT" -C "$KIZU" --color never exists CLAUDE.md
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: voidtrace phrase + case (the v1 silent miss) =="
VOID="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
if [[ -d "$VOID/.git" || -f "$VOID/.git" ]]; then
  echo "-- unquoted extra token is a dead pathspec"
  VU_JSON="$("$DWELT" -C "$VOID" --json grep finite breakpoint || true)"
  VU_WARN="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["warnings"][0] if r["warnings"] else "")' <<<"$VU_JSON")"
  assert "voidtrace unquoted pathspec warning" grep -q "breakpoint" <<<"$VU_WARN"

  echo "-- quoted phrase, wrong case, hints -i"
  VC_JSON="$("$DWELT" -C "$VOID" --json grep 'finite breakpoint' || true)"
  VC_HINT="$(python3 -c 'import json,sys; r=json.load(sys.stdin); print(" ".join(r.get("hints") or []))' <<<"$VC_JSON")"
  assert "voidtrace phrase hints -i" grep -q -- "-i" <<<"$VC_HINT"

  echo "---- voidtrace after improvement ----"
  "$DWELT" -C "$VOID" --color never grep finite breakpoint || true
  echo
  "$DWELT" -C "$VOID" --color never grep 'finite breakpoint' || true
  echo
  "$DWELT" -C "$VOID" --color never grep -i 'finite breakpoint' | head -20
else
  echo "skip voidtrace (not present)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
