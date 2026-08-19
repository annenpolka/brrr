#!/usr/bin/env bash
# Exercise wane: exclusive-A path-conditions (what died) occupied through history.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WANE="$ROOT/wane"
chmod +x "$WANE"

TENURE="${TENURE:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-05-tenure/tenure}"

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

echo "== selftest =="
"$WANE" --selftest
assert "selftest exit 0" true

echo
echo "== fixture: deaths only; births, moves, and AB else are silent =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/wane-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "wane-demo"
git -C "$FIX" config user.email "wane@example.test"

printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'ghost\n' > "$FIX/old name.txt"
git -C "$FIX" add keep.txt "old name.txt"
git -C "$FIX" commit -q -m "t0: birth of repo"

mkdir -p "$FIX/src"
cat > "$FIX/src/git.py" <<'PY'
def parse(rest, x=1, ready=True, enabled=True):
    if not ready:
        return None
    if x > 0:
        return "ok"
PY
git -C "$FIX" add src/git.py
git -C "$FIX" commit -q -m "t1: parse under ready and x>0"

git -C "$FIX" mv src/git.py src/parse.py
git -C "$FIX" commit -q -m "t2: move git.py -> parse.py"

cat > "$FIX/src/parse.py" <<'PY'
def parse(rest, x=1, ready=True, enabled=True):
    if not ready:
        return None
    if x > 0:
        flag = True
        return "ok"
PY
git -C "$FIX" add src/parse.py
git -C "$FIX" commit -q -m "t3: sibling line in the same stack"

mkdir -p "$FIX/tests"
cat > "$FIX/tests/test_parse.py" <<'PY'
def test_parse(rest="", x=1, ready=True):
    if not ready:
        return None
    if x > 0:
        return "ok"
PY
git -C "$FIX" add tests/test_parse.py
git -C "$FIX" commit -q -m "t4: tests copy the stack"

cat > "$FIX/src/parse.py" <<'PY'
def parse(rest, x=1, ready=True, enabled=True):
    if not enabled:
        return None
    if not ready:
        return None
    if x > 0:
        flag = True
        return "ok"
PY
git -C "$FIX" add src/parse.py
git -C "$FIX" commit -q -m "t5: production adds enabled guard"

cat > "$FIX/src/river.py" <<'PY'
def bar_color(flow_score):
    if flow_score > 0.2:
        return "flow"
    return "drift"
PY
git -C "$FIX" add src/river.py
git -C "$FIX" commit -q -m "t6: river island born"

rm "$FIX/src/river.py"
for i in 0 1 2 3 4 5 6 7; do
  cat > "$FIX/src/mod${i}.py" <<PY
def fn(unique_mod_${i}=0):
    if unique_mod_${i} > 0:
        return unique_mod_${i}
PY
  git -C "$FIX" add "src/mod${i}.py"
done
printf '計画\n' > "$FIX/計画.md"
git -C "$FIX" add "計画.md"
git -C "$FIX" mv "old name.txt" "new name.txt"
git -C "$FIX" add -A
git -C "$FIX" commit -q -m "t7: kill river, flood modules, 計画.md, rename"

T7="$(git -C "$FIX" rev-parse HEAD)"
T6="$(git -C "$FIX" rev-parse HEAD~1)"
T5="$(git -C "$FIX" rev-parse HEAD~2)"
T4="$(git -C "$FIX" rev-parse HEAD~3)"
T3="$(git -C "$FIX" rev-parse HEAD~4)"
T2="$(git -C "$FIX" rev-parse HEAD~5)"
T1="$(git -C "$FIX" rev-parse HEAD~6)"
T0="$(git -C "$FIX" rev-parse HEAD~7)"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "8"

echo "-- t0 vs t1: a birth is not a death; TOKEN_A is not a path-condition"
T01="$("$WANE" -C "$FIX" --json --color never --no-occupy "$T0" "$T1")"
python3 - "$T01" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert not any(p["true_on"] != "A" for p in wn), [(p["true_on"], p["role"]) for p in wn]
assert not any("TOKEN_A" in json.dumps(p) for p in wn), wn
# stack was born on B — invert the trees to name it
print("t01-ok")
PY
assert "t0 vs t1 empty exclusive-A, TOKEN_A silent" true

T01R="$("$WANE" -C "$FIX" --json --color never --no-occupy "$T1" "$T0")"
python3 - "$T01R" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert any(p["true_on"]=="A" and "x > 0" in p["label"] for p in wn), [p["label"] for p in wn]
print("t01-invert-ok")
PY
assert "invert t1 vs t0 names the born stack as a death" true

echo "-- t1 vs t2: a holder move is AB, not a death"
T12="$("$WANE" -C "$FIX" --json --color never --no-occupy "$T1" "$T2")"
python3 - "$T12" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert all(p["role"] != "move" for p in wn), [(p["role"], p["label"]) for p in wn]
assert all(p["true_on"] == "A" for p in wn), wn
print("t12-ok")
PY
assert "t1 vs t2 move is silent (not exclusive-A)" true

echo "-- t2 vs t3: sibling line is not a death"
T23="$("$WANE" -C "$FIX" --json --color never --no-occupy "$T2" "$T3")"
python3 - "$T23" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert not any(p["role"]=="move" for p in r["wane"]), [p["role"] for p in r["wane"]]
print("t23-ok")
PY
assert "sibling line does not split functions grain" true

echo "-- t4 vs t5: old stack ghosted to tests (AB), enabled is a birth"
T45="$("$WANE" -C "$FIX" --json --color never --no-occupy "$T4" "$T5")"
python3 - "$T45" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
# parse.py survived and tests still hold ready|x>0 — not exclusive-A
assert all(p["true_on"]=="A" for p in wn), [(p["true_on"], p["role"]) for p in wn]
assert not any("enabled" in p["label"] for p in wn), [p["label"] for p in wn]
print("t45-ok")
PY
assert "t4 vs t5 does not name the enabled birth" true

echo "-- t6 vs t7 --limit 4: island river occupies the whole budget"
T67="$("$WANE" -C "$FIX" --json --color never --limit 4 "$T6" "$T7")"
python3 - "$T67" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert len(wn) <= 4, len(wn)
assert wn, "island produced no deaths"
assert all(p["true_on"]=="A" for p in wn), [(p["true_on"], p["role"]) for p in wn]
assert any(
    "flow_score" in p["label"] or any("river.py" in h for h in p["holders_a"])
    for p in wn
), [(p["label"], p["holders_a"]) for p in wn]
assert not any("unique_mod_" in p["label"] for p in wn), [p["label"] for p in wn]
assert not any("計画" in (p["label"] + " ".join(p.get("covers") or [])) for p in wn)
occ = wn[0].get("occupy")
if occ:
    assert occ["eras"], "island occupy produced no eras"
print("t67-ok")
PY
assert "island vs flood is exclusive-A river, not module births" true

echo "-- --walks / identical / empty repo"
WALK_OUT="$("$WANE" -C "$FIX" --walks --no-occupy "$T6" "$T7")"
python3 - "$WALK_OUT" <<'PY'
import sys
text = sys.argv[1]
assert "tenure " in text
assert "grep " not in text
assert "exists " not in text
assert "src/river.py:" in text
print("walk-ok")
PY
assert "walks are tenure pins of the dead stack, not sheaf greps" true

set +e
"$WANE" -C "$FIX" -q "$T0" "$T0"
ID_RC=$?
"$WANE" -C "$FIX" -q --no-occupy "$T6" "$T7"
DIFF_RC=$?
set -e
assert_eq "identical trees exit" "$ID_RC" "1"
assert_eq "different trees exit" "$DIFF_RC" "0"

echo "-- --now / worktree: resurrection is a birth; invert to name it"
printf '%s\n' 'def bar_color(flow_score):' '    if flow_score > 0.2:' '        return "flow"' '    return "drift"' > "$FIX/src/river.py"
WT="$("$WANE" -C "$FIX" --json --no-occupy HEAD :worktree || true)"
python3 - "$WT" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert r["b"]["kind"]=="worktree"
# HEAD -> worktree *added* river; nothing died
assert not any(any("river.py" in h for h in p.get("holders_a") or []) for p in r["wane"]), r["wane"]
print("wt-ok")
PY
assert "HEAD vs :worktree does not treat a birth as a death" true
WTR="$("$WANE" -C "$FIX" --json --no-occupy :worktree HEAD || true)"
python3 - "$WTR" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert any(
    p["true_on"]=="A" and (any("river.py" in h for h in p["holders_a"]) or "flow_score" in p["label"])
    for p in r["wane"]
), [(p["true_on"], p["label"], p["holders_a"]) for p in r["wane"]]
print("wt-invert-ok")
PY
assert ":worktree vs HEAD names the uncommitted river as a death" true
rm -f "$FIX/src/river.py"

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/wane-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$WANE" -C "$EMPTY" HEAD HEAD~1 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -qi "empty\|needed a single revision\|cannot resolve" <<<"$EMPTY_ERR"

if [[ -x "$TENURE" ]]; then
  echo "-- generated tenure line actually runs"
  LINE="$("$WANE" -C "$FIX" --walks --no-occupy "$T6" "$T7" | head -1)"
  RUN="${LINE/#tenure /$TENURE }"
  set +e
  TEN_ERR="$(eval "$RUN" 2>&1)"
  TEN_RC=$?
  set -e
  assert "tenure walk is parseable (exit 0 or 1)" test "$TEN_RC" -eq 0 -o "$TEN_RC" -eq 1
  assert "tenure walk printed eras" grep -Eq 'TRUE|FALSE|now=' <<<"$TEN_ERR"
else
  echo "skip live tenure (binary not present)"
fi

echo
echo "---- fixture human (t6 vs t7 island death) ----"
"$WANE" -C "$FIX" --color never --limit 4 "$T6" "$T7" | head -50

echo
echo "== real repo: kizu git.rs -> parse.rs is a MOVE, so wane is silent =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  KZ="$("$WANE" -C "$KIZU" --json --color never --no-occupy --limit 6 3b3e0a9^ 3b3e0a9)"
  python3 - "$KZ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert all(p["true_on"]=="A" for p in wn), [(p["true_on"], p["role"]) for p in wn]
assert all(p["role"] != "move" for p in wn), [(p["role"], p["label"][:50]) for p in wn]
# no source file died; the split is a holder move. leftover must not spend
# --limit on arm-stacks inside surviving git.rs (v1 did).
assert not wn, [(p["label"][:60], p["holders_a"][:2]) for p in wn]
print("kizu-silent-move-ok")
PY
  assert "kizu split is not claimed as a death" true
  echo "---- kizu human ----"
  "$WANE" -C "$KIZU" --color never --limit 4 3b3e0a9^ 3b3e0a9 | head -40
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: sitbone FocusRiverView island =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- birth 14b1d6e^ vs 14b1d6e: nothing died"
  SBIRTH="$("$WANE" -C "$SITBONE" --json --color never --no-occupy --limit 6 14b1d6e^ 14b1d6e)"
  python3 - "$SBIRTH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert all(p["true_on"]=="A" for p in wn), wn
assert not any("FocusRiverView" in json.dumps(p) for p in wn), [
    (p["label"], p["holders_a"]) for p in wn
]
print("sitbone-birth-empty-ok")
PY
  assert "sitbone birth is not a death" true

  echo "-- death 70ec7df^ vs 70ec7df"
  SDEATH="$("$WANE" -C "$SITBONE" --json --color never --no-occupy --limit 6 70ec7df^ 70ec7df)"
  python3 - "$SDEATH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
blob = json.dumps(wn)
assert "FocusRiverView" in blob, [(p["label"], p["holders_a"]) for p in wn]
assert all(p["true_on"]=="A" for p in wn)
assert any("flowScore" in p["label"] or "FocusRiverView" in " ".join(p.get("holders_a") or []) for p in wn)
print("sitbone-death-ok")
PY
  assert "sitbone death covering names FocusRiverView on A" true

  echo "-- island 14b1d6e vs HEAD --limit 6 (git log -- path is empty)"
  SHEAD="$("$WANE" -C "$SITBONE" --json --color never --limit 6 14b1d6e HEAD)"
  python3 - "$SHEAD" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert wn, "island produced no deaths"
assert all(p["true_on"]=="A" for p in wn), [(p["true_on"], p["role"], p["label"][:60]) for p in wn]
assert all(p["role"]=="exclusive_a" for p in wn), [p["role"] for p in wn]
# no exclusive-B births, no generic AB else
assert not any(p["true_on"]=="B" for p in wn)
assert not any(p["role"] in ("spread", "move") for p in wn)
assert not any(p["label"].strip() in ("else", "guard-else") or p["label"].startswith("else ") for p in wn)
island = [
    p for p in wn
    if "FocusRiverView" in json.dumps(p)
]
assert island, [(p["true_on"], p["role"], p["label"][:60], p["holders_a"][:2]) for p in wn]
assert any(
    "flowScore" in p["label"] or "FocusRiverView" in " ".join(p.get("holders_a") or [])
    for p in island
), [(p["label"], p["holders_a"]) for p in island]
# budget is deaths of the deleted file, not surviving-file tick arms
assert any("flowScore" in p["label"] for p in island), [(p["label"][:80]) for p in island]
assert all("FocusRiverView" in " ".join(p.get("holders_a") or []) for p in wn), [
    (p["label"][:50], p["holders_a"][:2]) for p in wn
]
assert not any("SitboneCore" in " ".join(p.get("holders_a") or []) for p in wn)
assert all(w.get("true_on")=="A" for w in r["walks"]), r["walks"]
assert any(w.get("full") and w.get("true_on")=="A" for w in r["walks"]), r["walks"]
assert all("FocusRiverView" in (w.get("pin") or "") for w in r["walks"]), r["walks"]
# there are no exclusive-B walks to inherit --full
assert not any(w.get("true_on")=="B" for w in r["walks"]), r["walks"]
occ = island[0].get("occupy")
if occ:
    assert occ["eras"], "island occupy produced no eras"
    assert occ.get("first_parent") is False, "island occupy should be --full"
print("sitbone-island-ok")
PY
  assert "island vs HEAD is exclusive-A FocusRiverView, no B/AB else" true

  echo "-- PresenceArbiter guard isEnabled vs a parent that lacks it"
  SB="$("$WANE" -C "$SITBONE" --json --color never --limit 8 --occupy-limit 40 \
    "$(git -C "$SITBONE" log --reverse --format=%H -- Sources/SitboneCore/PresenceArbiter.swift | head -1)^" HEAD 2>/dev/null || true)"
  if [[ -n "$SB" ]]; then
    python3 - "$SB" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
wn = r["wane"]
assert all(p["true_on"]=="A" for p in wn), [(p["true_on"], p["role"]) for p in wn]
# isEnabled was born, not killed — default cover must not name it
assert not any("isEnabled" in p["label"] for p in wn), [p["label"] for p in wn]
print("sitbone-enabled-ok")
PY
    assert "sitbone isEnabled birth is silent on default wane" true
  else
    echo "skip sitbone isEnabled range (history walk failed)"
  fi

  echo "---- sitbone island (human) ----"
  "$WANE" -C "$SITBONE" --color never --no-occupy --limit 6 14b1d6e HEAD | head -60
else
  echo "skip sitbone (not present)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
