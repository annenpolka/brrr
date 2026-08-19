#!/usr/bin/env bash
# Exercise holt: file-identity occupancy from all-reachable R; tip occupant.
# ./demo.sh 0  — fixture + sitbone/skills + kizu (skip voidtrace)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
HOLT="$ROOT/holt"
chmod +x "$HOLT"
CHEAP=0
if [[ "${1:-}" == "0" ]]; then
  CHEAP=1
fi

if [[ ! -x "$HOLT" ]]; then
  echo "demo: holt is not executable" >&2
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

json_get() {
  python3 -c 'import json,sys; r=json.load(sys.stdin); '"$1"''
}

echo "== fixture: oscillating path, rename, TOKEN_B copy/move, nested git =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/holt-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "holt-demo"
git -C "$FIX" config user.email "holt@example.test"

# t0: always-on file + TOKEN_A in keep.txt + TOKEN_B in alpha.txt
mkdir -p "$FIX/nested/deep"
printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'born\n' > "$FIX/oscillate.txt"
printf 'ghost\n' > "$FIX/old name.txt"
printf 'hello\n' > "$FIX/nested/deep/weird (1).txt"
printf 'TOKEN_B\n' > "$FIX/alpha.txt"
git -C "$FIX" add keep.txt oscillate.txt "old name.txt" "nested/deep/weird (1).txt" alpha.txt
git -C "$FIX" commit -q -m "t0: birth"

# t1: delete oscillate, both tokens still present
rm "$FIX/oscillate.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t1: kill oscillate"

# t2: revive oscillate, drop TOKEN_A, copy TOKEN_B to beta.txt, Japanese path
printf 'reborn\n' > "$FIX/oscillate.txt"
printf 'keep\n' > "$FIX/keep.txt"
printf '計画\n' > "$FIX/計画.md"
printf 'TOKEN_B\n' > "$FIX/beta.txt"
git -C "$FIX" add oscillate.txt keep.txt "計画.md" beta.txt
git -C "$FIX" commit -q -m "t2: revive oscillate, drop TOKEN_A, copy TOKEN_B"

# t3: rename + shift TOKEN_B down a line in alpha.txt
git -C "$FIX" mv "old name.txt" "new name.txt"
printf 'header\nTOKEN_B\n' > "$FIX/alpha.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t3: rename with spaces, TOKEN_B line shifts"

# t4: kill oscillate, TOKEN_A reincarnates, TOKEN_B leaves alpha (only beta holds it)
rm "$FIX/oscillate.txt"
printf 'other\nTOKEN_A\n' > "$FIX/other.txt"
printf 'header\n' > "$FIX/alpha.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t4: kill oscillate, TOKEN_A reincarnates, TOKEN_B moves"

# t5: nested git repo that should NOT be walked as the root
mkdir -p "$FIX/vendor/nested"
git -C "$FIX/vendor/nested" init -q -b inner
git -C "$FIX/vendor/nested" config user.name "holt-demo"
git -C "$FIX/vendor/nested" config user.email "holt@example.test"
echo inner > "$FIX/vendor/nested/inner.txt"
git -C "$FIX/vendor/nested" add inner.txt
git -C "$FIX/vendor/nested" commit -q -m "inner commit"
echo 'vendor-marker' > "$FIX/vendor/marker.txt"
git -C "$FIX" add vendor/marker.txt
git -C "$FIX" commit -q -m "t5: nested git + marker"

# t6: TOKEN_A gone, TOKEN_B still only in beta.txt
printf 'keep\n' > "$FIX/other.txt"
git -C "$FIX" add other.txt
git -C "$FIX" commit -q -m "t6: TOKEN_A gone again"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "7"

echo "-- exists oscillate.txt (--no-follow path occupancy flips T F T F)"
OSC_JSON="$("$HOLT" -C "$FIX" --no-follow --color never --json exists oscillate.txt || true)"
OSC_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$OSC_JSON")"
OSC_TRUE="$(json_get 'print(r["true_commits"])' <<<"$OSC_JSON")"
OSC_PATTERN="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$OSC_JSON")"
assert_eq "oscillate holds_now" "$OSC_NOW" "0"
assert_eq "oscillate true_commits" "$OSC_TRUE" "3"
assert_eq "oscillate era pattern" "$OSC_PATTERN" "TFTF"
OSC_F="$("$HOLT" -C "$FIX" --follow --json exists oscillate.txt || true)"
OSC_FPAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"])' <<<"$OSC_F")"
assert_eq "follow oscillate does not reincarnate the same path (TF, true=1)" "$OSC_FPAT" "TF 1"

echo "-- exists 'old name.txt' vs 'new name.txt' (--no-follow: rename is a path death)"
OLD_PAT="$("$HOLT" -C "$FIX" --no-follow --oneline exists "old name.txt" || true)"
NEW_PAT="$("$HOLT" -C "$FIX" --no-follow --oneline exists "new name.txt" || true)"
OLD_TF="$(awk '{printf $1}' <<<"$OLD_PAT" | tr -d '\n')"
NEW_TF="$(awk '{printf $1}' <<<"$NEW_PAT" | tr -d '\n')"
assert_eq "old name --no-follow eras" "$OLD_TF" "TF"
assert_eq "new name --no-follow eras" "$NEW_TF" "FT"

echo "-- default exists: rename is one identity (query old or new, same roost)"
OLD_F="$("$HOLT" -C "$FIX" --json exists "old name.txt" || true)"
NEW_F="$("$HOLT" -C "$FIX" --json exists "new name.txt" || true)"
OLD_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$OLD_F")"
NEW_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$NEW_F")"
OLD_BOOL="$(json_get 'print(int(r["always_held"]), r["boolean_eras"], len(r["eras"]), int(r["follow"]))' <<<"$OLD_F")"
NEW_BOOL="$(json_get 'print(int(r["always_held"]), r["boolean_eras"], len(r["eras"]), int(r["follow"]))' <<<"$NEW_F")"
OLD_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$OLD_F")"
OLD_KINDS="$(json_get 'print([e["kind"] for e in r["eras"]])' <<<"$OLD_F")"
OLD_FP="$(json_get 'print(int(r["first_parent"]))' <<<"$OLD_F")"
assert_eq "follow identity from old name" "$OLD_ID" "old name.txt,new name.txt"
assert_eq "follow identity from new name" "$NEW_ID" "old name.txt,new name.txt"
assert_eq "follow old always held, boolean=1, 2 holder eras" "$OLD_BOOL" "1 1 2 1"
assert_eq "follow new matches old" "$NEW_BOOL" "$OLD_BOOL"
assert_eq "follow holders old then new" "$OLD_HOLD" "old name.txt | new name.txt"
assert_eq "follow kinds birth then move" "$OLD_KINDS" "['birth', 'move']"
assert_eq "default walk is not first-parent" "$OLD_FP" "0"

echo "-- copy is not identity (alpha.txt stays alpha)"
AL_F="$("$HOLT" -C "$FIX" --json exists alpha.txt || true)"
AL_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$AL_F")"
AL_NOW="$(json_get 'print(int(r["always_held"]), ",".join(r["eras"][-1]["holders"]))' <<<"$AL_F")"
assert_eq "follow alpha identity is not beta" "$AL_ID" "alpha.txt"
assert_eq "follow alpha still alpha at HEAD" "$AL_NOW" "1 alpha.txt"

echo "-- exists Japanese path"
"$HOLT" -C "$FIX" -q exists "計画.md"
assert "計画.md holds now" true

echo "-- glob exists 'nested/deep/*'"
if "$HOLT" -C "$FIX" -q exists 'nested/deep/*'; then
  assert "glob exists now" true
else
  assert "glob exists now" false
fi

echo "-- grep TOKEN_A reincarnation (T F T F)"
TOK_JSON="$("$HOLT" -C "$FIX" --json grep TOKEN_A || true)"
TOK_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$TOK_JSON")"
assert_eq "TOKEN_A era pattern" "$TOK_PAT" "TFTF"
WIT_START="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(trues[0]["holders"][0])' <<<"$TOK_JSON")"
WIT_LAST="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(trues[-1]["holders"][0])' <<<"$TOK_JSON")"
assert_eq "first TOKEN_A holder" "$WIT_START" "keep.txt"
assert_eq "last TOKEN_A holder" "$WIT_LAST" "other.txt"

echo "-- grep TOKEN_B: occupancy never flips, holders copy then move"
B_JSON="$("$HOLT" -C "$FIX" --json grep TOKEN_B || true)"
B_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$B_JSON")"
B_BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$B_JSON")"
B_N="$(json_get 'print(len(r["eras"]))' <<<"$B_JSON")"
B_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$B_JSON")"
B_ADDED="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(",".join(trues[1]["added"]))' <<<"$B_JSON")"
B_DROPPED="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(",".join(trues[2]["dropped"]))' <<<"$B_JSON")"
assert_eq "TOKEN_B always holds (boolean eras)" "$B_BOOL" "1"
assert_eq "TOKEN_B holder eras" "$B_N" "3"
assert_eq "TOKEN_B pattern" "$B_PAT" "TTT"
assert_eq "TOKEN_B holders" "$B_HOLD" "alpha.txt | alpha.txt,beta.txt | beta.txt"
assert_eq "TOKEN_B copy added beta" "$B_ADDED" "beta.txt"
assert_eq "TOKEN_B move dropped alpha" "$B_DROPPED" "alpha.txt"
B_KINDS="$(json_get 'print([e["kind"] for e in r["eras"]])' <<<"$B_JSON")"
assert_eq "TOKEN_B kinds birth/spread/shrink (not ghost: remaining holder is code)" "$B_KINDS" "['birth', 'spread', 'shrink']"
B_GHOST="$(json_get 'print(int(r["ghost_now"]))' <<<"$B_JSON")"
assert_eq "TOKEN_B ghost_now" "$B_GHOST" "0"

echo "-- --boolean recovers ancestor held (one TRUE era for TOKEN_B)"
BB_JSON="$("$HOLT" -C "$FIX" --boolean --json grep TOKEN_B || true)"
BB_N="$(json_get 'print(len(r["eras"]), int(r["split_holders"]))' <<<"$BB_JSON")"
assert_eq "TOKEN_B --boolean is one era" "$BB_N" "1 0"

echo "-- exec: wc -l keep.txt is 2 only while TOKEN_A lived there (t0-t1)"
EXEC_JSON="$("$HOLT" -C "$FIX" --json --timeout 5 exec -- sh -c 'test "$(wc -l < keep.txt)" -eq 2' || true)"
EXEC_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$EXEC_JSON")"
assert_eq "exec two-line keep.txt pattern" "$EXEC_PAT" "TF"

echo "-- --revs / --bounds / exit codes"
set +e
"$HOLT" -C "$FIX" -q exists oscillate.txt
OSC_RC=$?
"$HOLT" -C "$FIX" -q exists keep.txt
KEEP_RC=$?
"$HOLT" -C "$FIX" -q exists 'does-not-exist.xyz'
MISS_RC=$?
set -e
assert_eq "exists oscillate exit" "$OSC_RC" "1"
assert_eq "exists keep exit" "$KEEP_RC" "0"
assert_eq "exists missing exit" "$MISS_RC" "1"

REVS="$("$HOLT" -C "$FIX" --revs exists keep.txt)"
REVS_N="$(printf '%s\n' "$REVS" | grep -c .)"
assert_eq "keep.txt true revs == all commits" "$REVS_N" "7"

BOUNDS_N="$("$HOLT" -C "$FIX" --no-follow --true-bounds exists oscillate.txt | grep -c . || true)"
assert_eq "oscillate true-bounds rows" "$BOUNDS_N" "2"

echo "-- --now sees an uncommitted resurrection (path occupancy)"
printf 'dirty\n' > "$FIX/oscillate.txt"
NOW_JSON="$("$HOLT" -C "$FIX" --no-follow --now --json exists oscillate.txt || true)"
NOW_HOLD="$(json_get 'print(int(r["holds_now"]), r["eras"][-1]["end"]["kind"])' <<<"$NOW_JSON")"
assert_eq "uncommitted oscillate via --now" "$NOW_HOLD" "1 worktree"
rm -f "$FIX/oscillate.txt"

echo "-- dead pathspec warns instead of silent never-held"
DEAD_JSON="$("$HOLT" -C "$FIX" --json grep TOKEN_A definitely-not-a-file || true)"
DEAD_WARN="$(json_get 'print(r["warnings"][0] if r["warnings"] else "")' <<<"$DEAD_JSON")"
assert "dead pathspec warning" grep -q "definitely-not-a-file" <<<"$DEAD_WARN"
assert "dead pathspec suggests quoting" grep -q "holt grep 'TOKEN_A definitely-not-a-file'" <<<"$DEAD_WARN"

echo "-- wrong case hints -i"
CASE_JSON="$("$HOLT" -C "$FIX" --json grep token_a || true)"
CASE_HINT="$(json_get 'print((r["hints"] or [r["hint"] or ""])[0])' <<<"$CASE_JSON")"
assert "case-fold hint mentions -i" grep -q -- "-i" <<<"$CASE_HINT"

echo "-- 3-hop identity: old.txt → new name.txt → 最終.md, query any name"
HOP="$(mktemp -d "${TMPDIR:-/tmp}/holt-hop.XXXXXX")"
git -C "$HOP" init -q -b main
git -C "$HOP" config user.name "holt-demo"
git -C "$HOP" config user.email "holt@example.test"
printf 'same\n' > "$HOP/old.txt"
git -C "$HOP" add old.txt && git -C "$HOP" commit -q -m hop0
git -C "$HOP" mv old.txt "new name.txt" && git -C "$HOP" commit -q -m hop1
git -C "$HOP" mv "new name.txt" "最終.md" && git -C "$HOP" commit -q -m hop2
HOP_OLD="$("$HOLT" -C "$HOP" --json exists old.txt || true)"
HOP_MID="$("$HOLT" -C "$HOP" --json exists "new name.txt" || true)"
HOP_NEW="$("$HOLT" -C "$HOP" --json exists "最終.md" || true)"
HOP_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$HOP_OLD")"
HOP_ID2="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$HOP_MID")"
HOP_ID3="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$HOP_NEW")"
HOP_N="$(json_get 'print(r["true_commits"], len(r["eras"]), r["boolean_eras"])' <<<"$HOP_OLD")"
HOP_KINDS="$(json_get 'print([e["kind"] for e in r["eras"]])' <<<"$HOP_OLD")"
assert_eq "3-hop identity from old.txt" "$HOP_ID" "old.txt → new name.txt → 最終.md"
assert_eq "3-hop identity from mid name" "$HOP_ID2" "$HOP_ID"
assert_eq "3-hop identity from 最終.md" "$HOP_ID3" "$HOP_ID"
assert_eq "3-hop true=3 eras=3 boolean=1" "$HOP_N" "3 3 1"
assert_eq "3-hop kinds birth/move/move" "$HOP_KINDS" "['birth', 'move', 'move']"
rm -rf "$HOP"

echo "-- leftover name is this path's identity, not the twin that moved"
LEFT="$(mktemp -d "${TMPDIR:-/tmp}/holt-left.XXXXXX")"
git -C "$LEFT" init -q -b main
git -C "$LEFT" config user.name "holt-demo"
git -C "$LEFT" config user.email "holt@example.test"
echo ORIG > "$LEFT/old.txt"
git -C "$LEFT" add old.txt && git -C "$LEFT" commit -q -m t0
git -C "$LEFT" mv old.txt new.txt && git -C "$LEFT" commit -q -m t1
echo REINCARNATED > "$LEFT/old.txt"
git -C "$LEFT" add old.txt && git -C "$LEFT" commit -q -m t2
LEFT_OLD="$("$HOLT" -C "$LEFT" --json exists old.txt || true)"
LEFT_NEW="$("$HOLT" -C "$LEFT" --json exists new.txt || true)"
LEFT_NF="$("$HOLT" -C "$LEFT" --no-follow --json exists old.txt || true)"
LEFT_OID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$LEFT_OLD")"
LEFT_NID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$LEFT_NEW")"
LEFT_OPAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"], int(r["holds_now"]))' <<<"$LEFT_OLD")"
LEFT_NTRUE="$(json_get 'print(r["true_commits"], int(r["always_held"]))' <<<"$LEFT_NEW")"
LEFT_NFPAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$LEFT_NF")"
assert_eq "leftover old.txt identity is not new.txt" "$LEFT_OID" "old.txt"
assert_eq "leftover old.txt is reincarnation (FT true=1 now)" "$LEFT_OPAT" "FT 1 1"
assert_eq "moved file identity old → new" "$LEFT_NID" "old.txt → new.txt"
assert_eq "moved file always held true=3" "$LEFT_NTRUE" "3 1"
assert_eq "leftover --no-follow is TFT path occupancy" "$LEFT_NFPAT" "TFT"
rm -rf "$LEFT"

echo "-- serialized swap: exists a.txt occupies THIS occupant (BBB), not original AAA"
SW="$(mktemp -d "${TMPDIR:-/tmp}/holt-swap.XXXXXX")"
git -C "$SW" init -q -b main
git -C "$SW" config user.name "holt-demo"
git -C "$SW" config user.email "holt@example.test"
echo AAA > "$SW/a.txt"
echo BBB > "$SW/b.txt"
git -C "$SW" add a.txt b.txt && git -C "$SW" commit -q -m t0
git -C "$SW" mv a.txt tmp.txt && git -C "$SW" commit -q -m t1
git -C "$SW" mv b.txt a.txt && git -C "$SW" commit -q -m t2
git -C "$SW" mv tmp.txt b.txt && git -C "$SW" commit -q -m t3
SW_A="$("$HOLT" -C "$SW" --json exists a.txt || true)"
SW_B="$("$HOLT" -C "$SW" --json exists b.txt || true)"
SW_AID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$SW_A")"
SW_BID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$SW_B")"
SW_AH="$(json_get 'print(",".join(r["eras"][-1]["holders"]))' <<<"$SW_A")"
SW_BH="$(json_get 'print(",".join(r["eras"][-1]["holders"]))' <<<"$SW_B")"
assert_eq "swap exists a.txt identity is b → a (occupant BBB)" "$SW_AID" "b.txt → a.txt"
assert_eq "swap exists b.txt identity is a → tmp → b (occupant AAA)" "$SW_BID" "a.txt → tmp.txt → b.txt"
assert_eq "swap a.txt HEAD holder is a.txt" "$SW_AH" "a.txt"
assert_eq "swap b.txt HEAD holder is b.txt" "$SW_BH" "b.txt"
rm -rf "$SW"

echo "-- non-ff merge-birth: first-parent exists from the old name occupies dest"
MB="$(mktemp -d "${TMPDIR:-/tmp}/holt-merge.XXXXXX")"
git -C "$MB" init -q -b main
git -C "$MB" config user.name "holt-demo"
git -C "$MB" config user.email "holt@example.test"
echo base > "$MB/keep.txt"
git -C "$MB" add keep.txt && git -C "$MB" commit -q -m base
git -C "$MB" checkout -q -b topic
echo TOKEN_M > "$MB/old.txt"
git -C "$MB" add old.txt && git -C "$MB" commit -q -m birth
git -C "$MB" mv old.txt dest.txt && git -C "$MB" commit -q -m rename
git -C "$MB" checkout -q main
echo extra >> "$MB/keep.txt"
git -C "$MB" add keep.txt && git -C "$MB" commit -q -m extra
git -C "$MB" merge -q --no-ff --no-edit topic
MB_OLD="$("$HOLT" -C "$MB" --first-parent --json exists old.txt || true)"
MB_DEST="$("$HOLT" -C "$MB" --first-parent --json exists dest.txt || true)"
MB_NF="$("$HOLT" -C "$MB" --first-parent --no-follow --json exists old.txt || true)"
MB_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$MB_OLD")"
MB_ID2="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$MB_DEST")"
MB_N="$(json_get 'print(r["true_commits"], int(r["holds_now"]), "".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$MB_OLD")"
MB_N2="$(json_get 'print(r["true_commits"], int(r["holds_now"]), "".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$MB_DEST")"
MB_HOLD="$(json_get 'print(",".join(e["holders"][0] for e in r["eras"] if e["value"]))' <<<"$MB_OLD")"
MB_ORIGIN="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print((trues[0].get("origin") or {}).get("subject",""))' <<<"$MB_OLD")"
MB_NFN="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$MB_NF")"
assert_eq "merge-birth identity from old" "$MB_ID" "old.txt → dest.txt"
assert_eq "merge-birth identity from dest is the same roost" "$MB_ID2" "$MB_ID"
assert_eq "merge-birth first-parent follow old is FT now" "$MB_N" "1 1 FT"
assert_eq "merge-birth first-parent follow dest matches old" "$MB_N2" "$MB_N"
assert_eq "merge-birth first-parent holders dest" "$MB_HOLD" "dest.txt"
assert_eq "merge-birth origin is the topic birth" "$MB_ORIGIN" "birth"
assert_eq "merge-birth --no-follow old name never held on first-parent" "$MB_NFN" "0 0"
rm -rf "$MB"

echo "-- --now exists DEST of uncommitted git mv sees dest (either-name under --now)"
DR="$(mktemp -d "${TMPDIR:-/tmp}/holt-dirty.XXXXXX")"
git -C "$DR" init -q -b main
git -C "$DR" config user.name "holt-demo"
git -C "$DR" config user.email "holt@example.test"
echo ghost > "$DR/old name.txt"
git -C "$DR" add "old name.txt" && git -C "$DR" commit -q -m t0
git -C "$DR" mv "old name.txt" "new name.txt"
DR_NEW="$("$HOLT" -C "$DR" --now --json exists "new name.txt" || true)"
DR_OLD="$("$HOLT" -C "$DR" --now --json exists "old name.txt" || true)"
DR_NID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$DR_NEW")"
DR_OID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$DR_OLD")"
DR_NNOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], int(r["never_held"]))' <<<"$DR_NEW")"
DR_ONOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$DR_OLD")"
DR_NHOLD="$(json_get 'print(" | ".join(e["end"]["kind"]+":"+",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$DR_NEW")"
assert_eq "dirty dest identity old → new" "$DR_NID" "old name.txt → new name.txt"
assert_eq "dirty dest from old name is the same roost" "$DR_OID" "$DR_NID"
assert_eq "dirty dest --now is held (true=1, not never)" "$DR_NNOW" "1 1 0"
assert_eq "dirty old --now is held" "$DR_ONOW" "1 1"
assert_eq "dirty dest holders commit old then worktree new" "$DR_NHOLD" "commit:old name.txt | worktree:new name.txt"

echo "-- --now leftover at the old name is this path, not the twin"
echo DIRTY-REINCARNATE > "$DR/old name.txt"
DR_LEFT="$("$HOLT" -C "$DR" --now --json exists "old name.txt" || true)"
DR_DEST="$("$HOLT" -C "$DR" --now --json exists "new name.txt" || true)"
DR_LID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$DR_LEFT")"
DR_LPAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"], int(r["holds_now"]))' <<<"$DR_LEFT")"
DR_DID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$DR_DEST")"
DR_DTRUE="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$DR_DEST")"
assert_eq "dirty leftover identity is not dest" "$DR_LID" "old name.txt"
assert_eq "dirty leftover is worktree-only roost (FT true=0 now)" "$DR_LPAT" "FT 0 1"
assert_eq "dirty dest still occupies the moved file" "$DR_DID" "old name.txt → new name.txt"
assert_eq "dirty dest still held historically" "$DR_DTRUE" "1 1"
rm -rf "$DR"

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/holt-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$HOLT" -C "$EMPTY" exists README.md 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -q "empty" <<<"$EMPTY_ERR"

echo
echo "== real repo: sitbone FocusRiverView (git log -- path is empty) =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- git log -- path (the footgun held exists to replace)"
  LOG_N="$(git -C "$SITBONE" log --oneline -- Sources/SitboneUI/FocusRiverView.swift | grep -c . || true)"
  assert_eq "git log -- deleted-path is empty" "$LOG_N" "0"

  echo "-- default exists finds the side-history island (no --full required)"
  FULL_JSON="$("$HOLT" -C "$SITBONE" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  FULL_TRUE="$(json_get 'print(r["true_commits"])' <<<"$FULL_JSON")"
  FULL_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$FULL_JSON")"
  FULL_FP="$(json_get 'print(int(r["first_parent"]))' <<<"$FULL_JSON")"
  test "$FULL_TRUE" -ge 1
  assert "default walk found true commits ($FULL_TRUE)" true
  assert_eq "default walk holds_now" "$FULL_NOW" "0"
  assert_eq "default walk is not first-parent" "$FULL_FP" "0"

  echo "-- --first-parent exists (mainline never shipped the file)"
  FP_JSON="$("$HOLT" -C "$SITBONE" --first-parent --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  FP_NEVER="$(json_get 'print(int(r["never_held"]))' <<<"$FP_JSON")"
  FP_HINT="$(json_get 'print(r["hint"] or "")' <<<"$FP_JSON")"
  assert_eq "first-parent never_held" "$FP_NEVER" "1"
  assert "first-parent hint mentions without --first-parent" grep -q -- "--first-parent" <<<"$FP_HINT"

  echo "-- default grep FocusRiverView: occupancy is one TRUE island, holders move"
  FR_JSON="$("$HOLT" -C "$SITBONE" --json grep FocusRiverView || true)"
  FR_BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$FR_JSON")"
  FR_N="$(json_get 'print(len(r["eras"]))' <<<"$FR_JSON")"
  FR_TRUE_N="$(json_get 'print(sum(1 for e in r["eras"] if e["value"]))' <<<"$FR_JSON")"
  FR_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$FR_JSON")"
  FR_KINDS="$(json_get 'print([e["kind"] for e in r["eras"] if e["value"]])' <<<"$FR_JSON")"
  assert_eq "FocusRiverView boolean eras (F T F)" "$FR_BOOL" "3"
  assert_eq "FocusRiverView TRUE kinds (shrink is code, not ghost)" "$FR_KINDS" "['birth', 'spread', 'shrink']"
  python3 -c 'import sys; n,b=int(sys.argv[1]),int(sys.argv[2]); sys.exit(0 if n>b and int(sys.argv[3])>=2 else 1)' "$FR_N" "$FR_BOOL" "$FR_TRUE_N"
  assert "FocusRiverView holder splits inside the TRUE island ($FR_N eras, $FR_TRUE_N TRUE, holders: $FR_HOLD)" true

  echo
  echo "---- sitbone default exists (human) ----"
  "$HOLT" -C "$SITBONE" --color never exists Sources/SitboneUI/FocusRiverView.swift || true
  echo "---- sitbone grep FocusRiverView (human; holder splits) ----"
  "$HOLT" -C "$SITBONE" --color never grep FocusRiverView || true
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: skills circuit-breaker + preact-zero-mock ghost occupancy =="
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  CB_JSON="$("$HOLT" -C "$SKILLS" --json exists circuit-breaker/scripts/detect.sh || true)"
  CB_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$CB_JSON")"
  python3 -c 'import sys; p=sys.argv[1]; sys.exit(0 if ("T" in p and p.endswith("F")) else 1)' "$CB_PAT"
  assert "circuit-breaker lived then died ($CB_PAT)" true
  echo "---- skills circuit-breaker exists ----"
  "$HOLT" -C "$SKILLS" --color never exists circuit-breaker/scripts/detect.sh || true

  echo "-- grep preact-zero-mock: still TRUE after the plugin died (README is the holder)"
  PZ_JSON="$("$HOLT" -C "$SKILLS" --json grep preact-zero-mock || true)"
  PZ_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$PZ_JSON")"
  PZ_BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$PZ_JSON")"
  PZ_N="$(json_get 'print(len(r["eras"]))' <<<"$PZ_JSON")"
  PZ_TRUE_N="$(json_get 'print(sum(1 for e in r["eras"] if e["value"]))' <<<"$PZ_JSON")"
  PZ_LAST="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(",".join(trues[-1]["holders"]))' <<<"$PZ_JSON")"
  PZ_DROP="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(",".join(trues[-1]["dropped"]))' <<<"$PZ_JSON")"
  assert_eq "preact-zero-mock holds now (ghost occupancy)" "$PZ_NOW" "1"
  assert_eq "preact-zero-mock boolean eras (F T)" "$PZ_BOOL" "2"
  python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>=3 else 1)' "$PZ_TRUE_N"
  assert "preact-zero-mock has >=3 TRUE holder eras (got $PZ_TRUE_N, total $PZ_N)" true
  assert_eq "last preact-zero-mock holder is README.md" "$PZ_LAST" "README.md"
  assert "last era dropped the SKILL.md definition" grep -q "SKILL.md" <<<"$PZ_DROP"
  PZ_KIND="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(trues[-1]["kind"])' <<<"$PZ_JSON")"
  PZ_GHOST="$(json_get 'print(int(r["ghost_now"]))' <<<"$PZ_JSON")"
  PZ_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$PZ_JSON")"
  assert_eq "preact-zero-mock last era is ghost" "$PZ_KIND" "ghost"
  assert_eq "preact-zero-mock ghost_now" "$PZ_GHOST" "1"
  assert "ghost hint names the dead definition" grep -q "SKILL.md" <<<"$PZ_HINT"
  assert "ghost hint says documentation mention" grep -q "documentation mention" <<<"$PZ_HINT"
  echo "---- skills grep preact-zero-mock (human) ----"
  "$HOLT" -C "$SKILLS" --color never grep preact-zero-mock || true
else
  echo "skip skills (not present)"
fi

echo
echo "== real repo: kizu either-name TRUE on the default walk =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "-- default (all reachable) stitches R100 from either name"
  KD_JSON="$("$HOLT" -C "$KIZU" --json exists docs/deep-research-ai-agent-hooks.md || true)"
  KO_JSON="$("$HOLT" -C "$KIZU" --json exists deep-research-ai-agent-hooks.md || true)"
  KD_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KD_JSON")"
  KO_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KO_JSON")"
  KD_N="$(json_get 'print(r["true_commits"], r["boolean_eras"], int(r["holds_now"]), int(r["first_parent"]))' <<<"$KD_JSON")"
  KO_N="$(json_get 'print(r["true_commits"], r["boolean_eras"], int(r["holds_now"]), int(r["first_parent"]))' <<<"$KO_JSON")"
  KD_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$KD_JSON")"
  KN_JSON="$("$HOLT" -C "$KIZU" --no-follow --json exists deep-research-ai-agent-hooks.md || true)"
  KN_TRUE="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$KN_JSON")"
  assert_eq "kizu follow identity dest" "$KD_ID" "deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md"
  assert_eq "kizu follow identity old name is the same roost" "$KO_ID" "$KD_ID"
  assert_eq "kizu default true=187/boolean=2/now/not-fp" "$KD_N" "187 2 1 0"
  assert_eq "kizu default from old name matches dest" "$KO_N" "$KD_N"
  assert_eq "kizu follow holders old then docs/" "$KD_HOLD" "deep-research-ai-agent-hooks.md | docs/deep-research-ai-agent-hooks.md"
  assert_eq "kizu --no-follow old name is a path death" "$KN_TRUE" "13 0"
  KD_KINDS="$(json_get 'print([e["kind"] for e in r["eras"] if e["value"]])' <<<"$KD_JSON")"
  KD_GHOST="$(json_get 'print(int(r["ghost_now"]))' <<<"$KD_JSON")"
  assert_eq "kizu follow TRUE kinds are birth/move (not ghost: the file moved)" "$KD_KINDS" "['birth', 'move']"
  assert_eq "kizu follow ghost_now" "$KD_GHOST" "0"

  echo "-- --first-parent from either name is the dest roost (merge-birth stitch)"
  KP_OLD="$("$HOLT" -C "$KIZU" --first-parent --json exists deep-research-ai-agent-hooks.md || true)"
  KP_DEST="$("$HOLT" -C "$KIZU" --first-parent --json exists docs/deep-research-ai-agent-hooks.md || true)"
  KP_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KP_OLD")"
  KP_ID2="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KP_DEST")"
  KP_N="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$KP_OLD")"
  KP_N2="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$KP_DEST")"
  KP_ORIGIN="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print((trues[0].get("origin") or {}).get("short",""))' <<<"$KP_OLD")"
  KP_AS="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print((trues[0].get("holders") or [""])[0])' <<<"$KP_OLD")"
  assert_eq "kizu first-parent old identity" "$KP_ID" "deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md"
  assert_eq "kizu first-parent dest identity matches old" "$KP_ID2" "$KP_ID"
  assert_eq "kizu first-parent old true/now" "$KP_N" "21 1"
  assert_eq "kizu first-parent dest matches old" "$KP_N2" "$KP_N"
  assert_eq "kizu first-parent origin is old-name birth 321a830" "$KP_ORIGIN" "321a830"
  assert_eq "kizu first-parent holders dest" "$KP_AS" "docs/deep-research-ai-agent-hooks.md"

  echo "-- CLAUDE.md first-parent origin is still the topic-branch birth"
  KZ_JSON="$("$HOLT" -C "$KIZU" --first-parent --json exists CLAUDE.md || true)"
  KZ_SCAN="$(json_get 'print(r["commits_scanned"], r["reachable"])' <<<"$KZ_JSON")"
  python3 -c 'import sys; s,r=map(int,sys.argv[1].split()); sys.exit(0 if r>s else 1)' "$KZ_SCAN"
  assert "kizu reachable > first-parent scanned ($KZ_SCAN)" true
  KZ_ORIGIN="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print((trues[0].get("origin") or {}).get("short",""))' <<<"$KZ_JSON")"
  assert_eq "kizu first-parent origin is off-mainline birth e1098c8" "$KZ_ORIGIN" "e1098c8"

  echo "-- C056 leftover blob is not a follow; git.rs split is not a follow"
  INIT="$("$HOLT" -C "$KIZU" --json exists src/init.rs || true)"
  INST="$("$HOLT" -C "$KIZU" --json exists src/init/install.rs || true)"
  INIT_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$INIT")"
  INST_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$INST")"
  INST_KIND="$(json_get 'print([e["kind"] for e in r["eras"] if e["value"]])' <<<"$INST")"
  assert_eq "kizu init.rs identity stays init.rs" "$INIT_ID" "src/init.rs"
  assert_eq "kizu install.rs is its own birth" "$INST_ID" "src/init/install.rs"
  assert_eq "kizu install.rs TRUE kind is birth" "$INST_KIND" "['birth']"
  GITR="$("$HOLT" -C "$KIZU" --json exists src/git.rs || true)"
  PARSE="$("$HOLT" -C "$KIZU" --json exists src/git/parse.rs || true)"
  GIT_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$GITR")"
  PARSE_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$PARSE")"
  assert_eq "kizu git.rs follow identity stays git.rs" "$GIT_ID" "src/git.rs"
  assert_eq "kizu parse.rs is its own birth" "$PARSE_ID" "src/git/parse.rs"

  echo "---- kizu default follow dest (human) ----"
  "$HOLT" -C "$KIZU" --color never exists docs/deep-research-ai-agent-hooks.md || true
  echo "---- kizu first-parent follow old name (either-name TRUE) ----"
  "$HOLT" -C "$KIZU" --first-parent --color never exists deep-research-ai-agent-hooks.md || true
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: voidtrace phrase + case (ancestor silent miss) =="
VOID="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
if [[ "$CHEAP" -eq 1 ]]; then
  echo "skip voidtrace (demo.sh 0)"
elif [[ -d "$VOID/.git" || -f "$VOID/.git" ]]; then
  echo "-- unquoted extra token is a dead pathspec"
  VU_JSON="$("$HOLT" -C "$VOID" --json grep finite breakpoint || true)"
  VU_WARN="$(json_get 'print(r["warnings"][0] if r["warnings"] else "")' <<<"$VU_JSON")"
  assert "voidtrace unquoted pathspec warning" grep -q "breakpoint" <<<"$VU_WARN"

  echo "-- quoted phrase, wrong case, hints -i"
  VC_JSON="$("$HOLT" -C "$VOID" --json grep 'finite breakpoint' || true)"
  VC_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$VC_JSON")"
  assert "voidtrace phrase hints -i" grep -q -- "-i" <<<"$VC_HINT"
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
