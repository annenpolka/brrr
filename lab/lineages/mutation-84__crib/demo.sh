#!/usr/bin/env bash
# Exercise crib: occupancy of a new holder of this blob.
# git mv is FOLLOW (never cribbed). cp is COPY (dest is the extra holder).
# ./demo.sh 0  — fixture + sitbone + kizu (skip slower extras)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CRIB="$ROOT/crib"
chmod +x "$CRIB"
CHEAP=0
if [[ "${1:-}" == "0" ]]; then
  CHEAP=1
fi

if [[ ! -x "$CRIB" ]]; then
  echo "demo: crib is not executable" >&2
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

echo "== fixture: cp vs git mv, remaining blob, dest death, extract-and-edit =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/crib-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "crib-demo"
git -C "$FIX" config user.email "crib@example.test"

mkdir -p "$FIX/nested/deep"
printf 'alpha\nbeta\ngamma\n' > "$FIX/a.rs"
printf 'ghost\n' > "$FIX/old name.txt"
printf 'keep\n' > "$FIX/keep.txt"
printf 'hello\n' > "$FIX/nested/deep/weird (1).txt"
git -C "$FIX" add a.rs "old name.txt" keep.txt "nested/deep/weird (1).txt"
git -C "$FIX" commit -q -m "t0: birth"

# t1: exact cp — both names exist
cp "$FIX/a.rs" "$FIX/b.rs"
git -C "$FIX" add b.rs
git -C "$FIX" commit -q -m "t1: cp a.rs b.rs"

# t2: git mv is FOLLOW, not COPY
git -C "$FIX" mv "old name.txt" "new name.txt"
git -C "$FIX" commit -q -m "t3: rename with spaces"

# t3: dest of the copy dies
rm "$FIX/b.rs"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t3: dest b.rs dies"

# t4: Japanese dest copy of keep.txt
printf 'keep\n' > "$FIX/計画.md"
git -C "$FIX" add "計画.md"
git -C "$FIX" commit -q -m "t4: copy keep.txt to 計画.md"

# t5: nested git must not become the repo
mkdir -p "$FIX/vendor/nested"
git -C "$FIX/vendor/nested" init -q -b inner
git -C "$FIX/vendor/nested" config user.name "crib-demo"
git -C "$FIX/vendor/nested" config user.email "crib@example.test"
echo inner > "$FIX/vendor/nested/inner.txt"
git -C "$FIX/vendor/nested" add inner.txt
git -C "$FIX/vendor/nested" commit -q -m "inner commit"
echo 'vendor-marker' > "$FIX/vendor/marker.txt"
git -C "$FIX" add vendor/marker.txt
git -C "$FIX" commit -q -m "t5: nested git + marker"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "6"

echo "-- exists a.rs / copy a.rs: dest b.rs is the extra holder, then dest dies"
A_JSON="$("$CRIB" -C "$FIX" --json exists a.rs || true)"
A_PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$A_JSON")"
A_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$A_JSON")"
A_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$A_JSON")"
A_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$A_JSON")"
assert_eq "a.rs era pattern (birth of dest, then dest death)" "$A_PAT" "FTF"
assert_eq "a.rs now=0 true=2 (dest lives t1-t2, dies t3)" "$A_NOW" "0 2"
assert_eq "a.rs identity is copy not follow" "$A_ID" "a.rs → b.rs"
assert_eq "a.rs holder is dest b.rs" "$A_HOLD" "b.rs"

COPY_JSON="$("$CRIB" -C "$FIX" --json copy a.rs || true)"
COPY_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$COPY_JSON")"
assert_eq "copy a.rs is the same observer as exists a.rs" "$COPY_ID" "$A_ID"

echo "-- exists b.rs: dest query occupies the same crib"
B_JSON="$("$CRIB" -C "$FIX" --json exists b.rs || true)"
B_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$B_JSON")"
B_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$B_JSON")"
assert_eq "b.rs identity matches source query" "$B_ID" "a.rs → b.rs"
assert_eq "b.rs dest died after 2 commits" "$B_NOW" "0 2"

echo "-- git mv is FOLLOW, never a crib"
OLD_JSON="$("$CRIB" -C "$FIX" --json exists "old name.txt" || true)"
NEW_JSON="$("$CRIB" -C "$FIX" --json exists "new name.txt" || true)"
OLD_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], int(r["never_held"]))' <<<"$OLD_JSON")"
NEW_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], int(r["never_held"]))' <<<"$NEW_JSON")"
OLD_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$OLD_JSON")"
NEW_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$NEW_JSON")"
assert_eq "old name never cribbed" "$OLD_NOW" "0 0 1"
assert_eq "new name never cribbed" "$NEW_NOW" "0 0 1"
assert "old name hint names follow" grep -q "follow" <<<"$OLD_HINT"
assert "new name hint names follow" grep -q "follow" <<<"$NEW_HINT"
assert "follow hint points at berth" grep -q "berth --follow" <<<"$OLD_HINT"
assert "follow hint is not a copy identity" python3 -c 'import json,sys; r=json.loads(sys.argv[1]); sys.exit(0 if not r.get("identity") else 1)' "$OLD_JSON"

echo "-- Japanese dest copy of keep.txt"
KEEP_JSON="$("$CRIB" -C "$FIX" --json exists keep.txt || true)"
KEEP_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KEEP_JSON")"
KEEP_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$KEEP_JSON")"
assert_eq "keep.txt → 計画.md copy identity" "$KEEP_ID" "keep.txt → 計画.md"
assert_eq "keep.txt extra holder still lives" "$KEEP_NOW" "1 2"

echo "-- --follow is rejected (that is berth's verb)"
set +e
"$CRIB" -C "$FIX" --follow exists a.rs >/dev/null 2>&1
FOLLOW_RC=$?
set -e
assert_eq "--follow exit 2" "$FOLLOW_RC" "2"

echo "-- exit codes / --revs / empty repo"
set +e
"$CRIB" -C "$FIX" -q exists keep.txt
KEEP_RC=$?
"$CRIB" -C "$FIX" -q exists "old name.txt"
OLD_RC=$?
set -e
assert_eq "copy dest still held exit 0" "$KEEP_RC" "0"
assert_eq "follow dest exit 1" "$OLD_RC" "1"
REVS_N="$("$CRIB" -C "$FIX" --revs exists keep.txt | grep -c .)"
assert_eq "keep.txt true revs == 2 dest-alive commits" "$REVS_N" "2"

EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/crib-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$CRIB" -C "$EMPTY" exists README.md 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -q "empty" <<<"$EMPTY_ERR"

echo "-- remaining blob: exclusive same-SHA is COPY of the living holder, not FOLLOW of twin"
REMF="$(mktemp -d "${TMPDIR:-/tmp}/crib-remain.XXXXXX")"
git -C "$REMF" init -q -b main
git -C "$REMF" config user.name "crib-demo"
git -C "$REMF" config user.email "crib@example.test"
printf 'same\n' > "$REMF/a.rs"
printf 'same\n' > "$REMF/twin.rs"
git -C "$REMF" add a.rs twin.rs
git -C "$REMF" commit -q -m t0
rm "$REMF/twin.rs"
cp "$REMF/a.rs" "$REMF/b.rs"
git -C "$REMF" add -A
git -C "$REMF" commit -q -m "twin dies, a.rs copied to b.rs"
RJ="$("$CRIB" -C "$REMF" --json exists a.rs || true)"
TJ="$("$CRIB" -C "$REMF" --json exists twin.rs || true)"
BJ="$("$CRIB" -C "$REMF" --json exists b.rs || true)"
assert_eq "remaining a.rs identity" "$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$RJ")" "a.rs → b.rs"
assert_eq "remaining a.rs now" "$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$RJ")" "1 1"
assert_eq "twin is not a crib source" "$(json_get 'print(int(r["never_held"]))' <<<"$TJ")" "1"
assert_eq "b.rs is dest of a.rs" "$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$BJ")" "a.rs → b.rs"
assert "twin hint is not follow twin → b.rs" python3 -c 'import json,sys; r=json.loads(sys.argv[1]); h=" ".join(r.get("hints") or []); sys.exit(0 if "twin.rs → b.rs" not in h and "follow" not in h else 1)' "$TJ"
rm -rf "$REMF"

echo "-- extract-and-edit: dest-on-B vs source-on-A (B-vs-B would miss)"
SIM="$(mktemp -d "${TMPDIR:-/tmp}/crib-sim.XXXXXX")"
git -C "$SIM" init -q -b main
git -C "$SIM" config user.name "crib-demo"
git -C "$SIM" config user.email "crib@example.test"
python3 - "$SIM" <<'PY'
import sys
root = sys.argv[1]
lines = ["fn keep() {}"] + [f"fn install_{i}() {{ {i} }}" for i in range(20)] + ["fn leftover() {}"]
open(f"{root}/god.rs", "w").write("\n".join(lines) + "\n")
PY
git -C "$SIM" add god.rs
git -C "$SIM" commit -q -m t0
python3 - "$SIM" <<'PY'
import sys
root = sys.argv[1]
lines = open(f"{root}/god.rs").read().splitlines()
open(f"{root}/install.rs", "w").write("\n".join(ln for ln in lines if "install_" in ln) + "\n")
open(f"{root}/god.rs", "w").write("\n".join(ln for ln in lines if "install_" not in ln) + "\n")
PY
git -C "$SIM" add god.rs install.rs
git -C "$SIM" commit -q -m extract
SJ="$("$CRIB" -C "$SIM" --json exists god.rs || true)"
assert_eq "extract identity" "$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$SJ")" "god.rs → install.rs"
assert_eq "extract now" "$(json_get 'print(int(r["holds_now"]))' <<<"$SJ")" "1"
SIMS="$(json_get 'print(round(r["copies"][0]["similarity"], 2))' <<<"$SJ")"
python3 -c 'import sys; sys.exit(0 if float(sys.argv[1]) >= 0.5 else 1)' "$SIMS"
assert "extract similarity >= 0.5 (got $SIMS)" true
rm -rf "$SIM"

echo "-- --now sees an uncommitted extra holder"
printf 'keep\n' > "$FIX/dirty-copy.txt"
NOW_JSON="$("$CRIB" -C "$FIX" --now --json exists keep.txt || true)"
NOW_HOLD="$(json_get 'print(int(r["holds_now"]), r["eras"][-1]["end"]["kind"])' <<<"$NOW_JSON")"
NOW_DESTS="$(json_get 'print(",".join(sorted(r["eras"][-1]["holders"])))' <<<"$NOW_JSON")"
assert_eq "uncommitted dest via --now" "$NOW_HOLD" "1 worktree"
assert_eq "--now holders include dirty dest and 計画.md" "$NOW_DESTS" "dirty-copy.txt,計画.md"
rm -f "$FIX/dirty-copy.txt"

echo
echo "== real repo: sitbone FocusRiverView is a unique birth, not a crib =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  SF_JSON="$("$CRIB" -C "$SITBONE" --full --json exists Sources/SitboneUI/FocusRiverView.swift || true)"
  SF_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], int(r["never_held"]))' <<<"$SF_JSON")"
  SF_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$SF_JSON")"
  assert_eq "sitbone FocusRiverView never cribbed" "$SF_NOW" "0 0 1"
  assert "sitbone hint is unique birth, not follow" grep -q "unique birth" <<<"$SF_HINT"
  assert "sitbone hint points at held exists" grep -q "held exists" <<<"$SF_HINT"
  echo "---- sitbone --full exists FocusRiverView (human) ----"
  "$CRIB" -C "$SITBONE" --full --color never exists Sources/SitboneUI/FocusRiverView.swift || true
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: kizu C056 copy vs R100 follow =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  echo "-- first-parent: dest born at merge, origin-behind names 5671a72 (not Jaccard 0.195)"
  KF_JSON="$("$CRIB" -C "$KIZU" --json exists src/init.rs || true)"
  KI_JSON="$("$CRIB" -C "$KIZU" --json exists src/init/install.rs || true)"
  KF_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], int(r["never_held"]))' <<<"$KF_JSON")"
  KI_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$KI_JSON")"
  KF_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KF_JSON")"
  KF_ORIGIN="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print((trues[0].get("origin") or {}).get("short",""))' <<<"$KF_JSON")"
  KF_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$KF_JSON")"
  assert_eq "kizu first-parent init.rs now/true=5" "$KF_NOW" "1 5 0"
  assert_eq "kizu first-parent dest matches source occupancy" "$KI_NOW" "1 5"
  assert_eq "kizu first-parent identity is the C056 copy" "$KF_ID" "src/init.rs → src/init/install.rs"
  assert_eq "kizu first-parent origin is off-mainline copy 5671a72" "$KF_ORIGIN" "5671a72"
  assert_eq "kizu first-parent holder is install.rs" "$KF_HOLD" "src/init/install.rs"

  echo "-- --full: dest-on-B vs source-on-A at 5671a72 is C056"
  KU_JSON="$("$CRIB" -C "$KIZU" --full --json exists src/init.rs || true)"
  KD_JSON="$("$CRIB" -C "$KIZU" --full --json exists src/init/install.rs || true)"
  KU_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KU_JSON")"
  KD_ID="$(json_get 'print(" → ".join(r.get("identity") or []))' <<<"$KD_JSON")"
  KU_N="$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$KU_JSON")"
  KD_N="$(json_get 'print(int(r["holds_now"]), r["true_commits"])' <<<"$KD_JSON")"
  KU_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$KU_JSON")"
  assert_eq "kizu --full source identity" "$KU_ID" "src/init.rs → src/init/install.rs"
  assert_eq "kizu --full dest identity" "$KD_ID" "$KU_ID"
  assert_eq "kizu --full source now/true=12" "$KU_N" "1 12"
  assert_eq "kizu --full dest matches source" "$KD_N" "$KU_N"
  assert_eq "kizu --full holder is install.rs" "$KU_HOLD" "src/init/install.rs"

  echo "-- --full R100 dest is FOLLOW, not COPY"
  KR_JSON="$("$CRIB" -C "$KIZU" --full --json exists docs/deep-research-ai-agent-hooks.md || true)"
  KO_JSON="$("$CRIB" -C "$KIZU" --full --json exists deep-research-ai-agent-hooks.md || true)"
  KR_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], int(r["never_held"]))' <<<"$KR_JSON")"
  KO_NOW="$(json_get 'print(int(r["holds_now"]), r["true_commits"], int(r["never_held"]))' <<<"$KO_JSON")"
  KR_HINT="$(json_get 'print(" ".join(r.get("hints") or []))' <<<"$KR_JSON")"
  assert_eq "kizu R100 dest never cribbed" "$KR_NOW" "0 0 1"
  assert_eq "kizu R100 old name never cribbed" "$KO_NOW" "0 0 1"
  assert "R100 hint is follow into docs/" grep -q "follow" <<<"$KR_HINT"
  assert "R100 hint is not a copy identity" python3 -c 'import json,sys; r=json.loads(sys.argv[1]); sys.exit(0 if not r.get("identity") else 1)' "$KR_JSON"

  echo "---- kizu --full exists src/init.rs (human) ----"
  "$CRIB" -C "$KIZU" --full --color never exists src/init.rs || true
  echo "---- kizu first-parent exists src/init.rs (origin 5671a72) ----"
  "$CRIB" -C "$KIZU" --color never exists src/init.rs || true
  echo "---- kizu --full R100 dest (human) ----"
  "$CRIB" -C "$KIZU" --full --color never exists docs/deep-research-ai-agent-hooks.md || true
else
  echo "skip kizu (not present)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
