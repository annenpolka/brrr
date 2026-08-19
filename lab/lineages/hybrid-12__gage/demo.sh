#!/usr/bin/env bash
# Exercise gage. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/gage"
PY="${PYTHON:-python3}"
GAGE=("$PY" "$ROOT/gage.py")
passed=0
failed=0

ok() { passed=$((passed + 1)); echo "ok  $1"; }
fail() { failed=$((failed + 1)); echo "FAIL  $1" >&2; echo "      $2" >&2; }

assert_exit() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" -eq "$want" ]]; then ok "$label"
  else fail "$label" "exit want=$want got=$got"
  fi
}

assert_empty() {
  local hay="$1" label="$2"
  if [[ -z "$hay" ]]; then ok "$label"
  else fail "$label" "stdout not empty: ${hay:0:200}"
  fi
}

assert_contains() {
  local hay="$1" needle="$2" label="$3"
  if [[ "$hay" == *"$needle"* ]]; then ok "$label"
  else fail "$label" "missing: $needle"
  fi
}

assert_absent() {
  local hay="$1" needle="$2" label="$3"
  if [[ "$hay" != *"$needle"* ]]; then ok "$label"
  else fail "$label" "should not contain: $needle"
  fi
}

echo "======== 0. self-test ========"
set +e
out="$("${GAGE[@]}" --self-test 2>&1)"
rc=$?
set -e
assert_exit "$rc" 0 "self-test"
assert_contains "$out" "self-test ok" "self-test ok line"

DEMO="$ROOT/demo-tmp"
rm -rf "$DEMO"
mkdir -p "$DEMO"

init_repo() {
  local d="$1"
  mkdir -p "$d"
  git -C "$d" init -q
  git -C "$d" config user.email gage@demo
  git -C "$d" config user.name gage
  git -C "$d" config commit.gpgsign false
}

HOME_PATH="$("$PY" -c 'from pathlib import Path; print(Path.home())')"

echo "======== 1. LOCKED-and-OPEN (Brave) ========"
init_repo "$DEMO/open-lock"
cat > "$DEMO/open-lock/app.py" << 'PY'
BROWSERS = ['Chrome', 'Safari']
def is_browser(name):
    return name in BROWSERS
def tick():
    is_browser('Chrome')
PY
git -C "$DEMO/open-lock" add -A
git -C "$DEMO/open-lock" commit -qm 'old browsers'
cat > "$DEMO/open-lock/app.py" << 'PY'
BROWSERS = ['Chrome', 'Safari', 'Brave Browser']
def is_browser(name):
    return name in BROWSERS
def tick():
    is_browser('Brave Browser')
PY
set +e
out="$("${GAGE[@]}" -C "$DEMO/open-lock" 2>&1)"
rc=$?
rep="$("${GAGE[@]}" -C "$DEMO/open-lock" --report 2>&1)"
set -e
assert_exit "$rc" 0 "open-lock default exit 0"
assert_empty "$out" "open-lock default empty"
assert_contains "$rep" "LOCKED-and-OPEN" "open-lock --report verdict"
assert_contains "$rep" "Brave Browser" "open-lock pins Brave"
assert_absent "$rep" "macOS" "open-lock does not inherit a Darwin comment"

echo "======== 2. LOCKED-and-BOUND (live HOME) ========"
init_repo "$DEMO/bound-lock"
cat > "$DEMO/bound-lock/app.py" << 'PY'
def who(home):
    return home == '/tmp/nobody'
def boot():
    who('/tmp/nobody')
PY
git -C "$DEMO/bound-lock" add -A
git -C "$DEMO/bound-lock" commit -qm 'old who'
"$PY" - "$DEMO/bound-lock/app.py" "$HOME_PATH" << 'PY'
import pathlib, sys
path, home = sys.argv[1], sys.argv[2]
pathlib.Path(path).write_text(
    "def who(home):\n"
    f"    return home == {home!r}\n"
    "def boot():\n"
    f"    who({home!r})\n",
    encoding="utf-8",
)
PY
set +e
out="$("${GAGE[@]}" -C "$DEMO/bound-lock" 2>&1)"
rc=$?
set -e
assert_exit "$rc" 1 "bound-lock default exit 1"
assert_contains "$out" "LOCKED  BOUND" "bound-lock debt"
assert_contains "$out" "parent=CLEAN" "bound-lock new leak"
assert_absent "$out" "import pytest" "debt is not a test file"

echo "======== 3. SKIP-and-BOUND (Alice) ========"
init_repo "$DEMO/bound-skip"
cat > "$DEMO/bound-skip/app.py" << 'PY'
import os
def load_profile(home):
    return os.path.isdir(home)
def start():
    load_profile('/tmp')
PY
git -C "$DEMO/bound-skip" add -A
git -C "$DEMO/bound-skip" commit -qm 'tmp profile'
cat > "$DEMO/bound-skip/app.py" << 'PY'
import os
def load_profile(home):
    return os.path.isdir(home)
def start():
    load_profile('/Users/alice')
PY
set +e
out="$("${GAGE[@]}" -C "$DEMO/bound-skip" 2>&1)"
rc=$?
due_rc=0
"${GAGE[@]}" -C "$DEMO/bound-skip" --due -q
due_rc=$?
rep="$("${GAGE[@]}" -C "$DEMO/bound-skip" --report 2>&1)"
set -e
assert_exit "$rc" 0 "alice skip default exit 0"
assert_empty "$out" "alice skip default empty"
assert_exit "$due_rc" 1 "alice --due exit 1"
assert_contains "$rep" "SKIP-and-BOUND" "alice occupancy SKIP not LOOSE"

echo "======== 4. lockset debug-print (suite fallback) ========"
init_repo "$DEMO/debug-print"
cat > "$DEMO/debug-print/app.py" << 'PY'
def add(a, b):
    return 0
PY
cat > "$DEMO/debug-print/test.py" << 'PY'
from app import add
assert add(2, 3) == 5
PY
git -C "$DEMO/debug-print" add -A
git -C "$DEMO/debug-print" commit -qm 'red add'
cat > "$DEMO/debug-print/app.py" << 'PY'
def add(a, b):
    print("debug")
    return a + b
PY
cat > "$DEMO/debug-print/README.md" << 'EOF'
docs only
EOF
set +e
out="$("${GAGE[@]}" -C "$DEMO/debug-print" 2>&1)"
rc=$?
rep="$("${GAGE[@]}" -C "$DEMO/debug-print" --report 2>&1)"
set -e
assert_exit "$rc" 0 "debug-print default exit 0"
assert_empty "$out" "debug-print default empty"
assert_contains "$rep" "LOCKED-and-OPEN" "debug-print LOCKED-and-OPEN"
assert_absent "$rep" "README.md" "docs are not production"

echo "======== 5. stain ugly: SKIP-and-BOUND is not stain's debt ========"
STAIN_UGLY="${STAIN_UGLY:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6d-63db-74f0-bc26-320de6228199/fixtures/ugly}"
STAIN_BIN="${STAIN_BIN:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6d-63db-74f0-bc26-320de6228199/stain.py}"
if [[ -d "$STAIN_UGLY" ]]; then
  UGLY="$DEMO/ugly"
  rm -rf "$UGLY"
  mkdir -p "$UGLY"
  cp -R "$STAIN_UGLY/." "$UGLY/"
  find "$UGLY" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
  init_repo "$UGLY"
  "$PY" - "$UGLY" << 'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
for p in (root / "src").rglob("*"):
    if not p.is_file():
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    n = (
        t.replace("/Users/alice/Library/sitbone", "/tmp/sitbone")
        .replace("/Users/alice/Library", "/tmp/lib")
        .replace("/Users/alice", "/tmp")
    )
    if n != t:
        p.write_text(n, encoding="utf-8")
PY
  git -C "$UGLY" add -A
  git -C "$UGLY" commit -qm 'base: no Alice'
  rm -rf "$UGLY/src" "$UGLY/tests" "$UGLY/notes"
  cp -R "$STAIN_UGLY/." "$UGLY/"
  find "$UGLY" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
  set +e
  stain_out="$("$PY" "$STAIN_BIN" -C "$UGLY" 2>&1)"
  stain_rc=$?
  out="$("${GAGE[@]}" -C "$UGLY" 2>&1)"
  rc=$?
  rep="$("${GAGE[@]}" -C "$UGLY" --report 2>&1)"
  due_rc=0
  "${GAGE[@]}" -C "$UGLY" --due -q
  due_rc=$?
  set -e
  assert_exit "$stain_rc" 1 "stain ugly still exits 1 (production leaked Alice)"
  assert_contains "$stain_out" "HOME=/Users/alice" "stain names Alice"
  assert_exit "$rc" 0 "gage ugly default exit 0 (skip is not a lock)"
  assert_empty "$out" "gage ugly default empty"
  assert_contains "$rep" "SKIP-and-BOUND" "gage ugly Alice occupancy SKIP"
  assert_absent "$rep" "title.split" "gage ugly does not harvest title.split"
  assert_absent "$rep" "status=BROKEN" "gage ugly is not BROKEN"
  assert_exit "$due_rc" 1 "gage ugly --due exit 1 (stained tests did not occupy)"
else
  echo "skip  stain ugly (not at $STAIN_UGLY)"
fi

LOCKSET="${LOCKSET:-/tmp/lockset-bakeoff/fixtures/debug-print}"
if [[ -d "$LOCKSET/.git" ]]; then
  echo "======== 5b. lockset bakeoff debug-print ========"
  set +e
  out="$("${GAGE[@]}" -C "$LOCKSET" 2>&1)"
  rc=$?
  rep="$("${GAGE[@]}" -C "$LOCKSET" --report 2>&1)"
  set -e
  assert_exit "$rc" 0 "lockset debug-print exit 0"
  assert_empty "$out" "lockset debug-print default empty"
  assert_contains "$rep" "LOCKED-and-OPEN" "lockset debug-print LOCKED-and-OPEN"
  assert_absent "$rep" "README.md" "lockset docs ignored"
fi

echo "======== 6. CLEAN ========"
init_repo "$DEMO/clean"
cat > "$DEMO/clean/app.py" << 'PY'
def add(a, b):
    return a + b
PY
git -C "$DEMO/clean" add -A
git -C "$DEMO/clean" commit -qm 'ok'
set +e
out="$("${GAGE[@]}" -C "$DEMO/clean" 2>&1)"
rc=$?
set -e
assert_exit "$rc" 0 "clean exit 0"
assert_empty "$out" "clean empty"

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
