#!/usr/bin/env bash
# Exercise weir: merge occupancy is a recursive occupancy join, not a parent-tree join.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WEIR="$ROOT/weir"
chmod +x "$WEIR"

if [[ ! -x "$WEIR" ]]; then
  echo "demo: weir is not executable" >&2
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

jget() {
  python3 -c 'import json,sys; r=json.load(sys.stdin); '"$1"''
}

echo "== lattice tables (runnable, not just markdown) =="
LAT="$("$WEIR" --json lattice)"
MEET_TF="$(printf '%s' "$LAT" | jget 'print(r["all"]["table"][1][r["all"]["table"][0].index("FALSE")])')"
JOIN_TF="$(printf '%s' "$LAT" | jget 'print(r["any"]["table"][1][r["any"]["table"][0].index("FALSE")])')"
MEET_TU="$(printf '%s' "$LAT" | jget 'print(r["all"]["table"][1][r["all"]["table"][0].index("UNKNOWN")])')"
JOIN_FS="$(printf '%s' "$LAT" | jget 'print(r["any"]["table"][5][r["any"]["table"][0].index("SHALLOW")])')"
assert_eq "meet TRUE ⊓ FALSE = FALSE" "$MEET_TF" "FALSE"
assert_eq "join TRUE ⊔ FALSE = TRUE" "$JOIN_TF" "TRUE"
assert_eq "meet TRUE ⊓ UNKNOWN = UNKNOWN" "$MEET_TU" "UNKNOWN"
assert_eq "join FALSE ⊔ SHALLOW = SHALLOW (not FALSE)" "$JOIN_FS" "SHALLOW"

echo
echo "== hole: --now on a commit-less dirty tree answers the filesystem =="
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/weir-empty.XXXXXX")"
EMPTY_DIRTY="$(mktemp -d "${TMPDIR:-/tmp}/weir-empty-dirty.XXXXXX")"
git -C "$EMPTY" init -q -b main
git -C "$EMPTY_DIRTY" init -q -b main
printf 'hello from disk\n' > "$EMPTY_DIRTY/README.md"

set +e
EMPTY_JSON="$("$WEIR" -C "$EMPTY" --json exists README.md 2>/dev/null)"
EMPTY_RC=$?
EMPTY_NOW_JSON="$("$WEIR" -C "$EMPTY" --now --json exists README.md 2>/dev/null)"
EMPTY_NOW_RC=$?
DIRTY_JSON="$("$WEIR" -C "$EMPTY_DIRTY" --now --json exists README.md 2>/dev/null)"
DIRTY_RC=$?
DIRTY_OFF="$("$WEIR" -C "$EMPTY_DIRTY" --json exists README.md 2>/dev/null)"
DIRTY_OFF_RC=$?
set -e

EMPTY_ST="$(printf '%s' "$EMPTY_JSON" | jget 'print(r["holds_now"])')"
EMPTY_NOW_ST="$(printf '%s' "$EMPTY_NOW_JSON" | jget 'print(r["holds_now"])')"
DIRTY_ST="$(printf '%s' "$DIRTY_JSON" | jget 'print(r["holds_now"])')"
DIRTY_KIND="$(printf '%s' "$DIRTY_JSON" | jget 'print(r["eras"][-1]["end"]["kind"])')"
DIRTY_WALK="$(printf '%s' "$DIRTY_JSON" | jget 'print(r["walk"])')"
EMPTY_WALK="$(printf '%s' "$EMPTY_JSON" | jget 'print(r["walk"])')"
DIRTY_OFF_ST="$(printf '%s' "$DIRTY_OFF" | jget 'print(r["holds_now"])')"
assert_eq "empty without --now status" "$EMPTY_ST" "EMPTY"
assert_eq "empty without --now exit" "$EMPTY_RC" "3"
assert_eq "empty without --now walk" "$EMPTY_WALK" "unborn"
assert_eq "empty --now missing README" "$EMPTY_NOW_ST" "FALSE"
assert_eq "empty --now missing exit" "$EMPTY_NOW_RC" "1"
assert_eq "empty-dirty --now status" "$DIRTY_ST" "TRUE"
assert_eq "empty-dirty --now exit" "$DIRTY_RC" "0"
assert_eq "empty-dirty --now kind" "$DIRTY_KIND" "worktree"
assert_eq "empty-dirty --now walk" "$DIRTY_WALK" "filesystem"
assert_eq "empty-dirty without --now is EMPTY" "$DIRTY_OFF_ST" "EMPTY"
assert_eq "empty-dirty without --now exit" "$DIRTY_OFF_RC" "3"
rm -rf "$EMPTY" "$EMPTY_DIRTY"

echo
echo "== timeout is UNKNOWN, not FALSE; --timeout 0 is refused =="
TO="$(mktemp -d "${TMPDIR:-/tmp}/weir-timeout.XXXXXX")"
git -C "$TO" init -q -b main
git -C "$TO" config user.name "weir-demo"
git -C "$TO" config user.email "weir@example.test"
echo fast > "$TO/keep.txt"
git -C "$TO" add keep.txt
git -C "$TO" commit -q -m "fast only"
echo slow > "$TO/slow"
git -C "$TO" add slow
git -C "$TO" commit -q -m "slow present"
rm "$TO/slow"
git -C "$TO" add -A
git -C "$TO" commit -q -m "slow gone"

set +e
TO_JSON="$("$WEIR" -C "$TO" --json --timeout 0.2 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi')"
TO_RC=$?
TO0_ERR="$("$WEIR" -C "$TO" --timeout 0 exec -- true 2>&1)"
TO0_RC=$?
set -e
TO_PAT="$(printf '%s' "$TO_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
TO_NOW="$(printf '%s' "$TO_JSON" | jget 'print(r["holds_now"])')"
TO_UNK="$(printf '%s' "$TO_JSON" | jget 'print(r["unknown_commits"])')"
assert_eq "timeout era initials" "$TO_PAT" "TUT"
assert_eq "timeout now" "$TO_NOW" "TRUE"
assert_eq "timeout unknown count" "$TO_UNK" "1"
assert_eq "timeout last-true exit" "$TO_RC" "0"
assert_eq "--timeout 0 refused" "$TO0_RC" "2"
assert "--timeout 0 mentions UNKNOWN" grep -q "UNKNOWN" <<<"$TO0_ERR"

set +e
FOLLOW_ERR="$("$WEIR" -C "$TO" --follow exists keep.txt 2>&1)"
FOLLOW_RC=$?
BOOL_UNK_ERR="$("$WEIR" -C "$TO" --boolean --timeout 0.2 --json exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi' 2>&1)"
BOOL_UNK_RC=$?
set -e
assert_eq "--follow is berth (exit 2)" "$FOLLOW_RC" "2"
assert "--follow names berth" grep -q "berth" <<<"$FOLLOW_ERR"
assert_eq "--boolean that would downcast UNKNOWN is refused" "$BOOL_UNK_RC" "2"
assert "--boolean refuse names labelled lie" grep -q "labelled lie" <<<"$BOOL_UNK_ERR"
rm -rf "$TO"

echo
echo "== diamond: merge occupancy is the parent join, not a birth at M =="
DIA="$(mktemp -d "${TMPDIR:-/tmp}/weir-diamond.XXXXXX")"
git -C "$DIA" init -q -b main
git -C "$DIA" config user.name "weir-demo"
git -C "$DIA" config user.email "weir@example.test"
git -C "$DIA" config commit.gpgsign false

export_git_date() {
  export GIT_AUTHOR_DATE="$1"
  export GIT_COMMITTER_DATE="$1"
}

export_git_date "2022-01-01T00:00:00"
echo base > "$DIA/README"
git -C "$DIA" add README
git -C "$DIA" commit -q -m "A base"
A="$(git -C "$DIA" rev-parse HEAD)"

git -C "$DIA" checkout -q -b topic
export_git_date "2022-01-02T00:00:00"
mkdir -p "$DIA/src"
printf 'TOKEN\nif x > 0:\n    return 1\n' > "$DIA/src/app.py"
git -C "$DIA" add src/app.py
git -C "$DIA" commit -q -m "C TOKEN born on topic"
C="$(git -C "$DIA" rev-parse HEAD)"
export_git_date "2022-01-03T00:00:00"
echo still >> "$DIA/src/app.py"
git -C "$DIA" add src/app.py
git -C "$DIA" commit -q -m "D still holds on topic"
D="$(git -C "$DIA" rev-parse HEAD)"

git -C "$DIA" checkout -q main
export_git_date "2022-01-04T00:00:00"
echo mainline >> "$DIA/README"
git -C "$DIA" add README
git -C "$DIA" commit -q -m "B main no occupancy"
B="$(git -C "$DIA" rev-parse HEAD)"

export_git_date "2022-01-05T00:00:00"
git -C "$DIA" merge -q --no-ff topic -m "M merge topic"
M="$(git -C "$DIA" rev-parse HEAD)"
unset GIT_AUTHOR_DATE GIT_COMMITTER_DATE

ALL_JSON="$("$WEIR" -C "$DIA" --json exists src/app.py || true)"
ALL_NOW="$(printf '%s' "$ALL_JSON" | jget 'print(r["holds_now"])')"
ALL_TREE="$(printf '%s' "$ALL_JSON" | jget 'print(r["tree_now"])')"
ALL_FORDS="$(printf '%s' "$ALL_JSON" | jget 'print(r["fords"])')"
ALL_WEIRS="$(printf '%s' "$ALL_JSON" | jget 'print(r["weirs"])')"
ALL_JOIN="$(printf '%s' "$ALL_JSON" | jget 'print(r["join"])')"
ALL_KIND="$(printf '%s' "$ALL_JSON" | jget 'print(r["eras"][-1]["kind"])')"
ALL_EQ="$(printf '%s' "$ALL_JSON" | jget 'print(r["eras"][-1]["join"] or "")')"
ALL_ORIGIN="$(printf '%s' "$ALL_JSON" | jget 'print((r["eras"][-1].get("origin") or {}).get("sha",""))')"
ALL_TRUE_START="$(printf '%s' "$ALL_JSON" | jget 'print(next((e["start"]["sha"] for e in r["eras"] if e["status"]=="TRUE"), ""))')"
ALL_REFUSE="$(printf '%s' "$ALL_JSON" | jget 'print(r["eras"][-1].get("refused_birth"))')"
assert_eq "diamond --all now is FALSE (does not preserve)" "$ALL_NOW" "FALSE"
assert_eq "diamond --all tree_now is TRUE" "$ALL_TREE" "TRUE"
assert_eq "diamond --all fords" "$ALL_FORDS" "1"
assert_eq "diamond --all weirs" "$ALL_WEIRS" "1"
assert_eq "diamond --all join op" "$ALL_JOIN" "all"
assert_eq "diamond --all last era is a weir" "$ALL_KIND" "weir"
assert "diamond --all equation mentions FALSE" grep -q "FALSE" <<<"$ALL_EQ"
assert "diamond --all origin is topic D" grep -q "${D:0:7}" <<<"$ALL_ORIGIN"
assert_eq "diamond --all does not start TRUE at the merge" "$ALL_TRUE_START" ""
assert_eq "diamond --all refuses birth" "$ALL_REFUSE" "True"

ANY_JSON="$("$WEIR" -C "$DIA" --any --json exists src/app.py || true)"
ANY_NOW="$(printf '%s' "$ANY_JSON" | jget 'print(r["holds_now"])')"
ANY_KIND="$(printf '%s' "$ANY_JSON" | jget 'print(r["eras"][-1]["kind"])')"
ANY_EQ="$(printf '%s' "$ANY_JSON" | jget 'print(r["eras"][-1]["join"] or "")')"
ANY_ORIGIN="$(printf '%s' "$ANY_JSON" | jget 'print((r["eras"][-1].get("origin") or {}).get("short",""))')"
ANY_TRUE_N="$(printf '%s' "$ANY_JSON" | jget 'print(sum(1 for e in r["eras"] if e["status"]=="TRUE"))')"
assert_eq "diamond --any now is TRUE (introduced via a side)" "$ANY_NOW" "TRUE"
assert_eq "diamond --any last era is still a weir" "$ANY_KIND" "weir"
assert "diamond --any equation is a join" grep -q "TRUE" <<<"$ANY_EQ"
assert "diamond --any origin is D" grep -q "${D:0:7}" <<<"$ANY_ORIGIN"
assert_eq "diamond --any has a TRUE ford era, not a 3-commit birth" "$ANY_TRUE_N" "1"

TREE_JSON="$("$WEIR" -C "$DIA" --tree --json exists src/app.py || true)"
TREE_PAT="$(printf '%s' "$TREE_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
TREE_START="$(printf '%s' "$TREE_JSON" | jget 'print(next(e["start"]["sha"] for e in r["eras"] if e["status"]=="TRUE"))')"
TREE_FORDS="$(printf '%s' "$TREE_JSON" | jget 'print(r["fords"])')"
assert_eq "diamond --tree is held's FT birth at M" "$TREE_PAT" "FT"
assert "diamond --tree TRUE starts at merge" grep -q "${M:0:7}" <<<"$TREE_START"
assert_eq "diamond --tree has no fords" "$TREE_FORDS" "0"

BOOL_JSON="$("$WEIR" -C "$DIA" --boolean --json exists src/app.py || true)"
BOOL_PAT="$(printf '%s' "$BOOL_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
assert_eq "diamond --boolean recovers held FT" "$BOOL_PAT" "FT"

LAT_JSON="$("$WEIR" -C "$DIA" --full --json exists src/app.py || true)"
LAT_KINDS="$(printf '%s' "$LAT_JSON" | jget 'print(",".join(e["kind"]+":"+e["status"] for e in r["eras"]))')"
LAT_TRUE_START="$(printf '%s' "$LAT_JSON" | jget 'print(next(e["start"]["short"] for e in r["eras"] if e["status"]=="TRUE"))')"
LAT_FORD_SHA="$(printf '%s' "$LAT_JSON" | jget 'print(next(e["start"]["sha"] for e in r["eras"] if e["kind"]=="weir"))')"
LIST_JSON="$("$WEIR" -C "$DIA" --full --tree --list --json exists src/app.py || true)"
LIST_PAT="$(printf '%s' "$LIST_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
LAT_TRUE_KIND="$(printf '%s' "$LAT_JSON" | jget 'print(next(e["kind"] for e in r["eras"] if e["status"]=="TRUE"))')"
assert "diamond --full --all TRUE starts on topic (not M)" grep -q "${C:0:7}" <<<"$LAT_TRUE_START"
assert_eq "diamond --full topic TRUE is birth/run, not preserve" "$LAT_TRUE_KIND" "run"
assert "diamond --full weir is the merge" grep -q "${M:0:7}" <<<"$LAT_FORD_SHA"
assert_eq "diamond --full --tree --list is the FTFT lie" "$LIST_PAT" "FTFT"
echo "    --full --all kinds: $LAT_KINDS"

echo
echo "== merge-of-merges: parent merge contributes occupancy, not tree =="
MOM="$(mktemp -d "${TMPDIR:-/tmp}/weir-mom.XXXXXX")"
git -C "$MOM" init -q -b main
git -C "$MOM" config user.name "weir-demo"
git -C "$MOM" config user.email "weir@example.test"
git -C "$MOM" config commit.gpgsign false
echo base > "$MOM/README"
git -C "$MOM" add README
git -C "$MOM" commit -q -m "A base"
git -C "$MOM" checkout -q -b topic
mkdir -p "$MOM/src"
echo file > "$MOM/src/app.py"
git -C "$MOM" add src/app.py
git -C "$MOM" commit -q -m "C born on topic"
echo still >> "$MOM/src/app.py"
git -C "$MOM" add src/app.py
git -C "$MOM" commit -q -m "D still holds"
D1="$(git -C "$MOM" rev-parse HEAD)"
git -C "$MOM" checkout -q main
echo mainline >> "$MOM/README"
git -C "$MOM" add README
git -C "$MOM" commit -q -m "B main no occupancy"
git -C "$MOM" merge -q --no-ff topic -m "M1 merge topic"
M1="$(git -C "$MOM" rev-parse HEAD)"
git -C "$MOM" checkout -q -b topic2 "$D1"
echo more >> "$MOM/src/app.py"
git -C "$MOM" add src/app.py
git -C "$MOM" commit -q -m "E topic2 still holds"
E="$(git -C "$MOM" rev-parse HEAD)"
git -C "$MOM" checkout -q main
git -C "$MOM" merge -q --no-ff topic2 -m "M2 merge-of-merges"
M2="$(git -C "$MOM" rev-parse HEAD)"
echo after >> "$MOM/src/app.py"
git -C "$MOM" add src/app.py
git -C "$MOM" commit -q -m "G non-merge after M2"
G="$(git -C "$MOM" rev-parse HEAD)"

MOM_JSON="$("$WEIR" -C "$MOM" --json exists src/app.py || true)"
MOM_M1_KIND="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["kind"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M1:0:7}"'")))')"
MOM_M1_ST="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["status"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M1:0:7}"'")))')"
MOM_M2_KIND="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["kind"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M2:0:7}"'")))')"
MOM_M2_ST="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["status"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M2:0:7}"'")))')"
MOM_M2_REC="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["recursive"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M2:0:7}"'")))')"
MOM_M2_REASON="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["ford_reason"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M2:0:7}"'")))')"
MOM_M2_TREE="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["tree"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M2:0:7}"'")))')"
MOM_M2_SRC="$(printf '%s' "$MOM_JSON" | jget 'print(next(p["source"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M2:0:7}"'") for p in e["parents"] if p["is_merge"]))')"
MOM_M2_REFUSE="$(printf '%s' "$MOM_JSON" | jget 'print(next(e["refused_birth"] for e in r["eras"] if e["start"]["sha"].startswith("'"${M2:0:7}"'")))')"
MOM_TRUE_START="$(printf '%s' "$MOM_JSON" | jget 'print(next((e["start"]["sha"] for e in r["eras"] if e["status"]=="TRUE"), ""))')"
MOM_TRUE_KIND="$(printf '%s' "$MOM_JSON" | jget 'print(next((e["kind"] for e in r["eras"] if e["status"]=="TRUE"), ""))')"
assert_eq "M1 occupancy is FALSE weir" "$MOM_M1_ST" "FALSE"
assert_eq "M1 kind is weir" "$MOM_M1_KIND" "weir"
assert_eq "M2 occupancy is FALSE (recursive, not T⊓T preserve)" "$MOM_M2_ST" "FALSE"
assert_eq "M2 kind is weir" "$MOM_M2_KIND" "weir"
assert_eq "M2 is recursive" "$MOM_M2_REC" "True"
assert_eq "M2 reason is recursive" "$MOM_M2_REASON" "recursive"
assert_eq "M2 tree is TRUE" "$MOM_M2_TREE" "TRUE"
assert_eq "M2 merge-parent source is occupancy" "$MOM_M2_SRC" "occupancy"
assert_eq "M2 refuses birth" "$MOM_M2_REFUSE" "True"
assert "TRUE does not start at M2" python3 -c 'import sys; sys.exit(0 if sys.argv[1][:7]!=sys.argv[2][:7] else 1)' "$MOM_TRUE_START" "$M2"
assert "TRUE starts at non-merge G" grep -q "${G:0:7}" <<<"$MOM_TRUE_START"
assert_eq "TRUE after weir is continue, not birth" "$MOM_TRUE_KIND" "continue"
rm -rf "$MOM"

echo
echo "== preserve merge (T⊓T) is not a weir; merge-added file is tree≠join =="
PRES="$(mktemp -d "${TMPDIR:-/tmp}/weir-preserve.XXXXXX")"
git -C "$PRES" init -q -b main
git -C "$PRES" config user.name "weir-demo"
git -C "$PRES" config user.email "weir@example.test"
echo both > "$PRES/keep.txt"
git -C "$PRES" add keep.txt
git -C "$PRES" commit -q -m "root with file"
git -C "$PRES" checkout -q -b side
echo side > "$PRES/side.txt"
git -C "$PRES" add side.txt
git -C "$PRES" commit -q -m "side still has keep.txt"
git -C "$PRES" checkout -q main
echo main > "$PRES/main.txt"
git -C "$PRES" add main.txt
git -C "$PRES" commit -q -m "main still has keep.txt"
git -C "$PRES" merge -q --no-ff side -m "preserve merge"
PRES_JSON="$("$WEIR" -C "$PRES" --json exists keep.txt || true)"
PRES_FORDS="$(printf '%s' "$PRES_JSON" | jget 'print(r["fords"])')"
PRES_NOW="$(printf '%s' "$PRES_JSON" | jget 'print(r["holds_now"])')"
PRES_N="$(printf '%s' "$PRES_JSON" | jget 'print(len(r["eras"]))')"
assert_eq "T⊓T preserve is not a ford" "$PRES_FORDS" "0"
assert_eq "T⊓T now TRUE" "$PRES_NOW" "TRUE"
assert_eq "T⊓T compresses to one TRUE era" "$PRES_N" "1"
rm -rf "$PRES"

BORN="$(mktemp -d "${TMPDIR:-/tmp}/weir-mergeborn.XXXXXX")"
git -C "$BORN" init -q -b main
git -C "$BORN" config user.name "weir-demo"
git -C "$BORN" config user.email "weir@example.test"
echo a > "$BORN/a.txt"
git -C "$BORN" add a.txt
git -C "$BORN" commit -q -m "A"
git -C "$BORN" checkout -q -b side
echo b > "$BORN/b.txt"
git -C "$BORN" add b.txt
git -C "$BORN" commit -q -m "B"
git -C "$BORN" checkout -q main
git -C "$BORN" merge -q --no-ff --no-commit side
echo newborn > "$BORN/new.txt"
git -C "$BORN" add new.txt
git -C "$BORN" commit -q -m "M adds new.txt neither parent had"
BORN_JSON="$("$WEIR" -C "$BORN" --json exists new.txt || true)"
BORN_KIND="$(printf '%s' "$BORN_JSON" | jget 'print(r["eras"][-1]["kind"])')"
BORN_REASON="$(printf '%s' "$BORN_JSON" | jget 'print(r["eras"][-1]["ford_reason"] or "")')"
BORN_TREE="$(printf '%s' "$BORN_JSON" | jget 'print(r["eras"][-1]["tree"])')"
BORN_ST="$(printf '%s' "$BORN_JSON" | jget 'print(r["eras"][-1]["status"])')"
assert_eq "merge-added occupancy is parent join FALSE" "$BORN_ST" "FALSE"
assert_eq "merge-added tree is TRUE" "$BORN_TREE" "TRUE"
assert_eq "merge-added era is a weir" "$BORN_KIND" "weir"
assert_eq "merge-added reason is tree" "$BORN_REASON" "tree"
rm -rf "$BORN"

echo
echo "== timeout on a merge parent is UNKNOWN, not FALSE =="
TM="$(mktemp -d "${TMPDIR:-/tmp}/weir-timeout-merge.XXXXXX")"
git -C "$TM" init -q -b main
git -C "$TM" config user.name "weir-demo"
git -C "$TM" config user.email "weir@example.test"
echo fast > "$TM/keep.txt"
git -C "$TM" add keep.txt
git -C "$TM" commit -q -m "A fast"
git -C "$TM" checkout -q -b slow
echo slow > "$TM/slow"
git -C "$TM" add slow
git -C "$TM" commit -q -m "B slow"
git -C "$TM" checkout -q main
git -C "$TM" merge -q --no-ff slow -m "M"
set +e
TM_ALL="$("$WEIR" -C "$TM" --json --timeout 0.2 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi')"
TM_ALL_RC=$?
TM_ANY="$("$WEIR" -C "$TM" --any --json --timeout 0.2 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi')"
set -e
TM_NOW="$(printf '%s' "$TM_ALL" | jget 'print(r["holds_now"])')"
TM_FORD_ST="$(printf '%s' "$TM_ALL" | jget 'print(next(e["status"] for e in r["eras"] if e["kind"]=="weir"))')"
TM_EQ="$(printf '%s' "$TM_ALL" | jget 'print(next(e["join"] for e in r["eras"] if e["kind"]=="weir"))')"
TM_ANY_NOW="$(printf '%s' "$TM_ANY" | jget 'print(r["holds_now"])')"
assert_eq "timeout-merge --all now UNKNOWN" "$TM_NOW" "UNKNOWN"
assert_eq "timeout-merge ford is UNKNOWN not FALSE" "$TM_FORD_ST" "UNKNOWN"
assert_eq "timeout-merge exit 3" "$TM_ALL_RC" "3"
assert "timeout-merge equation has UNKNOWN" grep -q "UNKNOWN" <<<"$TM_EQ"
assert_eq "timeout-merge --any now TRUE (TRUE ⊔ UNKNOWN)" "$TM_ANY_NOW" "TRUE"
rm -rf "$TM"

echo
echo "== oscillating path still works; glob cost class; bad regex UNKNOWN =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/weir-osc.XXXXXX")"
git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "weir-demo"
git -C "$FIX" config user.email "weir@example.test"
printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'born\n' > "$FIX/oscillate.txt"
git -C "$FIX" add keep.txt oscillate.txt
git -C "$FIX" commit -q -m "t0: birth"
rm "$FIX/oscillate.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t1: kill oscillate"
printf 'reborn\n' > "$FIX/oscillate.txt"
printf 'keep\n' > "$FIX/keep.txt"
printf '計画\n' > "$FIX/計画.md"
git -C "$FIX" add oscillate.txt keep.txt "計画.md"
git -C "$FIX" commit -q -m "t2: revive"
printf 'stay\n' > "$FIX/stay.txt"
git -C "$FIX" add stay.txt
git -C "$FIX" commit -q -m "t3: stay"
rm "$FIX/oscillate.txt"
printf 'other\nTOKEN_A\n' > "$FIX/other.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t4: kill oscillate, TOKEN_A reincarnates"
printf 'keep\n' > "$FIX/other.txt"
git -C "$FIX" add other.txt
git -C "$FIX" commit -q -m "t5: TOKEN_A gone"

OSC_JSON="$("$WEIR" -C "$FIX" --json exists oscillate.txt || true)"
OSC_PAT="$(printf '%s' "$OSC_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
assert_eq "oscillate era initials" "$OSC_PAT" "TFTF"
"$WEIR" -C "$FIX" -q exists "計画.md"
assert "計画.md holds now" true

set +e
GLOB_ERR="$("$WEIR" -C "$FIX" exists '*' 2>&1)"
GLOB_RC=$?
set -e
assert_eq "exists * exit" "$GLOB_RC" "2"
assert "exists * points at glob" grep -q "weir glob" <<<"$GLOB_ERR"
GLOB_JSON="$("$WEIR" -C "$FIX" --json glob '計画.md' || true)"
GLOB_COST="$(printf '%s' "$GLOB_JSON" | jget 'print(r["cost"])')"
assert_eq "glob cost class" "$GLOB_COST" "per-tree"

set +e
RX_JSON="$("$WEIR" -C "$FIX" --json grep '[' 2>/dev/null)"
RX_RC=$?
set -e
RX_NOW="$(printf '%s' "$RX_JSON" | jget 'print(r["holds_now"])')"
RX_NEVER="$(printf '%s' "$RX_JSON" | jget 'print(int(r["never_held"]))')"
assert_eq "bad regex now UNKNOWN" "$RX_NOW" "UNKNOWN"
assert_eq "bad regex not never_held" "$RX_NEVER" "0"
assert_eq "bad regex exit 3" "$RX_RC" "3"

echo
echo "== binary-only occupancy is EMPTY, not FALSE =="
BIN="$(mktemp -d "${TMPDIR:-/tmp}/weir-binary.XXXXXX")"
git -C "$BIN" init -q -b main
git -C "$BIN" config user.name "weir-demo"
git -C "$BIN" config user.email "weir@example.test"
printf 'TOKEN_BIN visible\n' > "$BIN/visible.txt"
printf 'TOKEN_BIN\0hidden\n' > "$BIN/secret.bin"
git -C "$BIN" add visible.txt secret.bin
git -C "$BIN" commit -q -m "text + binary"
rm "$BIN/visible.txt"
git -C "$BIN" add -A
git -C "$BIN" commit -q -m "remove text"
BIN_JSON="$("$WEIR" -C "$BIN" --json grep TOKEN_BIN || true)"
BIN_PAT="$(printf '%s' "$BIN_JSON" | jget 'print("-".join(e["status"] for e in r["eras"]))')"
BIN_NOW="$(printf '%s' "$BIN_JSON" | jget 'print(r["holds_now"])')"
assert_eq "binary era pattern" "$BIN_PAT" "TRUE-EMPTY"
assert_eq "binary now EMPTY" "$BIN_NOW" "EMPTY"
rm -rf "$BIN"

echo
echo "== shallow clone is SHALLOW, not birth / never-held =="
SHALLOW="$(mktemp -d "${TMPDIR:-/tmp}/weir-shallow.XXXXXX")"
git clone -q --depth 1 "file://$FIX" "$SHALLOW"
SHA_JSON="$("$WEIR" -C "$SHALLOW" --json exists stay.txt || true)"
SHA_NOW="$(printf '%s' "$SHA_JSON" | jget 'print(r["holds_now"])')"
set +e
"$WEIR" -C "$SHALLOW" -q exists stay.txt
SHA_RC=$?
MISS_JSON="$("$WEIR" -C "$SHALLOW" --json exists oscillate.txt 2>/dev/null)"
MISS_RC=$?
set -e
MISS_NOW="$(printf '%s' "$MISS_JSON" | jget 'print(r["holds_now"])')"
assert_eq "shallow exists stay.txt" "$SHA_NOW" "SHALLOW"
assert_eq "shallow TRUE-graft exit 3" "$SHA_RC" "3"
assert_eq "shallow missing file is SHALLOW" "$MISS_NOW" "SHALLOW"
assert_eq "shallow missing exit 3" "$MISS_RC" "3"
LIM_JSON="$("$WEIR" -C "$FIX" --limit 1 --json exists stay.txt || true)"
LIM_NOW="$(printf '%s' "$LIM_JSON" | jget 'print(r["holds_now"])')"
assert_eq "--limit 1 of always-file is SHALLOW" "$LIM_NOW" "SHALLOW"
rm -rf "$SHALLOW"

echo
echo "== real repo: kizu CLAUDE.md — recursive join at 21ae074, not birth at 0ea3916 =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  KZ_ALL="$("$WEIR" -C "$KIZU" --json exists CLAUDE.md || true)"
  KZ_INTRO="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["start"]["short"] for e in r["eras"] if e["kind"]=="weir" and not e["recursive"]), ""))')"
  KZ_REC="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["start"]["short"] for e in r["eras"] if e["kind"]=="weir" and e["recursive"]), ""))')"
  KZ_REC_SRC="$(printf '%s' "$KZ_ALL" | jget 'print(next((p["source"] for e in r["eras"] if e["start"]["short"].startswith("21ae074") for p in e["parents"] if p["short"].startswith("0ea3916")), ""))')"
  KZ_REC_ST="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["status"] for e in r["eras"] if e["start"]["short"].startswith("21ae074")), ""))')"
  KZ_REC_TREE="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["tree"] for e in r["eras"] if e["start"]["short"].startswith("21ae074")), ""))')"
  KZ_REC_REASON="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["ford_reason"] for e in r["eras"] if e["start"]["short"].startswith("21ae074")), ""))')"
  KZ_TRUE_START="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["start"]["short"] for e in r["eras"] if e["status"]=="TRUE"), ""))')"
  KZ_ORIGIN="$(printf '%s' "$KZ_ALL" | jget 'print(next(((e.get("origin") or {}).get("short") or "") for e in r["eras"] if e["kind"]=="weir"), "")')"
  KZ_EQ="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["join"] or "" for e in r["eras"] if e["kind"]=="weir"), ""))')"
  KZ_REFUSE="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["refused_birth"] for e in r["eras"] if e["start"]["short"].startswith("0ea3916")), False))')"
  assert "kizu introducing weir is 0ea3916 (not a birth)" grep -q "0ea3916" <<<"$KZ_INTRO"
  assert "kizu first recursive weir is 21ae074 (merge-of-merges)" grep -q "21ae074" <<<"$KZ_REC"
  assert_eq "kizu 21ae074 occupancy is FALSE" "$KZ_REC_ST" "FALSE"
  assert_eq "kizu 21ae074 tree is TRUE" "$KZ_REC_TREE" "TRUE"
  assert_eq "kizu 21ae074 reason is recursive" "$KZ_REC_REASON" "recursive"
  assert_eq "kizu 0ea3916 contributes occupancy not tree" "$KZ_REC_SRC" "occupancy"
  assert "kizu TRUE does not start at 0ea3916" python3 -c 'import sys; sys.exit(0 if "0ea3916" not in sys.argv[1] else 1)' "$KZ_TRUE_START"
  assert "kizu TRUE does not start at 21ae074 (ford's preserve lie)" python3 -c 'import sys; sys.exit(0 if "21ae074" not in sys.argv[1] else 1)' "$KZ_TRUE_START"
  assert "kizu origin is e1098c8" grep -q "e1098c8" <<<"$KZ_ORIGIN"
  KZ_TRUE_KIND="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["kind"] for e in r["eras"] if e["status"]=="TRUE"), ""))')"
  KZ_TRUE_ORIGIN="$(printf '%s' "$KZ_ALL" | jget 'print(next(((e.get("origin") or {}).get("short") or "") for e in r["eras"] if e["status"]=="TRUE"), "")')"
  KZ_TRUE_FROM="$(printf '%s' "$KZ_ALL" | jget 'print(next(((e.get("continued_from") or {}).get("short") or "") for e in r["eras"] if e["status"]=="TRUE"), "")')"
  KZ_INH_N="$(printf '%s' "$KZ_ALL" | jget 'print(next((e["count"] for e in r["eras"] if e["kind"]=="inherited"), 0))')"
  KZ_INH_FROM="$(printf '%s' "$KZ_ALL" | jget 'print(next(((e.get("continued_from") or {}).get("short") or "") for e in r["eras"] if e["kind"]=="inherited"), "")')"
  KZ_ERAS="$(printf '%s' "$KZ_ALL" | jget 'print(len(r["eras"]))')"
  assert_eq "kizu TRUE after weir is continue, not birth" "$KZ_TRUE_KIND" "continue"
  assert "kizu TRUE origin is still e1098c8" grep -q "e1098c8" <<<"$KZ_TRUE_ORIGIN"
  assert "kizu TRUE continued_from is 21ae074 (the merge-of-merges)" grep -q "21ae074" <<<"$KZ_TRUE_FROM"
  assert_eq "kizu inherited cascade is 4 commits" "$KZ_INH_N" "4"
  assert "kizu inherited from 21ae074" grep -q "21ae074" <<<"$KZ_INH_FROM"
  assert_eq "kizu eras after inherited compress" "$KZ_ERAS" "5"
  assert_eq "kizu 0ea3916 refuses birth" "$KZ_REFUSE" "True"
  assert "kizu --all equation is a meet" grep -q "FALSE" <<<"$KZ_EQ"

  KZ_ANY="$("$WEIR" -C "$KIZU" --any --json exists CLAUDE.md || true)"
  KZ_ANY_KIND="$(printf '%s' "$KZ_ANY" | jget 'print(next((e["kind"] for e in r["eras"] if "0ea3916" in e["start"]["short"]), ""))')"
  KZ_ANY_ST="$(printf '%s' "$KZ_ANY" | jget 'print(next((e["status"] for e in r["eras"] if "0ea3916" in e["start"]["short"]), ""))')"
  assert_eq "kizu --any still a weir at the introducing merge" "$KZ_ANY_KIND" "weir"
  assert_eq "kizu --any merge is TRUE (introduced via e1098c8)" "$KZ_ANY_ST" "TRUE"

  KZ_BOOL="$("$WEIR" -C "$KIZU" --boolean --json exists CLAUDE.md || true)"
  KZ_BOOL_START="$(printf '%s' "$KZ_BOOL" | jget 'print(next(e["start"]["short"] for e in r["eras"] if e["status"]=="TRUE"))')"
  KZ_BOOL_LIE="$(printf '%s' "$KZ_BOOL" | jget 'print(r["boolean_lie"])')"
  assert "kizu --boolean recovers held birth at 0ea3916" grep -q "0ea3916" <<<"$KZ_BOOL_START"
  assert_eq "kizu --boolean is a labelled lie" "$KZ_BOOL_LIE" "True"

  echo "---- kizu first-parent --all (join, not birth) ----"
  "$WEIR" -C "$KIZU" --human --color never exists CLAUDE.md || true

  KIZU_SH="$(mktemp -d "${TMPDIR:-/tmp}/weir-kizu-shallow.XXXXXX")"
  git clone -q --depth 1 "file://$KIZU" "$KIZU_SH"
  KZS="$("$WEIR" -C "$KIZU_SH" --json exists CLAUDE.md || true)"
  KZS_NOW="$(printf '%s' "$KZS" | jget 'print(r["holds_now"])')"
  assert_eq "kizu depth-1 is SHALLOW not birth" "$KZS_NOW" "SHALLOW"
  rm -rf "$KIZU_SH"
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: sitbone FocusRiverView =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  LOG_N="$(git -C "$SITBONE" log --oneline -- Sources/SitboneUI/FocusRiverView.swift | grep -c . || true)"
  assert_eq "git log -- deleted-path is empty" "$LOG_N" "0"
  SB_JSON="$("$WEIR" -C "$SITBONE" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  SB_HINT="$(printf '%s' "$SB_JSON" | jget 'print(" ".join(r.get("hints") or []))')"
  SB_NEVER="$(printf '%s' "$SB_JSON" | jget 'print(int(r["never_held"]))')"
  assert_eq "sitbone first-parent never_held" "$SB_NEVER" "1"
  assert "sitbone first-parent hints --full" grep -q -- "--full" <<<"$SB_HINT"
  SB_FULL="$("$WEIR" -C "$SITBONE" --full --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  SB_TRUE="$(printf '%s' "$SB_FULL" | jget 'print(r["true_commits"])')"
  python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>=11 else 1)' "$SB_TRUE"
  assert "sitbone --full finds the 11-commit island ($SB_TRUE)" true
  SB_SH="$(mktemp -d "${TMPDIR:-/tmp}/weir-sitbone-shallow.XXXXXX")"
  git clone -q --depth 1 "file://$SITBONE" "$SB_SH"
  SBS="$("$WEIR" -C "$SB_SH" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  SBS_NOW="$(printf '%s' "$SBS" | jget 'print(r["holds_now"])')"
  assert_eq "sitbone depth-1 missing file is SHALLOW not never-held" "$SBS_NOW" "SHALLOW"
  rm -rf "$SB_SH"
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: skills preact-zero-mock =="
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  PZ_JSON="$("$WEIR" -C "$SKILLS" --json grep preact-zero-mock || true)"
  PZ_NOW="$(printf '%s' "$PZ_JSON" | jget 'print(r["holds_now"])')"
  PZ_WIT="$(printf '%s' "$PZ_JSON" | jget 'print(",".join(r["eras"][-1].get("witnesses_end") or r["eras"][-1].get("witnesses_start") or []))')"
  EX_JSON="$("$WEIR" -C "$SKILLS" --json exists preact-zero-mock/SKILL.md || true)"
  EX_NOW="$(printf '%s' "$EX_JSON" | jget 'print(r["holds_now"])')"
  assert_eq "grep preact-zero-mock still TRUE at HEAD" "$PZ_NOW" "TRUE"
  assert "README is the remaining witness" grep -q "README.md" <<<"$PZ_WIT"
  assert_eq "exists SKILL.md is FALSE (definition gone)" "$EX_NOW" "FALSE"
else
  echo "skip skills (not present)"
fi

rm -rf "$FIX" "$DIA"

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
