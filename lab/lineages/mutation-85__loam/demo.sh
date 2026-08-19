#!/usr/bin/env bash
# Exercise loam: seep's I/O-first test file, plus Type() so instance methods call.
# seep emits SiteObserver.record(...) — not a real call. loam constructs
# SiteObserver() (or reuses a test fixture of that type). --no-construct is seep.
# --check lists ranked worlds (no test file) and exits 1 when dues exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LOAM="$ROOT/loam"
chmod +x "$LOAM" "$ROOT/fixtures/rename/build.sh"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== self-test =="
"$LOAM" --self-test || fail "self-test"
pass "self-test"

echo "== ugly fixtures: default is a test file, I/O first =="
UGLY="$ROOT/fixtures/ugly"

swift_out="$("$LOAM" -C "$UGLY" --min-callers 1 isBrowser)"
echo "$swift_out"
echo "$swift_out" | grep -q 'import XCTest' || fail "isBrowser default must be XCTest"
echo "$swift_out" | grep -q 'XCTestCase' || fail "isBrowser missing XCTestCase"
echo "$swift_out" | grep -q 'Brave Browser' || fail "isBrowser missing Brave Browser"
echo "$swift_out" | grep -q 'func test' || fail "isBrowser missing test func"
echo "$swift_out" | grep -q 'XCTAssertTrue' || fail "isBrowser member must assert true"
echo "$swift_out" | grep -q 'LoamTests' || fail "isBrowser class must be LoamTests"
echo "$swift_out" | grep -q 'import pytest\|  due  \|tilt' && fail "isBrowser default leaked report/pytest" || true
pass "ugly isBrowser defaults to XCTest"

py_out="$("$LOAM" -C "$UGLY" --min-callers 1 connect)"
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

life="$("$LOAM" --report --color never -C "$UGLY" --min-callers 1 later)"
echo "$life"
echo "$life" | grep -q 'later' || fail "lifetime: later missing"
echo "$life" | grep -q '{x=1}' || fail "lifetime: later(1) missing"
echo "$life" | grep -q '{x=0}' && fail "lifetime: later(0) test world leaked" || true
pass "rust lifetimes do not swallow later fns"

porc="$("$LOAM" --porcelain -C "$UGLY")"
echo "$porc" | grep -q $'fixture\tconnect\t' || fail "porcelain connect fixture"
echo "$porc" | grep -q 'timeout=0' || fail "porcelain timeout=0"
echo "$porc" | grep -q 'Brave Browser' || fail "porcelain Brave"
echo "$porc" | grep -q $'tilt\t' && fail "porcelain tilt row" || true
pass "porcelain still fixture rows"

js="$("$LOAM" --json -C "$UGLY" connect)"
echo "$js" | grep -q '"tool": "loam"' || fail "json tool tag"
echo "$js" | grep -q '"fixtures"' || fail "json fixtures"
echo "$js" | grep -q '"io"' || fail "json missing io rank field"
pass "json still available"

echo "$porc" | grep -q 'timeout=99' && fail "comment leaked as a call" || true
pass "comments ignored"

"$LOAM" --summary -C "$UGLY" >/tmp/loam-ugly-summary.txt
cat /tmp/loam-ugly-summary.txt
grep -q 'due_fns=' /tmp/loam-ugly-summary.txt || fail "summary line"
grep -q 'io_due=' /tmp/loam-ugly-summary.txt || fail "summary missing io_due"
pass "ugly summary"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/loam-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R "$UGLY" "$TMP/ugly"
mkdir -p "$TMP/ugly/vendor/nested/src"
echo 'def inner(x): return x' > "$TMP/ugly/vendor/nested/src/inner.py"
git -C "$TMP/ugly/vendor/nested" init -q
git -C "$TMP/ugly/vendor/nested" add src/inner.py
git -C "$TMP/ugly/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'
"$LOAM" --summary -C "$TMP/ugly" >/tmp/loam-nested-summary.txt
pass "nested git walk"

echo "== --check lists ranked worlds (no test file) =="
set +e
"$LOAM" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --porcelain should exit 1 on due fixtures, got $rc"

set +e
"$LOAM" --check -C "$UGLY" isBrowser >/tmp/loam-check-isbrowser.txt
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check default should exit 1 on due fixtures, got $rc"
grep -q 'import XCTest' /tmp/loam-check-isbrowser.txt && fail "--check must not write XCTest" || true
grep -q 'Brave Browser' /tmp/loam-check-isbrowser.txt || fail "--check listing missing Brave"
pass "--check exits 1 and lists worlds (does not write tests)"

set +e
"$LOAM" --check --emit xctest -C "$UGLY" isBrowser >/tmp/loam-check-emit.swift
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --emit should exit 1, got $rc"
grep -q 'import XCTest' /tmp/loam-check-emit.swift || fail "--check --emit still writes tests"
pass "--check --emit still writes the test file"

echo "== --report is the opt-in listing =="
rep="$("$LOAM" --report --color never -C "$UGLY" --min-callers 1 isBrowser)"
echo "$rep"
echo "$rep" | grep -q 'due' || fail "--report missing due"
echo "$rep" | grep -q 'Brave Browser' || fail "--report missing Brave"
echo "$rep" | grep -q 'import XCTest' && fail "--report should not be XCTest" || true
pass "--report listing"

echo "== pytest collect on generated ugly connect file =="
if command -v pytest >/dev/null; then
  "$LOAM" -C "$UGLY" connect > "$TMP/test_loam_connect.py"
  PYTHONPATH="$UGLY" pytest -q --collect-only "$TMP/test_loam_connect.py" || fail "pytest collect generated connect tests"
  pass "pytest collects generated connect module"
else
  echo "skip pytest collect (pytest not installed)"
fi

echo "== rank fixture: timeout=0 / path worlds first =="
RANK="$ROOT/fixtures/rank"
rank_out="$("$LOAM" --emit pytest -C "$RANK" fetch)"
echo "$rank_out"
echo "$rank_out" | grep -q 'timeout=0' || fail "rank fetch missing timeout=0"
echo "$rank_out" | grep -q 'omega' || fail "rank fetch missing omega"
echo "$rank_out" | grep -q 'alpha' || fail "rank fetch missing alpha"
rt0="$(echo "$rank_out" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
ralpha="$(echo "$rank_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$rt0" ] && [ -n "$ralpha" ] && [ "$rt0" -lt "$ralpha" ] || fail "fetch timeout=0 must sort before alpha (t0=$rt0 alpha=$ralpha)"
pass "rank fetch: timeout=0 before alpha"

norank="$("$LOAM" --no-rank --emit pytest -C "$RANK" fetch)"
echo "$norank"
nt0="$(echo "$norank" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
nalpha="$(echo "$norank" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$nt0" ] && [ -n "$nalpha" ] && [ "$nalpha" -lt "$nt0" ] || fail "--no-rank must keep alpha before timeout=0 (alpha=$nalpha t0=$nt0)"
pass "--no-rank restores hatch/till order"

cfg_out="$("$LOAM" --emit pytest -C "$RANK" read_cfg)"
echo "$cfg_out"
ssh_n="$(echo "$cfg_out" | grep -n 'id_rsa\|~/.ssh' | head -1 | cut -d: -f1)"
cfg_a="$(echo "$cfg_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$ssh_n" ] && [ -n "$cfg_a" ] && [ "$ssh_n" -lt "$cfg_a" ] || fail "read_cfg ~/.ssh must sort before alpha"
pass "rank read_cfg: path/visa before alpha"

rec_rep="$("$LOAM" --report --color never -C "$RANK" record)"
echo "$rec_rep"
echo "$rec_rep" | grep -q 'duration=1' || fail "record missing duration=1"
echo "$rec_rep" | grep -q 'io=timeout' && fail "duration=1 must not rank as timeout" || true
pass "duration=1 is a clock, not timeout=0"

paint_out="$("$LOAM" --emit pytest -C "$RANK" paint)"
echo "$paint_out"
echo "$paint_out" | grep -q 'io=visa\|io=fs' || fail "paint path world must be visa/fs"
pssh="$(echo "$paint_out" | grep -n 'id_rsa\|~/.ssh' | head -1 | cut -d: -f1)"
palpha="$(echo "$paint_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$pssh" ] && [ -n "$palpha" ] && [ "$pssh" -lt "$palpha" ] || fail "paint ~/.ssh must sort before alpha"
echo "$paint_out" | grep -q 'io=body' || fail "one-hop must stain paint(alpha) as body"
pass "one-hop: paint(alpha) is body; ~/.ssh first"

inst_rep="$("$LOAM" --report --color never -C "$RANK" install)"
echo "$inst_rep"
echo "$inst_rep" | grep -q 'io=fs' || fail "install project_root must rank as fs"
pass "project_root glob ranks as fs"

rank_check="$("$LOAM" --check -C "$RANK" || true)"
echo "$rank_check"
echo "$rank_check" | head -1 | grep -q '^timeout' || fail "--check rank listing must start with timeout"
pass "--check rank listing leads with timeout=0"

echo "== construct fixture: instance methods get Type() =="
CTOR="$ROOT/fixtures/construct"
ctor_py="$("$LOAM" --emit pytest -C "$CTOR" record)"
echo "$ctor_py"
echo "$ctor_py" | grep -q 'clock = Clock(' || fail "construct record must bind Clock()"
echo "$ctor_py" | grep -q 'clock.record(' || fail "construct record must call via binding"
echo "$ctor_py" | grep -q 'Clock.record(' && fail "construct must not emit Type.method" || true
echo "$ctor_py" | grep -q 'duration=1' || fail "construct missing duration=1"
nor="$("$LOAM" --no-construct --emit pytest -C "$CTOR" record)"
echo "$nor"
echo "$nor" | grep -q 'Clock.record(' || fail "--no-construct must emit seep Type.method"
echo "$nor" | grep -q 'clock = Clock(' && fail "--no-construct leaked a receiver" || true
pass "construct Clock.record; --no-construct is seep"

ctor_ping="$("$LOAM" --emit pytest -C "$CTOR" ping)"
echo "$ctor_ping"
echo "$ctor_ping" | grep -q 'Clock.ping(' || fail "staticmethod must stay Type.method"
echo "$ctor_ping" | grep -q 'clock = Clock(' && fail "staticmethod must not construct" || true
pass "static ping does not construct"

ctor_box="$("$LOAM" --emit pytest -C "$CTOR" detect)"
echo "$ctor_box"
echo "$ctor_box" | grep -q 'box = SensorBox(' || fail "SensorBox.detect must construct"
echo "$ctor_box" | grep -q 'timeout=0' || fail "SensorBox missing timeout=0"
echo "$ctor_box" | grep -q 'SensorBox(\[\])' || fail "must reuse test SensorBox([])"
pass "SensorBox reuses test-fixture SensorBox([])"

ctor_sw="$("$LOAM" --emit xctest -C "$CTOR" record)"
echo "$ctor_sw"
echo "$ctor_sw" | grep -q 'let observer = SiteObserver(' || fail "swift record must let observer = SiteObserver()"
echo "$ctor_sw" | grep -q 'observer.record(' || fail "swift record must call via observer"
echo "$ctor_sw" | grep -q 'SiteObserver.record(' && fail "swift must not emit Type.method" || true
pass "swift SiteObserver() constructs"

echo "== rename fixture: sow/hatch miss, loam emits (till gold) =="
"$ROOT/fixtures/rename/build.sh" "$TMP/rename"
LEFT="$TMP/rename/leftover"
HIST="$TMP/rename/hist"

echo "-- leftover: --no-follow (hatch identity) misses Brave --"
no_left="$("$LOAM" --no-follow --emit pytest -C "$LEFT" isBrowser)"
echo "$no_left"
echo "$no_left" | grep -q 'Brave Browser' && fail "--no-follow leftover leaked Brave" || true
pass "--no-follow leftover misses Brave"

echo "-- leftover: loam follow emits Brave under HEAD name --"
yes_left="$("$LOAM" --emit pytest -C "$LEFT" isBrowser)"
echo "$yes_left"
echo "$yes_left" | grep -q 'Brave Browser' || fail "loam leftover missing Brave"
echo "$yes_left" | grep -q 'isBrowser' || fail "loam leftover must emit HEAD name"
echo "$yes_left" | grep -q 'isWebApp(' && fail "loam leftover emitted dead name" || true
pass "loam leftover emits isBrowser(Brave)"

echo "-- leftover: query by dead name isWebApp --"
by_old="$("$LOAM" --emit pytest -C "$LEFT" isWebApp)"
echo "$by_old"
echo "$by_old" | grep -q 'Brave Browser' || fail "query isWebApp missed Brave"
echo "$by_old" | grep -q 'isBrowser' || fail "query isWebApp must still emit HEAD name"
pass "query isWebApp follows to isBrowser"

echo "-- leftover Swift XCTest --"
sw_left="$("$LOAM" --emit xctest -C "$LEFT" isBrowser)"
echo "$sw_left"
echo "$sw_left" | grep -q 'import XCTest' || fail "swift leftover not XCTest"
echo "$sw_left" | grep -q 'Brave Browser' || fail "swift leftover missing Brave"
echo "$sw_left" | grep -q 'XCTAssertTrue' || fail "swift leftover predicate must XCTAssertTrue"
echo "$sw_left" | grep -q '\.\.\.' && fail "swift leftover emitted ..." || true
pass "swift leftover XCTest"

echo "-- leftover --report shows aka --"
rep_left="$("$LOAM" --report --color never -C "$LEFT" isBrowser)"
echo "$rep_left"
echo "$rep_left" | grep -q 'aka' || fail "--report missing aka chain"
echo "$rep_left" | grep -q 'isWebApp' || fail "--report missing old name"
echo "$rep_left" | grep -q 'ParserTests.swift' && fail "test-path hop leaked into identity" || true
pass "report aka chain"

echo "-- leftover --aka-map --"
amap="$("$LOAM" --aka-map -C "$LEFT")"
echo "$amap"
echo "$amap" | grep -q $'aka\t' || fail "aka-map missing aka rows"
echo "$amap" | grep -q 'isWebApp' || fail "aka-map missing isWebApp"
pass "aka-map"

echo "-- hist: Brave lives only as last week's isWebApp literal --"
no_hist="$("$LOAM" --no-follow --emit pytest -C "$HIST" isBrowser)"
echo "$no_hist"
echo "$no_hist" | grep -q 'Brave Browser' && fail "--no-follow hist leaked Brave" || true
yes_hist="$("$LOAM" --emit pytest -C "$HIST" isBrowser)"
echo "$yes_hist"
echo "$yes_hist" | grep -q 'Brave Browser' || fail "loam hist missing Brave"
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
"$LOAM" --check -C "$LEFT" isBrowser >/tmp/loam-check-left.txt
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "leftover --check should exit 1, got $rc"
grep -q 'Brave Browser' /tmp/loam-check-left.txt || fail "--check leftover listing missing Brave"
grep -q 'import pytest\|def test_' /tmp/loam-check-left.txt && fail "--check leftover wrote a test file" || true
pass "leftover --check exits 1 and lists"

echo "== real repos (read-only) =="
GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"

if [ -d "$GHQ/sitbone" ]; then
  echo "-- sitbone isBrowser (default XCTest) --"
  sit="$("$LOAM" -C "$GHQ/sitbone" isBrowser)"
  echo "$sit"
  echo "$sit" | grep -q 'import XCTest' || fail "sitbone isBrowser must default to XCTest"
  echo "$sit" | grep -q '@testable import SitboneCore' || fail "sitbone missing @testable import SitboneCore"
  echo "$sit" | grep -q 'Brave Browser' || fail "sitbone missing Brave Browser"
  echo "$sit" | grep -q 'func test' || fail "sitbone missing XCTest func"
  echo "$sit" | grep -q 'XCTAssertTrue' || fail "sitbone isBrowser member must XCTAssertTrue"
  echo "$sit" | grep -q 'import pytest' && fail "sitbone isBrowser leaked pytest" || true
  echo "$sit" | grep -q '\.\.\.' && fail "sitbone isBrowser emitted invalid Swift ..." || true
  echo "-- sitbone extractSiteName must be silent --"
  ext="$("$LOAM" --report --color never -C "$GHQ/sitbone" --min-callers 1 extractSiteName || true)"
  echo "$ext"
  echo "$ext" | grep -q 'extractSiteName' && fail "extractSiteName has no production callers" || true
  echo "-- sitbone record --"
  rec="$("$LOAM" --report --color never -C "$GHQ/sitbone" --min-callers 1 record || true)"
  echo "$rec"
  echo "$rec" | grep -q 'duration=1' || fail "sitbone record missing duration=1"
  echo "$rec" | grep -q 'io=timeout' && fail "sitbone duration=1 must not be timeout" || true
  rec_swift="$("$LOAM" -C "$GHQ/sitbone" record)"
  echo "$rec_swift"
  echo "$rec_swift" | grep -q 'XCTSkip' || fail "sitbone record dyn world must XCTSkip"
  echo "$rec_swift" | grep -q '\.\.\.' && fail "sitbone record emitted invalid Swift ..." || true
  echo "$rec_swift" | grep -q 'let observer = SiteObserver(' || fail "sitbone record must construct SiteObserver()"
  echo "$rec_swift" | grep -q 'SiteObserver.record(' && fail "sitbone record must not emit Type.method" || true
  echo "$rec" | grep -q 'construct  SiteObserver()' || fail "sitbone --report missing construct line"
  rec_off="$("$LOAM" --no-construct -C "$GHQ/sitbone" record)"
  echo "$rec_off"
  echo "$rec_off" | grep -q 'let observer = SiteObserver(' && fail "--no-construct sitbone leaked receiver" || true
  echo "-- sitbone --check isBrowser --"
  set +e
  "$LOAM" --check -C "$GHQ/sitbone" isBrowser >/tmp/loam-sitbone-isbrowser.txt
  rc=$?
  set -e
  [ "$rc" -eq 1 ] || fail "sitbone isBrowser --check should exit 1, got $rc"
  grep -q 'import XCTest' /tmp/loam-sitbone-isbrowser.txt && fail "sitbone --check must list, not write XCTest" || true
  grep -q 'Brave Browser' /tmp/loam-sitbone-isbrowser.txt || fail "sitbone --check listing missing Brave"
  if command -v swift >/dev/null; then
    echo "-- sitbone swift test overlay (generated XCTest) --"
    overlay="$TMP/sitbone-overlay"
    rsync -a --exclude .build --exclude .git --exclude scratch \
      "$GHQ/sitbone/" "$overlay/"
    "$LOAM" -C "$GHQ/sitbone" isBrowser > "$overlay/Tests/SitboneCoreTests/LoamIsBrowserTests.swift"
    "$LOAM" -C "$GHQ/sitbone" record > "$overlay/Tests/SitboneCoreTests/LoamRecordTests.swift"
    swift_out="$(cd "$overlay" && swift test --filter WindowTitleParserLoamTests 2>&1)" || {
      echo "$swift_out"
      fail "loamed sitbone isBrowser XCTest failed to build or run"
    }
    echo "$swift_out" | tail -20
    echo "$swift_out" | grep -q "testIsBrowserAppNameBraveBrowser" || fail "swift test missing Brave case"
    echo "$swift_out" | grep -q "Executed 6 tests, with 0 failures" || fail "expected 6 passing loamed isBrowser tests"
    pass "sitbone isBrowser XCTest ran 6/6"
    rec_swift_out="$(cd "$overlay" && swift test --filter SiteObserverLoamTests 2>&1)" || {
      echo "$rec_swift_out"
      fail "loamed sitbone record XCTest failed to build or run"
    }
    echo "$rec_swift_out" | tail -20
    echo "$rec_swift_out" | grep -q "testRecordSitePhaseDuration1" || fail "swift test missing constructed record case"
    echo "$rec_swift_out" | grep -q "0 failures" || fail "constructed record overlay had failures"
    echo "$rec_swift_out" | grep -q "skipped" || fail "dyn record world should XCTSkip"
    pass "sitbone record XCTest constructed and ran (skip is ok)"
  else
    echo "skip sitbone swift test overlay (swift not present)"
  fi
  echo "-- sitbone stopSession (real rename → stopCapture) --"
  sess="$("$LOAM" --report --color never -C "$GHQ/sitbone" stopSession || true)"
  echo "$sess"
  echo "$sess" | grep -q 'stopCapture' || fail "sitbone stopSession must follow to stopCapture"
  echo "$sess" | grep -q 'aka' || fail "sitbone stopSession missing aka (sown identity)"
  amap_s="$("$LOAM" --aka-map -C "$GHQ/sitbone" stopSession)"
  echo "$amap_s"
  echo "$amap_s" | grep -q 'stopSession' || fail "aka-map missing stopSession"
  echo "-- sitbone summary (follow on) --"
  "$LOAM" --summary --color never -C "$GHQ/sitbone" || fail "sitbone summary"
  pass "sitbone isBrowser"
else
  echo "skip sitbone (not present)"
fi

if [ -d "$GHQ/kizu" ]; then
  echo "-- kizu run_split_command --"
  kout="$("$LOAM" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target --min-callers 1 run_split_command || true)"
  echo "$kout"
  echo "$kout" | grep -q 'Ghostty' || fail "kizu missing Ghostty production context"
  echo "$kout" | grep -q 'sh ok\|sh failing' && fail "kizu test-only sh context leaked" || true
  "$LOAM" --emit pytest -C "$GHQ/kizu" --exclude tests/e2e --exclude target run_split_command | head -30
  echo "-- kizu install_claude_code (dead name; sow/hatch silent) --"
  k_no="$("$LOAM" --no-follow --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_no"
  echo "$k_no" | grep -q 'install_settings_hook_agent' && fail "no-follow should not see dead name" || true
  k_yes="$("$LOAM" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_yes"
  echo "$k_yes" | grep -q 'install_settings_hook_agent' || fail "kizu install_claude_code must follow"
  echo "$k_yes" | grep -q 'aka' || fail "kizu missing aka chain"
  n_due="$(echo "$k_yes" | grep -c 'due  ' || true)"
  [ "$n_due" -ge 4 ] || fail "kizu install_claude_code expected 4 due worlds, got $n_due"
  echo "$k_yes" | grep -q 'io=fs' || fail "kizu project_root worlds must rank as fs (not body)"
  echo "-- kizu summary --"
  "$LOAM" --summary --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target || fail "kizu summary"
  pass "kizu install_claude_code follow + run_split_command"
fi

if [ -d "$GHQ/tenaoshi" ]; then
  echo "-- tenaoshi PromptStore.validate --"
  tout="$("$LOAM" --report --color never -C "$GHQ/tenaoshi" --min-callers 1 validate || true)"
  echo "$tout"
  echo "-- tenaoshi summary --"
  "$LOAM" --summary --color never -C "$GHQ/tenaoshi" --exclude dist --exclude .build || fail "tenaoshi summary"
  pass "tenaoshi census"
fi

pass "demo complete"
exit 0
