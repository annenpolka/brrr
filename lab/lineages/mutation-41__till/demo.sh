#!/usr/bin/env bash
# Exercise till: hatch's test file, plus rename-follow so HEAD name is not identity.
# --check still exits 1 when due worlds exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
TILL="$ROOT/till"
chmod +x "$TILL" "$ROOT/fixtures/rename/build.sh"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== self-test =="
"$TILL" --self-test || fail "self-test"
pass "self-test"

echo "== ugly fixtures: default is a test file, not a report =="
UGLY="$ROOT/fixtures/ugly"

swift_out="$("$TILL" -C "$UGLY" --min-callers 1 isBrowser)"
echo "$swift_out"
echo "$swift_out" | grep -q 'import XCTest' || fail "isBrowser default must be XCTest"
echo "$swift_out" | grep -q 'XCTestCase' || fail "isBrowser missing XCTestCase"
echo "$swift_out" | grep -q 'Brave Browser' || fail "isBrowser missing Brave Browser"
echo "$swift_out" | grep -q 'func test' || fail "isBrowser missing test func"
echo "$swift_out" | grep -q 'XCTAssertTrue' || fail "isBrowser member must assert true"
echo "$swift_out" | grep -q 'import pytest\|  due  \|tilt' && fail "isBrowser default leaked report/pytest" || true
pass "ugly isBrowser defaults to XCTest"

py_out="$("$TILL" -C "$UGLY" --min-callers 1 connect)"
echo "$py_out"
echo "$py_out" | grep -q 'import pytest' || fail "connect default must be pytest"
echo "$py_out" | grep -q 'timeout=0' || fail "connect missing timeout=0"
echo "$py_out" | grep -q 'db.example.com' || fail "connect missing production host"
echo "$py_out" | grep -q 'localhost' && fail "test-only localhost leaked" || true
echo "$py_out" | grep -q $'tilt\t\|prod-only-const' && fail "tilt language leaked" || true
pass "ugly connect defaults to pytest"

life="$("$TILL" --report --color never -C "$UGLY" --min-callers 1 later)"
echo "$life"
echo "$life" | grep -q 'later' || fail "lifetime: later missing"
echo "$life" | grep -q '{x=1}' || fail "lifetime: later(1) missing"
echo "$life" | grep -q '{x=0}' && fail "lifetime: later(0) test world leaked" || true
pass "rust lifetimes do not swallow later fns"

porc="$("$TILL" --porcelain -C "$UGLY")"
echo "$porc" | grep -q $'fixture\tconnect\t' || fail "porcelain connect fixture"
echo "$porc" | grep -q 'timeout=0' || fail "porcelain timeout=0"
echo "$porc" | grep -q 'Brave Browser' || fail "porcelain Brave"
echo "$porc" | grep -q $'tilt\t' && fail "porcelain tilt row" || true
pass "porcelain still fixture rows"

js="$("$TILL" --json -C "$UGLY" connect)"
echo "$js" | grep -q '"tool": "till"' || fail "json tool tag"
echo "$js" | grep -q '"fixtures"' || fail "json fixtures"
pass "json still available"

echo "$porc" | grep -q 'timeout=99' && fail "comment leaked as a call" || true
pass "comments ignored"

"$TILL" --summary -C "$UGLY" >/tmp/till-ugly-summary.txt
cat /tmp/till-ugly-summary.txt
grep -q 'due_fns=' /tmp/till-ugly-summary.txt || fail "summary line"
pass "ugly summary"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/till-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R "$UGLY" "$TMP/ugly"
mkdir -p "$TMP/ugly/vendor/nested/src"
echo 'def inner(x): return x' > "$TMP/ugly/vendor/nested/src/inner.py"
git -C "$TMP/ugly/vendor/nested" init -q
git -C "$TMP/ugly/vendor/nested" add src/inner.py
git -C "$TMP/ugly/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'
"$TILL" --summary -C "$TMP/ugly" >/tmp/till-nested-summary.txt
pass "nested git walk"

echo "== --check exit code (still 1 when dues exist) =="
set +e
"$TILL" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --porcelain should exit 1 on due fixtures, got $rc"

set +e
"$TILL" --check -C "$UGLY" isBrowser >/tmp/till-check-isbrowser.swift
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check default should exit 1 on due fixtures, got $rc"
grep -q 'import XCTest' /tmp/till-check-isbrowser.swift || fail "--check stdout should still be the test file"
pass "--check exits 1 and still writes tests"

echo "== --report is the opt-in listing =="
rep="$("$TILL" --report --color never -C "$UGLY" --min-callers 1 isBrowser)"
echo "$rep"
echo "$rep" | grep -q 'due' || fail "--report missing due"
echo "$rep" | grep -q 'Brave Browser' || fail "--report missing Brave"
echo "$rep" | grep -q 'import XCTest' && fail "--report should not be XCTest" || true
pass "--report listing"

echo "== pytest collect on generated ugly connect file =="
if command -v pytest >/dev/null; then
  "$TILL" -C "$UGLY" connect > "$TMP/test_till_connect.py"
  PYTHONPATH="$UGLY" pytest -q --collect-only "$TMP/test_till_connect.py" || fail "pytest collect generated connect tests"
  pass "pytest collects generated connect module"
else
  echo "skip pytest collect (pytest not installed)"
fi

echo "== rename fixture: sow/hatch miss, till emits =="
"$ROOT/fixtures/rename/build.sh" "$TMP/rename"
LEFT="$TMP/rename/leftover"
HIST="$TMP/rename/hist"

echo "-- leftover: --no-follow (hatch identity) misses Brave --"
no_left="$("$TILL" --no-follow --emit pytest -C "$LEFT" isBrowser)"
echo "$no_left"
echo "$no_left" | grep -q 'Brave Browser' && fail "--no-follow leftover leaked Brave" || true
pass "--no-follow leftover misses Brave"

echo "-- leftover: till follow emits Brave under HEAD name --"
yes_left="$("$TILL" --emit pytest -C "$LEFT" isBrowser)"
echo "$yes_left"
echo "$yes_left" | grep -q 'Brave Browser' || fail "till leftover missing Brave"
echo "$yes_left" | grep -q 'isBrowser' || fail "till leftover must emit HEAD name"
echo "$yes_left" | grep -q 'isWebApp(' && fail "till leftover emitted dead name" || true
pass "till leftover emits isBrowser(Brave)"

echo "-- leftover: query by dead name isWebApp --"
by_old="$("$TILL" --emit pytest -C "$LEFT" isWebApp)"
echo "$by_old"
echo "$by_old" | grep -q 'Brave Browser' || fail "query isWebApp missed Brave"
echo "$by_old" | grep -q 'isBrowser' || fail "query isWebApp must still emit HEAD name"
pass "query isWebApp follows to isBrowser"

echo "-- leftover Swift XCTest --"
sw_left="$("$TILL" --emit xctest -C "$LEFT" isBrowser)"
echo "$sw_left"
echo "$sw_left" | grep -q 'import XCTest' || fail "swift leftover not XCTest"
echo "$sw_left" | grep -q 'Brave Browser' || fail "swift leftover missing Brave"
echo "$sw_left" | grep -q 'XCTAssertTrue' || fail "swift leftover predicate must XCTAssertTrue"
echo "$sw_left" | grep -q '\.\.\.' && fail "swift leftover emitted ..." || true
pass "swift leftover XCTest"

echo "-- leftover --report shows aka --"
rep_left="$("$TILL" --report --color never -C "$LEFT" isBrowser)"
echo "$rep_left"
echo "$rep_left" | grep -q 'aka' || fail "--report missing aka chain"
echo "$rep_left" | grep -q 'isWebApp' || fail "--report missing old name"
echo "$rep_left" | grep -q 'ParserTests.swift' && fail "test-path hop leaked into identity" || true
pass "report aka chain"

echo "-- leftover --aka-map --"
amap="$("$TILL" --aka-map -C "$LEFT")"
echo "$amap"
echo "$amap" | grep -q $'aka\t' || fail "aka-map missing aka rows"
echo "$amap" | grep -q 'isWebApp' || fail "aka-map missing isWebApp"
pass "aka-map"

echo "-- hist: Brave lives only as last week's isWebApp literal --"
no_hist="$("$TILL" --no-follow --emit pytest -C "$HIST" isBrowser)"
echo "$no_hist"
echo "$no_hist" | grep -q 'Brave Browser' && fail "--no-follow hist leaked Brave" || true
yes_hist="$("$TILL" --emit pytest -C "$HIST" isBrowser)"
echo "$yes_hist"
echo "$yes_hist" | grep -q 'Brave Browser' || fail "till hist missing Brave"
echo "$yes_hist" | grep -q '@' || fail "hist emit should cite a historical site"
pass "historical Brave recovered"

# Prove sibling sow/hatch miss the same fixture when those binaries exist.
for bin in \
  "${HATCH_BIN:-}" \
  /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b31-4c8e-79b3-81da-49b6359c8a52/hatch \
  /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ac6-9c54-76b0-8e7b-373cc8f86126/sow
do
  [ -n "$bin" ] && [ -x "$bin" ] || continue
  name="$(basename "$bin")"
  out="$("$bin" --emit pytest -C "$LEFT" isBrowser 2>/dev/null || "$bin" -C "$LEFT" isBrowser 2>/dev/null || true)"
  echo "-- sibling $name on leftover --"
  echo "$out" | head -20
  echo "$out" | grep -q 'Brave Browser' && fail "$name should miss leftover Brave" || true
  pass "$name misses leftover Brave"
done

echo "-- leftover --check exits 1 --"
set +e
"$TILL" --check --emit pytest -C "$LEFT" isBrowser >/tmp/till-check-left.py
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "leftover --check should exit 1, got $rc"
grep -q 'Brave Browser' /tmp/till-check-left.py || fail "--check leftover stdout missing Brave"
pass "leftover --check exits 1"

echo "== real repos (read-only) =="
GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"

if [ -d "$GHQ/sitbone" ]; then
  echo "-- sitbone isBrowser (default XCTest) --"
  sit="$("$TILL" -C "$GHQ/sitbone" isBrowser)"
  echo "$sit"
  echo "$sit" | grep -q 'import XCTest' || fail "sitbone isBrowser must default to XCTest"
  echo "$sit" | grep -q '@testable import SitboneCore' || fail "sitbone missing @testable import SitboneCore"
  echo "$sit" | grep -q 'Brave Browser' || fail "sitbone missing Brave Browser"
  echo "$sit" | grep -q 'func test' || fail "sitbone missing XCTest func"
  echo "$sit" | grep -q 'XCTAssertTrue' || fail "sitbone isBrowser member must XCTAssertTrue"
  echo "$sit" | grep -q 'import pytest' && fail "sitbone isBrowser leaked pytest" || true
  echo "$sit" | grep -q '\.\.\.' && fail "sitbone isBrowser emitted invalid Swift ..." || true
  echo "-- sitbone extractSiteName must be silent --"
  ext="$("$TILL" --report --color never -C "$GHQ/sitbone" --min-callers 1 extractSiteName || true)"
  echo "$ext"
  echo "$ext" | grep -q 'extractSiteName' && fail "extractSiteName has no production callers" || true
  echo "-- sitbone record --"
  rec="$("$TILL" --report --color never -C "$GHQ/sitbone" --min-callers 1 record || true)"
  echo "$rec"
  echo "$rec" | grep -q 'duration=1' || fail "sitbone record missing duration=1"
  rec_swift="$("$TILL" -C "$GHQ/sitbone" record)"
  echo "$rec_swift"
  echo "$rec_swift" | grep -q 'XCTSkip' || fail "sitbone record dyn world must XCTSkip"
  echo "$rec_swift" | grep -q '\.\.\.' && fail "sitbone record emitted invalid Swift ..." || true
  echo "-- sitbone --check isBrowser --"
  set +e
  "$TILL" --check -C "$GHQ/sitbone" isBrowser >/tmp/till-sitbone-isbrowser.swift
  rc=$?
  set -e
  [ "$rc" -eq 1 ] || fail "sitbone isBrowser --check should exit 1, got $rc"
  if command -v swift >/dev/null; then
    echo "-- sitbone swift test overlay (generated XCTest) --"
    overlay="$TMP/sitbone-overlay"
    rsync -a --exclude .build --exclude .git --exclude scratch \
      "$GHQ/sitbone/" "$overlay/"
    "$TILL" -C "$GHQ/sitbone" isBrowser > "$overlay/Tests/SitboneCoreTests/HatchIsBrowserTests.swift"
    swift_out="$(cd "$overlay" && swift test --filter WindowTitleParserHatchTests 2>&1)" || {
      echo "$swift_out"
      fail "tilled sitbone isBrowser XCTest failed to build or run"
    }
    echo "$swift_out" | tail -20
    echo "$swift_out" | grep -q "testIsBrowserAppNameBraveBrowser" || fail "swift test missing Brave case"
    echo "$swift_out" | grep -q "Executed 6 tests, with 0 failures" || fail "expected 6 passing tilled isBrowser tests"
    pass "sitbone isBrowser XCTest ran 6/6"
  else
    echo "skip sitbone swift test overlay (swift not present)"
  fi
  echo "-- sitbone stopSession (real rename → stopCapture) --"
  sess="$("$TILL" --report --color never -C "$GHQ/sitbone" stopSession || true)"
  echo "$sess"
  echo "$sess" | grep -q 'stopCapture' || fail "sitbone stopSession must follow to stopCapture"
  echo "$sess" | grep -q 'aka' || fail "sitbone stopSession missing aka (sown identity)"
  amap_s="$("$TILL" --aka-map -C "$GHQ/sitbone" stopSession)"
  echo "$amap_s"
  echo "$amap_s" | grep -q 'stopSession' || fail "aka-map missing stopSession"
  echo "-- sitbone summary (follow on) --"
  "$TILL" --summary --color never -C "$GHQ/sitbone" || fail "sitbone summary"
  pass "sitbone isBrowser"
else
  echo "skip sitbone (not present)"
fi

if [ -d "$GHQ/kizu" ]; then
  echo "-- kizu run_split_command --"
  kout="$("$TILL" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target --min-callers 1 run_split_command || true)"
  echo "$kout"
  echo "$kout" | grep -q 'Ghostty' || fail "kizu missing Ghostty production context"
  echo "$kout" | grep -q 'sh ok\|sh failing' && fail "kizu test-only sh context leaked" || true
  "$TILL" --emit pytest -C "$GHQ/kizu" --exclude tests/e2e --exclude target run_split_command | head -30
  echo "-- kizu install_claude_code (dead name; sow/hatch silent) --"
  k_no="$("$TILL" --no-follow --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_no"
  echo "$k_no" | grep -q 'install_settings_hook_agent' && fail "no-follow should not see dead name" || true
  k_yes="$("$TILL" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_yes"
  echo "$k_yes" | grep -q 'install_settings_hook_agent' || fail "kizu install_claude_code must follow"
  echo "$k_yes" | grep -q 'aka' || fail "kizu missing aka chain"
  echo "-- kizu summary --"
  "$TILL" --summary --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target || fail "kizu summary"
  pass "kizu run_split_command"
fi

if [ -d "$GHQ/tenaoshi" ]; then
  echo "-- tenaoshi PromptStore.validate --"
  tout="$("$TILL" --report --color never -C "$GHQ/tenaoshi" --min-callers 1 validate || true)"
  echo "$tout"
  echo "-- tenaoshi summary --"
  "$TILL" --summary --color never -C "$GHQ/tenaoshi" --exclude dist --exclude .build || fail "tenaoshi summary"
  pass "tenaoshi census"
fi

pass "demo complete"
exit 0
