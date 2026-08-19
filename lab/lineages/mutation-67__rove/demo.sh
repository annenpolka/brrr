#!/usr/bin/env bash
# Exercise rove: occupancy of a token along a file identity (grep --follow).
# ./demo.sh 0  — fixture + sitbone/skills + kizu follow (skip voidtrace)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
ROVE="$ROOT/rove"
chmod +x "$ROVE"
CHEAP=0
if [[ "${1:-}" == "0" ]]; then
  CHEAP=1
fi

if [[ ! -x "$ROVE" ]]; then
  echo "demo: rove is not executable" >&2
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
FIX="$(mktemp -d "${TMPDIR:-/tmp}/rove-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "rove-demo"
git -C "$FIX" config user.email "rove@example.test"

# t0: always-on file + TOKEN_A in keep.txt + TOKEN_B in alpha.txt + TOKEN_G in spaced name
mkdir -p "$FIX/nested/deep"
printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'born\n' > "$FIX/oscillate.txt"
printf 'ghost\nTOKEN_G\n' > "$FIX/old name.txt"
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

# t3: rename + shift TOKEN_B down a line in alpha.txt (line number changes, text does not)
git -C "$FIX" mv "old name.txt" "new name.txt"
printf 'header\nTOKEN_B\n' > "$FIX/alpha.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t3: rename with spaces, TOKEN_B line shifts"

# t4: kill oscillate, TOKEN_A reincarnates, TOKEN_B leaves alpha, TOKEN_G dropped from dest
rm "$FIX/oscillate.txt"
printf 'other\nTOKEN_A\n' > "$FIX/other.txt"
printf 'header\n' > "$FIX/alpha.txt"
printf 'ghost\n' > "$FIX/new name.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t4: kill oscillate, TOKEN_A reincarnates, TOKEN_B moves, TOKEN_G dies"

# t5: nested git repo that should NOT be walked as the root
mkdir -p "$FIX/vendor/nested"
git -C "$FIX/vendor/nested" init -q -b inner
git -C "$FIX/vendor/nested" config user.name "rove-demo"
git -C "$FIX/vendor/nested" config user.email "rove@example.test"
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
OSC_JSON="$("$ROVE" -C "$FIX" --no-follow --color never --json exists oscillate.txt || true)"
OSC_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$OSC_JSON")"
OSC_TRUE="$(json_get 'print(r["true_commits"])' <<<"$OSC_JSON")"
OSC_PATTERN="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$OSC_JSON")"
assert_eq "oscillate holds_now" "$OSC_NOW" "0"
assert_eq "oscillate true_commits" "$OSC_TRUE" "3"
assert_eq "oscillate era pattern" "$OSC_PATTERN" "TFTF"
OSC_F="$("$ROVE" -C "$FIX" --follow --json exists oscillate.txt || true)"
OSC_FPAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"])' <<<"$OSC_F")"
assert_eq "follow oscillate does not reincarnate the same path (TF, true=1)" "$OSC_FPAT" "TF 1"

echo "-- exists 'old name.txt' vs 'new name.txt' (--no-follow: rename is a path death)"
OLD_PAT="$("$ROVE" -C "$FIX" --no-follow --oneline exists "old name.txt" || true)"
NEW_PAT="$("$ROVE" -C "$FIX" --no-follow --oneline exists "new name.txt" || true)"
OLD_TF="$(awk '{printf $1}' <<<"$OLD_PAT" | tr -d '\n')"
NEW_TF="$(awk '{printf $1}' <<<"$NEW_PAT" | tr -d '\n')"
assert_eq "old name --no-follow eras" "$OLD_TF" "TF"
assert_eq "new name --no-follow eras" "$NEW_TF" "FT"

echo "-- --follow exists: rename is one identity (query old or new, same roost)"
OLD_F="$("$ROVE" -C "$FIX" --follow --json exists "old name.txt" || true)"
NEW_F="$("$ROVE" -C "$FIX" --json exists "new name.txt" || true)"
OLD_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$OLD_F")"
NEW_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$NEW_F")"
OLD_BOOL="$(json_get 'print(int(r["always_held"]), r["boolean_eras"], len(r["eras"]), int(r["follow"]))' <<<"$OLD_F")"
NEW_BOOL="$(json_get 'print(int(r["always_held"]), r["boolean_eras"], len(r["eras"]), int(r["follow"]))' <<<"$NEW_F")"
OLD_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$OLD_F")"
OLD_KINDS="$(json_get 'print([e["kind"] for e in r["eras"]])' <<<"$OLD_F")"
assert_eq "follow identity from old name" "$OLD_ID" "old name.txt,new name.txt"
assert_eq "follow identity from new name" "$NEW_ID" "old name.txt,new name.txt"
assert_eq "follow old always held, boolean=1, 2 holder eras" "$OLD_BOOL" "1 1 2 1"
assert_eq "follow new matches old" "$NEW_BOOL" "$OLD_BOOL"
assert_eq "follow holders old then new" "$OLD_HOLD" "old name.txt | new name.txt"
assert_eq "follow kinds birth then move" "$OLD_KINDS" "['birth', 'move']"

echo "-- grep --follow TOKEN_G along the spaced rename (the flipped assumption)"
G_NF="$("$ROVE" -C "$FIX" --no-follow --json grep TOKEN_G -- "old name.txt" || true)"
G_NF_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"], int(r["holds_now"]))' <<<"$G_NF")"
G_NF_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$G_NF")"
assert_eq "no-follow grep old TOKEN_G dies at rename (TF, true=3, now=0)" "$G_NF_PAT" "TF 3 0"
assert "no-follow names the dest and suggests --follow" grep -q -- "--follow" <<<"$G_NF_HINT"
assert "no-follow hint names new name.txt" grep -q "new name.txt" <<<"$G_NF_HINT"

G_OLD="$("$ROVE" -C "$FIX" --json grep TOKEN_G -- "old name.txt" || true)"
G_NEW="$("$ROVE" -C "$FIX" --json grep TOKEN_G -- "new name.txt" || true)"
G_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$G_OLD")"
G_ID2="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$G_NEW")"
G_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"], int(r["holds_now"]))' <<<"$G_OLD")"
G_PAT2="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"], int(r["holds_now"]))' <<<"$G_NEW")"
G_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$G_OLD")"
G_KINDS="$(json_get 'print([e["kind"] for e in r["eras"]])' <<<"$G_OLD")"
assert_eq "grep --follow identity from old name" "$G_ID" "old name.txt,new name.txt"
assert_eq "grep --follow identity from new name is the same roost" "$G_ID2" "$G_ID"
assert_eq "grep --follow TOKEN_G survives rename then dies when token drops (TTF, true=4)" "$G_PAT" "TTF 4 0"
assert_eq "grep --follow from dest matches old" "$G_PAT2" "$G_PAT"
assert_eq "grep --follow holders old then new" "$G_HOLD" "old name.txt | new name.txt"
assert_eq "grep --follow kinds birth/move/death" "$G_KINDS" "['birth', 'move', 'death']"

echo "-- grep --follow does not treat a copy as identity (TOKEN_B -- alpha stays alpha)"
GB_F="$("$ROVE" -C "$FIX" --json grep TOKEN_B -- alpha.txt || true)"
GB_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$GB_F")"
GB_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], ",".join(r["eras"][-1]["holders"] if r["eras"][-1]["value"] else []))' <<<"$GB_F")"
GB_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$GB_F")"
assert_eq "follow grep TOKEN_B -- alpha identity is not beta" "$GB_ID" "alpha.txt"
assert_eq "follow grep TOKEN_B -- alpha dies when token leaves alpha (now=0, true=4)" "$GB_NOW" "0 4 "
assert_eq "follow grep TOKEN_B -- alpha pattern TF" "$GB_PAT" "TF"

echo "-- grep --follow oscillate TOKEN_A is path-limited to oscillate (never held: TOKEN_A never lived there)"
# TOKEN_G reincarnation on oscillate.txt: --no-follow sees the second life, --follow does not
printf 'TOKEN_G\n' > "$FIX/oscillate.txt"
git -C "$FIX" add oscillate.txt
git -C "$FIX" commit -q -m "t7: reincarnate oscillate with TOKEN_G"
OSC_G_NF="$("$ROVE" -C "$FIX" --no-follow --json grep TOKEN_G -- oscillate.txt || true)"
OSC_G_F="$("$ROVE" -C "$FIX" --follow --json grep TOKEN_G -- oscillate.txt || true)"
OSC_G_NFP="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"], int(r["holds_now"]))' <<<"$OSC_G_NF")"
OSC_G_FP="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]), r["true_commits"], int(r["holds_now"]))' <<<"$OSC_G_F")"
# oscillate existed t0, t2-t3; TOKEN_G was never in it until t7. no-follow: F until t7 then T.
assert_eq "no-follow grep TOKEN_G -- oscillate is reincarnation (FT, true=1, now=1)" "$OSC_G_NFP" "FT 1 1"
assert_eq "follow grep TOKEN_G -- oscillate does not take the reincarnation (now=0)" "$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$OSC_G_F")" "0 0"

echo "-- exists Japanese path"
"$ROVE" -C "$FIX" -q exists "計画.md"
assert "計画.md holds now" true

echo "-- glob exists 'nested/deep/*'"
if "$ROVE" -C "$FIX" -q exists 'nested/deep/*'; then
  assert "glob exists now" true
else
  assert "glob exists now" false
fi

echo "-- grep TOKEN_A reincarnation (T F T F; FALSE gap already splits holders)"
TOK_JSON="$("$ROVE" -C "$FIX" --json grep TOKEN_A || true)"
TOK_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$TOK_JSON")"
assert_eq "TOKEN_A era pattern" "$TOK_PAT" "TFTF"
WIT_START="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(trues[0]["holders"][0])' <<<"$TOK_JSON")"
WIT_LAST="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(trues[-1]["holders"][0])' <<<"$TOK_JSON")"
assert_eq "first TOKEN_A holder" "$WIT_START" "keep.txt"
assert_eq "last TOKEN_A holder" "$WIT_LAST" "other.txt"

echo "-- grep TOKEN_B: occupancy never flips, holders copy then move"
B_JSON="$("$ROVE" -C "$FIX" --json grep TOKEN_B || true)"
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
BB_JSON="$("$ROVE" -C "$FIX" --boolean --json grep TOKEN_B || true)"
BB_N="$(json_get 'print(len(r["eras"]), int(r["split_holders"]))' <<<"$BB_JSON")"
assert_eq "TOKEN_B --boolean is one era" "$BB_N" "1 0"

echo "-- --follow grep without a path is a dedicated error"
set +e
NO_PATH_ERR="$("$ROVE" -C "$FIX" --follow grep TOKEN_G 2>&1)"
NO_PATH_RC=$?
set -e
assert_eq "follow grep without path exit" "$NO_PATH_RC" "2"
assert "follow grep without path mentions file identity" grep -q "file identity" <<<"$NO_PATH_ERR"

echo "-- --revs / exit codes"
set +e
"$ROVE" -C "$FIX" -q exists oscillate.txt
OSC_RC=$?
"$ROVE" -C "$FIX" -q exists keep.txt
KEEP_RC=$?
"$ROVE" -C "$FIX" -q exists 'does-not-exist.xyz'
MISS_RC=$?
set -e
assert_eq "exists oscillate exit" "$OSC_RC" "1"
assert_eq "exists keep exit" "$KEEP_RC" "0"
assert_eq "exists missing exit" "$MISS_RC" "1"

echo "-- dead pathspec warns instead of silent never-held"
DEAD_JSON="$("$ROVE" -C "$FIX" --json grep TOKEN_A definitely-not-a-file || true)"
DEAD_WARN="$(json_get 'print(r["warnings"][0] if r["warnings"] else "")' <<<"$DEAD_JSON")"
assert "dead pathspec warning" grep -q "definitely-not-a-file" <<<"$DEAD_WARN"
assert "dead pathspec suggests quoting" grep -q "rove grep 'TOKEN_A definitely-not-a-file'" <<<"$DEAD_WARN"

echo "-- wrong case hints -i"
CASE_JSON="$("$ROVE" -C "$FIX" --json grep token_a || true)"
CASE_HINT="$(json_get 'print((r["hints"] or [r["hint"] or ""])[0])' <<<"$CASE_JSON")"
assert "case-fold hint mentions -i" grep -q -- "-i" <<<"$CASE_HINT"

echo "-- 3-hop identity: old.txt → new name.txt → 最終.md, grep 計画TOKEN from any name"
HOP="$(mktemp -d "${TMPDIR:-/tmp}/rove-hop.XXXXXX")"
git -C "$HOP" init -q -b main
git -C "$HOP" config user.name "rove-demo"
git -C "$HOP" config user.email "rove@example.test"
printf '計画TOKEN\n' > "$HOP/old.txt"
git -C "$HOP" add old.txt && git -C "$HOP" commit -q -m hop0
git -C "$HOP" mv old.txt "new name.txt" && git -C "$HOP" commit -q -m hop1
git -C "$HOP" mv "new name.txt" "最終.md" && git -C "$HOP" commit -q -m hop2
HOP_OLD="$("$ROVE" -C "$HOP" --json grep 計画TOKEN -- old.txt || true)"
HOP_MID="$("$ROVE" -C "$HOP" --json grep 計画TOKEN -- "new name.txt" || true)"
HOP_NEW="$("$ROVE" -C "$HOP" --json grep 計画TOKEN -- "最終.md" || true)"
HOP_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$HOP_OLD")"
HOP_ID2="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$HOP_MID")"
HOP_ID3="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$HOP_NEW")"
HOP_N="$(json_get 'print(r["true_commits"], len(r["eras"]), r["boolean_eras"])' <<<"$HOP_OLD")"
HOP_KINDS="$(json_get 'print([e["kind"] for e in r["eras"]])' <<<"$HOP_OLD")"
HOP_EX="$(json_get 'print(r["true_commits"], len(r["eras"]))' <<<"$("$ROVE" -C "$HOP" --json exists old.txt || true)")"
assert_eq "3-hop grep identity from old.txt" "$HOP_ID" "old.txt → new name.txt → 最終.md"
assert_eq "3-hop grep identity from mid name" "$HOP_ID2" "$HOP_ID"
assert_eq "3-hop grep identity from 最終.md" "$HOP_ID3" "$HOP_ID"
assert_eq "3-hop grep true=3 eras=3 boolean=1" "$HOP_N" "3 3 1"
assert_eq "3-hop grep kinds birth/move/move" "$HOP_KINDS" "['birth', 'move', 'move']"
assert_eq "3-hop exists matches grep occupancy (token never left)" "$HOP_EX" "3 3"
rm -rf "$HOP"

echo "-- non-ff merge-birth: first-parent follow from the old name occupies dest"
MB="$(mktemp -d "${TMPDIR:-/tmp}/rove-merge.XXXXXX")"
git -C "$MB" init -q -b main
git -C "$MB" config user.name "rove-demo"
git -C "$MB" config user.email "rove@example.test"
echo base > "$MB/keep.txt"
git -C "$MB" add keep.txt && git -C "$MB" commit -q -m base
git -C "$MB" checkout -q -b topic
printf 'TOKEN_M\n' > "$MB/old.txt"
git -C "$MB" add old.txt && git -C "$MB" commit -q -m birth
git -C "$MB" mv old.txt dest.txt && git -C "$MB" commit -q -m rename
git -C "$MB" checkout -q main
echo extra >> "$MB/keep.txt"
git -C "$MB" add keep.txt && git -C "$MB" commit -q -m extra
git -C "$MB" merge -q --no-ff --no-edit topic
MB_OLD="$("$ROVE" -C "$MB" --json grep TOKEN_M -- old.txt || true)"
MB_DEST="$("$ROVE" -C "$MB" --json grep TOKEN_M -- dest.txt || true)"
MB_NF="$("$ROVE" -C "$MB" --no-follow --json grep TOKEN_M -- old.txt || true)"
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

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/rove-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$ROVE" -C "$EMPTY" exists README.md 2>&1)"
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

  echo "-- first-parent exists (mainline never shipped the file)"
  FP_JSON="$("$ROVE" -C "$SITBONE" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  FP_NEVER="$(json_get 'print(int(r["never_held"]))' <<<"$FP_JSON")"
  FP_HINT="$(json_get 'print(r["hint"] or "")' <<<"$FP_JSON")"
  assert_eq "first-parent never_held" "$FP_NEVER" "1"
  assert "first-parent hint mentions --full" grep -q -- "--full" <<<"$FP_HINT"

  echo "-- --full grep FocusRiverView: occupancy is one TRUE island, holders move"
  FR_JSON="$("$ROVE" -C "$SITBONE" --full --json grep FocusRiverView || true)"
  FR_BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$FR_JSON")"
  FR_N="$(json_get 'print(len(r["eras"]))' <<<"$FR_JSON")"
  FR_TRUE_N="$(json_get 'print(sum(1 for e in r["eras"] if e["value"]))' <<<"$FR_JSON")"
  FR_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$FR_JSON")"
  FR_KINDS="$(json_get 'print([e["kind"] for e in r["eras"] if e["value"]])' <<<"$FR_JSON")"
  assert_eq "FocusRiverView boolean eras (F T F)" "$FR_BOOL" "3"
  assert_eq "FocusRiverView TRUE kinds (shrink is code, not ghost)" "$FR_KINDS" "['birth', 'spread', 'shrink']"
  python3 -c 'import sys; n,b=int(sys.argv[1]),int(sys.argv[2]); sys.exit(0 if n>b and int(sys.argv[3])>=2 else 1)' "$FR_N" "$FR_BOOL" "$FR_TRUE_N"
  assert "FocusRiverView holder splits inside the TRUE island ($FR_N eras, $FR_TRUE_N TRUE, holders: $FR_HOLD)" true

  echo "---- sitbone --full grep FocusRiverView (human; holder splits) ----"
  "$ROVE" -C "$SITBONE" --full --color never grep FocusRiverView || true
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: skills circuit-breaker + preact-zero-mock ghost occupancy =="
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  CB_JSON="$("$ROVE" -C "$SKILLS" --json exists circuit-breaker/scripts/detect.sh || true)"
  CB_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$CB_JSON")"
  python3 -c 'import sys; p=sys.argv[1]; sys.exit(0 if ("T" in p and p.endswith("F")) else 1)' "$CB_PAT"
  assert "circuit-breaker lived then died ($CB_PAT)" true

  echo "-- grep preact-zero-mock: still TRUE after the plugin died (README is the holder)"
  PZ_JSON="$("$ROVE" -C "$SKILLS" --json grep preact-zero-mock || true)"
  PZ_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$PZ_JSON")"
  PZ_BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$PZ_JSON")"
  PZ_TRUE_N="$(json_get 'print(sum(1 for e in r["eras"] if e["value"]))' <<<"$PZ_JSON")"
  PZ_LAST="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(",".join(trues[-1]["holders"]))' <<<"$PZ_JSON")"
  PZ_DROP="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(",".join(trues[-1]["dropped"]))' <<<"$PZ_JSON")"
  assert_eq "preact-zero-mock holds now (ghost occupancy)" "$PZ_NOW" "1"
  assert_eq "preact-zero-mock boolean eras (F T)" "$PZ_BOOL" "2"
  python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>=3 else 1)' "$PZ_TRUE_N"
  assert "preact-zero-mock has >=3 TRUE holder eras (got $PZ_TRUE_N)" true
  assert_eq "last preact-zero-mock holder is README.md" "$PZ_LAST" "README.md"
  assert "last era dropped the SKILL.md definition" grep -q "SKILL.md" <<<"$PZ_DROP"
  PZ_KIND="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(trues[-1]["kind"])' <<<"$PZ_JSON")"
  PZ_GHOST="$(json_get 'print(int(r["ghost_now"]))' <<<"$PZ_JSON")"
  PZ_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$PZ_JSON")"
  assert_eq "preact-zero-mock last era is ghost" "$PZ_KIND" "ghost"
  assert_eq "preact-zero-mock ghost_now" "$PZ_GHOST" "1"
  assert "ghost hint names the dead definition" grep -q "SKILL.md" <<<"$PZ_HINT"
  echo "---- skills grep preact-zero-mock (human) ----"
  "$ROVE" -C "$SKILLS" --color never grep preact-zero-mock || true
else
  echo "skip skills (not present)"
fi

echo
echo "== real repo: kizu rename is one token occupancy =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  KZ_JSON="$("$ROVE" -C "$KIZU" --json exists CLAUDE.md || true)"
  KZ_SCAN="$(json_get 'print(r["commits_scanned"], r["reachable"])' <<<"$KZ_JSON")"
  python3 -c 'import sys; s,r=map(int,sys.argv[1].split()); sys.exit(0 if r>s else 1)' "$KZ_SCAN"
  assert "kizu reachable > first-parent scanned ($KZ_SCAN)" true
  KZ_ORIGIN="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print((trues[0].get("origin") or {}).get("short",""))' <<<"$KZ_JSON")"
  assert_eq "kizu first-parent origin is off-mainline birth e1098c8" "$KZ_ORIGIN" "e1098c8"

  echo "-- --full --follow stitches R100; grep -F '10 の AI' is the same roost from either name"
  KD_JSON="$("$ROVE" -C "$KIZU" --full --json grep -F '10 の AI' -- docs/deep-research-ai-agent-hooks.md || true)"
  KO_JSON="$("$ROVE" -C "$KIZU" --full --json grep -F '10 の AI' -- deep-research-ai-agent-hooks.md || true)"
  KD_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KD_JSON")"
  KO_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KO_JSON")"
  KD_N="$(json_get 'print(r["true_commits"], r["boolean_eras"], int(r["holds_now"]))' <<<"$KD_JSON")"
  KO_N="$(json_get 'print(r["true_commits"], r["boolean_eras"], int(r["holds_now"]))' <<<"$KO_JSON")"
  KD_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$KD_JSON")"
  KN_JSON="$("$ROVE" -C "$KIZU" --full --no-follow --json grep -F '10 の AI' -- deep-research-ai-agent-hooks.md || true)"
  KN_TRUE="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$KN_JSON")"
  KN_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$KN_JSON")"
  assert_eq "kizu follow grep identity dest" "$KD_ID" "deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md"
  assert_eq "kizu follow grep identity old name is the same roost" "$KO_ID" "$KD_ID"
  assert_eq "kizu follow grep true=187/boolean=2/now" "$KD_N" "187 2 1"
  assert_eq "kizu follow grep from old name matches dest" "$KO_N" "$KD_N"
  assert_eq "kizu follow grep holders old then docs/" "$KD_HOLD" "deep-research-ai-agent-hooks.md | docs/deep-research-ai-agent-hooks.md"
  assert_eq "kizu --no-follow grep old name is a path death" "$KN_TRUE" "13 0"
  assert "kizu --no-follow grep names the dest rename" grep -q "docs/deep-research-ai-agent-hooks.md" <<<"$KN_HINT"
  KD_KINDS="$(json_get 'print([e["kind"] for e in r["eras"] if e["value"]])' <<<"$KD_JSON")"
  KD_GHOST="$(json_get 'print(int(r["ghost_now"]))' <<<"$KD_JSON")"
  assert_eq "kizu follow grep TRUE kinds are birth/move (not ghost: the file moved)" "$KD_KINDS" "['birth', 'move']"
  assert_eq "kizu follow grep ghost_now" "$KD_GHOST" "0"

  echo "-- first-parent grep --follow from the OLD name is the dest roost (merge-birth stitch)"
  KP_OLD="$("$ROVE" -C "$KIZU" --json grep -F '10 の AI' -- deep-research-ai-agent-hooks.md || true)"
  KP_DEST="$("$ROVE" -C "$KIZU" --json grep -F '10 の AI' -- docs/deep-research-ai-agent-hooks.md || true)"
  KP_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KP_OLD")"
  KP_ID2="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KP_DEST")"
  KP_N="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$KP_OLD")"
  KP_N2="$(json_get 'print(r["true_commits"], int(r["holds_now"]))' <<<"$KP_DEST")"
  KP_ORIGIN="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print((trues[0].get("origin") or {}).get("short",""))' <<<"$KP_OLD")"
  KP_AS="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; w=(trues[0].get("origin") or {}); print((trues[0].get("holders") or [""])[0])' <<<"$KP_OLD")"
  assert_eq "kizu first-parent grep old identity" "$KP_ID" "deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md"
  assert_eq "kizu first-parent grep dest identity matches old" "$KP_ID2" "$KP_ID"
  assert_eq "kizu first-parent grep old true/now" "$KP_N" "21 1"
  assert_eq "kizu first-parent grep dest matches old" "$KP_N2" "$KP_N"
  assert_eq "kizu first-parent grep origin is old-name birth 321a830" "$KP_ORIGIN" "321a830"
  assert_eq "kizu first-parent grep holders dest" "$KP_AS" "docs/deep-research-ai-agent-hooks.md"

  echo "-- tenure split is refused: grep --follow -- src/git.rs does not jump to parse.rs"
  SPLIT="$("$ROVE" -C "$KIZU" --full --json grep -F parse_diff_git_header -- src/git.rs || true)"
  SPLIT_ID="$(json_get 'print(",".join(r.get("identity") or []))' <<<"$SPLIT")"
  SPLIT_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$SPLIT")"
  SPLIT_LAST="$(json_get 'print(r["eras"][-1]["kind"])' <<<"$SPLIT")"
  assert_eq "kizu git.rs follow identity stays git.rs" "$SPLIT_ID" "src/git.rs"
  assert_eq "kizu git.rs follow holds_now after split" "$SPLIT_NOW" "0"
  assert_eq "kizu git.rs follow last era is death" "$SPLIT_LAST" "death"

  echo "---- kizu --full follow grep dest (human) ----"
  "$ROVE" -C "$KIZU" --full --color never grep -F '10 の AI' -- docs/deep-research-ai-agent-hooks.md || true
  echo "---- kizu first-parent follow grep old name (origin is the old name) ----"
  "$ROVE" -C "$KIZU" --color never grep -F '10 の AI' -- deep-research-ai-agent-hooks.md || true
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
  VU_JSON="$("$ROVE" -C "$VOID" --json grep finite breakpoint || true)"
  VU_WARN="$(json_get 'print(r["warnings"][0] if r["warnings"] else "")' <<<"$VU_JSON")"
  assert "voidtrace unquoted pathspec warning" grep -q "breakpoint" <<<"$VU_WARN"

  echo "-- quoted phrase, wrong case, hints -i"
  VC_JSON="$("$ROVE" -C "$VOID" --json grep 'finite breakpoint' || true)"
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
