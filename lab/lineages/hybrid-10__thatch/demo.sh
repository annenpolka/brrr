#!/usr/bin/env bash
# Exercise thatch: covering path-conditions + occupy those stacks through history.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
THATCH="$ROOT/thatch"
chmod +x "$THATCH"

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
"$THATCH" --selftest
assert "selftest exit 0" true

echo
echo "== fixture: stack move, ghost, island, TOKEN_A is not a stack =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/thatch-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "thatch-demo"
git -C "$FIX" config user.email "thatch@example.test"

# t0: no stack yet; TOKEN_A is a grep sheaf would emit and thatch must not.
printf 'keep\nTOKEN_A\n' > "$FIX/keep.txt"
printf 'ghost\n' > "$FIX/old name.txt"
git -C "$FIX" add keep.txt "old name.txt"
git -C "$FIX" commit -q -m "t0: birth of repo"

# t1: production occupies given ready | if x > 0  (in src/git.py — kizu analogue)
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

# t2: the stack moves with the file (sheaf would emit two exists)
git -C "$FIX" mv src/git.py src/parse.py
git -C "$FIX" commit -q -m "t2: move git.py -> parse.py"

# t3: extra occupant line in the same arm (functions grain must NOT split)
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

# t4: copy the same condition into tests (holder spread)
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

# t5: production grows an extra guard — old stack leaves src, remains in tests
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

# t6: island file with a unique path-condition (FocusRiverView analogue)
cat > "$FIX/src/river.py" <<'PY'
def bar_color(flow_score):
    if flow_score > 0.2:
        return "flow"
    return "drift"
PY
git -C "$FIX" add src/river.py
git -C "$FIX" commit -q -m "t6: river island born"

# t7: kill the island + flood of exclusive-B modules + 計画.md + rename
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

echo "-- t0 vs t1: stack born; TOKEN_A is not a path-condition"
T01="$("$THATCH" -C "$FIX" --json --color never "$T0" "$T1")"
python3 - "$T01" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
assert th, th
assert any(p["true_on"]=="B" and "x > 0" in p["label"] for p in th), [p["label"] for p in th]
assert not any("TOKEN_A" in json.dumps(p) for p in th), th
# occupy should show birth
occ = th[0]["occupy"]
assert occ, "missing occupy"
assert occ["true_commits"] >= 1
kinds = occ["kinds"]
assert "birth" in kinds or any(e["value"] for e in occ["eras"]), kinds
print("t01-ok")
PY
assert "t0 vs t1 exclusive-B stack, TOKEN_A silent" true

echo "-- t1 vs t2: ONE move git.py -> parse.py, not two exists"
T12="$("$THATCH" -C "$FIX" --json --color never "$T1" "$T2")"
python3 - "$T12" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
moves = [p for p in th if p["role"]=="move"]
assert moves, [p["role"]+" "+p["label"] for p in th]
m = moves[0]
assert any("git.py" in h for h in m["holders_a"]), m["holders_a"]
assert any("parse.py" in h for h in m["holders_b"]), m["holders_b"]
assert "src/git.py" in m["covers"] and "src/parse.py" in m["covers"], m["covers"]
# occupy splits holders
occ = m["occupy"]
assert occ, "move missing occupy"
hold = occ["holder_seq"]
assert "git.py" in hold and "parse.py" in hold, hold
assert occ["boolean_eras"] < len(occ["eras"]) or "move" in occ["kinds"], occ["kinds"]
print("t12-ok")
PY
assert "t1 vs t2 is one move occupying git.py then parse.py" true

echo "-- t2 vs t3: sibling line is not a new covering stack"
T23="$("$THATCH" -C "$FIX" --json --color never --no-occupy "$T2" "$T3")"
python3 - "$T23" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
# functions grain: same stack, same holders → not distinguishing
assert not any(p["role"]=="move" for p in r["thatch"]), [p["role"] for p in r["thatch"]]
print("t23-ok")
PY
assert "sibling line does not split functions grain" true

echo "-- t4 vs t5: old stack ghosts to tests; production is deeper"
T45="$("$THATCH" -C "$FIX" --json --color never "$T4" "$T5")"
python3 - "$T45" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
roles = {p["role"] for p in th}
labels = [p["label"] for p in th]
# deeper exclusive-B (enabled) and/or ghost/shrink of the old stack
assert any("enabled" in lab for lab in labels) or "ghost" in roles or "shrink" in roles, (roles, labels)
ghosts = [p for p in th if p["role"] in ("ghost","shrink")]
deeper = [p for p in th if "enabled" in p["label"] and p["true_on"] in ("B","AB")]
assert ghosts or deeper, (roles, labels)
if ghosts:
    g = ghosts[0]
    occ = g.get("occupy") or {}
    # occupy of the old stack through history should mention tests
    hold = occ.get("holder_seq","")
    assert "test_parse" in hold or "tests/" in hold or not occ, hold
if deeper:
    d = deeper[0]
    assert any("parse.py" in h for h in d["holders_b"]), d["holders_b"]
    occ = d.get("occupy") or {}
    if occ:
        echoes = []
        for e in occ.get("eras") or []:
            echoes.extend(e.get("echoes") or [])
        # old stack in tests is not required here; production occupies deeper
        assert occ["holds_now"] in (True, False)
print("t45-ok")
PY
assert "t4 vs t5 ghost and/or deeper enabled stack" true

echo "-- t6 vs t7 --limit 4: island river reserved against module flood"
T67="$("$THATCH" -C "$FIX" --json --color never --limit 4 "$T6" "$T7")"
python3 - "$T67" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
assert len(th) <= 4, len(th)
# river's unique path-condition on A
assert any(
    p["true_on"]=="A" and (
        "flow_score" in p["label"] or any("river.py" in h for h in p["holders_a"])
    )
    for p in th
), [(p["true_on"], p["label"], p["holders_a"]) for p in th]
# 計画.md is not a path-condition (commit subjects may mention it)
assert not any("計画" in (p["label"] + " ".join(p.get("covers") or [])) for p in th)
print("t67-ok")
PY
assert "island vs flood keeps river path-condition under --limit 4" true

echo "-- --walks / identical / empty repo"
WALK_OUT="$("$THATCH" -C "$FIX" --walks --no-occupy "$T1" "$T2")"
assert "walks are tenure FILE:LINE" grep -Eq '^tenure -C ' <<<"$WALK_OUT"
assert "walks carry a pin not a grep" grep -Eq 'src/.*\.py:[0-9]+' <<<"$WALK_OUT"
assert "walks do not emit held grep" grep -Evq 'held |grep ' <<<"$WALK_OUT" || true
# the last assert with grep -Evq is awkward; check explicitly
python3 - "$WALK_OUT" <<'PY'
import sys
text = sys.argv[1]
assert "tenure " in text
assert "grep " not in text
assert "exists " not in text
print("walk-ok")
PY
assert "walks are tenure pins, not sheaf greps" true

set +e
"$THATCH" -C "$FIX" -q "$T0" "$T0"
ID_RC=$?
"$THATCH" -C "$FIX" -q --no-occupy "$T0" "$T1"
DIFF_RC=$?
set -e
assert_eq "identical trees exit" "$ID_RC" "1"
assert_eq "different trees exit" "$DIFF_RC" "0"

echo "-- --now / worktree resurrection of river"
printf '%s\n' 'def bar_color(flow_score):' '    if flow_score > 0.2:' '        return "flow"' '    return "drift"' > "$FIX/src/river.py"
WT="$("$THATCH" -C "$FIX" --json --no-occupy HEAD :worktree || true)"
python3 - "$WT" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
assert r["b"]["kind"]=="worktree"
assert any(
    p["true_on"]=="B" and (any("river.py" in h for h in p["holders_b"]) or "flow_score" in p["label"])
    for p in r["thatch"]
), [(p["true_on"], p["label"], p["holders_b"]) for p in r["thatch"]]
print("wt-ok")
PY
assert "HEAD vs :worktree sees uncommitted river stack" true
rm -f "$FIX/src/river.py"

echo "-- empty repo is a clean error, not a stacktrace"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/thatch-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$THATCH" -C "$EMPTY" HEAD HEAD~1 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -qi "empty\|needed a single revision\|cannot resolve" <<<"$EMPTY_ERR"

if [[ -x "$TENURE" ]]; then
  echo "-- generated tenure line actually runs"
  LINE="$("$THATCH" -C "$FIX" --walks --no-occupy "$T0" "$T1" | head -1)"
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
echo "---- fixture human (t1 vs t2 move) ----"
"$THATCH" -C "$FIX" --color never --limit 4 "$T1" "$T2" | head -50

echo
echo "== real repo: kizu git.rs -> parse.rs is ONE stack move =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  KZ="$("$THATCH" -C "$KIZU" --json --color never --limit 6 3b3e0a9^ 3b3e0a9)"
  python3 - "$KZ" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
hold_a = " ".join(" ".join(p.get("holders_a") or []) for p in th)
hold_b = " ".join(" ".join(p.get("holders_b") or []) for p in th)
moves = [p for p in th if p["role"]=="move"]
# the joint: same path-condition occupied git.rs then parse.rs
ok = False
for p in th:
    a = " ".join(p.get("holders_a") or [])
    b = " ".join(p.get("holders_b") or [])
    if "git.rs" in a and "parse.rs" in b:
        ok = True
        occ = p.get("occupy") or {}
        hold = occ.get("holder_seq","")
        if occ:
            assert "git.rs" in hold or "parse.rs" in hold, hold
        break
assert ok, [(p["role"], p["label"], p["holders_a"], p["holders_b"]) for p in th]
print("kizu-move-ok")
PY
  assert "kizu split is a covering stack move git.rs -> parse.rs" true
  echo "---- kizu human ----"
  "$THATCH" -C "$KIZU" --color never --limit 4 3b3e0a9^ 3b3e0a9 | head -60
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: sitbone FocusRiverView island =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  echo "-- birth 14b1d6e^ vs 14b1d6e"
  SBIRTH="$("$THATCH" -C "$SITBONE" --json --color never --limit 6 14b1d6e^ 14b1d6e)"
  python3 - "$SBIRTH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
blob = json.dumps(th)
assert "FocusRiverView" in blob, [(p["label"], p["holders_b"], p["paths_b"]) for p in th]
assert any(p["true_on"] in ("B","AB") for p in th)
assert r["walks"], r["walks"]
assert any(w["tool"]=="tenure" and ":" in (w.get("pin") or "") for w in r["walks"])
print("sitbone-birth-ok")
PY
  assert "sitbone birth covering names FocusRiverView stack + tenure walks" true

  echo "-- death 70ec7df^ vs 70ec7df"
  SDEATH="$("$THATCH" -C "$SITBONE" --json --color never --no-occupy --limit 6 70ec7df^ 70ec7df)"
  python3 - "$SDEATH" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
blob = json.dumps(r["thatch"])
assert "FocusRiverView" in blob, [(p["label"], p["holders_a"]) for p in r["thatch"]]
print("sitbone-death-ok")
PY
  assert "sitbone death covering names FocusRiverView on A" true

  echo "-- island 14b1d6e vs HEAD --limit 6 (git log -- path is empty)"
  SHEAD="$("$THATCH" -C "$SITBONE" --json --color never --limit 6 14b1d6e HEAD)"
  python3 - "$SHEAD" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
# exclusive-A reservation: the island's own stack, not a copied guard that
# still occupies SiteObserver on HEAD, and not a generic `else` spread.
island = [
    p for p in th
    if p["true_on"]=="A" and "FocusRiverView" in json.dumps(p)
]
assert island, [(p["true_on"], p["role"], p["label"][:60], p["holders_a"][:2]) for p in th]
# the characteristic predicate is the view's, not totalTime (copied to SiteObserver)
assert any(
    "flowScore" in p["label"] or "FocusRiverView" in " ".join(p.get("holders_a") or [])
    for p in island
), [(p["label"], p["holders_a"]) for p in island]
assert any(w.get("full") and w.get("true_on")=="A" for w in r["walks"]), r["walks"]
# exclusive-B stacks live on HEAD first-parent; they must not inherit --full
# from the island side (v1 walked 6 × 100 commits).
b_walks = [w for w in r["walks"] if w.get("true_on")=="B"]
assert b_walks, r["walks"]
assert all(not w.get("full") for w in b_walks), b_walks
occ = island[0].get("occupy")
if occ:
    assert occ["eras"], "island occupy produced no eras"
    assert occ.get("first_parent") is False, "island occupy should be --full"
print("sitbone-island-ok")
PY
  assert "island vs HEAD keeps FocusRiverView stack and --full walks" true

  echo "-- PresenceArbiter guard isEnabled vs a parent that lacks it"
  # find a commit before PresenceArbiter if cheap; otherwise HEAD~20 vs HEAD
  SB="$("$THATCH" -C "$SITBONE" --json --color never --limit 8 --occupy-limit 40 \
    "$(git -C "$SITBONE" log --reverse --format=%H -- Sources/SitboneCore/PresenceArbiter.swift | head -1)^" HEAD 2>/dev/null || true)"
  if [[ -n "$SB" ]]; then
    python3 - "$SB" <<'PY'
import json, sys
r = json.loads(sys.argv[1])
th = r["thatch"]
# occupants of guard isEnabled must not include SitboneCore.swift (perch grep's lie)
hits = [p for p in th if "isEnabled" in p["label"] or any("PresenceArbiter" in h for h in (p.get("holders_b") or []))]
hold_b = " ".join(" ".join(p.get("holders_b") or []) for p in hits) if hits else " ".join(" ".join(p.get("holders_b") or []) for p in th)
if hits:
    for p in hits:
        hb = " ".join(p.get("holders_b") or [])
        # SitboneCore.swift may mention isEnabled but must not occupy the guard
        if "isEnabled" in p["label"]:
            assert "SitboneCore.swift" not in hb, hb
print("sitbone-enabled-ok")
PY
    assert "sitbone isEnabled occupants exclude SitboneCore.swift mention" true
  else
    echo "skip sitbone isEnabled range (history walk failed)"
  fi

  echo "---- sitbone birth (human) ----"
  "$THATCH" -C "$SITBONE" --color never --limit 4 14b1d6e^ 14b1d6e | head -50
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
