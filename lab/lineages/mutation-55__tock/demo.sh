#!/usr/bin/env bash
# Exercise tock against synthetic git repos and, when present, parent tools.
# Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TOCK="$ROOT/tock.py"
PYTHON="${PYTHON:-python3}"
BASE="${TMPDIR:-/tmp}/tock-demo-$$"
WINNOW="${WINNOW:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-bf36-7370-8d54-8bed7c40c0c8/winnow}"
ALIBI="${ALIBI:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01abb-4faf-7c02-a6f1-67838af12a62/alibi.py}"
CINCH="${CINCH:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-03-cinch/cinch.py}"
SNUG="${SNUG:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/reimpl-06-snug/snug.py}"
trap 'rm -rf "$BASE"' EXIT

chmod +x "$ROOT/tock" "$TOCK" 2>/dev/null || true
mkdir -p "$BASE"

git_init() {
  local dir="$1"
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" config user.email "tock@example.com"
  git -C "$dir" config user.name "tock"
  git -C "$dir" config commit.gpgsign false
}

commit_all() {
  local dir="$1"
  git -C "$dir" add -A
  git -C "$dir" commit -qm "$2"
}

assert_eq() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" != "$want" ]]; then
    echo "FAIL $label" >&2
    echo "  want: $(printf %q "$want")" >&2
    echo "  got:  $(printf %q "$got")" >&2
    exit 1
  fi
  echo "ok  $label"
}

pass() { echo "ok  $1"; }

echo "======== 0. unit tests ========"
"$PYTHON" -m unittest discover -s "$ROOT/tests" -q
pass "unit tests"

# --- Case 1: lockset vs fingerprint (the hybrid's object) ---
# HEAD add returns 0. WIP: debug print + real return + new tests + README.
# tock wheat is only the return hunk. Tests are held. Print is chaff.
echo "======== 1. lockset drops debug print; holds tests ========"
case1="$BASE/trap"
git_init "$case1"
cat > "$case1/app.py" <<'PY'
def add(a, b):
    x = 0

    return 0
PY
cat > "$case1/test.py" <<'PY'
from app import add
assert add(2, 3) == 5
print("pass")
PY
echo "hello" > "$case1/README.md"
commit_all "$case1" "base"
cat > "$case1/app.py" <<'PY'
def add(a, b):
    print("debug")

    return a + b
PY
cat > "$case1/test.py" <<'PY'
# new test comment
from app import add
assert add(2, 3) == 5
print("pass")
PY
echo "hello world" > "$case1/README.md"

json1="$("$PYTHON" "$TOCK" -C "$case1" --json -- "$PYTHON" test.py)"
echo "$json1" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
wheat=d["wheat"]
assert len(wheat)==1 and wheat[0]["path"]=="app.py", wheat
wheat_ids=[w["id"] for w in wheat]
chaff_ids=[c["id"] for c in d["chaff"]]
assert "test.py" in d["held_tests"], d
assert "README.md" in d["ignored"], d
assert all(not i.startswith("test.py") for i in wheat_ids), wheat_ids
print("wheat", wheat_ids)
print("chaff", chaff_ids)
'
patch1="$("$PYTHON" "$TOCK" -C "$case1" --format patch -- "$PYTHON" test.py)"
echo "$patch1" | grep -q "return a + b"
if echo "$patch1" | grep -q 'print("debug")'; then
  echo "FAIL wheat patch included debug print" >&2
  echo "$patch1" >&2
  exit 1
fi
pass "lockset wheat is the return hunk, not the debug print"
pass "tests held, README ignored, patch is wheat-only"

# Parent contrast: winnow fingerprint wheat includes the debug print.
if [[ -f "$WINNOW" ]]; then
  echo "======== 1b. winnow contrast (fingerprint wheat) ========"
  wjson="$("$PYTHON" "$WINNOW" -C "$case1" --format json -- "$PYTHON" test.py)"
  echo "$wjson" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
ids=[w["id"] for w in d["wheat"]]
print("winnow wheat", ids)
assert any("app.py" in i for i in ids), ids
'
  wpaths="$("$PYTHON" "$WINNOW" -C "$case1" --format paths -- "$PYTHON" test.py)"
  cpaths="$("$PYTHON" "$TOCK" -C "$case1" --format paths -- "$PYTHON" test.py)"
  assert_eq "$cpaths" "app.py" "tock paths are production only"
  if echo "$wpaths" | grep -qx "test.py"; then
    pass "winnow wheat includes test.py (parent object); tock holds it"
  else
    echo "note: winnow did not mark test.py as wheat this run"
    echo "winnow paths:" $wpaths
  fi
  echo "$wjson" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
app=[w for w in d["wheat"] if w["path"]=="app.py"]
print("winnow app.py wheat units", len(app), [w.get("header") for w in app])
assert len(app) >= 1
'
  pass "winnow contrast ran"
else
  echo "(winnow parent not present, skip contrast)"
fi

if [[ -f "$ALIBI" ]]; then
  echo "======== 1c. alibi contrast (file grain LOCKED) ========"
  set +e
  ajson="$("$PYTHON" "$ALIBI" -C "$case1" --json --per-path --cmd "$PYTHON test.py" 2>/dev/null)"
  set -e
  echo "$ajson" | "$PYTHON" -c '
import json,sys
raw=sys.stdin.read()
d=json.loads(raw)
print("alibi status", d.get("status"), "per_path", d.get("per_path"))
assert d.get("status")=="LOCKED", d
assert d.get("per_path",{}).get("app.py")=="LOCKED" or "app.py" in d.get("production_changed",[]), d
'
  pass "alibi locks whole app.py; tock splits the hunks"
else
  echo "(alibi parent not present, skip contrast)"
fi

if [[ -f "$CINCH" ]]; then
  echo "======== 1d. cinch contrast (same fixture, same lockset) ========"
  cjson="$("$PYTHON" "$CINCH" -C "$case1" --json -- "$PYTHON" test.py)"
  "$PYTHON" -c '
import json,sys
a=json.loads(sys.argv[1])
b=json.loads(sys.argv[2])
print("tock  wheat", [w["id"] for w in a["wheat"]], "chaff", [c["id"] for c in a["chaff"]])
print("cinch wheat", [w["id"] for w in b["wheat"]], "chaff", [c["id"] for c in b["chaff"]])
assert a["status"]==b["status"]=="LOCKED"
assert [w["id"] for w in a["wheat"]]==[w["id"] for w in b["wheat"]]
assert [c["id"] for c in a["chaff"]]==[c["id"] for c in b["chaff"]]
' "$json1" "$cjson"
  cpatch="$("$PYTHON" "$CINCH" -C "$case1" --format patch -- "$PYTHON" test.py)"
  if ! echo "$cpatch" | grep -q "return a + b"; then
    echo "FAIL cinch patch missing return" >&2
    exit 1
  fi
  if echo "$cpatch" | grep -q 'print("debug")'; then
    echo "FAIL cinch patch included debug print" >&2
    exit 1
  fi
  pass "tock and cinch agree on debug-print vs return lockset"
else
  echo "(cinch parent not present, skip contrast)"
fi

# --- Case 2: two production files jointly required ---
echo "======== 2. joint wheat ========"
case2="$BASE/joint"
git_init "$case2"
echo 'KEY = "a"' > "$case2/a.py"
echo 'KEY = "b"' > "$case2/b.py"
echo 'noise = 1' > "$case2/c.py"
cat > "$case2/test.py" <<'PY'
import a, b
assert a.KEY == "AX" and b.KEY == "BX"
print("pass")
PY
commit_all "$case2" "base"
echo 'KEY = "AX"' > "$case2/a.py"
echo 'KEY = "BX"' > "$case2/b.py"
echo 'noise = 2' > "$case2/c.py"
got="$("$PYTHON" "$TOCK" -C "$case2" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" $'a.py\nb.py' "joint lockset keeps both required files"

# --- Case 3: LOOSE comment-only production ---
echo "======== 3. LOOSE ========"
case3="$BASE/loose"
git_init "$case3"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case3/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case3/test.py"
commit_all "$case3" "green"
printf '%s\n' 'def add(a, b):' '    # definitely correct' '    return a + b' > "$case3/app.py"
set +e
json3="$("$PYTHON" "$TOCK" -C "$case3" --json -- "$PYTHON" test.py)"
code3=$?
set -e
echo "$json3" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="LOOSE" and d["wheat"]==[], d'
assert_eq "$code3" "2" "LOOSE exit 2"

# --- Case 4: CLEAN test-only ---
echo "======== 4. CLEAN ========"
case4="$BASE/clean"
git_init "$case4"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case4/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case4/test.py"
commit_all "$case4" "green"
echo '# extra note' >> "$case4/test.py"
set +e
json4="$("$PYTHON" "$TOCK" -C "$case4" --json -- "$PYTHON" test.py)"
code4=$?
set -e
echo "$json4" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="CLEAN" and d["production_units"]==0, d'
assert_eq "$code4" "0" "CLEAN exit 0"

# --- Case 5: BROKEN ---
echo "======== 5. BROKEN ========"
case5="$BASE/broken"
git_init "$case5"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case5/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case5/test.py"
commit_all "$case5" "green"
printf '%s\n' 'def add(a, b):' '    # also dirty production' '    return a + b' > "$case5/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 99' > "$case5/test.py"
set +e
json5="$("$PYTHON" "$TOCK" -C "$case5" --json -- "$PYTHON" test.py)"
code5=$?
set -e
echo "$json5" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="BROKEN", d'
assert_eq "$code5" "3" "BROKEN exit 3"

# --- Case 6: two hunks in one file; only the far hunk is locked ---
echo "======== 6. hunk split inside one file ========"
case6="$BASE/hunks"
git_init "$case6"
cat > "$case6/app.py" <<'PY'
# header
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
def add(a, b):
    return 0

def extra():
    return 0
PY
cat > "$case6/test.py" <<'PY'
from app import add
assert add(2, 3) == 5
print("pass")
PY
commit_all "$case6" "base"
cat > "$case6/app.py" <<'PY'
# header changed (chaff)
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
def add(a, b):
    return a + b

def extra():
    return 0
PY
json6="$("$PYTHON" "$TOCK" -C "$case6" --json -- "$PYTHON" test.py)"
echo "$json6" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
wheat=d["wheat"]
assert [w["path"] for w in wheat]==["app.py"], wheat
assert len(wheat)==1, wheat
assert any(c["path"]=="app.py" and c.get("hunk")==1 for c in d["chaff"]), d["chaff"]
print("ok  hunk-level splits header comment from locked return")
'

# --- Case 7: new symbol the tests import ---
echo "======== 7. new production symbol is wheat ========"
case7="$BASE/newsym"
git_init "$case7"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case7/app.py"
cat > "$case7/test.py" <<'PY'
from app import add
assert add(2, 3) == 5
PY
commit_all "$case7" "green"
printf '%s\n' 'def add(a, b):' '    return a + b' '' 'def mul(a, b):' '    return a * b' > "$case7/app.py"
cat > "$case7/test.py" <<'PY'
from app import add, mul
assert add(2, 3) == 5
assert mul(2, 3) == 6
print("pass")
PY
json7="$("$PYTHON" "$TOCK" -C "$case7" --json -- "$PYTHON" test.py)"
echo "$json7" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
assert d["wheat"], d
assert all(w["path"]=="app.py" for w in d["wheat"]), d
print("ok  new symbol isolation")
'

# --- Case 8: spaces/parens in paths ---
echo "======== 8. ugly paths ========"
case8="$BASE/ugly"
git_init "$case8"
mkdir -p "$case8/sub dir"
echo 'VAL = 1' > "$case8/sub dir/weird (x).py"
echo 'other = 1' > "$case8/ok.py"
cat > "$case8/test.py" <<'PY'
import importlib.util, pathlib
p = pathlib.Path(__file__).parent / "sub dir" / "weird (x).py"
spec = importlib.util.spec_from_file_location("weird", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert m.VAL == 2
print("pass")
PY
commit_all "$case8" "base"
echo 'VAL = 2' > "$case8/sub dir/weird (x).py"
echo 'other = 2' > "$case8/ok.py"
got="$("$PYTHON" "$TOCK" -C "$case8" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "sub dir/weird (x).py" "spaces and parens in paths"

# --- Case 9: docs-only dirty tree is CLEAN ---
echo "======== 9. docs-only CLEAN ========"
case9="$BASE/docs"
git_init "$case9"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case9/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case9/test.py"
echo "# v1" > "$case9/README.md"
commit_all "$case9" "green"
echo "# dirty docs" > "$case9/README.md"
set +e
json9="$("$PYTHON" "$TOCK" -C "$case9" --json -- "$PYTHON" test.py)"
code9=$?
set -e
echo "$json9" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="CLEAN", d'
assert_eq "$code9" "0" "docs-only CLEAN"

# --- Case 10: 1-minimal of redundant production (A or B suffices) ---
echo "======== 10. 1-minimal of redundant locks ========"
case10="$BASE/redundant"
git_init "$case10"
cat > "$case10/app.py" <<'PY'
FLAG = False
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
VALUE = 0
PY
cat > "$case10/test.py" <<'PY'
import app
assert app.FLAG or app.VALUE == 5
print("pass")
PY
commit_all "$case10" "base"
cat > "$case10/app.py" <<'PY'
FLAG = True
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
VALUE = 5
PY
json10="$("$PYTHON" "$TOCK" -C "$case10" --json -- "$PYTHON" test.py)"
echo "$json10" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
assert len(d["wheat"])==1, d["wheat"]
assert len(d["chaff"])==1, d["chaff"]
print("ok  redundant lockset is 1-minimal (one of two hunks)")
'

# --- Case 11: working tree restored (we never touch it) ---
echo "======== 11. user tree untouched ========"
grep -q 'print("debug")' "$case1/app.py"
grep -q "hello world" "$case1/README.md"
pass "user worktree left dirty as we found it"

# --- Case 12: pycache must not poison isolation ---
echo "======== 12. pycache ========"
case12="$BASE/pycache"
git_init "$case12"
printf '%s\n' 'def add(a,b):' '    return 0' > "$case12/app.py"
printf '%s\n' 'from app import add' 'assert add(2,3)==5' 'print("pass")' > "$case12/test.py"
commit_all "$case12" "base"
printf '%s\n' 'def add(a,b):' '    return a+b' > "$case12/app.py"
got="$(env -u PYTHONDONTWRITEBYTECODE "$PYTHON" "$TOCK" -C "$case12" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "app.py" "pycache leak does not hide the lockset"

# --- Case 13: empty suite is EMPTY, not BROKEN ---
echo "======== 13. EMPTY suite ≠ BROKEN ========"
case13="$BASE/empty"
git_init "$case13"
printf '%s\n' 'def add(a, b):' '    return 0' > "$case13/app.py"
echo "v1" > "$case13/README.md"
commit_all "$case13" "base"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case13/app.py"
set +e
json13="$("$PYTHON" "$TOCK" -C "$case13" --json -- "$PYTHON" -m unittest discover -q)"
code13=$?
set -e
echo "$json13" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="EMPTY", d
assert d["wheat"]==[], d
assert any(c["path"]=="app.py" for c in d["chaff"]), d
print("ok  empty suite is EMPTY, production left as chaff")
'
assert_eq "$code13" "5" "EMPTY exit 5"

# --- Case 14: test-only red suite is BROKEN, not CLEAN (beats cinch v2 skip) ---
echo "======== 14. test-only red is BROKEN, not CLEAN ========"
case14="$BASE/testonlyred"
git_init "$case14"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case14/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case14/test.py"
commit_all "$case14" "green"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 99' > "$case14/test.py"
set +e
json14="$("$PYTHON" "$TOCK" -C "$case14" --json -- "$PYTHON" test.py)"
code14=$?
set -e
echo "$json14" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="BROKEN", d
assert d["production_units"]==0, d
assert d["wheat"]==[], d
assert "test.py" in d["held_tests"], d
assert d.get("new_run") and d["new_run"]["exit_code"] != 0, d
print("ok  test-only red is BROKEN")
'
assert_eq "$code14" "3" "test-only red BROKEN exit 3"
if [[ -f "$CINCH" ]]; then
  set +e
  cjson14="$("$PYTHON" "$CINCH" -C "$case14" --json -- "$PYTHON" test.py)"
  ccode14=$?
  set -e
  echo "$cjson14" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
print("cinch test-only red status", d.get("status"), "trials", d.get("trials"))
assert d.get("status")=="CLEAN", d
'
  assert_eq "$ccode14" "0" "cinch still reports CLEAN (skipped NEW)"
  pass "tock beats cinch on test-only red (BROKEN vs CLEAN)"
fi

# --- Case 15: FAST hunk is not wheat (timeout is unknown, not fail) ---
# DESTROYER_CINCH §5: FAST=False/VALUE=0 → FAST=True/VALUE=1.
# Tests sleep unless FAST, then assert VALUE==1. Tight --timeout.
# cinch/snug map timeout→fail so BOTH hunks are wheat.
# tock: VALUE is the assertion lock; FAST is speed chaff.
echo "======== 15. FAST hunk must not become wheat under timeout ========"
case15="$BASE/fast"
git_init "$case15"
cat > "$case15/app.py" <<'PY'
FAST = False
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
VALUE = 0
PY
cat > "$case15/test.py" <<'PY'
import app, time
if not app.FAST:
    time.sleep(1.5)
assert app.VALUE == 1
print("pass")
PY
commit_all "$case15" "base"
cat > "$case15/app.py" <<'PY'
FAST = True
# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
VALUE = 1
PY
json15="$("$PYTHON" "$TOCK" -C "$case15" --timeout 0.4 --json -- "$PYTHON" test.py)"
echo "$json15" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
wheat=d["wheat"]
chaff=d["chaff"]
assert len(wheat)==1, wheat
assert wheat[0]["path"]=="app.py" and wheat[0].get("hunk")==2, wheat
assert any(c.get("hunk")==1 for c in chaff), chaff
assert d.get("splice_run",{}).get("timed_out"), d.get("splice_run")
print("wheat", [w["id"] for w in wheat])
print("chaff", [c["id"] for c in chaff])
print("ok  FAST is chaff; VALUE is wheat")
'
if [[ -f "$SNUG" ]]; then
  sjson15="$("$PYTHON" "$SNUG" -C "$case15" --timeout 0.4 --json -- "$PYTHON" test.py)"
  echo "$sjson15" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
ids=[w["id"] for w in d.get("wheat") or []]
print("snug FAST-fixture wheat", ids, "status", d.get("status"))
assert d.get("status")=="LOCKED", d
assert len(ids)==2, ids
assert any(i.endswith("#1") for i in ids), ids
'
  pass "snug mints FAST as wheat (timeout-as-fail); tock does not"
fi
if [[ -f "$CINCH" ]]; then
  cjson15="$("$PYTHON" "$CINCH" -C "$case15" --timeout 0.4 --json -- "$PYTHON" test.py)"
  echo "$cjson15" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
ids=[w["id"] for w in d.get("wheat") or []]
print("cinch FAST-fixture wheat", ids, "status", d.get("status"))
assert d.get("status")=="LOCKED", d
assert len(ids)==2, ids
'
  pass "cinch mints FAST as wheat; tock keeps VALUE only"
fi
pass "FAST hunk that would have been wheat under timeout is chaff"

# --- Case 16: only FAST — timeout is TIMEOUT, wheat empty ---
echo "======== 16. only-FAST splice timeout is TIMEOUT, not wheat ========"
case16="$BASE/onlyfast"
git_init "$case16"
printf '%s\n' 'FAST = False' > "$case16/app.py"
cat > "$case16/test.py" <<'PY'
import app, time
if not app.FAST:
    time.sleep(1.5)
print("pass")
PY
commit_all "$case16" "base"
printf '%s\n' 'FAST = True' > "$case16/app.py"
set +e
json16="$("$PYTHON" "$TOCK" -C "$case16" --timeout 0.4 --json -- "$PYTHON" test.py)"
code16=$?
set -e
echo "$json16" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="TIMEOUT", d
assert d["wheat"]==[], d
assert d.get("splice_run",{}).get("timed_out"), d
print("ok  only-FAST is TIMEOUT with empty wheat")
'
assert_eq "$code16" "6" "TIMEOUT exit 6"
if [[ -f "$SNUG" ]]; then
  sjson16="$("$PYTHON" "$SNUG" -C "$case16" --timeout 0.4 --json -- "$PYTHON" test.py)"
  echo "$sjson16" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
ids=[w["id"] for w in d.get("wheat") or []]
print("snug only-FAST wheat", ids, "status", d.get("status"))
assert d.get("status")=="LOCKED" and ids, d
'
  pass "snug locks only-FAST; tock reports TIMEOUT (no wheat)"
fi

# --- Case 17: NEW timeout is still BROKEN ---
echo "======== 17. NEW timeout is BROKEN, not TIMEOUT ========"
case17="$BASE/newto"
git_init "$case17"
printf '%s\n' 'VALUE = 0' > "$case17/app.py"
cat > "$case17/test.py" <<'PY'
import time
time.sleep(1.5)
assert True
PY
commit_all "$case17" "base"
printf '%s\n' 'VALUE = 1' > "$case17/app.py"
set +e
json17="$("$PYTHON" "$TOCK" -C "$case17" --timeout 0.4 --json -- "$PYTHON" test.py)"
code17=$?
set -e
echo "$json17" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="BROKEN", d
assert d["wheat"]==[], d
assert d.get("new_run",{}).get("timed_out"), d
print("ok  NEW timeout is BROKEN")
'
assert_eq "$code17" "3" "NEW timeout BROKEN exit 3"

echo
echo "======== demo OK ========"
exit 0
