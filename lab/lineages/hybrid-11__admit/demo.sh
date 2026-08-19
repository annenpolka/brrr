#!/usr/bin/env bash
# Exercise admit. Exit 0 only if every case holds.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/admit"
PY="${PYTHON:-python3}"
ADMIT=("$PY" "$ROOT/admit.py")
UGLY="$ROOT/fixtures/ugly"
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

# Run a generated pytest module with a stub pytest.skip.
run_admitted() {
  local file="$1" root="$2"
  "$PY" - "$file" "$root" <<'PY'
import importlib.util, sys, types, traceback
from pathlib import Path

mod_path = Path(sys.argv[1])
root = Path(sys.argv[2])
sys.path.insert(0, str(root))

class Skip(Exception):
    def __init__(self, msg=""):
        self.msg = msg

pytest = types.ModuleType("pytest")
pytest.skip = lambda msg="": (_ for _ in ()).throw(Skip(msg))
sys.modules["pytest"] = pytest

spec = importlib.util.spec_from_file_location("admitted", mod_path)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print(f"LOAD_FAIL {e}")
    sys.exit(2)

n = skip = fail = err = 0
for name in sorted(dir(mod)):
    if not name.startswith("test_"):
        continue
    fn = getattr(mod, name)
    if not callable(fn):
        continue
    n += 1
    try:
        fn()
        print(f"PASS {name}")
    except Skip as s:
        skip += 1
        print(f"SKIP {name} {s.msg}")
    except Exception as e:
        fail += 1
        print(f"FAIL {name} {e}")
        traceback.print_exc()
print(f"SUMMARY n={n} skip={skip} fail={fail}")
sys.exit(1 if fail else 0)
PY
}

echo "======== 1. self-test ========"
"${ADMIT[@]}" --self-test
ok "admit --self-test"

echo "======== 2. Brave is OPEN (file macOS comment is not the world) ========"
swift_out="$("${ADMIT[@]}" -C "$UGLY" isBrowser)"
echo "$swift_out"
assert_contains "$swift_out" "import XCTest" "isBrowser defaults to XCTest"
assert_contains "$swift_out" "AdmitTests" "AdmitTests class"
assert_contains "$swift_out" "Brave Browser" "Brave pinned"
assert_contains "$swift_out" "XCTAssertTrue" "member oracle asserts"
assert_contains "$swift_out" "visa OPEN" "Brave visa OPEN"
assert_absent "$swift_out" "admitMisses" "OPEN isBrowser has no skip helper"
assert_absent "$swift_out" "XCTSkip" "OPEN isBrowser has no XCTSkip"
assert_absent "$swift_out" "BraveBrowser_2" "member+world dupe dropped"
assert_absent "$swift_out" "HatchTests" "must not speak hatch class names"
assert_absent "$swift_out" "import pytest" "isBrowser is not pytest"

echo "======== 3. Alice home is skipif + assert ========"
py_out="$("${ADMIT[@]}" -C "$UGLY" load_profile)"
echo "$py_out"
assert_contains "$py_out" "visa BOUND" "load_profile BOUND"
assert_contains "$py_out" "fate=skipif" "load_profile skipif"
assert_contains "$py_out" "_admit_misses" "pytest visa helper"
assert_contains "$py_out" "from src.profile import load_profile" "subject import"
if [[ "$py_out" == *'assert load_profile'* && "$py_out" == *'/Users/alice'* ]]; then
  ok "BOUND world asserts"
else
  fail "BOUND world asserts" "$py_out"
fi
assert_contains "$py_out" "HOME=/Users/alice" "require Alice HOME"

echo "======== 4. Runtime: Alice skips; hatch-style assert would fail ========"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/admit-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
"${ADMIT[@]}" -C "$UGLY" load_profile > "$TMP/test_alice.py"
alice_run="$(run_admitted "$TMP/test_alice.py" "$UGLY" || true)"
echo "$alice_run"
assert_contains "$alice_run" "SKIP" "alice tests skip on this host"
assert_contains "$alice_run" "visa MISS" "skip names the visa miss"
assert_contains "$alice_run" "SUMMARY n=" "runner counted tests"
assert_absent "$alice_run" "FAIL " "alice must skip, not fail"

# The production world is a real oracle: /Users/alice is not a directory here.
if "$PY" -c 'import os,sys; sys.path.insert(0,"'"$UGLY"'"); from src.profile import load_profile; raise SystemExit(0 if not load_profile("/Users/alice") else 1)'; then
  ok "Alice home does not exist here (hatch-style assert would fail)"
else
  fail "Alice home does not exist here" "load_profile(/Users/alice) was True"
fi

echo "======== 5. Live HOME MATCH asserts and passes ========"
HOME_NOW="$("$PY" -c 'import pathlib; print(pathlib.Path.home().as_posix())')"
mkdir -p "$TMP/live/src" "$TMP/live/tests"
cat > "$TMP/live/src/probe.py" <<EOF
import os

def probe(home):
    return os.path.isdir(home)

def go():
    probe("$HOME_NOW")
EOF
cat > "$TMP/live/tests/test_probe.py" <<'EOF'
from src.probe import probe

def test_tmp():
    probe("/tmp")
EOF
live_src="$("${ADMIT[@]}" -C "$TMP/live" probe)"
echo "$live_src"
assert_contains "$live_src" "visa BOUND" "live probe BOUND"
assert_contains "$live_src" "fate=skipif" "live probe skipif"
assert_contains "$live_src" "$HOME_NOW" "live probe pins this HOME"
"${ADMIT[@]}" -C "$TMP/live" probe > "$TMP/test_live.py"
live_run="$(run_admitted "$TMP/test_live.py" "$TMP/live")"
echo "$live_run"
assert_contains "$live_run" "PASS" "live HOME MATCH runs the assertion"
assert_absent "$live_run" "SKIP" "live HOME must not skip"
assert_absent "$live_run" "FAIL " "live HOME must pass"

echo "======== 6. Textbook quote is SPEC (not a skip) ========"
quote_out="$("${ADMIT[@]}" -C "$UGLY" quote)"
echo "$quote_out"
assert_contains "$quote_out" "visa SPEC" "quote SPEC"
assert_absent "$quote_out" "_admit_misses" "SPEC has no skip helper"
assert_absent "$quote_out" "pytest.skip" "SPEC does not skip"
assert_contains "$quote_out" "/home/user/project" "textbook /home/user still emitted"
assert_contains "$quote_out" "/Users/John Doe/kizu" "John Doe still emitted"

echo "======== 7. GitHub title is not USER=you ========"
title_out="$("${ADMIT[@]}" -C "$UGLY" extract_title)"
echo "$title_out"
assert_contains "$title_out" "visa OPEN" "github title OPEN"
assert_absent "$title_out" "pytest.skip" "github title does not skip"
assert_absent "$title_out" "USER=" "github title does not visa USER"
assert_contains "$title_out" "Pull Request #3" "recovered full GitHub title"
# the call must not use hatch's 45-char cut
call_side="${title_out#*extract_title(}"
assert_absent "$call_side" "Pull Reque..." "call is the production world, not an abridgement"

echo "======== 8. Anti-concat: same file, Brave OPEN / loadHome skipif ========"
both="$("${ADMIT[@]}" --emit xctest -C "$UGLY" isBrowser loadHome)"
echo "$both"
assert_contains "$both" "visa OPEN" "Brave still OPEN beside Alice"
assert_contains "$both" "visa BOUND" "loadHome BOUND in the same file"
assert_contains "$both" "admitMisses" "helper only because loadHome is BOUND"
# Brave test function must not throw XCTSkip
brave_body="$(printf '%s\n' "$both" | awk '/testIsBrowserAppNameBraveBrowser\(/,/func test/ {print}' | head -n 20)"
assert_absent "$brave_body" "XCTSkip" "Brave body has no XCTSkip"
assert_contains "$both" "XCTSkip" "loadHome uses XCTSkip"
# Concat lie: treat the production file as one golden. Alice's path
# stains the whole file. Brave is then skipped even though its world
# is OPEN. (visa of App.swift *as source* demotes textbook alice;
# a snapshot path is how you wrap hatch output as an oracle.)
file_visa="$("$PY" -c "
import visalib
from pathlib import Path
v = visalib.infer(Path('$UGLY/src/App.swift').read_text(), 'production.world.snap')
print(v.status, v.require)
")"
echo "file-as-golden visa: $file_visa"
assert_contains "$file_visa" "BOUND" "file-as-golden visa is BOUND (concat would skip Brave)"
assert_contains "$file_visa" "/Users/alice" "file-as-golden requires Alice"

echo "======== 9. dyn timeout is skip, not visa MISS ========"
conn="$("${ADMIT[@]}" -C "$UGLY" connect)"
echo "$conn"
assert_contains "$conn" "dynamic slots: host" "timeout=0 is dyn skip"
assert_contains "$conn" "db.example.com" "production host still asserted/called"
assert_absent "$conn" "visa MISS" "dyn skip is not a visa miss"

echo "======== 10. --check / --bound / porcelain / summary ========"
set +e
"${ADMIT[@]}" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
assert_exit "$rc" 1 "--check exits 1 when dues exist"

set +e
"${ADMIT[@]}" --check -C "$UGLY" isBrowser > "$TMP/check.swift"
rc=$?
set -e
assert_exit "$rc" 1 "--check isBrowser exits 1"
assert_contains "$(cat "$TMP/check.swift")" "import XCTest" "--check stdout is still the test file"

porc="$("${ADMIT[@]}" --porcelain -C "$UGLY" load_profile)"
assert_contains "$porc" $'admit\tload_profile\t' "porcelain tag"
assert_contains "$porc" $'skipif\tBOUND\t' "porcelain skipif BOUND"

sum="$("${ADMIT[@]}" --summary -C "$UGLY")"
echo "$sum"
assert_contains "$sum" "skipif=" "summary skipif"
assert_contains "$sum" "bound=" "summary bound"

bound_rep="$("${ADMIT[@]}" --bound --report --color never -C "$UGLY")"
echo "$bound_rep"
assert_contains "$bound_rep" "load_profile" "--bound keeps Alice"
assert_absent "$bound_rep" "isBrowser" "--bound drops OPEN Brave"
assert_absent "$bound_rep" "extract_title" "--bound drops OPEN titles"

echo "======== 11. sitbone (read-only) ========"
GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"
if [ -d "$GHQ/sitbone" ]; then
  sit="$("${ADMIT[@]}" -C "$GHQ/sitbone" isBrowser)"
  echo "$sit"
  assert_contains "$sit" "@testable import SitboneCore" "sitbone module"
  assert_contains "$sit" "Brave Browser" "sitbone Brave"
  assert_contains "$sit" "XCTAssertTrue" "sitbone member oracle"
  assert_contains "$sit" "AdmitTests" "sitbone AdmitTests"
  # six OPEN members, no skip
  nopen="$(printf '%s\n' "$sit" | grep -c 'visa OPEN' || true)"
  if [[ "$nopen" -ge 6 ]]; then ok "sitbone isBrowser 6 OPEN ($nopen)"
  else fail "sitbone isBrowser 6 OPEN" "open=$nopen"
  fi
  assert_absent "$sit" "XCTSkip" "sitbone isBrowser has no skip"
  assert_absent "$sit" "admitMisses" "sitbone isBrowser needs no helper"

  rec="$("${ADMIT[@]}" -C "$GHQ/sitbone" record)"
  echo "$rec"
  assert_contains "$rec" "XCTSkip" "sitbone record dyn is XCTSkip"
  assert_contains "$rec" "duration=1" "sitbone record pins duration=1"
  assert_absent "$rec" "visa MISS" "sitbone record skip is dyn, not visa"

  ext="$("${ADMIT[@]}" --report --color never -C "$GHQ/sitbone" extractSiteName || true)"
  echo "$ext"
  if [[ "$ext" == *"extractSiteName"* ]]; then
    fail "extractSiteName silent" "$ext"
  else
    ok "extractSiteName has no production callers"
  fi

  ssum="$("${ADMIT[@]}" --summary -C "$GHQ/sitbone")"
  echo "$ssum"
  assert_contains "$ssum" "bound=0" "sitbone production leaked no machine"
  assert_contains "$ssum" "skipif=0" "sitbone skipif=0"

  set +e
  "${ADMIT[@]}" --check --bound -C "$GHQ/sitbone" >/dev/null
  brc=$?
  set -e
  assert_exit "$brc" 0 "sitbone --check --bound is clean (no machine-tied debt)"

  set +e
  "${ADMIT[@]}" --check -C "$GHQ/sitbone" isBrowser > "$TMP/sit-isbrowser.swift"
  src=$?
  set -e
  assert_exit "$src" 1 "sitbone isBrowser --check still 1 (dues exist)"

  applescript="$("${ADMIT[@]}" -C "$GHQ/sitbone" runAppleScript)"
  echo "$applescript"
  assert_contains "$applescript" "tell application \"Safari\"" "sitbone recovered Safari AppleScript"
  assert_contains "$applescript" "front document" "sitbone recovered full script body"
  assert_contains "$applescript" "end tell" "sitbone recovered closing tell"

  if command -v swift >/dev/null; then
    echo "-- sitbone swift test overlay --"
    overlay="$TMP/sitbone-overlay"
    rsync -a --exclude .build --exclude .git --exclude scratch \
      "$GHQ/sitbone/" "$overlay/"
    "${ADMIT[@]}" -C "$GHQ/sitbone" isBrowser \
      > "$overlay/Tests/SitboneCoreTests/AdmitIsBrowserTests.swift"
    if swift_out="$(cd "$overlay" && swift test --filter WindowTitleParserAdmitTests 2>&1)"; then
      echo "$swift_out" | tail -n 20
      ok "sitbone overlay AdmitTests passed"
    else
      echo "$swift_out"
      fail "sitbone overlay AdmitTests" "swift test failed"
    fi
  else
    echo "skip sitbone overlay (no swift)"
  fi
else
  echo "skip sitbone (not cloned)"
fi

echo "======== 12. ugly rust lifetimes still parse ========"
life="$("${ADMIT[@]}" --report --color never -C "$UGLY" later)"
echo "$life"
assert_contains "$life" "later" "lifetime later survived"
assert_contains "$life" "{x=1}" "later(1) due"

echo
echo "passed=$passed failed=$failed"
if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
exit 0
