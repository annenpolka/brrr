#!/usr/bin/env bash
# Exercise mute against synthetic git ranges and, when present, parent tools.
# Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MUTE="$ROOT/mute.py"
PYTHON="${PYTHON:-python3}"
BASE="${TMPDIR:-/tmp}/mute-demo-$$"
HASP="${HASP:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-06-hasp/hasp.py}"
CINCH="${CINCH:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-03-cinch/cinch.py}"
trap 'rm -rf "$BASE"' EXIT

chmod +x "$ROOT/mute" "$MUTE" 2>/dev/null || true
mkdir -p "$BASE"

git_init() {
  local dir="$1"
  mkdir -p "$dir"
  git -C "$dir" init -q -b main
  git -C "$dir" config user.email "mute@example.com"
  git -C "$dir" config user.name "mute"
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
    x = 0

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
    print("debug")

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

# --- Case 1: required fixture — new test locks add(), not the debug print ---
echo "======== 1. new test locks add(); debug print is mute ========"
case1="$BASE/pr"
make_pr "$case1"
[[ -z "$(git -C "$case1" status --porcelain)" ]] || { echo "FAIL worktree dirty" >&2; exit 1; }

set +e
json1="$("$PYTHON" "$MUTE" -C "$case1" --json main...HEAD)"
code1=$?
set -e
echo "$json1" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="MUTE", d
assert d["reason"]=="partial", d
new=[t["id"] for t in d["new_tests"]]
assert new==["TestApp.test_add"], new
assert any("test_extra" in t["id"] for t in d["background_tests"]), d
locked=" ".join(" ".join(w.get("added") or []) for w in d["locked"])
mute=" ".join(" ".join(c.get("added") or []) for c in d["mute"])
assert "return a + b" in locked, d["locked"]
assert "print(\"debug\")" not in locked, d["locked"]
assert "print(\"debug\")" in mute, d["mute"]
assert "return a + b" not in mute, d["mute"]
assert "DEBUG = True" in mute, d["mute"]
assert "return 1" in mute, d["mute"]
print("locked", [w["id"] for w in d["locked"]])
print("mute", [c["id"] for c in d["mute"]])
'
assert_eq "$code1" "1" "unlocked production exits 1"

# Parent contrast: hasp wheat is add(); mute product is the rest.
if [[ -f "$HASP" ]]; then
  echo "======== 1b. hasp contrast (lockset is the other object) ========"
  hjson="$("$PYTHON" "$HASP" -C "$case1" --json main...HEAD)"
  echo "$hjson" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
wheat=" ".join(" ".join(w.get("added") or []) for w in d["wheat"])
chaff=" ".join(" ".join(c.get("added") or []) for c in d["chaff"])
assert "return a + b" in wheat, d["wheat"]
assert "print(\"debug\")" in chaff, d["chaff"]
print("hasp wheat", [w["id"] for w in d["wheat"]])
print("hasp chaff", [c["id"] for c in d["chaff"]])
'
  pass "hasp wheat is add(); mute is debug+extra+DEBUG"
else
  echo "(hasp parent not present, skip contrast)"
fi

if [[ -f "$CINCH" ]]; then
  echo "======== 1c. cinch contrast (whole suite is the lock) ========"
  cjson="$("$PYTHON" "$CINCH" -C "$case1" --base main --json -- "$PYTHON" -m unittest discover -s tests -q)"
  echo "$cjson" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
assert len(d["wheat"])>=2, d["wheat"]
print("cinch wheat", [w["id"] for w in d["wheat"]])
'
  pass "cinch locks extra() too because old test_extra at NEW is the lock"
fi

# --- Case 2: required fixture — production-only PR is MUTE (entire production) ---
echo "======== 2. production-only PR is MUTE ========"
case2="$BASE/prodonly"
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
json2="$("$PYTHON" "$MUTE" -C "$case2" --json main...HEAD)"
code2=$?
set -e
echo "$json2" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="MUTE", d
assert d["reason"]=="no-new-tests", d
assert d["new_tests"]==[], d
assert d["locked"]==[], d
assert len(d["mute"])==d["production_units"]>=1, d
mute=" ".join(" ".join(c.get("added") or []) for c in d["mute"])
assert "return a + b" in mute and "print(\"debug\")" in mute, d["mute"]
'
assert_eq "$code2" "1" "production-only MUTE exit 1"

# --- Case 3: required fixture — tests-only PR is empty mute ---
echo "======== 3. tests-only PR is empty mute ========"
case3="$BASE/testsonly"
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
cat > "$case3/tests/test_app.py" <<'PY'
import unittest
from app import add
class TestApp(unittest.TestCase):
    def test_old(self):
        self.assertEqual(add(2, 3), 5)
    def test_new(self):
        self.assertEqual(add(0, 0), 0)
PY
commit_all "$case3" "tests only"
set +e
json3="$("$PYTHON" "$MUTE" -C "$case3" --json main...HEAD)"
code3=$?
set -e
echo "$json3" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="CLEAN", d
assert d["mute"]==[], d
assert d["production_units"]==0, d
assert any("test_new" in t["id"] for t in d["new_tests"]), d
'
assert_eq "$code3" "0" "tests-only empty mute exit 0"

# --- Case 4: every production hunk locked → empty mute, exit 0 ---
echo "======== 4. all-locked production is empty mute ========"
case4="$BASE/alllocked"
git_init "$case4"
cat > "$case4/app.py" <<'PY'
def add(a, b):
    return 0
PY
mkdir -p "$case4/tests"
: > "$case4/tests/__init__.py"
cat > "$case4/tests/test_app.py" <<'PY'
import unittest
class T(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
PY
commit_all "$case4" "base"
git -C "$case4" checkout -q -b pr
cat > "$case4/app.py" <<'PY'
def add(a, b):
    return a + b
PY
cat > "$case4/tests/test_app.py" <<'PY'
import unittest
from app import add
class T(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
PY
commit_all "$case4" "fix"
set +e
json4="$("$PYTHON" "$MUTE" -C "$case4" --json main...HEAD)"
code4=$?
set -e
echo "$json4" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="LOCKED", d
assert d["mute"]==[], d
assert d["locked"], d
'
assert_eq "$code4" "0" "all locked empty mute exit 0"

# --- Case 5: --format patch is the mute set ---
echo "======== 5. patch is the mute set ========"
patch5="$("$PYTHON" "$MUTE" -C "$case1" --format patch main...HEAD)" || true
echo "$patch5" | grep -q 'print("debug")'
if echo "$patch5" | grep -q "return a + b"; then
  echo "FAIL patch included locked add()" >&2
  echo "$patch5" >&2
  exit 1
fi
pass "patch contains debug print, not add()"

# --- Case 6: user tree untouched ---
echo "======== 6. user tree untouched ========"
grep -q 'print("debug")' "$case1/app.py"
grep -q "v2" "$case1/README.md"
[[ -z "$(git -C "$case1" status --porcelain)" ]]
pass "user worktree left as we found it"

# --- Case 7: FOREIGN swift names, isolation refused ---
echo "======== 7. FOREIGN ========"
case7="$BASE/swift"
git_init "$case7"
cat > "$case7/App.swift" <<'SW'
func add(_ a: Int, _ b: Int) -> Int { 0 }
SW
commit_all "$case7" "base"
git -C "$case7" checkout -q -b pr
cat > "$case7/App.swift" <<'SW'
func add(_ a: Int, _ b: Int) -> Int { a + b }
SW
mkdir -p "$case7/Tests"
cat > "$case7/Tests/AddTests.swift" <<'SW'
import Testing
@Test func addsTwoNumbers() { }
SW
commit_all "$case7" "swift tests"
set +e
json7="$("$PYTHON" "$MUTE" -C "$case7" --json main...HEAD)"
code7=$?
set -e
echo "$json7" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="FOREIGN", d
assert d["mute"]==[], d
ids=[t["id"] for t in d["new_tests"]]
assert "addsTwoNumbers" in ids, ids
'
assert_eq "$code7" "2" "FOREIGN exit 2"

# --- Case 8: paths format lists mute paths ---
echo "======== 8. --format paths ========"
paths8="$("$PYTHON" "$MUTE" -C "$case1" --format paths main...HEAD)" || true
assert_eq "$paths8" "app.py" "mute paths are unlocked production files"

# --- Case 9: v2 dogfood — extensionless shebang is production, and mute ---
echo "======== 9. shebang wrapper is mute, not ignored ========"
case9="$BASE/shebang"
git_init "$case9"
cat > "$case9/app.py" <<'PY'
def add(a, b):
    return 0
PY
mkdir -p "$case9/tests"
: > "$case9/tests/__init__.py"
cat > "$case9/tests/test_app.py" <<'PY'
import unittest
class T(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
PY
commit_all "$case9" "base"
git -C "$case9" checkout -q -b pr
cat > "$case9/app.py" <<'PY'
def add(a, b):
    return a + b
PY
printf '%s\n' '#!/usr/bin/env bash' 'exec python3 app.py "$@"' > "$case9/tool"
cat > "$case9/tests/test_app.py" <<'PY'
import unittest
from app import add
class T(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
PY
commit_all "$case9" "fix + wrapper"
set +e
json9="$("$PYTHON" "$MUTE" -C "$case9" --json main...HEAD)"
code9=$?
set -e
echo "$json9" | "$PYTHON" -c '
import json,sys
d=json.load(sys.stdin)
assert d["status"]=="MUTE", d
mute_paths={m["path"] for m in d["mute"]}
locked_paths={m["path"] for m in d["locked"]}
assert "tool" in mute_paths, d["mute"]
assert "app.py" in locked_paths, d["locked"]
assert "tool" not in d["ignored"], d["ignored"]
print("mute", [m["id"] for m in d["mute"]])
print("locked", [m["id"] for m in d["locked"]])
'
assert_eq "$code9" "1" "shebang wrapper is unlocked production"

echo
echo "======== demo OK ========"
exit 0
