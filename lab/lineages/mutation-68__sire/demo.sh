#!/usr/bin/env bash
# Exercise sire: leftover locator → natal change.
# Not git blame. Not a leftover-name walker.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SIRE="$ROOT/sire"
chmod +x "$SIRE"

pass=0
fail=0

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  ok  $label"
    pass=$((pass + 1))
  else
    echo "  FAIL $label"
    echo "    missing: $needle"
    echo "$haystack" | sed 's/^/    /' | head -80
    fail=$((fail + 1))
  fi
}

assert_not_contains() {
  local haystack="$1" needle="$2" label="$3"
  if grep -Fq -- "$needle" <<<"$haystack"; then
    echo "  FAIL $label"
    echo "    unexpectedly found: $needle"
    echo "$haystack" | sed 's/^/    /' | head -80
    fail=$((fail + 1))
  else
    echo "  ok  $label"
    pass=$((pass + 1))
  fi
}

assert_exit() {
  local got="$1" want="$2" label="$3"
  if [[ "$got" == "$want" ]]; then
    echo "  ok  $label (exit $got)"
    pass=$((pass + 1))
  else
    echo "  FAIL $label (exit $got, want $want)"
    fail=$((fail + 1))
  fi
}

echo "== self-test =="
set +e
"$SIRE" self-test
st=$?
set -e
assert_exit "$st" 0 "embedded natal/locator/naive-vs-typed tests"

RUN="$ROOT/fixtures/.run"
rm -rf "$RUN"
mkdir -p "$RUN"

echo
echo "== joint fixture: leftover locator names the rename commit =="
FIX="$RUN/joint"
mkdir -p "$FIX/docs" "$FIX/tests"
git -C "$FIX" init -q
git -C "$FIX" config user.email "sire@example.test"
git -C "$FIX" config user.name "sire"

cat > "$FIX/core.py" << 'EOF'
t1 = 15
present_threshold = 0.4
PORT = 8080
HOOK_TIMEOUT = 10
ENABLE_CACHE = True
EOF

cat > "$FIX/plugin.json" << 'EOF'
{
  "name": "toy",
  "version": "0.3.0",
  "hooks": {
    "timeout": 10
  }
}
EOF

cat > "$FIX/docs/how to set (t1).md" << 'EOF'
# Timing

T1 is 15 seconds.
The present_threshold is 0.4.
plugin version 0.3.0, hook timeout 10 seconds.
Listen on 8080.
Cache is enabled (`ENABLE_CACHE = True`).
shipped 2024-10-01
EOF

cat > "$FIX/tests/test_core.py" << 'EOF'
from core import t1, present_threshold

def test_t1():
    assert t1 == 15
    assert present_threshold == 0.4
EOF

git -C "$FIX" add core.py plugin.json docs tests
git -C "$FIX" commit -q -m 'introduce t1=15 present_threshold=0.4 version=0.3.0 timeout=10'

cat > "$FIX/core.py" << 'EOF'
driftDelay = 15
presentThreshold = 0.45
PORT = 8080
HOOK_TIMEOUT = 30
ENABLE_CACHE = False
EOF

cat > "$FIX/plugin.json" << 'EOF'
{
  "name": "toy",
  "version": "0.7.0",
  "hooks": {
    "timeout": 10
  }
}
EOF

git -C "$FIX" add core.py plugin.json
git -C "$FIX" commit -q -m 'rename t1→driftDelay, bump threshold/timeout/version, flip cache'
HEAD7="$(git -C "$FIX" rev-parse --short=7 HEAD)"

set +e
OUT="$("$SIRE" --no-color -C "$FIX" "docs/how to set (t1).md:4" 2>&1)"
st=$?
set -e
printf '%s\n' "$OUT"
assert_exit "$st" 0 "present_threshold leftover finds a sire"
assert_contains "$OUT" "$HEAD7" "sire is the rename/bump commit"
assert_contains "$OUT" "both:" "via=both"
assert_contains "$OUT" "0.4 → 0.45" "old→new"
assert_contains "$OUT" "present_threshold" "natal name"

set +e
T1OUT="$("$SIRE" --no-color -C "$FIX" "docs/how to set (t1).md:3" 2>&1)"
T1ST=$?
set -e
printf '%s\n' "$T1OUT"
assert_exit "$T1ST" 0 "T1 leftover finds a sire (inflected pickaxe t1)"
assert_contains "$T1OUT" "$HEAD7" "T1 leftover sires the rename commit"
assert_contains "$T1OUT" "both:" "T1 is 15 is via=both"
assert_contains "$T1OUT" "t1↔driftDelay" "natal pair t1↔driftDelay"

set +e
VEROUT="$("$SIRE" --no-color -C "$FIX" "docs/how to set (t1).md:5" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "version leftover finds a sire"
assert_contains "$VEROUT" "0.3.0 → 0.7.0" "typed version natal is the full token"

set +e
"$SIRE" --no-color -C "$FIX" core.py:1 >/dev/null
PAID=$?
set -e
assert_exit "$PAID" 1 "paid driftDelay=15 is not a leftover"

echo
echo "== FILE:LINE is the object; unified diff is refused =="
set +e
GARBAGE="$(printf 'diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a\n+b\n' | "$SIRE" --no-color -C "$FIX" 2>&1)"
st=$?
set -e
assert_exit "$st" 2 "unified-diff stdin exits 2"
assert_contains "$GARBAGE" "FILE:LINE" "diff stdin names the inverted object"

set +e
printf '' | "$SIRE" --no-color -C "$FIX" >/dev/null 2>&1
st=$?
set -e
assert_exit "$st" 2 "empty stdin exits 2"

echo
echo "== stdin locators (lien dest-line shape) =="
set +e
PIPE="$(printf 'docs/how to set (t1).md:4: both: leftover\n' | "$SIRE" --no-color -C "$FIX" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "piped locator exits 0"
assert_contains "$PIPE" "$HEAD7" "piped locator still names the bump commit"

echo
echo "== sitbone e9b0f75 leftover CLAUDE.md:329 =="
SIT="${SITBONE:-$HOME/ghq/github.com/annenpolka/sitbone}"
if [[ ! -d "$SIT/.git" ]]; then
  echo "  SKIP sitbone not at $SIT"
else
  set +e
  S329="$("$SIRE" --no-color -C "$SIT" CLAUDE.md:329 2>&1)"
  st=$?
  set -e
  printf '%s\n' "$S329" | head -20
  assert_exit "$st" 0 "CLAUDE.md:329 finds a sire"
  assert_contains "$S329" "e9b0f75" "natal change is e9b0f75 (hysteresis)"
  assert_contains "$S329" "both:" "via=both (threshold ∧ 0.4)"
  assert_contains "$S329" "0.4 → 0.45" "old→new"
  assert_contains "$S329" "threshold↔presentThreshold" "natal pair"
  assert_not_contains "$S329" "a2512fe" "not git blame (initial design docs)"
  assert_not_contains "$S329" "FOREGROUND_STYLE" "0.50 is not natal 0.5"
  assert_not_contains "$S329" "CORNER_RADIUS" "0.4 is not integer 4"
  assert_not_contains "$S329" "prevPhase" "0 in 0.4 is not integer 0"
  BOTH_ROWS="$(grep -c -E ': both:' <<<"$S329" || true)"
  if [[ "$BOTH_ROWS" -ge 1 ]]; then
    echo "  ok  CLAUDE.md:329 has via=both ($BOTH_ROWS)"
    pass=$((pass + 1))
  else
    echo "  FAIL CLAUDE.md:329 missing via=both"
    fail=$((fail + 1))
  fi
  CLAIM_ROWS="$(grep -c -E ': claim:' <<<"$S329" || true)"
  if [[ "$CLAIM_ROWS" -eq 0 ]]; then
    echo "  ok  CLAUDE.md:329 has no hungry claim-sires"
    pass=$((pass + 1))
  else
    echo "  FAIL CLAUDE.md:329 still has $CLAIM_ROWS claim-sires"
    echo "$S329" | sed 's/^/    /'
    fail=$((fail + 1))
  fi

  BLAME="$(git -C "$SIT" blame -L 329,329 --porcelain -- CLAUDE.md | head -1 | awk '{print substr($1,1,7)}')"
  echo "  git blame CLAUDE.md:329 → $BLAME"
  if [[ "$BLAME" != "e9b0f75" ]]; then
    echo "  ok  git blame SHA ($BLAME) ≠ sire e9b0f75"
    pass=$((pass + 1))
  else
    echo "  FAIL git blame unexpectedly equals sire"
    fail=$((fail + 1))
  fi

  echo
  echo "== wrong natal: SPEC.md:436 v0.4 vs float 0.4 =="
  set +e
  S436="$("$SIRE" --no-color -C "$SIT" SPEC.md:436 2>&1)"
  st=$?
  set -e
  printf '%s\n' "$S436" | head -20
  assert_not_contains "$S436" "e9b0f75" "v0.4 is not leftover float 0.4"
  assert_not_contains "$S436" "CORNER_RADIUS" "v0.4 is not leftover integer 4"
  if [[ "$st" -eq 1 ]]; then
    echo "  ok  SPEC.md:436 speaks no natal (exit 1)"
    pass=$((pass + 1))
  elif [[ "$st" -eq 0 ]]; then
    echo "  note  SPEC.md:436 found some other sire (exit 0, not e9b0f75)"
    pass=$((pass + 1))
  else
    echo "  FAIL SPEC.md:436 exit $st"
    fail=$((fail + 1))
  fi

  echo
  echo "== kin-only ADR quote =="
  set +e
  ADR="$("$SIRE" --no-color --explain -C "$SIT" docs/adr/0019-presence-hysteresis.md:12 2>&1)"
  st=$?
  set -e
  printf '%s\n' "$ADR" | head -30
  assert_exit "$st" 0 "ADR:12 finds a sire"
  assert_contains "$ADR" "e9b0f75" "ADR quote still speaks the hysteresis natal"
  assert_contains "$ADR" "via       kin" "ADR:12 is via=kin (no 0.4 on the line)"
  assert_not_contains "$ADR" "CATEGORY" "ADR:12 does not sire unrelated CATEGORY"
  assert_not_contains "$ADR" "via       both" "kin-only ADR is not via=both"
fi

echo
echo "== kizu leftover plugin version 0.3.0, if present =="
KIZU="${KIZU_ROOT:-$HOME/ghq/github.com/annenpolka/kizu}"
if [[ -f "$KIZU/plugin/plugin.json" ]]; then
  set +e
  KOUT="$("$SIRE" --no-color -C "$KIZU" plugin/plugin.json:4 2>&1)"
  st=$?
  set -e
  printf '%s\n' "$KOUT" | head -12
  assert_contains "$KOUT" "0.3.0" "kizu plugin leftover names a 0.3.0 natal"
  assert_not_contains "$KOUT" "BUFFER" "0 in 0.3.0 is not integer 0"
  if grep -E 'kin: VERSION' <<<"$KOUT" >/dev/null; then
    echo "  FAIL kizu leftover still sires later version bumps as kin"
    echo "$KOUT" | sed 's/^/    /'
    fail=$((fail + 1))
  else
    echo "  ok  later version bumps are not kin of leftover 0.3.0"
    pass=$((pass + 1))
  fi
else
  echo "  SKIP kizu not at $KIZU"
fi

echo
if [[ "$fail" -ne 0 ]]; then
  echo "sire demo: passed=$pass failed=$fail"
  exit 1
fi
echo "sire demo: passed=$pass failed=0"
exit 0
