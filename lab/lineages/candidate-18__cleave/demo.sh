#!/usr/bin/env bash
# Exercise cleave against the ugly fixture tree and, when present, real repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLEAVE="$ROOT/cleave"
chmod +x "$CLEAVE"

if ! command -v python3 >/dev/null; then
  echo "demo.sh: python3 is required" >&2
  exit 1
fi

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== self-test =="
"$CLEAVE" --self-test || fail "self-test"
pass "self-test"

echo "== ugly fixtures =="
UGLY="$ROOT/fixtures/ugly"
out="$("$CLEAVE" --color never -C "$UGLY" --min-callers 1 connect listen isBrowser)"
echo "$out"
echo "$out" | grep -q 'prod-only-const' || fail "python/js connect-or-listen missing prod-only-const"
echo "$out" | grep -q 'timeout=0' || fail "python connect missing timeout=0 world/tilt"
echo "$out" | grep -q 'prod-open' || fail "missing prod-open (tests const, prod dynamic)"
echo "$out" | grep -q 'isBrowser' || fail "swift isBrowser missing"
echo "$out" | grep -q 'Chrome' || fail "swift test literals missing"

porc="$("$CLEAVE" --porcelain -C "$UGLY")"
echo "$porc" | grep -q $'tilt\tconnect\tprod-only-const\t' || fail "porcelain prod-only-const"
echo "$porc" | grep -q 'timeout' || fail "porcelain timeout world"
echo "$porc" | grep -q 'unwitnessed-member' || fail "porcelain collection envelope"
pass "ugly fixture tilts"

# colon / spaces / unicode files must be parsed, not crash
"$CLEAVE" --summary -C "$UGLY" >/tmp/cleave-ugly-summary.txt
cat /tmp/cleave-ugly-summary.txt
grep -q 'tilt_fns=' /tmp/cleave-ugly-summary.txt || fail "summary line"

# comments must not invent a timeout=99 world
echo "$porc" | grep -q 'timeout=99' && fail "comment leaked as a call" || true
pass "comments ignored"

# nested git must not hijack discovery
TMP="$(mktemp -d "${TMPDIR:-/tmp}/cleave-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
cp -R "$UGLY" "$TMP/ugly"
mkdir -p "$TMP/ugly/vendor/nested/src"
echo 'def inner(x): return x' > "$TMP/ugly/vendor/nested/src/inner.py"
git -C "$TMP/ugly/vendor/nested" init -q
git -C "$TMP/ugly/vendor/nested" add src/inner.py
git -C "$TMP/ugly/vendor/nested" \
  -c user.name=nested -c user.email=nested@example.com \
  commit -q -m 'nested repo seed'
"$CLEAVE" --summary -C "$TMP/ugly" >/tmp/cleave-nested-summary.txt
# vendor/ is skipped as a dir name; nested git should not crash either
pass "nested git walk"

echo "== --check exit code =="
set +e
"$CLEAVE" --check --porcelain -C "$UGLY" >/dev/null
rc=$?
set -e
[ "$rc" -eq 1 ] || fail "--check should exit 1 on tilts, got $rc"
pass "--check exits 1"

echo "== real repos (read-only) =="
dogfood() {
  local name="$1" path="$2" extra=("${@:3}")
  if [ ! -d "$path" ]; then
    echo "skip $name (not present)"
    return 0
  fi
  echo "-- $name --"
  "$CLEAVE" --summary --color never -C "$path" "${extra[@]}" || fail "summary $name"
}

GHQ="${GHQ_ROOT:-$HOME/ghq/github.com/annenpolka}"
dogfood sitbone "$GHQ/sitbone"
dogfood kizu "$GHQ/kizu" --exclude tests/e2e --exclude target
dogfood voidtrace "$GHQ/voidtrace" --exclude node_modules --exclude dist
dogfood tenaoshi "$GHQ/tenaoshi"
dogfood skills "$GHQ/skills"
dogfood stratal "$GHQ/stratal"

if [ -d "$GHQ/sitbone" ]; then
  echo "-- sitbone isBrowser --"
  "$CLEAVE" --color never -C "$GHQ/sitbone" --min-callers 1 isBrowser extractSiteName || true
fi

pass "demo complete"
exit 0
