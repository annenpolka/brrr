#!/usr/bin/env bash
# Exercise tenure: occupancy of a path-condition, split when occupants change.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TENURE="$ROOT/tenure"
chmod +x "$TENURE"

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

echo "== selftest =="
"$TENURE" --selftest
assert "selftest exit 0" true

echo
echo "== fixture: stack occupancy, copy, production-leaves-tests ghost =="
FIX="$(mktemp -d "${TMPDIR:-/tmp}/tenure-demo.XXXXXX")"
cleanup() { rm -rf "$FIX"; }
trap cleanup EXIT

git -C "$FIX" init -q -b main
git -C "$FIX" config user.name "tenure-demo"
git -C "$FIX" config user.email "tenure@example.test"

# t0: no stack yet
printf 'keep\n' > "$FIX/README.md"
git -C "$FIX" add README.md
git -C "$FIX" commit -q -m "t0: birth of repo"

# t1: production occupies given ready | if x > 0
mkdir -p "$FIX/src"
cat > "$FIX/src/app.py" <<'PY'
def process(x, ready=True, enabled=True):
    if not ready:
        return None
    if x > 0:
        return "ok"
PY
git -C "$FIX" add src/app.py
git -C "$FIX" commit -q -m "t1: process under ready and x>0"

# t2: extra occupant line in the same arm (functions grain must NOT split)
cat > "$FIX/src/app.py" <<'PY'
def process(x, ready=True, enabled=True):
    if not ready:
        return None
    if x > 0:
        flag = True
        return "ok"
PY
git -C "$FIX" add src/app.py
git -C "$FIX" commit -q -m "t2: sibling line in the same stack"

# t3: copy the same condition into tests (holder spread; occupancy never flips)
mkdir -p "$FIX/tests"
cat > "$FIX/tests/test_app.py" <<'PY'
def test_process(x=1, ready=True):
    if not ready:
        return None
    if x > 0:
        return "ok"
PY
git -C "$FIX" add tests/test_app.py
git -C "$FIX" commit -q -m "t3: tests copy the stack"

# t4: production grows an extra guard — old stack leaves src, remains in tests
cat > "$FIX/src/app.py" <<'PY'
def process(x, ready=True, enabled=True):
    if not enabled:
        return None
    if not ready:
        return None
    if x > 0:
        flag = True
        return "ok"
PY
git -C "$FIX" add src/app.py
git -C "$FIX" commit -q -m "t4: production adds enabled guard"

N="$(git -C "$FIX" rev-list --count HEAD)"
assert_eq "fixture commit count" "$N" "5"

# Pin a line that still sits in the ORIGINAL stack at HEAD: the test copy.
# (HEAD's src/app.py:8 is a deeper stack — given enabled | given ready | if x>0.)
echo "-- pin tests/test_app.py:5 (original stack, now a ghost occupant)"
JSON="$("$TENURE" -C "$FIX" --color never --json tests/test_app.py:5 || true)"

BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$JSON")"
N_ERAS="$(json_get 'print(len(r["eras"]))' <<<"$JSON")"
PAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$JSON")"
HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$JSON")"
KINDS="$(json_get 'print([e["kind"] for e in r["eras"]])' <<<"$JSON")"
NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$JSON")"
GHOST="$(json_get 'print(int(r["ghost_now"]))' <<<"$JSON")"
PRED="$(json_get 'print(r["predicate"])' <<<"$JSON")"
TRUE_N="$(json_get 'print(r["true_commits"])' <<<"$JSON")"

echo "predicate: $PRED"
echo "pattern:   $PAT"
echo "holders:   $HOLD"
echo "kinds:     $KINDS"

assert_eq "boolean eras (F T)" "$BOOL" "2"
assert_eq "holder eras" "$N_ERAS" "4"
assert_eq "era pattern" "$PAT" "FTTT"
assert_eq "true commits" "$TRUE_N" "4"
assert_eq "holds now (ghost occupancy)" "$NOW" "1"
assert_eq "ghost_now" "$GHOST" "1"
assert_eq "kinds" "$KINDS" "['absent', 'birth', 'spread', 'ghost']"
assert_eq "holders sequence" "$HOLD" "src/app.py:process | src/app.py:process,tests/test_app.py:test_process | tests/test_app.py:test_process"

GHOST_ECHO="$(json_get 'ghost=[e for e in r["eras"] if e["kind"]=="ghost"]; print(ghost[0]["echoes"][0]["kind"]+" "+ghost[0]["echoes"][0]["holder"] if ghost and ghost[0]["echoes"] else "")' <<<"$JSON")"
assert_eq "ghost era echo is deeper production" "$GHOST_ECHO" "deeper src/app.py:process"
GHOST_STACK="$(json_get 'ghost=[e for e in r["eras"] if e["kind"]=="ghost"]; print(ghost[0]["echoes"][0]["stack"] if ghost and ghost[0]["echoes"] else "")' <<<"$JSON")"
assert "ghost echo names enabled guard" grep -q "enabled" <<<"$GHOST_STACK"

T1T2="$(json_get 'trues=[e for e in r["eras"] if e["value"]]; print(trues[0]["count"])' <<<"$JSON")"
assert_eq "birth era covers t1+t2 (sibling line is not a function split)" "$T1T2" "2"

echo "-- --boolean recovers ancestor held (one TRUE island)"
BJ="$("$TENURE" -C "$FIX" --boolean --color never --json tests/test_app.py:5 || true)"
BN="$(json_get 'print(len(r["eras"]), int(r["split_holders"]))' <<<"$BJ")"
BPAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$BJ")"
assert_eq " --boolean is two eras, no holder split" "$BN" "2 0"
assert_eq "--boolean pattern" "$BPAT" "FT"

echo "-- --grain loci splits t2 sibling line; functions did not"
LJ="$("$TENURE" -C "$FIX" --grain loci --color never --json tests/test_app.py:5 || true)"
LN="$(json_get 'print(len(r["eras"]))' <<<"$LJ")"
python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>4 else 1)' "$LN"
assert "loci grain splits the sibling line (eras=$LN > 4)" true

echo "-- HEAD src/app.py:8 is the deeper stack (enabled+ready); occupancy starts at t4"
DJ="$("$TENURE" -C "$FIX" --color never --json src/app.py:8 || true)"
DPAT="$(json_get 'print("".join("T" if e["value"] else "F" for e in r["eras"]))' <<<"$DJ")"
DHOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$DJ")"
assert_eq "deeper stack pattern" "$DPAT" "FT"
assert_eq "deeper stack holder is production only" "$DHOLD" "src/app.py:process"

echo "-- empty repo is a clean error"
EMPTY="$(mktemp -d "${TMPDIR:-/tmp}/tenure-empty.XXXXXX")"
git -C "$EMPTY" init -q -b main
set +e
EMPTY_ERR="$("$TENURE" -C "$EMPTY" README.md:1 2>&1)"
EMPTY_RC=$?
set -e
rm -rf "$EMPTY"
assert_eq "empty repo exit" "$EMPTY_RC" "2"
assert "empty repo mentions empty" grep -q "empty" <<<"$EMPTY_ERR"

echo
echo "---- fixture human (functions grain, original stack) ----"
"$TENURE" -C "$FIX" --color never tests/test_app.py:5 || true

echo
echo "== real repo: kizu parse.rs:60 (stack moved git.rs → parse.rs) =="
KIZU="/Users/annenpolka/ghq/github.com/annenpolka/kizu"
if [[ -d "$KIZU/.git" || -f "$KIZU/.git" ]]; then
  KZ="$("$TENURE" -C "$KIZU" --color never --json src/git/parse.rs:60 || true)"
  KZ_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$KZ")"
  KZ_BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$KZ")"
  KZ_N="$(json_get 'print(len(r["eras"]))' <<<"$KZ")"
  KZ_TRUE="$(json_get 'print(r["true_commits"])' <<<"$KZ")"
  KZ_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$KZ")"
  KZ_PRED="$(json_get 'print(r["predicate"])' <<<"$KZ")"
  assert_eq "kizu holds now" "$KZ_NOW" "1"
  python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>=1 else 1)' "$KZ_TRUE"
  assert "kizu found TRUE commits ($KZ_TRUE)" true
  echo "predicate: $KZ_PRED"
  echo "holders:   $KZ_HOLD"
  echo "boolean=$KZ_BOOL eras=$KZ_N"
  python3 -c '
import sys
hold=sys.argv[1]
sys.exit(0 if ("git.rs" in hold and "parse.rs" in hold) else 1)
' "$KZ_HOLD"
  assert "kizu holder split git.rs → parse.rs (not when|grep of the if-text)" true
  python3 -c 'import sys; n,b=int(sys.argv[1]),int(sys.argv[2]); sys.exit(0 if n>b else 1)' "$KZ_N" "$KZ_BOOL"
  assert "kizu holder eras ($KZ_N) exceed boolean ($KZ_BOOL)" true
  echo "---- kizu human ----"
  "$TENURE" -C "$KIZU" --color never src/git/parse.rs:60 || true
else
  echo "skip kizu (not present)"
fi

echo
echo "== real repo: sitbone PresenceArbiter.swift:81 (guard isEnabled) =="
SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/.git" || -f "$SITBONE/.git" ]]; then
  SB="$("$TENURE" -C "$SITBONE" --color never --json Sources/SitboneCore/PresenceArbiter.swift:81 || true)"
  SB_NOW="$(json_get 'print(int(r["holds_now"]))' <<<"$SB")"
  SB_BOOL="$(json_get 'print(r["boolean_eras"])' <<<"$SB")"
  SB_HOLD="$(json_get 'print(" | ".join(",".join(e["holders"]) for e in r["eras"] if e["value"]))' <<<"$SB")"
  SB_PRED="$(json_get 'print(r["predicate"])' <<<"$SB")"
  SB_TRUE="$(json_get 'print(r["true_commits"])' <<<"$SB")"
  assert_eq "sitbone holds now" "$SB_NOW" "1"
  python3 -c 'import sys; sys.exit(0 if int(sys.argv[1])>=1 else 1)' "$SB_TRUE"
  assert "sitbone found TRUE commits ($SB_TRUE)" true
  assert "sitbone holder is PresenceArbiter" grep -q "PresenceArbiter.swift" <<<"$SB_HOLD"
  SB_ECHO="$(json_get 'echoes=[];
[echoes.extend(e.get("echoes") or []) for e in r["eras"]];
print(",".join(sorted({e["holder"] for e in echoes})))' <<<"$SB")"
  echo "predicate: $SB_PRED"
  echo "holders:   $SB_HOLD"
  echo "echoes:    $SB_ECHO"
  echo "boolean=$SB_BOOL"
  # perch grep isEnabled also names SitboneCore.swift (arbiter.isEnabled = …).
  # That file never occupies guard isEnabled. tenure must say so.
  assert "sitbone echo names SitboneCore mention (perch grep's extra holder)" \
    grep -q "SitboneCore.swift" <<<"$SB_ECHO"
  python3 -c 'import sys; sys.exit(0 if "SitboneCore.swift" not in sys.argv[1] else 1)' "$SB_HOLD"
  assert "sitbone holders do not include SitboneCore.swift" true
  echo "---- sitbone human ----"
  "$TENURE" -C "$SITBONE" --color never Sources/SitboneCore/PresenceArbiter.swift:81 || true
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
