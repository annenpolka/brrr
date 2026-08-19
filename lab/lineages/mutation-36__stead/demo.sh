#!/usr/bin/env bash
# Exercise stead against DESTROYER occupancy holes and one real repo each.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
STEAD="$ROOT/stead"
chmod +x "$STEAD"

if [[ ! -x "$STEAD" ]]; then
  echo "demo: stead is not executable" >&2
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

echo "== fixture: oscillating path (held still has to work) =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/stead-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "stead-demo"
git -C "$FIX" config user.email "stead@example.test"

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
git -C "$FIX" commit -q -m "t2: revive oscillate, drop TOKEN_A"

git -C "$FIX" mv keep.txt "new name.txt" 2>/dev/null || true
# keep a stable always-file
printf 'stay\n' > "$FIX/stay.txt"
git -C "$FIX" add stay.txt
git -C "$FIX" commit -q -m "t3: stay"

rm "$FIX/oscillate.txt"
printf 'other\nTOKEN_A\n' > "$FIX/other.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t4: kill oscillate, TOKEN_A reincarnates"

printf 'keep\n' > "$FIX/other.txt"
git -C "$FIX" add other.txt
git -C "$FIX" commit -q -m "t5: TOKEN_A gone again"

OSC_JSON="$("$STEAD" -C "$FIX" --json exists oscillate.txt || true)"
OSC_PAT="$(printf '%s' "$OSC_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
OSC_NOW="$(printf '%s' "$OSC_JSON" | jget 'print(r["holds_now"])')"
assert_eq "oscillate era initials" "$OSC_PAT" "TFTF"
assert_eq "oscillate now" "$OSC_NOW" "FALSE"

TOK_JSON="$("$STEAD" -C "$FIX" --json grep TOKEN_A || true)"
TOK_PAT="$(printf '%s' "$TOK_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
assert_eq "TOKEN_A era initials" "$TOK_PAT" "TFTF"

"$STEAD" -C "$FIX" -q exists "計画.md"
assert "計画.md holds now" true

echo "-- exists glob chars are refused (cost class)"
set +e
GLOB_ERR="$("$STEAD" -C "$FIX" exists '*' 2>&1)"
GLOB_RC=$?
set -e
assert_eq "exists * exit" "$GLOB_RC" "2"
assert "exists * points at glob" grep -q "stead glob" <<<"$GLOB_ERR"

GLOB_JSON="$("$STEAD" -C "$FIX" --json glob '計画.md' || true)"
GLOB_NOW="$(printf '%s' "$GLOB_JSON" | jget 'print(r["holds_now"])')"
GLOB_COST="$(printf '%s' "$GLOB_JSON" | jget 'print(r["cost"])')"
assert_eq "glob 計画.md now" "$GLOB_NOW" "TRUE"
assert_eq "glob cost class" "$GLOB_COST" "per-tree"

echo
echo "== hole 1: --now on a commit-less dirty tree answers the filesystem =="
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/stead-empty.XXXXXX")"
EMPTY_DIRTY="$(mktemp -d "${TMPDIR:-/tmp}/stead-empty-dirty.XXXXXX")"
git -C "$EMPTY" init -q -b main
git -C "$EMPTY_DIRTY" init -q -b main
printf 'hello from disk\n' > "$EMPTY_DIRTY/README.md"

set +e
EMPTY_JSON="$("$STEAD" -C "$EMPTY" --json exists README.md 2>/dev/null)"
EMPTY_RC=$?
EMPTY_NOW_JSON="$("$STEAD" -C "$EMPTY" --now --json exists README.md 2>/dev/null)"
EMPTY_NOW_RC=$?
DIRTY_JSON="$("$STEAD" -C "$EMPTY_DIRTY" --now --json exists README.md 2>/dev/null)"
DIRTY_RC=$?
DIRTY_OFF="$("$STEAD" -C "$EMPTY_DIRTY" --json exists README.md 2>/dev/null)"
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
echo "== hole 2: timeout is UNKNOWN, not FALSE; --timeout 0 is refused =="
TO="$(mktemp -d "${TMPDIR:-/tmp}/stead-timeout.XXXXXX")"
git -C "$TO" init -q -b main
git -C "$TO" config user.name "stead-demo"
git -C "$TO" config user.email "stead@example.test"
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
TO_JSON="$("$STEAD" -C "$TO" --json --timeout 0.2 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi')"
TO_RC=$?
TO0_ERR="$("$STEAD" -C "$TO" --timeout 0 exec -- true 2>&1)"
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
rm -rf "$TO"

echo
echo "== hole 3: binary-only occupancy is EMPTY, not FALSE =="
BIN="$(mktemp -d "${TMPDIR:-/tmp}/stead-binary.XXXXXX")"
git -C "$BIN" init -q -b main
git -C "$BIN" config user.name "stead-demo"
git -C "$BIN" config user.email "stead@example.test"
printf 'TOKEN_BIN visible\n' > "$BIN/visible.txt"
printf 'TOKEN_BIN\0hidden\n' > "$BIN/secret.bin"
mkdir -p "$BIN/src"
printf 'TOKEN_BIN\0if x > 0\n' > "$BIN/src/evil.py"
git -C "$BIN" add visible.txt secret.bin src/evil.py
git -C "$BIN" commit -q -m "text + binary"
rm "$BIN/visible.txt"
git -C "$BIN" add -A
git -C "$BIN" commit -q -m "remove text TOKEN_BIN, binary still has it"

BIN_JSON="$("$STEAD" -C "$BIN" --json grep TOKEN_BIN || true)"
BIN_PAT="$(printf '%s' "$BIN_JSON" | jget 'print("-".join(e["status"] for e in r["eras"]))')"
BIN_NOW="$(printf '%s' "$BIN_JSON" | jget 'print(r["holds_now"])')"
BIN_EMPTY="$(printf '%s' "$BIN_JSON" | jget 'print(r["empty_commits"])')"
assert_eq "binary era pattern" "$BIN_PAT" "TRUE-EMPTY"
assert_eq "binary now" "$BIN_NOW" "EMPTY"
assert_eq "binary empty count" "$BIN_EMPTY" "1"
set +e
"$STEAD" -C "$BIN" -q grep TOKEN_BIN
BIN_RC=$?
set -e
assert_eq "binary-only exit 3" "$BIN_RC" "3"

# exists still sees the blob
"$STEAD" -C "$BIN" -q exists secret.bin
assert "exists secret.bin still TRUE" true
rm -rf "$BIN"

echo
echo "== hole 4: invalid regex is UNKNOWN, not never-held =="
set +e
RX_JSON="$("$STEAD" -C "$FIX" --json grep '[' 2>/dev/null)"
RX_RC=$?
set -e
RX_NOW="$(printf '%s' "$RX_JSON" | jget 'print(r["holds_now"])')"
RX_UNK="$(printf '%s' "$RX_JSON" | jget 'print(r["unknown_commits"])')"
RX_NEVER="$(printf '%s' "$RX_JSON" | jget 'print(int(r["never_held"]))')"
assert_eq "bad regex now" "$RX_NOW" "UNKNOWN"
assert "bad regex unknown>0" python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>0 else 1)' "$RX_UNK"
assert_eq "bad regex not never_held" "$RX_NEVER" "0"
assert_eq "bad regex exit 3" "$RX_RC" "3"

echo
echo "== hole 5: diamond --full is a lattice, not FTFT list order =="
DIA="$(mktemp -d "${TMPDIR:-/tmp}/stead-diamond.XXXXXX")"
git -C "$DIA" init -q -b main
git -C "$DIA" config user.name "stead-demo"
git -C "$DIA" config user.email "stead@example.test"
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
export_git_date "2022-01-03T00:00:00"
echo still >> "$DIA/src/app.py"
git -C "$DIA" add src/app.py
git -C "$DIA" commit -q -m "D still holds on topic"

git -C "$DIA" checkout -q main
export_git_date "2022-01-04T00:00:00"
echo mainline >> "$DIA/README"
git -C "$DIA" add README
git -C "$DIA" commit -q -m "B main no occupancy"

export_git_date "2022-01-05T00:00:00"
git -C "$DIA" merge -q --no-ff topic -m "M merge topic"

unset GIT_AUTHOR_DATE GIT_COMMITTER_DATE

LAT_JSON="$("$STEAD" -C "$DIA" --full --json exists src/app.py || true)"
LAT_PAT="$(printf '%s' "$LAT_JSON" | jget 'print("-".join(e["status"] for e in r["eras"]))')"
LAT_WALK="$(printf '%s' "$LAT_JSON" | jget 'print(r["walk"])')"
LAT_N="$(printf '%s' "$LAT_JSON" | jget 'print(len(r["eras"]))')"
LAT_TRUE="$(printf '%s' "$LAT_JSON" | jget 'print(r["true_commits"])')"
LIST_JSON="$("$STEAD" -C "$DIA" --full --list --json exists src/app.py || true)"
LIST_PAT="$(printf '%s' "$LIST_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
FP_JSON="$("$STEAD" -C "$DIA" --json exists src/app.py || true)"
FP_PAT="$(printf '%s' "$FP_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"

assert_eq "diamond lattice walk name" "$LAT_WALK" "lattice"
assert_eq "diamond lattice eras" "$LAT_N" "2"
assert_eq "diamond lattice pattern" "$LAT_PAT" "FALSE-TRUE"
assert_eq "diamond lattice true=3" "$LAT_TRUE" "3"
assert_eq "diamond --list is the FTFT lie" "$LIST_PAT" "FTFT"
assert_eq "diamond first-parent" "$FP_PAT" "FT"
rm -rf "$DIA"

echo
echo "== hole 6: shallow clone is SHALLOW, not birth / never-held =="
SHALLOW_SRC="$FIX"
SHALLOW="$(mktemp -d "${TMPDIR:-/tmp}/stead-shallow.XXXXXX")"
git clone -q --depth 1 "file://$SHALLOW_SRC" "$SHALLOW"
SHA_JSON="$("$STEAD" -C "$SHALLOW" --json exists stay.txt || true)"
SHA_NOW="$(printf '%s' "$SHA_JSON" | jget 'print(r["holds_now"])')"
SHA_N="$(printf '%s' "$SHA_JSON" | jget 'print(r["shallow_commits"])')"
set +e
"$STEAD" -C "$SHALLOW" -q exists stay.txt
SHA_RC=$?
MISS_JSON="$("$STEAD" -C "$SHALLOW" --json exists oscillate.txt 2>/dev/null)"
MISS_RC=$?
set -e
MISS_NOW="$(printf '%s' "$MISS_JSON" | jget 'print(r["holds_now"])')"
assert_eq "shallow exists stay.txt" "$SHA_NOW" "SHALLOW"
assert "shallow count>0" python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>0 else 1)' "$SHA_N"
assert_eq "shallow TRUE-graft exit 3" "$SHA_RC" "3"
assert_eq "shallow missing file is SHALLOW" "$MISS_NOW" "SHALLOW"
assert_eq "shallow missing exit 3" "$MISS_RC" "3"

# --limit is the same horizon
LIM_JSON="$("$STEAD" -C "$FIX" --limit 1 --json exists stay.txt || true)"
LIM_NOW="$(printf '%s' "$LIM_JSON" | jget 'print(r["holds_now"])')"
assert_eq "--limit 1 of always-file is SHALLOW" "$LIM_NOW" "SHALLOW"
rm -rf "$SHALLOW"

echo
echo "== --boolean recovers held on a TRUE/FALSE-only probe =="
BOOL_JSON="$("$STEAD" -C "$FIX" --boolean --json exists oscillate.txt || true)"
BOOL_PAT="$(printf '%s' "$BOOL_JSON" | jget 'print("".join(e["status"][0] for e in r["eras"]))')"
assert_eq "--boolean oscillate still TFTF" "$BOOL_PAT" "TFTF"
set +e
"$STEAD" -C "$FIX" --boolean -q exists stay.txt
BOOL_RC=$?
set -e
assert_eq "--boolean stay.txt exit 0" "$BOOL_RC" "0"

echo
echo "== TSV default rows compose =="
TSV="$("$STEAD" -C "$FIX" --tsv --no-header exists oscillate.txt || true)"
TSV_FIRST="$(printf '%s\n' "$TSV" | awk -F'\t' 'NR==1{print $1}')"
assert_eq "tsv first status" "$TSV_FIRST" "TRUE"

echo
echo "== real repo: kizu CLAUDE.md merge vs topic birth =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  KZ_JSON="$("$STEAD" -C "$KIZU" --json exists CLAUDE.md || true)"
  KZ_TRUE_START="$(printf '%s' "$KZ_JSON" | jget 'print(next(e["start"]["short"] for e in r["eras"] if e["status"]=="TRUE"))')"
  KZ_SCAN="$(printf '%s' "$KZ_JSON" | jget 'print(r["commits_scanned"], r["reachable"])')"
  python3 -c 'import sys; s,r=map(int,sys.argv[1].split()); sys.exit(0 if r>s else 1)' "$KZ_SCAN"
  assert "kizu reachable > first-parent ($KZ_SCAN)" true
  assert "kizu first-parent birth is the merge" grep -q "0ea3916" <<<"$KZ_TRUE_START"

  KZ_FULL="$("$STEAD" -C "$KIZU" --full --json exists CLAUDE.md || true)"
  KZ_FULL_START="$(printf '%s' "$KZ_FULL" | jget 'print(next(e["start"]["short"] for e in r["eras"] if e["status"]=="TRUE"))')"
  assert "kizu --full birth is e1098c8" grep -q "e1098c8" <<<"$KZ_FULL_START"
  echo "---- kizu first-parent ----"
  "$STEAD" -C "$KIZU" --human --color never exists CLAUDE.md || true
  echo "---- kizu --full lattice ----"
  "$STEAD" -C "$KIZU" --full --human --color never exists CLAUDE.md | head -20 || true

  KIZU_SH="$(mktemp -d "${TMPDIR:-/tmp}/stead-kizu-shallow.XXXXXX")"
  git clone -q --depth 1 "file://$KIZU" "$KIZU_SH"
  KZS="$("$STEAD" -C "$KIZU_SH" --json exists CLAUDE.md || true)"
  KZS_NOW="$(printf '%s' "$KZS" | jget 'print(r["holds_now"])')"
  assert_eq "kizu depth-1 is SHALLOW not birth" "$KZS_NOW" "SHALLOW"
  rm -rf "$KIZU_SH"
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: sitbone FocusRiverView (git log -- path is empty) =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  LOG_N="$(git -C "$SITBONE" log --oneline -- Sources/SitboneUI/FocusRiverView.swift | grep -c . || true)"
  assert_eq "git log -- deleted-path is empty" "$LOG_N" "0"

  SB_JSON="$("$STEAD" -C "$SITBONE" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  SB_HINT="$(printf '%s' "$SB_JSON" | jget 'print(" ".join(r.get("hints") or []))')"
  SB_NEVER="$(printf '%s' "$SB_JSON" | jget 'print(int(r["never_held"]))')"
  assert_eq "sitbone first-parent never_held" "$SB_NEVER" "1"
  assert "sitbone first-parent hints --full" grep -q -- "--full" <<<"$SB_HINT"

  SB_FULL="$("$STEAD" -C "$SITBONE" --full --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  SB_TRUE="$(printf '%s' "$SB_FULL" | jget 'print(r["true_commits"])')"
  python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>=11 else 1)' "$SB_TRUE"
  assert "sitbone --full finds the 11-commit island ($SB_TRUE)" true

  SB_SH="$(mktemp -d "${TMPDIR:-/tmp}/stead-sitbone-shallow.XXXXXX")"
  git clone -q --depth 1 "file://$SITBONE" "$SB_SH"
  SBS="$("$STEAD" -C "$SB_SH" --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  SBS_NOW="$(printf '%s' "$SBS" | jget 'print(r["holds_now"])')"
  assert_eq "sitbone depth-1 missing file is SHALLOW not never-held" "$SBS_NOW" "SHALLOW"
  rm -rf "$SB_SH"
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: skills preact-zero-mock (perch gold: README-only tenure) =="
SKILLS="/Users/annenpolka/ghq/github.com/annenpolka/skills"
if [[ -d "$SKILLS/.git" || -f "$SKILLS/.git" ]]; then
  PZ_JSON="$("$STEAD" -C "$SKILLS" --json grep preact-zero-mock || true)"
  PZ_NOW="$(printf '%s' "$PZ_JSON" | jget 'print(r["holds_now"])')"
  PZ_WIT="$(printf '%s' "$PZ_JSON" | jget 'print(",".join(r["eras"][-1].get("witnesses_end") or r["eras"][-1].get("witnesses_start") or []))')"
  EX_JSON="$("$STEAD" -C "$SKILLS" --json exists preact-zero-mock/SKILL.md || true)"
  EX_NOW="$(printf '%s' "$EX_JSON" | jget 'print(r["holds_now"])')"
  assert_eq "grep preact-zero-mock still TRUE at HEAD" "$PZ_NOW" "TRUE"
  assert "README is the remaining witness" grep -q "README.md" <<<"$PZ_WIT"
  assert_eq "exists SKILL.md is FALSE (definition gone)" "$EX_NOW" "FALSE"
  echo "---- skills grep preact-zero-mock (boolean occupancy; README still holds) ----"
  "$STEAD" -C "$SKILLS" --human --color never grep preact-zero-mock || true
else
  echo "skip skills (not present)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
