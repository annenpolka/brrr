#!/usr/bin/env bash
# Exercise tell against a synthetic ugly fixture and the dogfood repositories.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TELL="$ROOT/tell"
chmod +x "$TELL"

if [[ ! -x "$TELL" ]]; then
  echo "demo: tell is not executable" >&2
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
FIX="$(mktemp -d "${TMPDIR:-/tmp}/tell-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "tell-demo"
git -C "$FIX" config user.email "tell@example.test"

mkdir -p "$FIX/nested/deep"
printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'born\n' > "$FIX/oscillate.txt"
printf 'ghost\n' > "$FIX/old name.txt"
printf 'hello\n' > "$FIX/nested/deep/weird (1).txt"
git -C "$FIX" add keep.txt oscillate.txt "old name.txt" "nested/deep/weird (1).txt"
git -C "$FIX" commit -q -m "t0: birth"
T0="$(git -C "$FIX" rev-parse HEAD)"

rm "$FIX/oscillate.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t1: kill oscillate"
T1="$(git -C "$FIX" rev-parse HEAD)"

printf 'reborn\n' > "$FIX/oscillate.txt"
printf 'keep\n' > "$FIX/keep.txt"
printf '計画\n' > "$FIX/計画.md"
git -C "$FIX" add oscillate.txt keep.txt "計画.md"
git -C "$FIX" commit -q -m "t2: revive oscillate, drop TOKEN_A"
T2="$(git -C "$FIX" rev-parse HEAD)"

git -C "$FIX" mv "old name.txt" "new name.txt"
git -C "$FIX" commit -q -m "t3: rename with spaces"
T3="$(git -C "$FIX" rev-parse HEAD)"

rm "$FIX/oscillate.txt"
printf 'other\nTOKEN_A\n' > "$FIX/other.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t4: kill oscillate, TOKEN_A reincarnates"
T4="$(git -C "$FIX" rev-parse HEAD)"

mkdir -p "$FIX/vendor/nested"
git -C "$FIX/vendor/nested" init -q -b inner
git -C "$FIX/vendor/nested" config user.name "tell-demo"
git -C "$FIX/vendor/nested" config user.email "tell@example.test"
echo inner > "$FIX/vendor/nested/inner.txt"
git -C "$FIX/vendor/nested" add inner.txt
git -C "$FIX/vendor/nested" commit -q -m "inner commit"
echo 'vendor-marker' > "$FIX/vendor/marker.txt"
git -C "$FIX" add vendor/marker.txt
git -C "$FIX" commit -q -m "t5: nested git + marker"
T5="$(git -C "$FIX" rev-parse HEAD)"

printf 'keep\n' > "$FIX/other.txt"
git -C "$FIX" add other.txt
git -C "$FIX" commit -q -m "t6: TOKEN_A gone again"
T6="$(git -C "$FIX" rev-parse HEAD)"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "7"

echo "-- t0 vs t1: oscillate.txt dies, TOKEN_A still shared"
T01="$("$TELL" -C "$FIX" --json --color never "$T0" "$T1")"
python3 - "$T01" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["predicates"]
held = [p["held"] for p in preds]
cover = [p["held"] for p in r["cover"]]
assert any("oscillate" in h for h in held + cover), held
# TOKEN_A lives on both sides — must NOT distinguish
assert not any("TOKEN_A" in p["pattern"] for p in preds), preds
# only-A occupancy
assert any(p["true_on"]=="A" and p["kind"]=="exists" and "oscillate" in p["pattern"] for p in preds)
print("t01-ok")
PY
assert "t0 vs t1 oscillate exists on A only, TOKEN_A silent" true

echo "-- t1 vs t2: TOKEN_A dies, 計画.md born, oscillate revives"
T12="$("$TELL" -C "$FIX" --json --color never "$T1" "$T2")"
python3 - "$T12" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["predicates"]
held = [p["held"] for p in preds]
# TOKEN_A true on A (t1). Shortest well-formed may be TOKEN or TOKEN_A.
assert any(p["true_on"]=="A" and ("TOKEN_A" in p["pattern"] or p["pattern"]=="TOKEN") for p in preds), held
# Japanese path true on B — shortest exists may collapse to *.md
assert any(p["true_on"]=="B" and ("計画" in p["held"] or (p["kind"]=="exists" and ".md" in p["pattern"])) for p in preds), held
# oscillate true on B
assert any(p["true_on"]=="B" and "oscillate" in p["pattern"] for p in preds), held
print("t12-ok")
PY
assert "t1 vs t2 TOKEN_A / 計画.md / oscillate" true

echo "-- t2 vs t3: rename with spaces is exists, not grep of ghost"
T23="$("$TELL" -C "$FIX" --json --color never "$T2" "$T3")"
python3 - "$T23" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["predicates"]]
assert any("old name" in h for h in held), held
assert any("new name" in h for h in held), held
# content 'ghost' lives on both sides under different paths — grep should not claim it
assert not any(p["kind"]=="grep" and p["pattern"]=="ghost" for p in r["predicates"]), held
print("t23-ok")
PY
assert "rename is exists on both sides, shared blob is not grep" true

echo "-- t4 vs t6: TOKEN_A reincarnation then death"
T46="$("$TELL" -C "$FIX" --json --color never "$T4" "$T6")"
python3 - "$T46" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "TOKEN_A" in p["pattern"] for p in r["predicates"])
print("t46-ok")
PY
assert "t4 vs t6 TOKEN_A on A only" true

echo "-- --held / --oneline / --cover / exit codes"
HELD_OUT="$("$TELL" -C "$FIX" --held "$T0" "$T2" | head -5)"
assert "held-language lines look like exists/grep" grep -Eq '^(exists|grep) ' <<<"$HELD_OUT"

set +e
"$TELL" -C "$FIX" -q "$T0" "$T0"
ID_RC=$?
"$TELL" -C "$FIX" -q "$T0" "$T1"
DIFF_RC=$?
set -e
assert_eq "identical trees exit" "$ID_RC" "1"
assert_eq "different trees exit" "$DIFF_RC" "0"

echo "-- --now / worktree resurrection"
printf 'dirty\n' > "$FIX/oscillate.txt"
WT="$("$TELL" -C "$FIX" --json HEAD :worktree || true)"
python3 - "$WT" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert r["b"]["kind"]=="worktree"
assert any(p["true_on"]=="B" and "oscillate" in p["pattern"] for p in r["predicates"]), [p["held"] for p in r["predicates"]]
print("wt-ok")
PY
assert "HEAD vs :worktree sees uncommitted oscillate" true
rm -f "$FIX/oscillate.txt"

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/tell-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$TELL" -C "$EMPTY" HEAD HEAD~1 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -qi "empty\|needed a single revision\|cannot resolve" <<<"$EMPTY_ERR"

echo
echo "== real repo: sitbone FocusRiverView island =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- birth 14b1d6e^ vs 14b1d6e (file appears)"
  SBIRTH="$("$TELL" -C "$SITBONE" --json --color never 14b1d6e^ 14b1d6e)"
  python3 - "$SBIRTH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["predicates"]]
assert any("FocusRiverView" in h for h in held), held
assert any(p["true_on"]=="B" and "FocusRiverView" in p["held"] for p in r["predicates"])
print("sitbone-birth-ok")
PY
  assert "sitbone birth names FocusRiverView on B" true

  echo "-- death 70ec7df^ vs 70ec7df (file disappears)"
  SDEATH="$("$TELL" -C "$SITBONE" --json --color never 70ec7df^ 70ec7df)"
  python3 - "$SDEATH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["predicates"]), [p["held"] for p in r["predicates"]]
print("sitbone-death-ok")
PY
  assert "sitbone death names FocusRiverView on A" true

  echo "-- island 14b1d6e vs HEAD (git log -- path is empty)"
  SHEAD="$("$TELL" -C "$SITBONE" --json --color never --limit 6 14b1d6e HEAD)"
  python3 - "$SHEAD" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["predicates"]), [p["held"] for p in r["predicates"]]
print("sitbone-island-ok")
PY
  assert "island vs HEAD still finds FocusRiverView on the island" true

  echo "---- sitbone birth (human) ----"
  "$TELL" -C "$SITBONE" --color never --limit 4 14b1d6e^ 14b1d6e | head -40
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: voidtrace finite breakpoint =="
VOID="/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
if [[ -d "$VOID/.git" || -f "$VOID/.git" ]]; then
  VB="$("$TELL" -C "$VOID" --json --color never --limit 8 66d6fa1 6e3368b)"
  python3 - "$VB" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = " ".join(p["held"] for p in r["predicates"])
# slice commit already says "breakpoint"; distinguishing should still mention the feature
assert "breakpoint" in held.lower() or "finite-breakpoint" in held.lower(), held
assert any(p["true_on"]=="B" for p in r["predicates"])
print("voidtrace-ok")
PY
  assert "voidtrace 66d6fa1 vs 6e3368b mentions breakpoint on B" true
  echo "---- voidtrace finite-breakpoint (human cover) ----"
  "$TELL" -C "$VOID" --color never --cover --limit 5 66d6fa1 6e3368b | head -40
else
  echo "skip voidtrace (not present)"
fi

echo
echo "== real repo: kizu CLAUDE.md birth + jsx =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  K1="$("$TELL" -C "$KIZU" --json --color never e1098c8^ e1098c8)"
  python3 - "$K1" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["predicates"]]
assert any("CLAUDE.md" in h for h in held), held
print("kizu-claude-ok")
PY
  assert "kizu CLAUDE.md birth is an exists/grep on B" true

  K2="$("$TELL" -C "$KIZU" --json --color never --limit 8 04adde1^ 04adde1)"
  python3 - "$K2" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = " ".join(p["held"] for p in r["predicates"])
assert "jsx" in held.lower() or "tsx" in held.lower() or "js_ts" in held, held
print("kizu-jsx-ok")
PY
  assert "kizu jsx/tsx commit is named by tell" true
  echo "---- kizu CLAUDE.md birth ----"
  "$TELL" -C "$KIZU" --color never --limit 4 e1098c8^ e1098c8 | head -30
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: tenaoshi 第一級 =="
TENA="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
if [[ -d "$TENA/.git" || -f "$TENA/.git" ]]; then
  TN="$("$TELL" -C "$TENA" --json --color never 70b450d^ 70b450d)"
  python3 - "$TN" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = " ".join(p["held"] for p in r["predicates"])
assert "第一級" in held, held
print("tenaoshi-ok")
PY
  assert "tenaoshi policy commit distinguished by 第一級" true
  echo "---- tenaoshi 第一級 ----"
  "$TELL" -C "$TENA" --color never --limit 6 70b450d^ 70b450d | head -40
else
  echo "skip tenaoshi (not present)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
