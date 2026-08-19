#!/usr/bin/env bash
# Exercise hasp against synthetic git ranges and, when present, parent tools.
# Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
HASP="$ROOT/hasp.py"
PYTHON="${PYTHON:-python3}"
BASE="${TMPDIR:-/tmp}/hasp-demo-$$"
CINCH="${CINCH:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-03-cinch/cinch.py}"
ALIBI="${ALIBI:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01abb-4faf-7c02-a6f1-67838af12a62/alibi.py}"
trap 'rm -rf "$BASE"' EXIT

chmod +x "$ROOT/hasp" "$HASP" 2>/dev/null || true
mkdir -p "$BASE"

git_init() {
  local dir="$1"
  mkdir -p "$dir"
  git -C "$dir" init -q -b main
  git -C "$dir" config user.email "hasp@example.com"
  git -C "$dir" config user.name "hasp"
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

write_app_base() {
  cat > "$1/app.py" <<'PY'
def add(a, b):
    return 0


# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
def extra():
    return 0


# pad9
# pad10
# pad11
# pad12
# pad13
# pad14
# pad15
# pad16
DEBUG = False
PY
}

write_app_pr() {
  cat > "$1/app.py" <<'PY'
def add(a, b):
    return a + b


# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
def extra():
    return 1


# pad9
# pad10
# pad11
# pad12
# pad13
# pad14
# pad15
# pad16
DEBUG = True
PY
}

write_test_base() {
  mkdir -p "$1/tests"
  : > "$1/tests/__init__.py"
  cat > "$1/tests/test_app.py" <<'PY'
import unittest
from app import extra


class TestApp(unittest.TestCase):
    def test_extra(self):
        self.assertEqual(extra(), 0)
PY
}

write_test_pr() {
  mkdir -p "$1/tests"
  : > "$1/tests/__init__.py"
  cat > "$1/tests/test_app.py" <<'PY'
import unittest
from app import add, extra


class TestApp(unittest.TestCase):
    def test_extra(self):
        self.assertEqual(extra(), 1)

    def test_add(self):
        self.assertEqual(add(2, 3), 5)
PY
}

make_pr() {
  local dir="$1"
  git_init "$dir"
  write_app_base "$dir"
  write_test_base "$dir"
  echo "v1" > "$dir/README.md"
  commit_all "$dir" "main"
  git -C "$dir" checkout -q -b pr
  write_app_pr "$dir"
  write_test_pr "$dir"
  echo "v2" > "$dir/README.md"
  commit_all "$dir" "feature"
}

echo "======== 0. unit tests ========"
"$PYTHON" -m unittest discover -s "$ROOT/tests" -q
pass "unit tests"

# --- Case 1: the object ---
# Committed PR, clean worktree. New test_add locks add(); extra() and DEBUG
# are chaff even though test_extra was updated to require extra()==1.
echo "======== 1. new tests lock; updated old tests do not ========"
case1="$BASE/pr"
make_pr "$case1"
[[ -z "$(git -C "$case1" status --porcelain)" ]] || { echo "FAIL worktree dirty" >&2; exit 1; }

json1="$("$PYTHON" "$HASP" -C "$case1" --json main...HEAD)"
echo "$json1" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
new=[t["id"] for t in d["new_tests"]]
bg=[t["id"] for t in d["background_tests"]]
assert new==["TestApp.test_add"], new
assert "TestApp.test_extra" in bg, bg
wheat=" ".join(" ".join(w.get("added") or []) for w in d["wheat"])
chaff=" ".join(" ".join(c.get("added") or []) for c in d["chaff"])
assert "return a + b" in wheat, d["wheat"]
assert "return 1" not in wheat, d["wheat"]
assert "DEBUG = True" not in wheat, d["wheat"]
assert "return 1" in chaff and "DEBUG = True" in chaff, d["chaff"]
assert len(d["wheat"])==1, d["wheat"]
print("wheat", [w["id"] for w in d["wheat"]])
print("chaff", [c["id"] for c in d["chaff"]])
'
pass "new test_add locks add(); extra()+DEBUG are chaff"

# HEAD vs worktree on a clean PR is CLEAN — the object is the range.
set +e
json1b="$("$PYTHON" "$HASP" -C "$case1" --json)"
code1b=$?
set -e
echo "$json1b" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="CLEAN" and d["production_units"]==0, d'
assert_eq "$code1b" "0" "committed PR vs HEAD is CLEAN; range is required"

# Parent contrast: cinch holds ALL tests at NEW, so extra() is wheat.
if [[ -f "$CINCH" ]]; then
  echo "======== 1b. cinch contrast (whole suite is the lock) ========"
  cjson="$("$PYTHON" "$CINCH" -C "$case1" --base main --json -- "$PYTHON" -m unittest discover -s tests -q)"
  echo "$cjson" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
added=" ".join(" ".join(w.get("added") or w.get("header") or "" if False else (w.get("added") or [])) for w in d["wheat"])
# cinch JSON may not include added lines; fall back to wheat count / headers
wheat=d["wheat"]
assert len(wheat)>=2, wheat
print("cinch wheat", [(w["id"], w.get("header")) for w in wheat])
'
  pass "cinch wheat has >=2 production units (old test_extra keeps extra())"
else
  echo "(cinch parent not present, skip contrast)"
fi

if [[ -f "$ALIBI" ]]; then
  echo "======== 1c. alibi contrast (binary LOCKED, whole production) ========"
  set +e
  ajson="$("$PYTHON" "$ALIBI" -C "$case1" main --json --cmd "$PYTHON -m unittest discover -s tests -q" 2>/dev/null)"
  set -e
  echo "$ajson" | "$PYTHON" -c '
import json,sys
raw=sys.stdin.read()
d=json.loads(raw)
print("alibi status", d.get("status"), "prod", d.get("production_changed"))
assert d.get("status")=="LOCKED", d
'
  pass "alibi LOCKED on the whole production diff; hasp splits hunks"
else
  echo "(alibi parent not present, skip contrast)"
fi

# --- Case 2: MUTE — production + updated old tests, no new test names ---
echo "======== 2. MUTE: production with no new tests ========"
case2="$BASE/mute"
git_init "$case2"
write_app_base "$case2"
write_test_base "$case2"
commit_all "$case2" "main"
git -C "$case2" checkout -q -b pr
write_app_pr "$case2"
cat > "$case2/tests/test_app.py" <<'PY'
import unittest
from app import extra


class TestApp(unittest.TestCase):
    def test_extra(self):
        self.assertEqual(extra(), 1)
PY
commit_all "$case2" "no new tests"
set +e
json2="$("$PYTHON" "$HASP" -C "$case2" --json main...HEAD)"
code2=$?
set -e
echo "$json2" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="MUTE", d
assert d["new_tests"]==[], d
assert d["wheat"]==[], d
assert d["production_units"]>=1, d
assert any("test_extra" in t["id"] for t in d["background_tests"]), d
'
assert_eq "$code2" "6" "MUTE exit 6"

# cinch on the same tree LOCKS extra() because the updated old test requires it
if [[ -f "$CINCH" ]]; then
  cjson2="$("$PYTHON" "$CINCH" -C "$case2" --base main --json -- "$PYTHON" -m unittest discover -s tests -q)"
  echo "$cjson2" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
assert d["wheat"], d
print("cinch mute-contrast wheat", [w["id"] for w in d["wheat"]])
'
  pass "cinch LOCKED the MUTE tree; hasp refuses to use old tests as the lock"
fi

# --- Case 3: LOOSE new test already true on old production ---
echo "======== 3. LOOSE ========"
case3="$BASE/loose"
git_init "$case3"
cat > "$case3/app.py" <<'PY'
def add(a, b):
    return a + b
PY
mkdir -p "$case3/tests"
: > "$case3/tests/__init__.py"
cat > "$case3/tests/test_app.py" <<'PY'
import unittest
from app import add
class TestApp(unittest.TestCase):
    def test_old(self):
        self.assertEqual(add(2, 3), 5)
PY
commit_all "$case3" "green"
git -C "$case3" checkout -q -b pr
cat > "$case3/app.py" <<'PY'
def add(a, b):
    # comment
    return a + b
PY
cat > "$case3/tests/test_app.py" <<'PY'
import unittest
from app import add
class TestApp(unittest.TestCase):
    def test_old(self):
        self.assertEqual(add(2, 3), 5)
    def test_new(self):
        self.assertEqual(add(1, 1), 2)
PY
commit_all "$case3" "comment + new test"
set +e
json3="$("$PYTHON" "$HASP" -C "$case3" --json main...HEAD)"
code3=$?
set -e
echo "$json3" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="LOOSE" and d["wheat"]==[], d'
assert_eq "$code3" "2" "LOOSE exit 2"

# --- Case 4: CLEAN test-only PR ---
echo "======== 4. CLEAN test-only range ========"
case4="$BASE/clean"
git_init "$case4"
cat > "$case4/app.py" <<'PY'
def add(a, b):
    return a + b
PY
mkdir -p "$case4/tests"
: > "$case4/tests/__init__.py"
cat > "$case4/tests/test_app.py" <<'PY'
import unittest
from app import add
class TestApp(unittest.TestCase):
    def test_old(self):
        self.assertEqual(add(2, 3), 5)
PY
commit_all "$case4" "green"
git -C "$case4" checkout -q -b pr
cat > "$case4/tests/test_app.py" <<'PY'
import unittest
from app import add
class TestApp(unittest.TestCase):
    def test_old(self):
        self.assertEqual(add(2, 3), 5)
    def test_new(self):
        self.assertEqual(add(0, 0), 0)
PY
commit_all "$case4" "tests only"
set +e
json4="$("$PYTHON" "$HASP" -C "$case4" --json main...HEAD)"
code4=$?
set -e
echo "$json4" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="CLEAN", d'
assert_eq "$code4" "0" "CLEAN exit 0"

# --- Case 5: BROKEN new test ---
echo "======== 5. BROKEN ========"
case5="$BASE/broken"
git_init "$case5"
cat > "$case5/app.py" <<'PY'
def add(a, b):
    return a + b
PY
mkdir -p "$case5/tests"
: > "$case5/tests/__init__.py"
cat > "$case5/tests/test_app.py" <<'PY'
import unittest
from app import add
class TestApp(unittest.TestCase):
    def test_old(self):
        self.assertEqual(add(2, 3), 5)
PY
commit_all "$case5" "green"
git -C "$case5" checkout -q -b pr
cat > "$case5/app.py" <<'PY'
def add(a, b):
    return a + b
def mul(a, b):
    return 0
PY
cat > "$case5/tests/test_app.py" <<'PY'
import unittest
from app import add, mul
class TestApp(unittest.TestCase):
    def test_old(self):
        self.assertEqual(add(2, 3), 5)
    def test_mul(self):
        self.assertEqual(mul(2, 3), 6)
PY
commit_all "$case5" "wrong mul"
set +e
json5="$("$PYTHON" "$HASP" -C "$case5" --json main...HEAD)"
code5=$?
set -e
echo "$json5" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="BROKEN", d'
assert_eq "$code5" "3" "BROKEN exit 3"

# --- Case 6: two-dot vs three-dot: extra commit on main is not in the PR ---
echo "======== 6. three-dot PR range ignores later main ========"
case6="$BASE/threedot"
git_init "$case6"
write_app_base "$case6"
write_test_base "$case6"
commit_all "$case6" "main"
git -C "$case6" checkout -q -b pr
write_app_pr "$case6"
write_test_pr "$case6"
commit_all "$case6" "feature"
git -C "$case6" checkout -q main
# later main commit that the PR does not contain
cat > "$case6/app.py" <<'PY'
def add(a, b):
    return 0


# pad1
# pad2
# pad3
# pad4
# pad5
# pad6
# pad7
# pad8
def extra():
    return 0


# pad9
# pad10
# pad11
# pad12
# pad13
# pad14
# pad15
# pad16
DEBUG = False
SIDE = "main-only"
PY
commit_all "$case6" "main moved"
git -C "$case6" checkout -q pr
json6="$("$PYTHON" "$HASP" -C "$case6" --json --list main...HEAD)"
echo "$json6" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
added=" ".join(" ".join(u.get("added") or []) for u in d["units"] if u["role"]=="production")
assert "SIDE" not in added, d
assert "return a + b" in added, d
print("ok  three-dot list does not include main-only SIDE")
'
# two-dot against main tip would include a revert of SIDE or a confusing diff
pass "three-dot range is the PR, not main..HEAD"

# --- Case 7: joint wheat of two files, both required by the new test ---
echo "======== 7. joint wheat ========"
case7="$BASE/joint"
git_init "$case7"
echo 'KEY = "a"' > "$case7/a.py"
echo 'KEY = "b"' > "$case7/b.py"
echo 'noise = 1' > "$case7/c.py"
mkdir -p "$case7/tests"
: > "$case7/tests/__init__.py"
cat > "$case7/tests/test_app.py" <<'PY'
import unittest
class TestApp(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
PY
commit_all "$case7" "base"
git -C "$case7" checkout -q -b pr
echo 'KEY = "AX"' > "$case7/a.py"
echo 'KEY = "BX"' > "$case7/b.py"
echo 'noise = 2' > "$case7/c.py"
cat > "$case7/tests/test_app.py" <<'PY'
import unittest
import a, b
class TestApp(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
    def test_keys(self):
        self.assertEqual(a.KEY, "AX")
        self.assertEqual(b.KEY, "BX")
PY
commit_all "$case7" "keys"
got="$("$PYTHON" "$HASP" -C "$case7" --format paths main...HEAD)"
assert_eq "$got" $'a.py\nb.py' "joint lockset keeps both required files"

# --- Case 8: ugly paths ---
echo "======== 8. ugly paths ========"
case8="$BASE/ugly"
git_init "$case8"
mkdir -p "$case8/sub dir"
echo 'VAL = 1' > "$case8/sub dir/weird (x).py"
echo 'other = 1' > "$case8/ok.py"
mkdir -p "$case8/tests"
: > "$case8/tests/__init__.py"
cat > "$case8/tests/test_app.py" <<'PY'
import unittest
class TestApp(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
PY
commit_all "$case8" "base"
git -C "$case8" checkout -q -b pr
echo 'VAL = 2' > "$case8/sub dir/weird (x).py"
echo 'other = 2' > "$case8/ok.py"
cat > "$case8/tests/test_app.py" <<'PY'
import importlib.util, pathlib, unittest
class TestApp(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
    def test_weird(self):
        p = pathlib.Path(__file__).resolve().parents[1] / "sub dir" / "weird (x).py"
        spec = importlib.util.spec_from_file_location("weird", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual(m.VAL, 2)
PY
commit_all "$case8" "weird"
got="$("$PYTHON" "$HASP" -C "$case8" --format paths main...HEAD)"
assert_eq "$got" "sub dir/weird (x).py" "spaces and parens in paths"

# --- Case 9: docs-only is CLEAN ---
echo "======== 9. docs-only CLEAN ========"
case9="$BASE/docs"
git_init "$case9"
write_app_base "$case9"
write_test_base "$case9"
echo "v1" > "$case9/README.md"
commit_all "$case9" "green"
git -C "$case9" checkout -q -b pr
echo "dirty docs" > "$case9/README.md"
commit_all "$case9" "docs"
set +e
json9="$("$PYTHON" "$HASP" -C "$case9" --json main...HEAD)"
code9=$?
set -e
echo "$json9" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="CLEAN", d'
assert_eq "$code9" "0" "docs-only CLEAN"

# --- Case 10: 1-minimal of redundant production ---
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
mkdir -p "$case10/tests"
: > "$case10/tests/__init__.py"
cat > "$case10/tests/test_app.py" <<'PY'
import unittest
import app
class TestApp(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
PY
commit_all "$case10" "base"
git -C "$case10" checkout -q -b pr
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
cat > "$case10/tests/test_app.py" <<'PY'
import unittest
import app
class TestApp(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
    def test_either(self):
        self.assertTrue(app.FLAG or app.VALUE == 5)
PY
commit_all "$case10" "both"
json10="$("$PYTHON" "$HASP" -C "$case10" --json main...HEAD)"
echo "$json10" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
assert len(d["wheat"])==1, d["wheat"]
assert len(d["chaff"])==1, d["chaff"]
print("ok  redundant lockset is 1-minimal")
'

# --- Case 11: user tree untouched ---
echo "======== 11. user tree untouched ========"
grep -q "return a + b" "$case1/app.py"
grep -q "v2" "$case1/README.md"
pass "user worktree left as we found it"

# --- Case 12: --format patch is wheat only ---
echo "======== 12. patch is the lockset ========"
patch12="$("$PYTHON" "$HASP" -C "$case1" --format patch main...HEAD)"
echo "$patch12" | grep -q "return a + b"
if echo "$patch12" | grep -q "DEBUG = True"; then
  echo "FAIL patch included DEBUG chaff" >&2
  echo "$patch12" >&2
  exit 1
fi
if echo "$patch12" | grep -q "return 1"; then
  echo "FAIL patch included extra() chaff" >&2
  echo "$patch12" >&2
  exit 1
fi
pass "patch contains add() only"

# --- Case 13: new-file test (whole module) ---
echo "======== 13. brand-new test file ========"
case13="$BASE/newfile"
git_init "$case13"
cat > "$case13/app.py" <<'PY'
def add(a, b):
    return 0
PY
commit_all "$case13" "base"
git -C "$case13" checkout -q -b pr
cat > "$case13/app.py" <<'PY'
def add(a, b):
    return a + b
PY
mkdir -p "$case13/tests"
: > "$case13/tests/__init__.py"
cat > "$case13/tests/test_app.py" <<'PY'
from app import add
assert add(2, 3) == 5
print("pass")
PY
commit_all "$case13" "add test file"
json13="$("$PYTHON" "$HASP" -C "$case13" --json main...HEAD)"
echo "$json13" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
assert any(t["id"]=="<module>" for t in d["new_tests"]), d
assert d["wheat"], d
print("ok  new test file is the lock")
'

# --- Case 14: FOREIGN — Swift named tests are listed, not exec'd as Python ---
echo "======== 14. FOREIGN swift names, not <module> ========"
case14="$BASE/swift"
git_init "$case14"
cat > "$case14/App.swift" <<'SW'
func add(_ a: Int, _ b: Int) -> Int { 0 }
SW
commit_all "$case14" "base"
git -C "$case14" checkout -q -b pr
cat > "$case14/App.swift" <<'SW'
func add(_ a: Int, _ b: Int) -> Int { a + b }
SW
mkdir -p "$case14/Tests"
cat > "$case14/Tests/AddTests.swift" <<'SW'
import Testing
@Suite("add")
struct AddTests {
    @Test("adds two numbers")
    func addsTwoNumbers() {
        #expect(add(2, 3) == 5)
    }
    func testXCTestStyle() {
        #expect(add(1, 1) == 2)
    }
}
SW
commit_all "$case14" "swift tests"
list14="$("$PYTHON" "$HASP" -C "$case14" --list --json main...HEAD)"
echo "$list14" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
ids=[t["id"] for t in d["new_tests"]]
assert "addsTwoNumbers" in ids, ids
assert "testXCTestStyle" in ids, ids
assert "<module>" not in ids, ids
assert all(not t["path"].endswith(".json") for t in d["new_tests"])
print("swift names", ids)
'
set +e
json14="$("$PYTHON" "$HASP" -C "$case14" --json main...HEAD)"
code14=$?
set -e
echo "$json14" | "$PYTHON" -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="FOREIGN", d'
assert_eq "$code14" "7" "FOREIGN exit 7"

echo
echo "======== demo OK ========"
exit 0
