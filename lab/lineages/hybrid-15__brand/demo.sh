#!/usr/bin/env bash
# Exercise brand. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/brand"
PY="${PYTHON:-python3}"
BRAND=("$PY" "$ROOT/brand.py")
passed=0
failed=0

ok() { passed=$((passed + 1)); echo "ok  $1"; }
fail() { failed=$((failed + 1)); echo "FAIL  $1" >&2; echo "      $2" >&2; }

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

echo "======== 0. self-test ========"
set +e
out="$("${BRAND[@]}" --self-test 2>&1)"
rc=$?
set -e
assert_exit "$rc" 0 "self-test"
assert_contains "$out" "self-test ok" "self-test ok line"

FIX="$(mktemp -d "${TMPDIR:-/tmp}/brand-demo-XXXX")"
git -C "$FIX" init -q
git -C "$FIX" config user.email brand@lab
git -C "$FIX" config user.name brand
git -C "$FIX" config commit.gpgsign false

mkdir -p "$FIX/src" "$FIX/tests"
cat > "$FIX/src/profile.py" <<'PY'
import os
def load_profile(home):
    return home == "/tmp/cache" or os.path.isdir(home)
def who(home):
    return home == "/tmp/cache"
def start():
    load_profile("/tmp/cache")
    who("/tmp/cache")
PY
cat > "$FIX/tests/test_profile.py" <<'PY'
from src.profile import load_profile
def test_tmp():
    load_profile("/tmp")
PY
cat > "$FIX/src/App.swift" <<'SWIFT'
// when the macOS PollWatcher fallback is active.
public enum WindowTitleParser {
    private static let browsers: Set<String> = ["Chrome", "Safari", "Brave Browser"]
    public static func isBrowser(_ appName: String) -> Bool {
        browsers.contains(appName)
    }
}
public func loadHome(_ path: String) -> Bool { true }
public func boot() {
    _ = loadHome("/tmp/sitbone")
    _ = WindowTitleParser.isBrowser("Brave Browser")
}
SWIFT
cat > "$FIX/src/quote.py" <<'PY'
def quote(path):
    return path
def examples():
    quote("/home/user/project")
PY
git -C "$FIX" add -A
git -C "$FIX" commit -qm "open portable worlds"
C_OPEN="$(git -C "$FIX" rev-parse HEAD)"

echo "======== 1. mint-only: pin Alice, tests still /tmp ========"
cat > "$FIX/src/profile.py" <<'PY'
import os
def load_profile(home):
    return home == "/Users/alice" or os.path.isdir(home)
def who(home):
    return home == "/Users/alice"
def start():
    load_profile("/Users/alice")
    who("/Users/alice")
PY
git -C "$FIX" add -A
git -C "$FIX" commit -qm "pin Alice home"
C_MINT="$(git -C "$FIX" rev-parse HEAD)"

set +e
mint_out="$("${BRAND[@]}" -C "$FIX" "$C_MINT" 2>/tmp/brand-mint.err)"
mint_rc=$?
mint_rep="$("${BRAND[@]}" -C "$FIX" --report "$C_MINT" 2>/tmp/brand-mint-rep.err)"
set -e
echo "$mint_rep"
assert_exit "$mint_rc" 0 "mint-only commit exit 0 (not a brand)"
assert_empty "$mint_out" "mint-only default empty"
assert_contains "$mint_rep" "MINT" "mint-only --report names MINT"
assert_contains "$mint_rep" "brands=0" "mint-only report brands=0"
assert_absent "$mint_rep" "    BRAND" "mint-only is not a brand"
assert_contains "$mint_rep" "SPEC→BOUND" "mint-only still sees the visa-birth"
assert_absent "$mint_out" "import pytest" "default is not a test file"
assert_absent "$mint_rep" "Brave" "OPEN Brave is not a birth"
assert_absent "$mint_rep" "/home/user" "textbook quote is not a birth"
assert_absent "$mint_rep" "erst" "not leftover natal keys"

echo "======== 2. SPREAD Alice into Swift — not a mint, not a brand ========"
perl -pi -e 's#loadHome\("/tmp/sitbone"\)#loadHome("/Users/alice/Library/sitbone")#' "$FIX/src/App.swift"
git -C "$FIX" add -A
git -C "$FIX" commit -qm "spread Alice into Swift"
C_SPREAD="$(git -C "$FIX" rev-parse HEAD)"
set +e
spread_out="$("${BRAND[@]}" -C "$FIX" "$C_SPREAD")"
spread_rc=$?
spread_show="$("${BRAND[@]}" -C "$FIX" --spread --report "$C_SPREAD")"
set -e
assert_exit "$spread_rc" 0 "SPREAD is not a brand"
assert_empty "$spread_out" "default hides SPREAD"
assert_absent "$spread_show" "    BRAND" "SPREAD report is not a brand"

echo "======== 3. gage-now: lock Alice after the birth ========"
cat > "$FIX/tests/test_profile.py" <<'PY'
from src.profile import who
def test_alice():
    assert who("/Users/alice")
PY
git -C "$FIX" add -A
git -C "$FIX" commit -qm "lock Alice after the birth"
C_GAGE="$(git -C "$FIX" rev-parse HEAD)"
set +e
gage_out="$("${BRAND[@]}" -C "$FIX" "$C_GAGE")"
gage_rc=$?
range_out="$("${BRAND[@]}" -C "$FIX" "${C_OPEN}..${C_GAGE}")"
range_rc=$?
set -e
assert_exit "$gage_rc" 0 "lock-after-birth exit 0 (gage-now, not a brand)"
assert_empty "$gage_out" "lock-after-birth default empty"
assert_exit "$range_rc" 0 "range spanning mint-then-lock is not a brand"
assert_empty "$range_out" "range spanning mint-then-lock empty"
# mint on that range would still name the Alice birth; brand requires co-occurrence.

echo "======== 4. GitHub titles — not a visa, not a brand ========"
cat > "$FIX/src/titles.py" <<'PY'
def extract_title(title):
    return title.split(" - ", 1)[0]
def crawl():
    extract_title("GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome")
PY
git -C "$FIX" add -A
git -C "$FIX" commit -qm "add GitHub titles"
C_TITLE="$(git -C "$FIX" rev-parse HEAD)"
set +e
title_out="$("${BRAND[@]}" -C "$FIX" "$C_TITLE")"
title_rc=$?
head_out="$("${BRAND[@]}" -C "$FIX")"
head_rc=$?
walk_out="$("${BRAND[@]}" -C "$FIX" --walk --max 12 "$C_TITLE")"
walk_rc=$?
set -e
assert_exit "$title_rc" 0 "titles commit exit 0"
assert_empty "$title_out" "titles default empty"
assert_exit "$head_rc" 0 "HEAD titles exit 0"
assert_empty "$head_out" "HEAD default empty"
assert_exit "$walk_rc" 0 "split-history walk is not a brand"
assert_empty "$walk_out" "split-history walk empty"
assert_absent "$walk_out" "annenpolka" "GitHub title is not USER"

echo "======== 5. joint: pin + lock in the same commit ========"
JOINT="$(mktemp -d "${TMPDIR:-/tmp}/brand-joint-XXXX")"
git -C "$JOINT" init -q
git -C "$JOINT" config user.email brand@lab
git -C "$JOINT" config user.name brand
git -C "$JOINT" config commit.gpgsign false
mkdir -p "$JOINT/src" "$JOINT/tests"
cat > "$JOINT/src/profile.py" <<'PY'
def who(home):
    return home == "/tmp/cache"
def start():
    who("/tmp/cache")
PY
cat > "$JOINT/tests/test_profile.py" <<'PY'
from src.profile import who
def test_tmp():
    assert who("/tmp/cache")
PY
git -C "$JOINT" add -A
git -C "$JOINT" commit -qm "open portable worlds"
cat > "$JOINT/src/profile.py" <<'PY'
def who(home):
    return home == "/Users/alice"
def start():
    who("/Users/alice")
PY
cat > "$JOINT/tests/test_profile.py" <<'PY'
from src.profile import who
def test_alice():
    assert who("/Users/alice")
PY
git -C "$JOINT" add -A
git -C "$JOINT" commit -qm "pin Alice home and lock it"
C_BRAND="$(git -C "$JOINT" rev-parse HEAD)"
set +e
brand_out="$("${BRAND[@]}" -C "$JOINT" "$C_BRAND")"
brand_rc=$?
brand_json="$("${BRAND[@]}" -C "$JOINT" --json "$C_BRAND")"
set -e
echo "$brand_out"
assert_exit "$brand_rc" 1 "joint birth+lock exit 1"
assert_contains "$brand_out" "BRAND" "joint names BRAND"
assert_contains "$brand_out" "LOCKED-and-BOUND-at-birth" "joint verdict"
assert_contains "$brand_out" "/Users/alice" "joint names Alice"
assert_contains "$brand_out" "test_profile" "joint names the locking tests"
assert_absent "$brand_out" "import pytest" "joint is not a test file"
assert_absent "$brand_out" "Brave" "OPEN Brave is not a brand"
assert_contains "$brand_json" '"tool": "brand"' "json names brand"
assert_absent "$brand_json" '"tool": "mint"' "json is not mint"
assert_absent "$brand_json" '"tool": "gage"' "json is not gage"

echo "======== 6. skip-at-birth ========"
SKIPDIR="$(mktemp -d "${TMPDIR:-/tmp}/brand-skip-XXXX")"
git -C "$SKIPDIR" init -q
git -C "$SKIPDIR" config user.email brand@lab
git -C "$SKIPDIR" config user.name brand
git -C "$SKIPDIR" config commit.gpgsign false
mkdir -p "$SKIPDIR/src" "$SKIPDIR/tests"
cat > "$SKIPDIR/src/profile.py" <<'PY'
def who(home):
    return home == "/tmp/cache"
def start():
    who("/tmp/cache")
PY
cat > "$SKIPDIR/tests/test_profile.py" <<'PY'
from src.profile import who
def test_tmp():
    assert who("/tmp/cache")
PY
git -C "$SKIPDIR" add -A
git -C "$SKIPDIR" commit -qm "open"
cat > "$SKIPDIR/src/profile.py" <<'PY'
def who(home):
    return home == "/Users/alice"
def start():
    who("/Users/alice")
PY
cat > "$SKIPDIR/tests/test_profile.py" <<'PY'
import os
import unittest
from src.profile import who

@unittest.skipUnless(os.path.expanduser("~") == "/Users/alice", "alice only")
class TestAlice(unittest.TestCase):
    def test_alice(self):
        self.assertTrue(who("/Users/alice"))
PY
git -C "$SKIPDIR" add -A
git -C "$SKIPDIR" commit -qm "pin Alice with skipif lock"
C_SKIP="$(git -C "$SKIPDIR" rev-parse HEAD)"
set +e
skip_out="$("${BRAND[@]}" -C "$SKIPDIR" "$C_SKIP")"
skip_rc=$?
"${BRAND[@]}" -C "$SKIPDIR" --due -q "$C_SKIP"
due_rc=$?
skip_rep="$("${BRAND[@]}" -C "$SKIPDIR" --report "$C_SKIP")"
set -e
assert_exit "$skip_rc" 0 "skip-at-birth default exit 0"
assert_empty "$skip_out" "skip-at-birth default empty"
assert_exit "$due_rc" 1 "skip-at-birth --due exit 1"
assert_contains "$skip_rep" "SKIP" "skip-at-birth occupancy SKIP"

echo "======== 7. sitbone / kizu (mint's gold: births=0 ⇒ brands=0) ========"
SITBONE="${SITBONE:-$HOME/ghq/github.com/annenpolka/sitbone}"
KIZU="${KIZU:-$HOME/ghq/github.com/annenpolka/kizu}"

if [[ -d "$SITBONE/.git" ]]; then
  set +e
  sb_out="$("${BRAND[@]}" -C "$SITBONE" 2>/tmp/brand-sitbone.err)"
  sb_rc=$?
  sbw_out="$("${BRAND[@]}" -C "$SITBONE" --walk --max 40 HEAD 2>/tmp/brand-sitbone-walk.err)"
  sbw_rc=$?
  set -e
  echo "sitbone HEAD rc=$sb_rc"
  echo "$sb_out"
  echo "sitbone --walk rc=$sbw_rc"
  echo "$sbw_out"
  if [[ "$sb_rc" -eq 2 ]]; then
    fail "sitbone HEAD runs" "$(cat /tmp/brand-sitbone.err)"
  else
    ok "sitbone HEAD runs"
  fi
  assert_exit "$sb_rc" 0 "sitbone HEAD is not a brand (births=0 gold)"
  assert_empty "$sb_out" "sitbone HEAD empty"
  if [[ "$sbw_rc" -eq 2 ]]; then
    fail "sitbone walk runs" "$(cat /tmp/brand-sitbone-walk.err)"
  else
    ok "sitbone walk runs"
  fi
  assert_exit "$sbw_rc" 0 "sitbone walk is not a brand"
  assert_empty "$sbw_out" "sitbone walk empty"
  assert_absent "$sbw_out" "Brave Browser" "sitbone walk does not mint Brave"
  assert_absent "$sbw_out" "erst" "sitbone walk is not natal keys"
  assert_absent "$sb_out" "import pytest" "sitbone is not a test file"
else
  echo "(skip sitbone — not present)"
fi

if [[ -d "$KIZU/.git" ]]; then
  set +e
  kz_out="$("${BRAND[@]}" -C "$KIZU" 2>/tmp/brand-kizu.err)"
  kz_rc=$?
  kzw_out="$("${BRAND[@]}" -C "$KIZU" --walk --max 40 HEAD 2>/tmp/brand-kizu-walk.err)"
  kzw_rc=$?
  kzw_err="$(cat /tmp/brand-kizu-walk.err 2>/dev/null || true)"
  set -e
  echo "kizu HEAD rc=$kz_rc"
  echo "$kz_out"
  echo "kizu --walk rc=$kzw_rc"
  echo "$kzw_out"
  if [[ "$kz_rc" -eq 2 ]]; then
    fail "kizu HEAD runs" "$(cat /tmp/brand-kizu.err)"
  else
    ok "kizu HEAD runs"
  fi
  if [[ "$kzw_rc" -eq 2 ]]; then
    fail "kizu walk runs" "$kzw_err"
  else
    ok "kizu walk runs (no AbsoluteLinkError)"
  fi
  assert_exit "$kz_rc" 0 "kizu HEAD is not a brand"
  assert_empty "$kz_out" "kizu HEAD empty"
  assert_exit "$kzw_rc" 0 "kizu walk is not a brand"
  assert_empty "$kzw_out" "kizu walk empty"
  assert_absent "$kz_out" "/home/user" "kizu textbook is not a birth"
  assert_absent "$kz_out" "John Doe" "kizu quoting fixture is not a birth"
  assert_absent "$kzw_out" "/home/user" "kizu walk textbook is not a birth"
  assert_absent "$kzw_out" "John Doe" "kizu walk quoting fixture is not a birth"
  assert_absent "$kzw_err" "AbsoluteLinkError" "kizu walk has no AbsoluteLinkError"
  assert_absent "$kzw_err" "Traceback" "kizu walk has no traceback"
else
  echo "(skip kizu — not present)"
fi

rm -rf "$FIX" "$JOINT" "$SKIPDIR"

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
