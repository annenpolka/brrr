#!/usr/bin/env bash
# Exercise seat: loam's constructed worlds, appended into the existing test type.
# loam writes a sibling *LoamTests class. seat appends into SiteObserverTests
# (or PresenceArbiterTests). Type() is only the fallback. --no-seat is loam.
# --check lists ranked worlds (no test file) and exits 1 when dues exist.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SEAT="$ROOT/seat"
chmod +x "$SEAT" "$ROOT/fixtures/rename/build.sh"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== self-test =="
"$SEAT" --self-test || fail "self-test"
pass "self-test"

echo "== ugly fixtures: default is a test file, I/O first =="
UGLY="$ROOT/fixtures/ugly"

swift_out="$("$SEAT" -C "$UGLY" --min-callers 1 isBrowser)"
echo "$swift_out"
echo "$swift_out" | grep -q 'import XCTest' || fail "isBrowser default must be XCTest"
echo "$swift_out" | grep -q 'XCTestCase' || fail "isBrowser missing XCTestCase"
echo "$swift_out" | grep -q 'Brave Browser' || fail "isBrowser missing Brave Browser"
echo "$swift_out" | grep -q 'func test' || fail "isBrowser missing test func"
echo "$swift_out" | grep -q 'XCTAssertTrue' || fail "isBrowser member must assert true"
echo "$swift_out" | grep -q 'WindowTitleParserTests' || fail "isBrowser must sit in existing WindowTitleParserTests"
echo "$swift_out" | grep -q 'func testChrome' || fail "existing testChrome must stay"
echo "$swift_out" | grep -q 'SeatTests\|LoamTests' && fail "isBrowser must not emit a sibling class" || true
echo "$swift_out" | grep -q 'import pytest\|  due  \|tilt' && fail "isBrowser default leaked report/pytest" || true
sib_swift="$("$SEAT" --no-seat -C "$UGLY" --min-callers 1 isBrowser)"
echo "$sib_swift" | grep -q 'SeatTests' || fail "--no-seat must emit sibling SeatTests"
echo "$sib_swift" | grep -q 'testChrome' && fail "--no-seat sibling must not copy existing tests" || true
pass "ugly isBrowser seats into WindowTitleParserTests"

py_out="$("$SEAT" -C "$UGLY" --min-callers 1 connect)"
echo "$py_out"
echo "$py_out" | grep -q 'import pytest' || fail "connect default must be pytest"
echo "$py_out" | grep -q 'timeout=0' || fail "connect missing timeout=0"
echo "$py_out" | grep -q 'db.example.com' || fail "connect missing production host"
echo "$py_out" | grep -q 'def test_local' || fail "seated connect must keep existing test_local"
echo "$py_out" | grep -q $'tilt\t\|prod-only-const' && fail "tilt language leaked" || true
t0="$(echo "$py_out" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
db="$(echo "$py_out" | grep -n 'db.example.com' | head -1 | cut -d: -f1)"
[ -n "$t0" ] && [ -n "$db" ] && [ "$t0" -lt "$db" ] || fail "timeout=0 must emit before db.example.com (t0=$t0 db=$db)"
sib_py="$("$SEAT" --no-seat -C "$UGLY" --min-callers 1 connect)"
echo "$sib_py" | grep -q 'def test_local' && fail "--no-seat sibling must not copy existing tests" || true
echo "$sib_py" | grep -q 'localhost' && fail "sibling leaked test-only localhost" || true
pass "ugly connect seats into test_connect.py; timeout=0 first"

life="$("$SEAT" --report --color never -C "$UGLY" --min-callers 1 later)"
echo "$life"
echo "$life" | grep -q 'later' || fail "lifetime: later missing"
echo "$life" | grep -q '{x=1}' || fail "lifetime: later(1) missing"
echo "$life" | grep -q '{x=0}' && fail "lifetime: later(0) test world leaked" || true
pass "rust lifetimes do not swallow later fns"

porc="$("$SEAT" --porcelain -C "$UGLY")"
echo "$porc" | grep -q $'fixture\tconnect\t' || fail "porcelain connect fixture"
echo "$porc" | grep -q 'timeout=0' || fail "porcelain timeout=0"
echo "$porc" | grep -q 'Brave Browser' || fail "porcelain Brave"
echo "$porc" | grep -q $'tilt\t' && fail "porcelain tilt row" || true
pass "porcelain still fixture rows"

js="$("$SEAT" --json -C "$UGLY" connect)"
echo "$js" | grep -q '"tool": "seat"' || fail "json tool tag"
echo "$js" | grep -q '"fixtures"' || fail "json fixtures"
echo "$js" | grep -q '"io"' || fail "json missing io rank field"
pass "json still available"

echo "$porc" | grep -q 'timeout=99' && fail "comment leaked as a call" || true
pass "comments ignored"

"$SEAT" --summary -C "$UGLY" >/tmp/seat-ugly-summary.txt
cat /tmp/seat-ugly-summary.txt
grep -q 'due_fns=' /tmp/seat-ugly-summary.txt || fail "summary line"
grep -q 'io_due=' /tmp/seat-ugly-summary.txt || fail "summary missing io_due"
pass "ugly summary"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/seat-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R "$UGLY" "$TMP/ugly"
mkdir -p "$TMP/ugly/vendor/nested/src"
echo 'def inner(x): return x' > "$TMP/ugly/vendor/nested/src/inner.py"
git -C "$TMP/ugly/vendor/nested" init -q
git -C "$TMP/ugly/vendor/nested" add src/inner.py
git -C "$TMP/ugly/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'
"$SEAT" --summary -C "$TMP/ugly" >/tmp/seat-nested-summary.txt
pass "nested git walk"

echo "== --check lists ranked worlds (no test file) =="
set +e
"$SEAT" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --porcelain should exit 1 on due fixtures, got $rc"

set +e
"$SEAT" --check -C "$UGLY" isBrowser >/tmp/seat-check-isbrowser.txt
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check default should exit 1 on due fixtures, got $rc"
grep -q 'import XCTest' /tmp/seat-check-isbrowser.txt && fail "--check must not write XCTest" || true
grep -q 'Brave Browser' /tmp/seat-check-isbrowser.txt || fail "--check listing missing Brave"
pass "--check exits 1 and lists worlds (does not write tests)"

set +e
"$SEAT" --check --emit xctest -C "$UGLY" isBrowser >/tmp/seat-check-emit.swift
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check --emit should exit 1, got $rc"
grep -q 'import XCTest' /tmp/seat-check-emit.swift || fail "--check --emit still writes tests"
pass "--check --emit still writes the test file"

echo "== --report is the opt-in listing =="
rep="$("$SEAT" --report --color never -C "$UGLY" --min-callers 1 isBrowser)"
echo "$rep"
echo "$rep" | grep -q 'due' || fail "--report missing due"
echo "$rep" | grep -q 'Brave Browser' || fail "--report missing Brave"
echo "$rep" | grep -q 'import XCTest' && fail "--report should not be XCTest" || true
pass "--report listing"

echo "== pytest collect on generated ugly connect file =="
if command -v pytest >/dev/null; then
  "$SEAT" -C "$UGLY" connect > "$TMP/test_seat_connect.py"
  PYTHONPATH="$UGLY" pytest -q --collect-only "$TMP/test_seat_connect.py" || fail "pytest collect generated connect tests"
  pass "pytest collects generated connect module"
else
  echo "skip pytest collect (pytest not installed)"
fi

echo "== rank fixture: timeout=0 / path worlds first =="
RANK="$ROOT/fixtures/rank"
rank_out="$("$SEAT" --emit pytest -C "$RANK" fetch)"
echo "$rank_out"
echo "$rank_out" | grep -q 'timeout=0' || fail "rank fetch missing timeout=0"
echo "$rank_out" | grep -q 'omega' || fail "rank fetch missing omega"
echo "$rank_out" | grep -q 'alpha' || fail "rank fetch missing alpha"
rt0="$(echo "$rank_out" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
ralpha="$(echo "$rank_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$rt0" ] && [ -n "$ralpha" ] && [ "$rt0" -lt "$ralpha" ] || fail "fetch timeout=0 must sort before alpha (t0=$rt0 alpha=$ralpha)"
pass "rank fetch: timeout=0 before alpha"

norank="$("$SEAT" --no-rank --emit pytest -C "$RANK" fetch)"
echo "$norank"
nt0="$(echo "$norank" | grep -n 'timeout=0' | head -1 | cut -d: -f1)"
nalpha="$(echo "$norank" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$nt0" ] && [ -n "$nalpha" ] && [ "$nalpha" -lt "$nt0" ] || fail "--no-rank must keep alpha before timeout=0 (alpha=$nalpha t0=$nt0)"
pass "--no-rank restores hatch/till order"

cfg_out="$("$SEAT" --emit pytest -C "$RANK" read_cfg)"
echo "$cfg_out"
ssh_n="$(echo "$cfg_out" | grep -n 'id_rsa\|~/.ssh' | head -1 | cut -d: -f1)"
cfg_a="$(echo "$cfg_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$ssh_n" ] && [ -n "$cfg_a" ] && [ "$ssh_n" -lt "$cfg_a" ] || fail "read_cfg ~/.ssh must sort before alpha"
pass "rank read_cfg: path/visa before alpha"

rec_rep="$("$SEAT" --report --color never -C "$RANK" record)"
echo "$rec_rep"
echo "$rec_rep" | grep -q 'duration=1' || fail "record missing duration=1"
echo "$rec_rep" | grep -q 'io=timeout' && fail "duration=1 must not rank as timeout" || true
pass "duration=1 is a clock, not timeout=0"

paint_out="$("$SEAT" --emit pytest -C "$RANK" paint)"
echo "$paint_out"
echo "$paint_out" | grep -q 'io=visa\|io=fs' || fail "paint path world must be visa/fs"
pssh="$(echo "$paint_out" | grep -n 'id_rsa\|~/.ssh' | head -1 | cut -d: -f1)"
palpha="$(echo "$paint_out" | grep -n 'alpha' | head -1 | cut -d: -f1)"
[ -n "$pssh" ] && [ -n "$palpha" ] && [ "$pssh" -lt "$palpha" ] || fail "paint ~/.ssh must sort before alpha"
echo "$paint_out" | grep -q 'io=body' || fail "one-hop must stain paint(alpha) as body"
pass "one-hop: paint(alpha) is body; ~/.ssh first"

inst_rep="$("$SEAT" --report --color never -C "$RANK" install)"
echo "$inst_rep"
echo "$inst_rep" | grep -q 'io=fs' || fail "install project_root must rank as fs"
pass "project_root glob ranks as fs"

rank_check="$("$SEAT" --check -C "$RANK" || true)"
echo "$rank_check"
echo "$rank_check" | head -1 | grep -q '^timeout' || fail "--check rank listing must start with timeout"
pass "--check rank listing leads with timeout=0"

echo "== construct fixture: instance methods get Type() =="
CTOR="$ROOT/fixtures/construct"
ctor_py="$("$SEAT" --emit pytest -C "$CTOR" record)"
echo "$ctor_py"
echo "$ctor_py" | grep -q 'clock = Clock(' || fail "construct record must bind Clock()"
echo "$ctor_py" | grep -q 'clock.record(' || fail "construct record must call via binding"
echo "$ctor_py" | grep -q 'Clock.record(' && fail "construct must not emit Type.method" || true
echo "$ctor_py" | grep -q 'duration=1' || fail "construct missing duration=1"
echo "$ctor_py" | grep -q 'def test_record_default' || fail "construct must seat into existing test_clock.py"
nor="$("$SEAT" --no-construct --no-seat --emit pytest -C "$CTOR" record)"
echo "$nor"
echo "$nor" | grep -q 'Clock.record(' || fail "--no-construct must emit seep Type.method"
echo "$nor" | grep -q 'clock = Clock(' && fail "--no-construct leaked a receiver" || true
pass "construct Clock.record; --no-construct is seep"

ctor_ping="$("$SEAT" --emit pytest -C "$CTOR" ping)"
echo "$ctor_ping"
echo "$ctor_ping" | grep -q 'Clock.ping(' || fail "staticmethod must stay Type.method"
echo "$ctor_ping" | grep -q 'clock = Clock(' && fail "staticmethod must not construct" || true
pass "static ping does not construct"

ctor_box="$("$SEAT" --emit pytest -C "$CTOR" detect)"
echo "$ctor_box"
echo "$ctor_box" | grep -q 'box = SensorBox(' || fail "SensorBox.detect must construct"
echo "$ctor_box" | grep -q 'timeout=0' || fail "SensorBox missing timeout=0"
echo "$ctor_box" | grep -q 'SensorBox(\[\])' || fail "must reuse test SensorBox([])"
pass "SensorBox reuses test-fixture SensorBox([])"

ctor_sw="$("$SEAT" --emit xctest -C "$CTOR" record)"
echo "$ctor_sw"
echo "$ctor_sw" | grep -q 'let observer = SiteObserver(' || fail "swift record must let observer = SiteObserver()"
echo "$ctor_sw" | grep -q 'observer.record(' || fail "swift record must call via observer"
echo "$ctor_sw" | grep -q 'SiteObserver.record(' && fail "swift must not emit Type.method" || true
echo "$ctor_sw" | grep -q 'final class SiteObserverTests' || fail "swift record must sit in SiteObserverTests"
echo "$ctor_sw" | grep -q 'func testRecordFive' || fail "existing testRecordFive must stay"
echo "$ctor_sw" | grep -q 'SeatTests\|LoamTests' && fail "swift record must not sibling" || true
sib_sw="$("$SEAT" --no-seat --emit xctest -C "$CTOR" record)"
echo "$sib_sw" | grep -q 'SeatTests' || fail "--no-seat swift must sibling"
echo "$sib_sw" | grep -q 'testRecordFive' && fail "--no-seat sibling copied existing methods" || true
pass "swift record seats into SiteObserverTests"

echo "== seat fixture: XCTestCase + Swift Testing struct =="
SEATFIX="$ROOT/fixtures/seat"
seat_rec="$("$SEAT" --emit xctest -C "$SEATFIX" record)"
echo "$seat_rec"
echo "$seat_rec" | grep -q 'final class SiteObserverTests' || fail "seat fixture record not in SiteObserverTests"
echo "$seat_rec" | grep -q 'SeatTests' && fail "seat fixture record sibling" || true
echo "$seat_rec" | grep -q 'testRecordFive' || fail "seat fixture lost existing method"
diff_rec="$("$SEAT" --diff --emit xctest -C "$SEATFIX" record)"
echo "$diff_rec" | head -40
echo "$diff_rec" | grep -q '^+.*testRecordSiteProdDuration1\|^+    func testRecord' || fail "--diff must add a method"
echo "$diff_rec" | grep -q '^[-+]import XCTest' && fail "--diff must not rewrite the whole imports as a new file" || true
pass "seat fixture record; --diff is a patch against SiteObserverTests"

seat_det="$("$SEAT" -C "$SEATFIX" detect)"
echo "$seat_det"
echo "$seat_det" | grep -q 'struct PresenceArbiterTests' || fail "detect must sit in PresenceArbiterTests"
echo "$seat_det" | grep -q 'defaultTimeout' || fail "existing Swift Testing method must stay"
echo "$seat_det" | grep -q 'timeout: 0' || fail "timeout=0 world missing"
echo "$seat_det" | grep -q 'SeatTests\|XCTestCase' && fail "arbiter must not wrap a sibling XCTestCase" || true
pass "PresenceArbiter.detect seats into existing Swift Testing struct"

echo "== rename fixture: sow/hatch miss, seat emits (till gold) =="
"$ROOT/fixtures/rename/build.sh" "$TMP/rename"
LEFT="$TMP/rename/leftover"
HIST="$TMP/rename/hist"

echo "-- leftover: --no-follow (hatch identity) misses Brave --"
no_left="$("$SEAT" --no-follow --emit pytest -C "$LEFT" isBrowser)"
echo "$no_left"
echo "$no_left" | grep -q 'Brave Browser' && fail "--no-follow leftover leaked Brave" || true
pass "--no-follow leftover misses Brave"

echo "-- leftover: seat follow emits Brave under HEAD name --"
yes_left="$("$SEAT" --emit pytest -C "$LEFT" isBrowser)"
echo "$yes_left"
echo "$yes_left" | grep -q 'Brave Browser' || fail "seat leftover missing Brave"
echo "$yes_left" | grep -q 'isBrowser' || fail "seat leftover must emit HEAD name"
echo "$yes_left" | grep -q 'isWebApp(' && fail "seat leftover emitted dead name" || true
echo "$yes_left" | grep -q 'def test_safari' || fail "leftover must seat into existing test_web.py"
pass "seat leftover emits isBrowser(Brave)"

echo "-- leftover: query by dead name isWebApp --"
by_old="$("$SEAT" --emit pytest -C "$LEFT" isWebApp)"
echo "$by_old"
echo "$by_old" | grep -q 'Brave Browser' || fail "query isWebApp missed Brave"
echo "$by_old" | grep -q 'isBrowser' || fail "query isWebApp must still emit HEAD name"
pass "query isWebApp follows to isBrowser"

echo "-- leftover Swift XCTest --"
sw_left="$("$SEAT" --emit xctest -C "$LEFT" isBrowser)"
echo "$sw_left"
echo "$sw_left" | grep -q 'import XCTest' || fail "swift leftover not XCTest"
echo "$sw_left" | grep -q 'Brave Browser' || fail "swift leftover missing Brave"
echo "$sw_left" | grep -q 'XCTAssertTrue' || fail "swift leftover predicate must XCTAssertTrue"
echo "$sw_left" | grep -q '\.\.\.' && fail "swift leftover emitted ..." || true
echo "$sw_left" | grep -q 'WindowTitleParserTests' || fail "swift leftover must sit in existing class"
echo "$sw_left" | grep -q 'SeatTests' && fail "swift leftover sibling" || true
echo "$sw_left" | grep -q 'func testSafari' || fail "swift leftover lost existing testSafari"
pass "swift leftover XCTest"

echo "-- leftover --report shows aka --"
rep_left="$("$SEAT" --report --color never -C "$LEFT" isBrowser)"
echo "$rep_left"
echo "$rep_left" | grep -q 'aka' || fail "--report missing aka chain"
echo "$rep_left" | grep -q 'isWebApp' || fail "--report missing old name"
echo "$rep_left" | grep 'follow' | grep -q 'ParserTests.swift' && fail "test-path hop leaked into identity" || true
pass "report aka chain"

echo "-- leftover --aka-map --"
amap="$("$SEAT" --aka-map -C "$LEFT")"
echo "$amap"
echo "$amap" | grep -q $'aka\t' || fail "aka-map missing aka rows"
echo "$amap" | grep -q 'isWebApp' || fail "aka-map missing isWebApp"
pass "aka-map"

echo "-- hist: Brave lives only as last week's isWebApp literal --"
no_hist="$("$SEAT" --no-follow --emit pytest -C "$HIST" isBrowser)"
echo "$no_hist"
echo "$no_hist" | grep -q 'Brave Browser' && fail "--no-follow hist leaked Brave" || true
yes_hist="$("$SEAT" --emit pytest -C "$HIST" isBrowser)"
echo "$yes_hist"
echo "$yes_hist" | grep -q 'Brave Browser' || fail "seat hist missing Brave"
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
"$SEAT" --check -C "$LEFT" isBrowser >/tmp/seat-check-left.txt
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "leftover --check should exit 1, got $rc"
grep -q 'Brave Browser' /tmp/seat-check-left.txt || fail "--check leftover listing missing Brave"
grep -q 'import pytest\|def test_' /tmp/seat-check-left.txt && fail "--check leftover wrote a test file" || true
pass "leftover --check exits 1 and lists"

echo "== real repos (read-only) =="
GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"

if [ -d "$GHQ/sitbone" ]; then
  echo "-- sitbone isBrowser (default XCTest) --"
  sit="$("$SEAT" -C "$GHQ/sitbone" isBrowser)"
  echo "$sit"
  echo "$sit" | grep -q 'import XCTest' || fail "sitbone isBrowser must default to XCTest"
  echo "$sit" | grep -q '@testable import SitboneCore' || fail "sitbone missing @testable import SitboneCore"
  echo "$sit" | grep -q 'Brave Browser' || fail "sitbone missing Brave Browser"
  echo "$sit" | grep -q 'func test' || fail "sitbone missing XCTest func"
  echo "$sit" | grep -q 'XCTAssertTrue' || fail "sitbone isBrowser member must XCTAssertTrue"
  echo "$sit" | grep -q 'import pytest' && fail "sitbone isBrowser leaked pytest" || true
  echo "$sit" | grep -q '\.\.\.' && fail "sitbone isBrowser emitted invalid Swift ..." || true
  echo "$sit" | grep -q 'final class WindowTitleParserTests' || fail "sitbone isBrowser must sit in WindowTitleParserTests"
  echo "$sit" | grep -q 'SeatTests\|LoamTests' && fail "sitbone isBrowser must not sibling" || true
  echo "$sit" | grep -q 'func testChromeTitle' || fail "sitbone isBrowser lost existing testChromeTitle"
  echo "-- sitbone extractSiteName must be silent --"
  ext="$("$SEAT" --report --color never -C "$GHQ/sitbone" --min-callers 1 extractSiteName || true)"
  echo "$ext"
  echo "$ext" | grep -q 'extractSiteName' && fail "extractSiteName has no production callers" || true
  echo "-- sitbone record --"
  rec="$("$SEAT" --report --color never -C "$GHQ/sitbone" --min-callers 1 record || true)"
  echo "$rec"
  echo "$rec" | grep -q 'duration=1' || fail "sitbone record missing duration=1"
  echo "$rec" | grep -q 'io=timeout' && fail "sitbone duration=1 must not be timeout" || true
  echo "$rec" | grep -q 'seat  SiteObserverTests' || fail "sitbone --report missing seat SiteObserverTests"
  rec_swift="$("$SEAT" -C "$GHQ/sitbone" record)"
  echo "$rec_swift"
  echo "$rec_swift" | grep -q 'XCTSkip' || fail "sitbone record dyn world must XCTSkip"
  echo "$rec_swift" | grep -q '\.\.\.' && fail "sitbone record emitted invalid Swift ..." || true
  echo "$rec_swift" | grep -q 'let observer = SiteObserver(' || fail "sitbone record must construct SiteObserver()"
  echo "$rec_swift" | grep -q 'SiteObserver.record(' && fail "sitbone record must not emit Type.method" || true
  echo "$rec_swift" | grep -q 'final class SiteObserverTests' || fail "sitbone record must sit in SiteObserverTests"
  echo "$rec_swift" | grep -q 'SeatTests\|LoamTests' && fail "sitbone record must not sibling" || true
  echo "$rec_swift" | grep -q 'func testRecordFlowVisit' || fail "sitbone record lost existing testRecordFlowVisit"
  echo "$rec" | grep -q 'construct  SiteObserver()' || fail "sitbone --report missing construct line"
  rec_off="$("$SEAT" --no-construct --no-seat -C "$GHQ/sitbone" record)"
  echo "$rec_off"
  echo "$rec_off" | grep -q 'let observer = SiteObserver(' && fail "--no-construct --no-seat sitbone leaked receiver" || true
  echo "$rec_off" | grep -q 'SeatTests' || fail "--no-seat sitbone record must sibling"
  arb="$("$SEAT" --report --color never -C "$GHQ/sitbone" logEntry || true)"
  echo "$arb"
  echo "$arb" | grep -q 'PresenceArbiter' || fail "sitbone logEntry must be PresenceArbiter"
  echo "$arb" | grep -q 'seat  PresenceArbiterTests' || fail "sitbone logEntry must seat into PresenceArbiterTests"
  arb_sw="$("$SEAT" -C "$GHQ/sitbone" logEntry)"
  echo "$arb_sw" | tail -30
  echo "$arb_sw" | grep -q 'struct PresenceArbiterTests' || fail "logEntry must sit in PresenceArbiterTests struct"
  echo "$arb_sw" | grep -q 'SeatTests' && fail "logEntry must not sibling" || true
  det="$("$SEAT" --report --color never -C "$GHQ/sitbone" detect || true)"
  echo "$det"
  echo "$det" | grep -q 'SystemSleepTests' && fail "detect must not sit in SystemSleepTests (function-name false friend)" || true
  echo "-- sitbone --check isBrowser --"
  set +e
  "$SEAT" --check -C "$GHQ/sitbone" isBrowser >/tmp/seat-sitbone-isbrowser.txt
  rc=$?
  set -e
  [ "$rc" -eq 1 ] || fail "sitbone isBrowser --check should exit 1, got $rc"
  grep -q 'import XCTest' /tmp/seat-sitbone-isbrowser.txt && fail "sitbone --check must list, not write XCTest" || true
  grep -q 'Brave Browser' /tmp/seat-sitbone-isbrowser.txt || fail "sitbone --check listing missing Brave"
  if command -v swift >/dev/null; then
    echo "-- sitbone swift test overlay (--apply into existing classes) --"
    overlay="$TMP/sitbone-overlay"
    rsync -a --exclude .build --exclude .git --exclude scratch \
      "$GHQ/sitbone/" "$overlay/"
    "$SEAT" --apply -C "$overlay" isBrowser || fail "apply isBrowser"
    "$SEAT" --apply -C "$overlay" record || fail "apply record"
    ls "$overlay/Tests/SitboneCoreTests" | grep -q 'SeatTests\|LoamTests' && fail "apply wrote a sibling *SeatTests file" || true
    grep -q 'testIsBrowserAppNameBraveBrowser' \
      "$overlay/Tests/SitboneCoreTests/WindowTitleParserTests.swift" \
      || fail "apply did not seat Brave into WindowTitleParserTests"
    grep -q 'testChromeTitle' \
      "$overlay/Tests/SitboneCoreTests/WindowTitleParserTests.swift" \
      || fail "apply dropped existing testChromeTitle"
    grep -q 'testRecordSitePhaseDuration1' \
      "$overlay/Tests/SitboneCoreTests/SiteObserverTests.swift" \
      || fail "apply did not seat duration=1 into SiteObserverTests"
    grep -q 'testRecordFlowVisit' \
      "$overlay/Tests/SitboneCoreTests/SiteObserverTests.swift" \
      || fail "apply dropped existing testRecordFlowVisit"
    swift_out="$(cd "$overlay" && swift test --filter WindowTitleParserTests 2>&1)" || {
      echo "$swift_out"
      fail "seated sitbone isBrowser XCTest failed to build or run"
    }
    echo "$swift_out" | tail -30
    echo "$swift_out" | grep -q "testIsBrowserAppNameBraveBrowser" || fail "swift test missing Brave case"
    echo "$swift_out" | grep -q "testChromeTitle" || fail "swift test missing existing Chrome title case"
    echo "$swift_out" | grep -q "0 failures" || fail "seated WindowTitleParserTests had failures"
    pass "sitbone isBrowser seated into WindowTitleParserTests and ran"
    rec_swift_out="$(cd "$overlay" && swift test --filter SiteObserverTests 2>&1)" || {
      echo "$rec_swift_out"
      fail "seated sitbone record XCTest failed to build or run"
    }
    echo "$rec_swift_out" | tail -30
    echo "$rec_swift_out" | grep -q "testRecordSitePhaseDuration1" || fail "swift test missing seated record case"
    echo "$rec_swift_out" | grep -q "testRecordFlowVisit" || fail "swift test missing existing record case"
    echo "$rec_swift_out" | grep -q "0 failures" || fail "seated SiteObserverTests had failures"
    echo "$rec_swift_out" | grep -q "skipped" || fail "dyn record world should XCTSkip"
    pass "sitbone record seated into SiteObserverTests and ran (skip is ok)"
  else
    echo "skip sitbone swift test overlay (swift not present)"
  fi
  echo "-- sitbone stopSession (real rename → stopCapture) --"
  sess="$("$SEAT" --report --color never -C "$GHQ/sitbone" stopSession || true)"
  echo "$sess"
  echo "$sess" | grep -q 'stopCapture' || fail "sitbone stopSession must follow to stopCapture"
  echo "$sess" | grep -q 'aka' || fail "sitbone stopSession missing aka (sown identity)"
  amap_s="$("$SEAT" --aka-map -C "$GHQ/sitbone" stopSession)"
  echo "$amap_s"
  echo "$amap_s" | grep -q 'stopSession' || fail "aka-map missing stopSession"
  echo "-- sitbone summary (follow on) --"
  "$SEAT" --summary --color never -C "$GHQ/sitbone" || fail "sitbone summary"
  pass "sitbone isBrowser"
else
  echo "skip sitbone (not present)"
fi

if [ -d "$GHQ/kizu" ]; then
  echo "-- kizu run_split_command --"
  kout="$("$SEAT" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target --min-callers 1 run_split_command || true)"
  echo "$kout"
  echo "$kout" | grep -q 'Ghostty' || fail "kizu missing Ghostty production context"
  echo "$kout" | grep -q 'sh ok\|sh failing' && fail "kizu test-only sh context leaked" || true
  "$SEAT" --emit pytest -C "$GHQ/kizu" --exclude tests/e2e --exclude target run_split_command | head -30
  echo "-- kizu install_claude_code (dead name; sow/hatch silent) --"
  k_no="$("$SEAT" --no-follow --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_no"
  echo "$k_no" | grep -q 'install_settings_hook_agent' && fail "no-follow should not see dead name" || true
  k_yes="$("$SEAT" --report --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target install_claude_code || true)"
  echo "$k_yes"
  echo "$k_yes" | grep -q 'install_settings_hook_agent' || fail "kizu install_claude_code must follow"
  echo "$k_yes" | grep -q 'aka' || fail "kizu missing aka chain"
  n_due="$(echo "$k_yes" | grep -c 'due  ' || true)"
  [ "$n_due" -ge 4 ] || fail "kizu install_claude_code expected 4 due worlds, got $n_due"
  echo "$k_yes" | grep -q 'io=fs' || fail "kizu project_root worlds must rank as fs (not body)"
  echo "-- kizu summary --"
  "$SEAT" --summary --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target || fail "kizu summary"
  pass "kizu install_claude_code follow + run_split_command"
fi

if [ -d "$GHQ/tenaoshi" ]; then
  echo "-- tenaoshi PromptStore.validate --"
  tout="$("$SEAT" --report --color never -C "$GHQ/tenaoshi" --min-callers 1 validate || true)"
  echo "$tout"
  echo "-- tenaoshi summary --"
  "$SEAT" --summary --color never -C "$GHQ/tenaoshi" --exclude dist --exclude .build || fail "tenaoshi summary"
  pass "tenaoshi census"
fi

pass "demo complete"
exit 0
