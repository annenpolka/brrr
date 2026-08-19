#!/usr/bin/env bash
# Exercise hatch: default stdout is a runnable test file.
# --check still exits 1 when due worlds exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
HATCH="$ROOT/hatch"
chmod +x "$HATCH"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== self-test =="
"$HATCH" --self-test || fail "self-test"
pass "self-test"

echo "== ugly fixtures: default is a test file, not a report =="
UGLY="$ROOT/fixtures/ugly"

swift_out="$("$HATCH" -C "$UGLY" --min-callers 1 isBrowser)"
echo "$swift_out"
echo "$swift_out" | grep -q 'import XCTest' || fail "isBrowser default must be XCTest"
echo "$swift_out" | grep -q 'XCTestCase' || fail "isBrowser missing XCTestCase"
echo "$swift_out" | grep -q 'Brave Browser' || fail "isBrowser missing Brave Browser"
echo "$swift_out" | grep -q 'func test' || fail "isBrowser missing test func"
echo "$swift_out" | grep -q 'XCTAssertTrue' || fail "isBrowser member must assert true"
echo "$swift_out" | grep -q 'import pytest\|  due  \|tilt' && fail "isBrowser default leaked report/pytest" || true
pass "ugly isBrowser defaults to XCTest"

py_out="$("$HATCH" -C "$UGLY" --min-callers 1 connect)"
echo "$py_out"
echo "$py_out" | grep -q 'import pytest' || fail "connect default must be pytest"
echo "$py_out" | grep -q 'timeout=0' || fail "connect missing timeout=0"
echo "$py_out" | grep -q 'db.example.com' || fail "connect missing production host"
echo "$py_out" | grep -q 'localhost' && fail "test-only localhost leaked" || true
echo "$py_out" | grep -q $'tilt\t\|prod-only-const' && fail "tilt language leaked" || true
pass "ugly connect defaults to pytest"

# rust lifetimes must not swallow later
life="$("$HATCH" --report --color never -C "$UGLY" --min-callers 1 later)"
echo "$life"
echo "$life" | grep -q 'later' || fail "lifetime: later missing"
echo "$life" | grep -q '{x=1}' || fail "lifetime: later(1) missing"
echo "$life" | grep -q '{x=0}' && fail "lifetime: later(0) test world leaked" || true
pass "rust lifetimes do not swallow later fns"

porc="$("$HATCH" --porcelain -C "$UGLY")"
echo "$porc" | grep -q $'fixture\tconnect\t' || fail "porcelain connect fixture"
echo "$porc" | grep -q 'timeout=0' || fail "porcelain timeout=0"
echo "$porc" | grep -q 'Brave Browser' || fail "porcelain Brave"
echo "$porc" | grep -q $'tilt\t' && fail "porcelain tilt row" || true
pass "porcelain still fixture rows"

js="$("$HATCH" --json -C "$UGLY" connect)"
echo "$js" | grep -q '"tool": "hatch"' || fail "json tool tag"
echo "$js" | grep -q '"fixtures"' || fail "json fixtures"
pass "json still available"

# comments must not invent timeout=99
echo "$porc" | grep -q 'timeout=99' && fail "comment leaked as a call" || true
pass "comments ignored"

"$HATCH" --summary -C "$UGLY" >/tmp/hatch-ugly-summary.txt
cat /tmp/hatch-ugly-summary.txt
grep -q 'due_fns=' /tmp/hatch-ugly-summary.txt || fail "summary line"
pass "ugly summary"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/hatch-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R "$UGLY" "$TMP/ugly"
mkdir -p "$TMP/ugly/vendor/nested/src"
echo 'def inner(x): return x' > "$TMP/ugly/vendor/nested/src/inner.py"
git -C "$TMP/ugly/vendor/nested" init -q
git -C "$TMP/ugly/vendor/nested" add src/inner.py
git -C "$TMP/ugly/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'
"$HATCH" --summary -C "$TMP/ugly" >/tmp/hatch-nested-summary.txt
pass "nested git walk"

echo "== --check exit code (still 1 when dues exist) =="
set +e
"$HATCH" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --porcelain should exit 1 on due fixtures, got $rc"

set +e
"$HATCH" --check -C "$UGLY" isBrowser >/tmp/hatch-check-isbrowser.swift
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check default should exit 1 on due fixtures, got $rc"
grep -q 'import XCTest' /tmp/hatch-check-isbrowser.swift || fail "--check stdout should still be the test file"
pass "--check exits 1 and still writes tests"

echo "== --report is the opt-in listing =="
rep="$("$HATCH" --report --color never -C "$UGLY" --min-callers 1 isBrowser)"
echo "$rep" | grep -q 'due' || fail "--report missing due"
echo "$rep" | grep -q 'Brave Browser' || fail "--report missing Brave"
echo "$rep" | grep -q 'import XCTest' && fail "--report should not be XCTest" || true
pass "--report listing"

echo "== pytest collect on generated ugly connect file =="
if command -v pytest >/dev/null; then
  "$HATCH" -C "$UGLY" connect > "$TMP/test_hatch_connect.py"
  # collection only: the calls need the fixture tree on sys.path
  PYTHONPATH="$UGLY" pytest -q --collect-only "$TMP/test_hatch_connect.py" || fail "pytest collect generated connect tests"
  pass "pytest collects generated connect module"
else
  echo "skip pytest collect (pytest not installed)"
fi

echo "== real repos (read-only) =="
GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"

if [ -d "$GHQ/sitbone" ]; then
  echo "-- sitbone isBrowser (default XCTest) --"
  sit="$("$HATCH" -C "$GHQ/sitbone" isBrowser)"
  echo "$sit"
  echo "$sit" | grep -q 'import XCTest' || fail "sitbone isBrowser must default to XCTest"
  echo "$sit" | grep -q '@testable import SitboneCore' || fail "sitbone missing @testable import SitboneCore"
  echo "$sit" | grep -q 'Brave Browser' || fail "sitbone missing Brave Browser"
  echo "$sit" | grep -q 'func test' || fail "sitbone missing XCTest func"
  echo "$sit" | grep -q 'XCTAssertTrue' || fail "sitbone isBrowser member must XCTAssertTrue"
  echo "$sit" | grep -q 'import pytest' && fail "sitbone isBrowser leaked pytest" || true
  echo "$sit" | grep -q '\.\.\.' && fail "sitbone isBrowser emitted invalid Swift ..." || true
  echo "-- sitbone extractSiteName must be silent --"
  ext="$("$HATCH" --report --color never -C "$GHQ/sitbone" --min-callers 1 extractSiteName || true)"
  echo "$ext"
  echo "$ext" | grep -q 'extractSiteName' && fail "extractSiteName has no production callers" || true
  echo "-- sitbone record --"
  rec="$("$HATCH" --report --color never -C "$GHQ/sitbone" --min-callers 1 record || true)"
  echo "$rec"
  echo "$rec" | grep -q 'duration=1' || fail "sitbone record missing duration=1"
  rec_swift="$("$HATCH" -C "$GHQ/sitbone" record)"
  echo "$rec_swift"
  echo "$rec_swift" | grep -q 'XCTSkip' || fail "sitbone record dyn world must XCTSkip"
  echo "$rec_swift" | grep -q '\.\.\.' && fail "sitbone record emitted invalid Swift ..." || true
  echo "-- sitbone --check isBrowser --"
  set +e
  "$HATCH" --check -C "$GHQ/sitbone" isBrowser >/tmp/hatch-sitbone-isbrowser.swift
  rc=$?
  set -e
  [ "$rc" -eq 1 ] || fail "sitbone isBrowser --check should exit 1, got $rc"
  if command -v swift >/dev/null; then
    echo "-- sitbone swift test overlay (generated XCTest) --"
    overlay="$TMP/sitbone-overlay"
    rsync -a --exclude .build --exclude .git --exclude scratch \
      "$GHQ/sitbone/" "$overlay/"
    "$HATCH" -C "$GHQ/sitbone" isBrowser > "$overlay/Tests/SitboneCoreTests/HatchIsBrowserTests.swift"
    swift_out="$(cd "$overlay" && swift test --filter WindowTitleParserHatchTests 2>&1)" || {
      echo "$swift_out"
      fail "hatched sitbone isBrowser XCTest failed to build or run"
    }
    echo "$swift_out" | tail -20
    echo "$swift_out" | grep -q "testIsBrowserAppNameBraveBrowser" || fail "swift test missing Brave case"
    echo "$swift_out" | grep -q "Executed 6 tests, with 0 failures" || fail "expected 6 passing hatched isBrowser tests"
    pass "sitbone isBrowser XCTest ran 6/6"
  else
    echo "skip sitbone swift test overlay (swift not present)"
  fi
  pass "sitbone isBrowser"
else
  echo "skip sitbone (not present)"
fi

if [ -d "$GHQ/kizu" ]; then
  echo "-- kizu run_split_command --"
  kout="$("$HATCH" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target --min-callers 1 run_split_command || true)"
  echo "$kout"
  echo "$kout" | grep -q 'Ghostty' || fail "kizu missing Ghostty production context"
  echo "$kout" | grep -q 'sh ok\|sh failing' && fail "kizu test-only sh context leaked" || true
  "$HATCH" --emit pytest -C "$GHQ/kizu" --exclude tests/e2e --exclude target run_split_command | head -30
fi

pass "demo complete"
exit 0
