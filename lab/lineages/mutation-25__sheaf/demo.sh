#!/usr/bin/env bash
# Exercise sheaf against a synthetic ugly fixture and the dogfood repositories.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SHEAF="$ROOT/sheaf"
chmod +x "$SHEAF"

HELD="${HELD:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-796f-76d0-988f-5c2c16399eaa/held}"
PERCH="${PERCH:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ad1-c9bd-7c52-b01b-c771008e6951/perch}"

if [[ ! -x "$SHEAF" ]]; then
  echo "demo: sheaf is not executable" >&2
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
FIX="$(mktemp -d "${TMPDIR:-/tmp}/sheaf-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "sheaf-demo"
git -C "$FIX" config user.email "sheaf@example.test"

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
git -C "$FIX/vendor/nested" config user.name "sheaf-demo"
git -C "$FIX/vendor/nested" config user.email "sheaf@example.test"
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
T01="$("$SHEAF" -C "$FIX" --json --color never "$T0" "$T1")"
python3 - "$T01" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["sheaf"]
held = [p["held"] for p in preds]
assert any("oscillate" in h for h in held), held
assert not any("TOKEN_A" in p["pattern"] for p in preds), preds
# shortest set may pick grep oscillate (shorter) over exists *oscillate*
assert any(p["true_on"]=="A" and "oscillate" in p["pattern"] for p in preds), held
walks = r["walks"]
assert walks, walks
assert any(w["tool"]=="held" and "oscillate" in w["line"] for w in walks), walks
assert any(w["tool"]=="perch" and w["line"].startswith("perch ") for w in walks), walks
print("t01-ok")
PY
assert "t0 vs t1 oscillate sheaf + walks, TOKEN_A silent" true

echo "-- t1 vs t2: TOKEN_A dies, 計画.md born, oscillate revives"
T12="$("$SHEAF" -C "$FIX" --json --color never "$T1" "$T2")"
python3 - "$T12" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
preds = r["sheaf"]
held = [p["held"] for p in preds]
assert any(p["true_on"]=="A" and ("TOKEN_A" in p["pattern"] or p["pattern"]=="TOKEN") for p in preds), held
assert any(p["true_on"]=="B" and ("計画" in p["held"] or (p["kind"]=="exists" and ".md" in p["pattern"])) for p in preds), held
assert any(p["true_on"]=="B" and "oscillate" in p["pattern"] for p in preds), held
# shortest set: a few predicates, not a catalog
assert 1 <= len(preds) <= 8, len(preds)
print("t12-ok")
PY
assert "t1 vs t2 TOKEN_A / 計画.md / oscillate in sheaf" true

echo "-- t2 vs t3: rename with spaces is exists, not grep of ghost"
T23="$("$SHEAF" -C "$FIX" --json --color never "$T2" "$T3")"
python3 - "$T23" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["sheaf"]]
assert any("old name" in h for h in held), held
assert any("new name" in h for h in held), held
assert not any(p["kind"]=="grep" and p["pattern"]=="ghost" for p in r["sheaf"]), held
print("t23-ok")
PY
assert "rename is exists on both sides, shared blob is not grep" true

echo "-- t4 vs t6: TOKEN_A reincarnation then death"
T46="$("$SHEAF" -C "$FIX" --json --color never "$T4" "$T6")"
python3 - "$T46" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "TOKEN_A" in p["pattern"] for p in r["sheaf"])
print("t46-ok")
PY
assert "t4 vs t6 TOKEN_A on A only" true

echo "-- --held / --walks / --oneline / exit codes"
HELD_OUT="$("$SHEAF" -C "$FIX" --held "$T0" "$T2" | head -5)"
assert "held-language lines look like exists/grep" grep -Eq '^(exists|grep) ' <<<"$HELD_OUT"

WALK_OUT="$("$SHEAF" -C "$FIX" --walks --walk held "$T0" "$T2")"
assert "walks are ready-to-run held lines" grep -Eq '^held -C ' <<<"$WALK_OUT"
assert "walks carry the predicate" grep -Eq ' (exists|grep) ' <<<"$WALK_OUT"

set +e
"$SHEAF" -C "$FIX" -q "$T0" "$T0"
ID_RC=$?
"$SHEAF" -C "$FIX" -q "$T0" "$T1"
DIFF_RC=$?
set -e
assert_eq "identical trees exit" "$ID_RC" "1"
assert_eq "different trees exit" "$DIFF_RC" "0"

echo "-- --now / worktree resurrection"
printf 'dirty\n' > "$FIX/oscillate.txt"
WT="$("$SHEAF" -C "$FIX" --json HEAD :worktree || true)"
python3 - "$WT" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert r["b"]["kind"]=="worktree"
assert any(p["true_on"]=="B" and "oscillate" in p["pattern"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
assert any(w.get("now") for w in r["walks"]), r["walks"]
print("wt-ok")
PY
assert "HEAD vs :worktree sees uncommitted oscillate and --now walks" true
rm -f "$FIX/oscillate.txt"

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/sheaf-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$SHEAF" -C "$EMPTY" HEAD HEAD~1 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -qi "empty\|needed a single revision\|cannot resolve" <<<"$EMPTY_ERR"

if [[ -x "$HELD" ]]; then
  echo "-- generated held line actually runs"
  LINE="$("$SHEAF" -C "$FIX" --walks --walk held "$T0" "$T1" | head -1)"
  RUN="${LINE/#held /$HELD }"
  set +e
  HELD_ERR="$(eval "$RUN" 2>&1)"
  HELD_RC=$?
  set -e
  assert "held walk is parseable (exit 0 or 1)" test "$HELD_RC" -eq 0 -o "$HELD_RC" -eq 1
  assert "held walk printed eras" grep -Eq 'TRUE|FALSE|now=' <<<"$HELD_ERR"
else
  echo "skip live held (binary not present)"
fi

echo
echo "== real repo: sitbone FocusRiverView island =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- birth 14b1d6e^ vs 14b1d6e (file appears)"
  SBIRTH="$("$SHEAF" -C "$SITBONE" --json --color never 14b1d6e^ 14b1d6e)"
  python3 - "$SBIRTH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["sheaf"]]
assert any("FocusRiverView" in h for h in held), held
assert any(p["true_on"]=="B" and "FocusRiverView" in p["held"] for p in r["sheaf"])
assert any(w["tool"]=="held" and "FocusRiverView" in w["line"] for w in r["walks"]), r["walks"]
assert any(w["tool"]=="perch" and "FocusRiverView" in w["line"] for w in r["walks"]), r["walks"]
print("sitbone-birth-ok")
PY
  assert "sitbone birth sheaf names FocusRiverView on B + walks" true

  echo "-- death 70ec7df^ vs 70ec7df (file disappears)"
  SDEATH="$("$SHEAF" -C "$SITBONE" --json --color never 70ec7df^ 70ec7df)"
  python3 - "$SDEATH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
print("sitbone-death-ok")
PY
  assert "sitbone death sheaf names FocusRiverView on A" true

  echo "-- island 14b1d6e vs HEAD (git log -- path is empty)"
  SHEAD="$("$SHEAF" -C "$SITBONE" --json --color never --limit 6 14b1d6e HEAD)"
  python3 - "$SHEAD" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(p["true_on"]=="A" and "FocusRiverView" in p["held"] for p in r["sheaf"]), [p["held"] for p in r["sheaf"]]
# island is off first-parent: walks must pass --full
assert any(w["full"] and "FocusRiverView" in w["line"] and "--full" in w["line"] for w in r["walks"]), r["walks"]
print("sitbone-island-ok")
PY
  assert "island vs HEAD sheaf keeps FocusRiverView and --full walks" true

  echo "---- sitbone birth (human) ----"
  "$SHEAF" -C "$SITBONE" --color never --limit 4 14b1d6e^ 14b1d6e | head -40
else
  echo "skip sitbone (not present)"
fi

echo
echo "== real repo: kizu CLAUDE.md birth + jsx =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  K1="$("$SHEAF" -C "$KIZU" --json --color never e1098c8^ e1098c8)"
  python3 - "$K1" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = [p["held"] for p in r["sheaf"]]
assert any("CLAUDE" in h for h in held), held
assert r["walks"], r["walks"]
print("kizu-claude-ok")
PY
  assert "kizu CLAUDE.md birth is in the sheaf + walks" true

  K2="$("$SHEAF" -C "$KIZU" --json --color never --limit 8 04adde1^ 04adde1)"
  python3 - "$K2" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
held = " ".join(p["held"] for p in r["sheaf"])
assert "jsx" in held.lower() or "tsx" in held.lower() or "js_ts" in held, held
print("kizu-jsx-ok")
PY
  assert "kizu jsx/tsx commit is named by the sheaf" true
  echo "---- kizu CLAUDE.md birth ----"
  "$SHEAF" -C "$KIZU" --color never --limit 4 e1098c8^ e1098c8 | head -30
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
