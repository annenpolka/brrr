#!/usr/bin/env bash
# Exercise sow against the ugly fixture tree and, when present, real repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SOW="$ROOT/sow"
chmod +x "$SOW"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== self-test =="
"$SOW" --self-test || fail "self-test"
pass "self-test"

echo "== ugly fixtures =="
UGLY="$ROOT/fixtures/ugly"
out="$("$SOW" --color never -C "$UGLY" --min-callers 1 connect listen isBrowser)"
echo "$out"
echo "$out" | grep -q 'timeout=0' || fail "python connect missing timeout=0 production world"
echo "$out" | grep -q 'db.example.com' || fail "python connect missing production host literal"
echo "$out" | grep -q 'Brave Browser' || fail "swift collection member missing"
echo "$out" | grep -q 'isBrowser' || fail "swift isBrowser missing"
echo "$out" | grep -q 'due' || fail "missing due fixtures"
# killed: must not speak tilt / test-only worlds
echo "$out" | grep -q $'tilt\t\|  TILT\|prod-only-const\|test-only-const' && fail "tilt language leaked" || true
echo "$out" | grep -q 'localhost' && fail "test-only localhost world leaked as due" || true

# rust lifetime signatures must not swallow later functions
life="$("$SOW" --color never -C "$UGLY" --min-callers 1 later)"
echo "$life"
echo "$life" | grep -q 'later' || fail "lifetime: later missing (swallowed by new?)"
echo "$life" | grep -q '{x=1}' || fail "lifetime: later(1) production world missing"
echo "$life" | grep -q '{x=0}' && fail "lifetime: later(0) test world leaked as due" || true
pass "rust lifetimes do not swallow later fns"

porc="$("$SOW" --porcelain -C "$UGLY")"
echo "$porc" | grep -q $'fixture\tconnect\t' || fail "porcelain connect fixture"
echo "$porc" | grep -q 'timeout=0' || fail "porcelain timeout=0 world"
echo "$porc" | grep -q 'Brave Browser' || fail "porcelain collection member"
echo "$porc" | grep -q $'tilt\t' && fail "porcelain tilt row" || true
pass "ugly fixture seeds"

# json is test-generator input
js="$("$SOW" --json -C "$UGLY" connect)"
echo "$js" | grep -q '"tool": "sow"' || fail "json tool tag"
echo "$js" | grep -q '"fixtures"' || fail "json fixtures array"
echo "$js" | grep -q 'db.example.com' || fail "json production host"
pass "json generator input"

# ndjson is one object per fixture
nd="$("$SOW" --ndjson -C "$UGLY" isBrowser)"
echo "$nd" | grep -q '"kind": "member"' || fail "ndjson member"
echo "$nd" | grep -q 'Brave' || fail "ndjson Brave"
pass "ndjson stream"

# comments must not invent a timeout=99 world
echo "$porc" | grep -q 'timeout=99' && fail "comment leaked as a call" || true
pass "comments ignored"

# colon / spaces / unicode files must be parsed, not crash
"$SOW" --summary -C "$UGLY" >/tmp/sow-ugly-summary.txt
cat /tmp/sow-ugly-summary.txt
grep -q 'due_fns=' /tmp/sow-ugly-summary.txt || fail "summary line"
pass "ugly summary"

# nested git must not hijack discovery
TMP="$(mktemp -d "${TMPDIR:-/tmp}/sow-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R "$UGLY" "$TMP/ugly"
mkdir -p "$TMP/ugly/vendor/nested/src"
echo 'def inner(x): return x' > "$TMP/ugly/vendor/nested/src/inner.py"
git -C "$TMP/ugly/vendor/nested" init -q
git -C "$TMP/ugly/vendor/nested" add src/inner.py
git -C "$TMP/ugly/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'
"$SOW" --summary -C "$TMP/ugly" >/tmp/sow-nested-summary.txt
pass "nested git walk"

echo "== --check exit code =="
set +e
"$SOW" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check should exit 1 on due fixtures, got $rc"
pass "--check exits 1"

echo "== --emit pytest =="
stubs="$("$SOW" --emit pytest -C "$UGLY" isBrowser)"
echo "$stubs"
echo "$stubs" | grep -q 'def test_isBrowser_appName_Brave_Browser' || fail "pytest stub name"
echo "$stubs" | grep -q 'Brave Browser' || fail "pytest stub value"
pass "emit pytest"

echo "== real repos (read-only) =="
dogfood() {
  local name="$1" path="$2" extra=("${@:3}")
  if [ ! -d "$path" ]; then
    echo "skip $name (not present)"
    return 0
  fi
  echo "-- $name --"
  "$SOW" --summary --color never -C "$path" "${extra[@]}" || fail "summary $name"
}

GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"
dogfood sitbone "$GHQ/sitbone"
dogfood kizu "$GHQ/kizu" --exclude tests/e2e --exclude target

if [ -d "$GHQ/sitbone" ]; then
  echo "-- sitbone isBrowser --"
  "$SOW" --color never -C "$GHQ/sitbone" --min-callers 1 isBrowser extractSiteName || true
  echo "-- sitbone record (duration=1) --"
  rec="$("$SOW" --color never -C "$GHQ/sitbone" --min-callers 1 record || true)"
  echo "$rec"
  echo "$rec" | grep -q 'duration=1' || fail "sitbone record missing duration=1 production world"
  ext="$("$SOW" --color never -C "$GHQ/sitbone" --min-callers 1 extractSiteName || true)"
  echo "$ext"
  echo "$ext" | grep -q 'extractSiteName' && fail "extractSiteName has no production callers; must be silent" || true
  stubs="$("$SOW" --emit pytest -C "$GHQ/sitbone" record || true)"
  echo "$stubs" | grep -q 'duration: 1' || fail "sitbone emit missing duration: 1"
fi
if [ -d "$GHQ/kizu" ]; then
  echo "-- kizu run_split_command --"
  kout="$("$SOW" --color never -C "$GHQ/kizu" --exclude tests/e2e --exclude target --min-callers 1 run_split_command || true)"
  echo "$kout"
  echo "$kout" | grep -q 'Ghostty' || fail "kizu missing Ghostty production context"
  echo "$kout" | grep -q 'sh ok\|sh failing' && fail "kizu test-only sh context leaked" || true
  "$SOW" --emit pytest -C "$GHQ/kizu" --exclude tests/e2e --exclude target run_split_command | head -30
fi

pass "demo complete"
exit 0
