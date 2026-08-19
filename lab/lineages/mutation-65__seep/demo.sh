#!/usr/bin/env bash
# Exercise seep: hatch's test file + till's rename-follow, I/O worlds first.
# hatch/till emit call-site/label order; seep emits timeout=0 / path worlds first.
# --check lists ranked worlds (no test file) and exits 1 when dues exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SEEP="$ROOT/seep"
chmod +x "$SEEP" "$ROOT/fixtures/rename/build.sh"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== self-test =="
"$SEEP" --self-test || fail "self-test"
pass "self-test"

echo "== ugly fixtures: default is a test file, I/O first =="
UGLY="$ROOT/fixtures/ugly"

swift_out="$("$SEEP" -C "$UGLY" --min-callers 1 isBrowser)"
echo "$swift_out"
echo "$swift_out" | grep -q 'import XCTest' || fail "isBrowser default must be XCTest"
echo "$swift_out" | grep -q 'XCTestCase' || fail "isBrowser missing XCTestCase"
echo "$swift_out" | grep -q 'Brave Browser' || fail "isBrowser missing Brave Browser"
echo "$swift_out" | grep -q 'func test' || fail "isBrowser missing test func"
echo "$swift_out" | grep -q 'XCTAssertTrue' || fail "isBrowser member must assert true"
echo "$swift_out" | grep -q 'SeepTests' || fail "isBrowser class must be SeepTests"
echo "$swift_out" | grep -q 'import pytest\|  due  \|tilt' && fail "isBrowser default leaked report/pytest" || true
pass "ugly isBrowser defaults to XCTest"

py_out="$("$SEEP" -C "$UGLY" --min-callers 1 connect)"
echo "$py_out"
echo "$py_out" | grep -q 'import pytest' || fail "connect default must be pytest"
echo "$py_out" | grep -q 'timeout=0' || fail "connect missing timeout=0"
echo "$py_out" | grep -q 'db.example.com' || fail "connect missing production host"
echo "$py_out" | grep -q 'localhost' && fail "test-only localhost leaked" || true
echo "$py_out" | grep -q $'tilt\t\|prod-only-const' && fail "tilt language leaked" || true
t0="$(echo "$py_out" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
db="$(echo "$py_out" | grep -n 'db.example.com' | head -1 | cut -d: -f1)"
[ -n "$t0" ] && [ -n "$db" ] && [ "$t0" -lt "$db" ] || fail "timeout=0 must emit before db.example.com (t0=$t0 db=$db)"
pass "ugly connect defaults to pytest; timeout=0 first"

life="$("$SEEP" --report --color never -C "$UGLY" --min-callers 1 later)"
echo "$life"
echo "$life" | grep -q 'later' || fail "lifetime: later missing"
echo "$life" | grep -q '{x=1}' || fail "lifetime: later(1) missing"
echo "$life" | grep -q '{x=0}' && fail "lifetime: later(0) test world leaked" || true
pass "rust lifetimes do not swallow later fns"

porc="$("$SEEP" --porcelain -C "$UGLY")"
echo "$porc" | grep -q $'fixture\tconnect\t' || fail "porcelain connect fixture"
echo "$porc" | grep -q 'timeout=0' || fail "porcelain timeout=0"
echo "$porc" | grep -q 'Brave Browser' || fail "porcelain Brave"
echo "$porc" | grep -q $'tilt\t' && fail "porcelain tilt row" || true
pass "porcelain still fixture rows"

js="$("$SEEP" --json -C "$UGLY" connect)"
echo "$js" | grep -q '"tool": "seep"' || fail "json tool tag"
echo "$js" | grep -q '"fixtures"' || fail "json fixtures"
echo "$js" | grep -q '"io"' || fail "json missing io rank field"
pass "json still available"

echo "$porc" | grep -q 'timeout=99' && fail "comment leaked as a call" || true
pass "comments ignored"

"$SEEP" --summary -C "$UGLY" >/tmp/seep-ugly-summary.txt
cat /tmp/seep-ugly-summary.txt
grep -q 'due_fns=' /tmp/seep-ugly-summary.txt || fail "summary line"
grep -q 'io_due=' /tmp/seep-ugly-summary.txt || fail "summary missing io_due"
pass "ugly summary"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/seep-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R "$UGLY" "$TMP/ugly"
mkdir -p "$TMP/ugly/vendor/nested/src"
echo 'def inner(x): return x' > "$TMP/ugly/vendor/nested/src/inner.py"
git -C "$TMP/ugly/vendor/nested" init -q
git -C "$TMP/ugly/vendor/nested" add src/inner.py
git -C "$TMP/ugly/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'
"$SEEP" --summary -C "$TMP/ugly" >/tmp/seep-nested-summary.txt
pass "nested git walk"

echo "== --check lists ranked worlds (no test file) =="
set +e
"$SEEP" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --porcelain should exit 1 on due fixtures, got $rc"

set +e
"$SEEP" --check -C "$UGLY" isBrowser >/tmp/seep-check-isbrowser.txt
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check default should exit 1 on due fixtures, got $rc"
grep -q 'import XCTest' /tmp/seep-check-isbrowser.txt && fail "--check must not write XCTest" || true
grep -q 'Brave Browser' /tmp/seep-check-isbrowser.txt || fail "--check listing missing Brave"
pass "--check exits 1 and lists worlds (does not write tests)"

set +e
"$SEEP" --check --emit xctest -C "$UGLY" isBrowser >/tmp/seep-check-emit.swift
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --emit should exit 1, got $rc"
grep -q 'import XCTest' /tmp/seep-check-emit.swift || fail "--check --emit still writes tests"
pass "--check --emit still writes the test file"

echo "== --report is the opt-in listing =="
rep="$("$SEEP" --report --color never -C "$UGLY" --min-callers 1 isBrowser)"
echo "$rep"
echo "$rep" | grep -q 'due' || fail "--report missing due"
echo "$rep" | grep -q 'Brave Browser' || fail "--report missing Brave"
echo "$rep" | grep -q 'import XCTest' && fail "--report should not be XCTest" || true
pass "--report listing"

echo "== pytest collect on generated ugly connect file =="
if command -v pytest >/dev/null; then
  "$SEEP" -C "$UGLY" connect > "$TMP/test_seep_connect.py"
  PYTHONPATH="$UGLY" pytest -q --collect-only "$TMP/test_seep_connect.py" || fail "pytest collect generated connect tests"
  pass "pytest collects generated connect module"
else
  echo "skip pytest collect (pytest not installed)"
fi

echo "== rank fixture: timeout=0 / path worlds first =="
RANK="$ROOT/fixtures/rank"
rank_out="$("$SEEP" --emit pytest -C "$RANK" fetch)"
echo "$rank_out"
echo "$rank_out" | grep -q 'timeout=0' || fail "rank fetch missing timeout=0"
echo "$rank_out" | grep -q 'omega' || fail "rank fetch missing omega"
echo "$rank_out" | grep -q 'alpha' || fail "rank fetch missing alpha"
rt0="$(echo "$rank_out" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
ralpha="$(echo "$rank_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$rt0" ] && [ -n "$ralpha" ] && [ "$rt0" -lt "$ralpha" ] || fail "fetch timeout=0 must sort before alpha (t0=$rt0 alpha=$ralpha)"
pass "rank fetch: timeout=0 before alpha"

norank="$("$SEEP" --no-rank --emit pytest -C "$RANK" fetch)"
echo "$norank"
nt0="$(echo "$norank" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
nalpha="$(echo "$norank" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$nt0" ] && [ -n "$nalpha" ] && [ "$nalpha" -lt "$nt0" ] || fail "--no-rank must keep alpha before timeout=0 (alpha=$nalpha t0=$nt0)"
pass "--no-rank restores hatch/till order"

cfg_out="$("$SEEP" --emit pytest -C "$RANK" read_cfg)"
echo "$cfg_out"
ssh_n="$(echo "$cfg_out" | grep -n 'id_rsa\|~/.ssh' | head -1 | cut -d: -f1)"
cfg_a="$(echo "$cfg_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$ssh_n" ] && [ -n "$cfg_a" ] && [ "$ssh_n" -lt "$cfg_a" ] || fail "read_cfg ~/.ssh must sort before alpha"
pass "rank read_cfg: path/visa before alpha"

rec_rep="$("$SEEP" --report --color never -C "$RANK" record)"
echo "$rec_rep"
echo "$rec_rep" | grep -q 'duration=1' || fail "record missing duration=1"
echo "$rec_rep" | grep -q 'io=timeout' && fail "duration=1 must not rank as timeout" || true
pass "duration=1 is a clock, not timeout=0"

paint_out="$("$SEEP" --emit pytest -C "$RANK" paint)"
echo "$paint_out"
echo "$paint_out" | grep -q 'io=visa\|io=fs' || fail "paint path world must be visa/fs"
pssh="$(echo "$paint_out" | grep -n 'id_rsa\|~/.ssh' | head -1 | cut -d: -f1)"
palpha="$(echo "$paint_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$pssh" ] && [ -n "$palpha" ] && [ "$pssh" -lt "$palpha" ] || fail "paint ~/.ssh must sort before alpha"
echo "$paint_out" | grep -q 'io=body' || fail "one-hop must stain paint(alpha) as body"
pass "one-hop: paint(alpha) is body; ~/.ssh first"

inst_rep="$("$SEEP" --report --color never -C "$RANK" install)"
echo "$inst_rep"
echo "$inst_rep" | grep -q 'io=fs' || fail "install project_root must rank as fs"
pass "project_root glob ranks as fs"

rank_check="$("$SEEP" --check -C "$RANK" || true)"
echo "$rank_check"
echo "$rank_check" | head -1 | grep -q '^timeout' || fail "--check rank listing must start with timeout"
pass "--check rank listing leads with timeout=0"

echo "== rename fixture: sow/hatch miss, seep emits (till gold) =="
"$ROOT/fixtures/rename/build.sh" "$TMP/rename"
LEFT="$TMP/rename/leftover"
HIST="$TMP/rename/hist"

echo "-- leftover: --no-follow (hatch identity) misses Brave --"
no_left="$("$SEEP" --no-follow --emit pytest -C "$LEFT" isBrowser)"
echo "$no_left"
echo "$no_left" | grep -q 'Brave Browser' && fail "--no-follow leftover leaked Brave" || true
pass "--no-follow leftover misses Brave"

echo "-- leftover: seep follow emits Brave under HEAD name --"
yes_left="$("$SEEP" --emit pytest -C "$LEFT" isBrowser)"
echo "$yes_left"
echo "$yes_left" | grep -q 'Brave Browser' || fail "seep leftover missing Brave"
echo "$yes_left" | grep -q 'isBrowser' || fail "seep leftover must emit HEAD name"
echo "$yes_left" | grep -q 'isWebApp(' && fail "seep leftover emitted dead name" || true
pass "seep leftover emits isBrowser(Brave)"

echo "-- leftover: query by dead name isWebApp --"
by_old="$("$SEEP" --emit pytest -C "$LEFT" isWebApp)"
echo "$by_old"
echo "$by_old" | grep -q 'Brave Browser' || fail "query isWebApp missed Brave"
echo "$by_old" | grep -q 'isBrowser' || fail "query isWebApp must still emit HEAD name"
pass "query isWebApp follows to isBrowser"

echo "-- leftover Swift XCTest --"
sw_left="$("$SEEP" --emit xctest -C "$LEFT" isBrowser)"
echo "$sw_left"
echo "$sw_left" | grep -q 'import XCTest' || fail "swift leftover not XCTest"
echo "$sw_left" | grep -q 'Brave Browser' || fail "swift leftover missing Brave"
echo "$sw_left" | grep -q 'XCTAssertTrue' || fail "swift leftover predicate must XCTAssertTrue"
echo "$sw_left" | grep -q '\.\.\.' && fail "swift leftover emitted ..." || true
pass "swift leftover XCTest"

echo "-- leftover --report shows aka --"
rep_left="$("$SEEP" --report --color never -C "$LEFT" isBrowser)"
echo "$rep_left"
echo "$rep_left" | grep -q 'aka' || fail "--report missing aka chain"
echo "$rep_left" | grep -q 'isWebApp' || fail "--report missing old name"
echo "$rep_left" | grep -q 'ParserTests.swift' && fail "test-path hop leaked into identity" || true
pass "report aka chain"

echo "-- leftover --aka-map --"
amap="$("$SEEP" --aka-map -C "$LEFT")"
echo "$amap"
echo "$amap" | grep -q $'aka\t' || fail "aka-map missing aka rows"
echo "$amap" | grep -q 'isWebApp' || fail "aka-map missing isWebApp"
pass "aka-map"

echo "-- hist: Brave lives only as last week's isWebApp literal --"
no_hist="$("$SEEP" --no-follow --emit pytest -C "$HIST" isBrowser)"
echo "$no_hist"
echo "$no_hist" | grep -q 'Brave Browser' && fail "--no-follow hist leaked Brave" || true
yes_hist="$("$SEEP" --emit pytest -C "$HIST" isBrowser)"
echo "$yes_hist"
echo "$yes_hist" | grep -q 'Brave Browser' || fail "seep hist missing Brave"
echo "$yes_hist" | grep -q '@' || fail "hist emit should cite a historical site"
pass "historical Brave recovered"

# Prove sibling sow/hatch miss the same fixture when those binaries exist.
for bin in \
  "${HATCH_BIN:-}" \
  /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b31-4c8e-79b3-81da-49b6359c8a52/hatch \
  /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ac6-9c54-76b0-8e7b-373cc8f86126/sow \
  /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b59-bd04-73e2-91aa-55fbce2020ab/till
do
  [ -n "$bin" ] && [ -x "$bin" ] || continue
  name="$(basename "$bin")"
  out="$("$bin" --emit pytest -C "$LEFT" isBrowser 2>/dev/null || "$bin" -C "$LEFT" isBrowser 2>/dev/null || true)"
  echo "-- sibling $name on leftover --"
  echo "$out" | head -20
  if [ "$name" = "till" ]; then
    echo "$out" | grep -q 'Brave Browser' || fail "till should still emit leftover Brave"
    pass "till emits leftover Brave (parent)"
  else
    echo "$out" | grep -q 'Brave Browser' && fail "$name should miss leftover Brave" || true
    pass "$name misses leftover Brave"
  fi
done

echo "-- leftover --check exits 1 (listing, not tests) --"
set +e
"$SEEP" --check -C "$LEFT" isBrowser >/tmp/seep-check-left.txt
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "leftover --check should exit 1, got $rc"
grep -q 'Brave Browser' /tmp/seep-check-left.txt || fail "--check leftover listing missing Brave"
grep -q 'import pytest\|def test_' /tmp/seep-check-left.txt && fail "--check leftover wrote a test file" || true
pass "leftover --check exits 1 and lists"

echo "== real repos (read-only) =="
GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"

if [ -d "$GHQ/sitbone" ]; then
  echo "-- sitbone isBrowser (default XCTest) --"
  sit="$("$SEEP" -C "$GHQ/sitbone" isBrowser)"
  echo "$sit"
  echo "$sit" | grep -q 'import XCTest' || fail "sitbone isBrowser must default to XCTest"
  echo "$sit" | grep -q '@testable import SitboneCore' || fail "sitbone missing @testable import SitboneCore"
  echo "$sit" | grep -q 'Brave Browser' || fail "sitbone missing Brave Browser"
  echo "$sit" | grep -q 'func test' || fail "sitbone missing XCTest func"
  echo "$sit" | grep -q 'XCTAssertTrue' || fail "sitbone isBrowser member must XCTAssertTrue"
  echo "$sit" | grep -q 'import pytest' && fail "sitbone isBrowser leaked pytest" || true
  echo "$sit" | grep -q '\.\.\.' && fail "sitbone isBrowser emitted invalid Swift ..." || true
  echo "-- sitbone extractSiteName must be silent --"
  ext="$("$SEEP" --report --color never -C "$GHQ/sitbone" --min-callers 1 extractSiteName || true)"
  echo "$ext"
  echo "$ext" | grep -q 'extractSiteName' && fail "extractSiteName has no production callers" || true
  echo "-- sitbone record --"
  rec="$("$SEEP" --report --color never -C "$GHQ/sitbone" --min-callers 1 record || true)"
  echo "$rec"
  echo "$rec" | grep -q 'duration=1' || fail "sitbone record missing duration=1"
  echo "$rec" | grep -q 'io=timeout' && fail "sitbone duration=1 must not be timeout" || true
  rec_swift="$("$SEEP" -C "$GHQ/sitbone" record)"
  echo "$rec_swift"
  echo "$rec_swift" | grep -q 'XCTSkip' || fail "sitbone record dyn world must XCTSkip"
  echo "$rec_swift" | grep -q '\.\.\.' && fail "sitbone record emitted invalid Swift ..." || true
  echo "-- sitbone --check isBrowser --"
  set +e
  "$SEEP" --check -C "$GHQ/sitbone" isBrowser >/tmp/seep-sitbone-isbrowser.txt
  rc=$?
  set -e
  [ "$rc" -eq 1 ] || fail "sitbone isBrowser --check should exit 1, got $rc"
  grep -q 'import XCTest' /tmp/seep-sitbone-isbrowser.txt && fail "sitbone --check must list, not write XCTest" || true
  grep -q 'Brave Browser' /tmp/seep-sitbone-isbrowser.txt || fail "sitbone --check listing missing Brave"
  if command -v swift >/dev/null; then
    echo "-- sitbone swift test overlay (generated XCTest) --"
    overlay="$TMP/sitbone-overlay"
    rsync -a --exclude .build --exclude .git --exclude scratch \
      "$GHQ/sitbone/" "$overlay/"
    "$SEEP" -C "$GHQ/sitbone" isBrowser > "$overlay/Tests/SitboneCoreTests/SeepIsBrowserTests.swift"
    swift_out="$(cd "$overlay" && swift test --filter WindowTitleParserSeepTests 2>&1)" || {
      echo "$swift_out"
      fail "seeped sitbone isBrowser XCTest failed to build or run"
    }
    echo "$swift_out" | tail -20
    echo "$swift_out" | grep -q "testIsBrowserAppNameBraveBrowser" || fail "swift test missing Brave case"
    echo "$swift_out" | grep -q "Executed 6 tests, with 0 failures" || fail "expected 6 passing seeped isBrowser tests"
    pass "sitbone isBrowser XCTest ran 6/6"
  else
    echo "skip sitbone swift test overlay (swift not present)"
  fi
  echo "-- sitbone stopSession (real rename → stopCapture) --"
  sess="$("$SEEP" --report --color never -C "$GHQ/sitbone" stopSession || true)"
  echo "$sess"
  echo "$sess" | grep -q 'stopCapture' || fail "sitbone stopSession must follow to stopCapture"
  echo "$sess" | grep -q 'aka' || fail "sitbone stopSession missing aka (sown identity)"
  amap_s="$("$SEEP" --aka-map -C "$GHQ/sitbone" stopSession)"
  echo "$amap_s"
  echo "$amap_s" | grep -q 'stopSession' || fail "aka-map missing stopSession"
  echo "-- sitbone summary (follow on) --"
  "$SEEP" --summary --color never -C "$GHQ/sitbone" || fail "sitbone summary"
  pass "sitbone isBrowser"
else
  echo "skip sitbone (not present)"
fi

if [ -d "$GHQ/kizu" ]; then
  echo "-- kizu run_split_command --"
  kout="$("$SEEP" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target --min-callers 1 run_split_command || true)"
  echo "$kout"
  echo "$kout" | grep -q 'Ghostty' || fail "kizu missing Ghostty production context"
  echo "$kout" | grep -q 'sh ok\|sh failing' && fail "kizu test-only sh context leaked" || true
  "$SEEP" --emit pytest -C "$GHQ/kizu" --exclude tests/e2e --exclude target run_split_command | head -30
  echo "-- kizu install_claude_code (dead name; sow/hatch silent) --"
  k_no="$("$SEEP" --no-follow --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_no"
  echo "$k_no" | grep -q 'install_settings_hook_agent' && fail "no-follow should not see dead name" || true
  k_yes="$("$SEEP" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_yes"
  echo "$k_yes" | grep -q 'install_settings_hook_agent' || fail "kizu install_claude_code must follow"
  echo "$k_yes" | grep -q 'aka' || fail "kizu missing aka chain"
  n_due="$(echo "$k_yes" | grep -c 'due  ' || true)"
  [ "$n_due" -ge 4 ] || fail "kizu install_claude_code expected 4 due worlds, got $n_due"
  echo "$k_yes" | grep -q 'io=fs' || fail "kizu project_root worlds must rank as fs (not body)"
  echo "-- kizu summary --"
  "$SEEP" --summary --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target || fail "kizu summary"
  pass "kizu install_claude_code follow + run_split_command"
fi

if [ -d "$GHQ/tenaoshi" ]; then
  echo "-- tenaoshi PromptStore.validate --"
  tout="$("$SEEP" --report --color never -C "$GHQ/tenaoshi" --min-callers 1 validate || true)"
  echo "$tout"
  echo "-- tenaoshi summary --"
  "$SEEP" --summary --color never -C "$GHQ/tenaoshi" --exclude dist --exclude .build || fail "tenaoshi summary"
  pass "tenaoshi census"
fi

pass "demo complete"
exit 0
