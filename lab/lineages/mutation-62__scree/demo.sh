#!/usr/bin/env bash
# Exercise scree against synthetic git repos and, when present, cinch/tock.
# Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SCREE="$ROOT/scree.py"
PYTHON="${PYTHON:-python3}"
BASE="${TMPDIR:-/tmp}/scree-demo-$$"
CINCH="${CINCH:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27/cinch.py}"
TOCK="${TOCK:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b70-5374-7cb0-9db0-c86bf9cbd218/tock.py}"
trap 'rm -rf "$BASE"' EXIT

chmod +x "$ROOT/scree" "$SCREE" 2>/dev/null || true
mkdir -p "$BASE"

git_init() {
  local dir="$1"
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" config user.email "scree@example.com"
  git -C "$dir" config user.name "scree"
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

# --- Case 1: invert of the founding split ---
# HEAD add returns 0. WIP: debug print + real return + new tests + README.
# cinch wheat is the return. scree unlocked is the print.
echo "======== 1. unlocked is debug print; return stays locked ========"
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

json1="$("$PYTHON" "$SCREE" -C "$case1" --json -- "$PYTHON" test.py)"
echo "$json1" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="SLACK", d
unlocked=d["unlocked"]
locked=d["locked"]
assert len(unlocked)==1 and unlocked[0]["path"]=="app.py", unlocked
assert unlocked[0].get("hunk")==1, unlocked
assert len(locked)==1 and locked[0].get("hunk")==2, locked
assert "test.py" in d["held_tests"], d
assert "README.md" in d["ignored"], d
print("unlocked", [u["id"] for u in unlocked])
print("locked", [u["id"] for u in locked])
'
patch1="$("$PYTHON" "$SCREE" -C "$case1" --format patch -- "$PYTHON" test.py)"
echo "$patch1" | grep -q 'print("debug")'
if echo "$patch1" | grep -q "return a + b"; then
  echo "FAIL unlocked patch included locked return" >&2
  echo "$patch1" >&2
  exit 1
fi
pass "unlocked patch is the debug print, not the return"

if [[ -f "$CINCH" ]]; then
  echo "======== 1b. cinch contrast (wheat is the complement) ========"
  cjson="$("$PYTHON" "$CINCH" -C "$case1" --json -- "$PYTHON" test.py)"
  "$PYTHON" -c '
import json,sys
s=json.loads(sys.argv[1])
c=json.loads(sys.argv[2])
print("scree unlocked", [u["id"] for u in s["unlocked"]], "locked", [u["id"] for u in s["locked"]])
print("cinch wheat   ", [w["id"] for w in c["wheat"]], "chaff", [x["id"] for x in c["chaff"]])
assert [u["id"] for u in s["unlocked"]]==[x["id"] for x in c["chaff"]]
assert [u["id"] for u in s["locked"]]==[w["id"] for w in c["wheat"]]
' "$json1" "$cjson"
  cpatch="$("$PYTHON" "$CINCH" -C "$case1" --format patch -- "$PYTHON" test.py)"
  echo "$cpatch" | grep -q "return a + b"
  if echo "$cpatch" | grep -q 'print("debug")'; then
    echo "FAIL cinch wheat patch included debug print" >&2
    exit 1
  fi
  pass "scree unlocked == cinch chaff; patches are complements"
else
  echo "(cinch parent not present, skip contrast)"
fi

if [[ -f "$TOCK" ]]; then
  echo "======== 1c. tock contrast (same complement) ========"
  tjson="$("$PYTHON" "$TOCK" -C "$case1" --json -- "$PYTHON" test.py)"
  "$PYTHON" -c '
import json,sys
s=json.loads(sys.argv[1])
t=json.loads(sys.argv[2])
assert [u["id"] for u in s["unlocked"]]==[x["id"] for x in t["chaff"]]
assert [u["id"] for u in s["locked"]]==[w["id"] for w in t["wheat"]]
print("tock wheat", [w["id"] for w in t["wheat"]], "chaff", [x["id"] for x in t["chaff"]])
' "$json1" "$tjson"
  pass "scree unlocked == tock chaff on debug-print fixture"
else
  echo "(tock parent not present, skip contrast)"
fi

# --- Case 2: joint required + noise ---
echo "======== 2. joint lock; noise is unlocked ========"
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
got="$("$PYTHON" "$SCREE" -C "$case2" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "c.py" "paths are unlocked noise, not the joint lockset"

# --- Case 3: LOOSE ---
echo "======== 3. LOOSE ========"
case3="$BASE/loose"
git_init "$case3"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case3/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case3/test.py"
commit_all "$case3" "green"
printf '%s\n' 'def add(a, b):' '    # definitely correct' '    return a + b' > "$case3/app.py"
set +e
json3="$("$PYTHON" "$SCREE" -C "$case3" --json -- "$PYTHON" test.py)"
code3=$?
set -e
echo "$json3" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="LOOSE" and d["locked"]==[] and d["unlocked"], d'
assert_eq "$code3" "2" "LOOSE exit 2"

# --- Case 4: CLEAN ---
echo "======== 4. CLEAN ========"
case4="$BASE/clean"
git_init "$case4"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case4/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case4/test.py"
commit_all "$case4" "green"
echo '# extra note' >> "$case4/test.py"
set +e
json4="$("$PYTHON" "$SCREE" -C "$case4" --json -- "$PYTHON" test.py)"
code4=$?
set -e
echo "$json4" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="CLEAN" and d["production_units"]==0, d
assert d.get("trials",0)>=1, d
'
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
json5="$("$PYTHON" "$SCREE" -C "$case5" --json -- "$PYTHON" test.py)"
code5=$?
set -e
echo "$json5" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="BROKEN" and d["unlocked"]==[], d'
assert_eq "$code5" "3" "BROKEN exit 3"

# --- Case 6: hunk split ---
echo "======== 6. hunk split: header comment is unlocked ========"
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
json6="$("$PYTHON" "$SCREE" -C "$case6" --json -- "$PYTHON" test.py)"
echo "$json6" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="SLACK", d
assert len(d["unlocked"])==1 and d["unlocked"][0].get("hunk")==1, d["unlocked"]
assert len(d["locked"])==1, d["locked"]
print("ok  header comment is unlocked; return is locked")
'

# --- Case 7: all-required is TIGHT ---
echo "======== 7. new symbol is TIGHT (nothing unlocked) ========"
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
set +e
json7="$("$PYTHON" "$SCREE" -C "$case7" --json -- "$PYTHON" test.py)"
code7=$?
set -e
echo "$json7" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="TIGHT", d
assert d["unlocked"]==[], d
assert d["locked"], d
print("ok  new symbol is locked; unlocked empty")
'
assert_eq "$code7" "1" "TIGHT exit 1"

# --- Case 8: ugly paths ---
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
got="$("$PYTHON" "$SCREE" -C "$case8" --format paths -- "$PYTHON" test.py)"
assert_eq "$got" "ok.py" "unlocked path is the unused file, including when the lock has spaces"

# --- Case 9: docs-only CLEAN ---
echo "======== 9. docs-only CLEAN ========"
case9="$BASE/docs"
git_init "$case9"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case9/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case9/test.py"
echo "# v1" > "$case9/README.md"
commit_all "$case9" "green"
echo "# dirty docs" > "$case9/README.md"
set +e
json9="$("$PYTHON" "$SCREE" -C "$case9" --json -- "$PYTHON" test.py)"
code9=$?
set -e
echo "$json9" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="CLEAN", d'
assert_eq "$code9" "0" "docs-only CLEAN"

# --- Case 10: redundant — largest unlocked is one hunk ---
echo "======== 10. redundant: largest unlocked has size 1 ========"
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
json10="$("$PYTHON" "$SCREE" -C "$case10" --json -- "$PYTHON" test.py)"
echo "$json10" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="SLACK", d
assert len(d["unlocked"])==1, d["unlocked"]
assert len(d["locked"])==1, d["locked"]
print("ok  redundant: one unlocked, one locked")
'

# --- Case 11: user tree untouched ---
echo "======== 11. user tree untouched ========"
grep -q 'print("debug")' "$case1/app.py"
grep -q "hello world" "$case1/README.md"
pass "user worktree left dirty as we found it"

# --- Case 12: empty suite is EMPTY, unlocked empty ---
echo "======== 12. EMPTY suite is not a giant unlocked set ========"
case12="$BASE/empty"
git_init "$case12"
printf '%s\n' 'def add(a, b):' '    return 0' > "$case12/app.py"
echo "v1" > "$case12/README.md"
commit_all "$case12" "base"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case12/app.py"
set +e
json12="$("$PYTHON" "$SCREE" -C "$case12" --json -- "$PYTHON" -m unittest discover -q)"
code12=$?
set -e
echo "$json12" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="EMPTY", d
assert d["unlocked"]==[], d
assert d["production_units"]>=1, d
print("ok  empty suite unlocked=[] (not the dirty production)")
'
assert_eq "$code12" "5" "EMPTY exit 5"

# --- Case 13: test-only red ---
echo "======== 13. test-only red is BROKEN ========"
case13="$BASE/test-only-red"
git_init "$case13"
printf '%s\n' 'def add(a, b):' '    return a + b' > "$case13/app.py"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 5' > "$case13/test.py"
commit_all "$case13" "green"
printf '%s\n' 'from app import add' 'assert add(2, 3) == 99' > "$case13/test.py"
set +e
json13="$("$PYTHON" "$SCREE" -C "$case13" --json -- "$PYTHON" test.py)"
code13=$?
set -e
echo "$json13" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="BROKEN", d
assert d["unlocked"]==[], d
assert d.get("trials",0)>=1, d
assert "test.py" in d["held_tests"], d
print("ok  test-only red ran NEW and is BROKEN")
'
assert_eq "$code13" "3" "test-only red BROKEN exit 3"

# --- Case 14: FAST+VALUE (v0.2: timeout is unknown, not unlocked) ---
echo "======== 14. FAST+VALUE timeout: FAST is neither locked nor unlocked ========"
case14="$BASE/timeout-lock"
git_init "$case14"
cat > "$case14/app.py" <<'PY'
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
cat > "$case14/test.py" <<'PY'
import app, time
if not app.FAST:
    time.sleep(1.5)
assert app.VALUE == 1
print("pass")
PY
commit_all "$case14" "base"
cat > "$case14/app.py" <<'PY'
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
set +e
json14="$("$PYTHON" "$SCREE" -C "$case14" --json --timeout 0.4 -- "$PYTHON" test.py)"
code14=$?
set -e
echo "$json14" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
ids_u=[u["id"] for u in d["unlocked"]]
ids_k=[u["id"] for u in d["locked"]]
ids_n=[u["id"] for u in d.get("unknown") or []]
print("status", d["status"], "unlocked", ids_u, "locked", ids_k, "unknown", ids_n)
assert d["status"]=="TIGHT", d
assert ids_u==[], d
assert "app.py#2" in ids_k, d
assert "app.py#1" in ids_n, d
assert "app.py#1" not in ids_k and "app.py#1" not in ids_u, d
assert d.get("splice_run",{}).get("timed_out"), d.get("splice_run")
print("ok  FAST is unknown; VALUE is locked; unlocked empty")
'
assert_eq "$code14" "1" "FAST+VALUE TIGHT exit 1 (nothing observed-unlocked)"
set +e
patch14="$("$PYTHON" "$SCREE" -C "$case14" --format patch --timeout 0.4 -- "$PYTHON" test.py)"
set -e
if echo "$patch14" | grep -q "FAST = True"; then
  echo "FAIL unlocked patch included FAST speed hunk" >&2
  echo "$patch14" >&2
  exit 1
fi
if echo "$patch14" | grep -q "VALUE = 1"; then
  echo "FAIL unlocked patch included locked VALUE" >&2
  echo "$patch14" >&2
  exit 1
fi
pass "unlocked patch is empty of FAST and VALUE"

# --- Case 15: NEW timeout BROKEN ---
echo "======== 15. NEW timeout is BROKEN ========"
case15="$BASE/new-timeout"
git_init "$case15"
printf '%s\n' 'VALUE = 0' > "$case15/app.py"
printf '%s\n' 'import time' 'time.sleep(8)' 'assert True' > "$case15/test.py"
commit_all "$case15" "base"
printf '%s\n' 'VALUE = 1' > "$case15/app.py"
set +e
json15="$("$PYTHON" "$SCREE" -C "$case15" --json --timeout 0.3 -- "$PYTHON" test.py)"
code15=$?
set -e
echo "$json15" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="BROKEN", d
assert d.get("new_run",{}).get("timed_out"), d.get("new_run")
assert d["unlocked"]==[], d
print("ok  NEW timeout refused as BROKEN")
'
assert_eq "$code15" "3" "NEW timeout BROKEN exit 3"

# --- Case 16: timeout 0 ---
echo "======== 16. timeout 0 is usage error ========"
case16="$BASE/timeout-zero"
git_init "$case16"
printf '%s\n' 'VALUE = 0' > "$case16/app.py"
printf '%s\n' 'assert True' > "$case16/test.py"
commit_all "$case16" "base"
printf '%s\n' 'VALUE = 1' > "$case16/app.py"
set +e
err16="$("$PYTHON" "$SCREE" -C "$case16" --json --timeout 0 -- "$PYTHON" test.py 2>&1)"
code16=$?
set -e
echo "$err16" | grep -q "timeout must be > 0"
assert_eq "$code16" "2" "timeout 0 exit 2"

# --- Case 17: only-FAST is TIMEOUT, not slack ---
echo "======== 17. only-FAST timeout is TIMEOUT, not unlocked ========"
case17="$BASE/speed-only"
git_init "$case17"
printf '%s\n' 'FAST = False' > "$case17/app.py"
cat > "$case17/test.py" <<'PY'
import app, time
if not app.FAST:
    time.sleep(1.5)
assert True
PY
commit_all "$case17" "base"
printf '%s\n' 'FAST = True' > "$case17/app.py"
set +e
json17="$("$PYTHON" "$SCREE" -C "$case17" --json --timeout 0.4 -- "$PYTHON" test.py)"
code17=$?
set -e
echo "$json17" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
ids_u=[u["id"] for u in d["unlocked"]]
ids_n=[u["id"] for u in d.get("unknown") or []]
assert d["status"]=="TIMEOUT", d
assert ids_u==[], d
assert "app.py#1" in ids_n, d
assert d.get("splice_run",{}).get("timed_out"), d.get("splice_run")
print("ok  only-FAST is unknown; unlocked empty; TIMEOUT")
'
assert_eq "$code17" "6" "only-FAST TIMEOUT exit 6"

if [[ -f "$TOCK" ]]; then
  echo "======== 17b. tock contrast on FAST+VALUE ========"
  tjson="$("$PYTHON" "$TOCK" -C "$case14" --json --timeout 0.4 -- "$PYTHON" test.py)"
  "$PYTHON" -c '
import json,sys
s=json.loads(sys.argv[1])
t=json.loads(sys.argv[2])
print("scree unlocked", [u["id"] for u in s["unlocked"]], "unknown", [u["id"] for u in s["unknown"]], "locked", [u["id"] for u in s["locked"]])
print("tock  wheat   ", [w["id"] for w in t["wheat"]], "chaff", [x["id"] for x in t["chaff"]])
# tock wheat is VALUE (same as our locked). tock chaff is FAST (our unknown — we refuse to call it unlocked).
assert [w["id"] for w in t["wheat"]]==[u["id"] for u in s["locked"]]
assert [x["id"] for x in t["chaff"]]==[u["id"] for u in s["unknown"]]
assert s["unlocked"]==[]
' "$json14" "$tjson"
  pass "tock chaffs FAST; scree keeps FAST unknown (not unlocked)"
fi

if [[ -f "$CINCH" ]]; then
  echo "======== 17c. cinch 0.3 contrast on FAST+VALUE ========"
  cjson="$("$PYTHON" "$CINCH" -C "$case14" --json --timeout 0.4 -- "$PYTHON" test.py)"
  "$PYTHON" -c '
import json,sys
s=json.loads(sys.argv[1])
c=json.loads(sys.argv[2])
print("scree locked", [u["id"] for u in s["locked"]], "unknown", [u["id"] for u in s["unknown"]])
print("cinch wheat ", [w["id"] for w in c["wheat"]], "budget", [b["id"] for b in c.get("budget") or []])
assert [w["id"] for w in c["wheat"]]==[u["id"] for u in s["locked"]]
assert [b["id"] for b in c.get("budget") or []]==[u["id"] for u in s["unknown"]]
assert s["unlocked"]==[]
' "$json14" "$cjson"
  pass "cinch budget == scree unknown; neither mints FAST as slack"
fi

echo
echo "======== demo OK ========"
exit 0
