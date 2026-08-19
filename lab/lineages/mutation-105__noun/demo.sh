#!/usr/bin/env bash
# Exercise noun: natal identity is (package, noun), not bare version.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
NOUN="$ROOT/noun"
chmod +x "$NOUN"

KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"

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
"$NOUN" self-test
st=$?
set -e
assert_exit "$st" 0 "embedded (package, noun) + natal/via tests"

RUN="$ROOT/fixtures/.run"
rm -rf "$RUN"
mkdir -p "$RUN"

echo
echo "== gold binding: t1=15 → driftDelay=15 still via=both =="
FIX="$RUN/joint"
mkdir -p "$FIX/docs"
git -C "$FIX" init -q
git -C "$FIX" config user.email "noun@example.test"
git -C "$FIX" config user.name "noun"
printf 't1 = 15\n' > "$FIX/core.py"
printf '# Timing\n\nT1 is 15 seconds.\n' > "$FIX/docs/how to set (t1).md"
git -C "$FIX" add core.py docs
git -C "$FIX" commit -q -m 't1=15'
printf 'driftDelay = 15\n' > "$FIX/core.py"
git -C "$FIX" add core.py
git -C "$FIX" commit -q -m 't1→driftDelay'
set +e
T1OUT="$(git -C "$FIX" diff HEAD^ HEAD | "$NOUN" --no-color -C "$FIX" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "t1 leftover exits 1"
assert_contains "$T1OUT" "t1↔driftDelay" "natal pair on the lien"
assert_contains "$T1OUT" "T1 is 15 seconds" "inflected T1 leftover"
assert_contains "$T1OUT" ": both:" "joint via=both"
assert_not_contains "$T1OUT" "NATAL" "default check is not the dump"

echo
echo "== workspace: bump only cli; core 0.3.0 is a different noun =="
WS="$RUN/ws-same"
mkdir -p "$WS/crates/cli" "$WS/crates/core"
git -C "$WS" init -q
git -C "$WS" config user.email "noun@example.test"
git -C "$WS" config user.name "noun"
cat > "$WS/crates/cli/Cargo.toml" << 'EOF'
[package]
name = "cli"
version = "0.3.0"
edition = "2021"
EOF
cat > "$WS/crates/core/Cargo.toml" << 'EOF'
[package]
name = "core"
version = "0.3.0"
edition = "2021"
EOF
cat > "$WS/README.md" << 'EOF'
cli 0.3.0 and core 0.3.0 ship together.
EOF
git -C "$WS" add .
git -C "$WS" commit -q -m 'cli+core 0.3.0'
cat > "$WS/crates/cli/Cargo.toml" << 'EOF'
[package]
name = "cli"
version = "0.7.0"
edition = "2021"
EOF
git -C "$WS" add crates/cli/Cargo.toml
git -C "$WS" commit -q -m 'bump cli 0.3.0→0.7.0'

set +e
WSFACTS="$(git -C "$WS" diff HEAD^ HEAD | "$NOUN" --facts-only --no-color -C "$WS" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "workspace facts-only exits 0"
assert_contains "$WSFACTS" "cli" "cli package on the natal"
assert_contains "$WSFACTS" "0.3.0 → 0.7.0" "cli bump values"
assert_not_contains "$WSFACTS" "core" "core was not in the diff; not a second natal from dest"

set +e
WSOUT="$(git -C "$WS" diff HEAD^ HEAD | "$NOUN" --no-color -C "$WS" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "cli bump still has leftovers"
assert_contains "$WSOUT" "README.md" "docs leftover of cli 0.3.0"
assert_contains "$WSOUT" "cli 0.3.0" "docs still speak cli natal"
assert_not_contains "$WSOUT" "crates/core/Cargo.toml" "core manifest is not leftover of cli"

echo
echo "== workspace: bump both, different versions — two nouns =="
WS2="$RUN/ws-two"
mkdir -p "$WS2/crates/cli" "$WS2/crates/core" "$WS2/docs"
git -C "$WS2" init -q
git -C "$WS2" config user.email "noun@example.test"
git -C "$WS2" config user.name "noun"
cat > "$WS2/crates/cli/Cargo.toml" << 'EOF'
[package]
name = "cli"
version = "0.3.0"
edition = "2021"
EOF
cat > "$WS2/crates/core/Cargo.toml" << 'EOF'
[package]
name = "core"
version = "1.2.0"
edition = "2021"
EOF
printf 'cli version 0.3.0. core crate version 1.2.0.\n' > "$WS2/README.md"
printf 'core version 1.2.0 is the library API\n' > "$WS2/docs/core.md"
git -C "$WS2" add .
git -C "$WS2" commit -q -m 'two packages'
cat > "$WS2/crates/cli/Cargo.toml" << 'EOF'
[package]
name = "cli"
version = "0.7.0"
edition = "2021"
EOF
cat > "$WS2/crates/core/Cargo.toml" << 'EOF'
[package]
name = "core"
version = "1.3.0"
edition = "2021"
EOF
git -C "$WS2" add crates
git -C "$WS2" commit -q -m 'bump cli 0.3.0→0.7.0 and core 1.2.0→1.3.0'

set +e
TWOFACTS="$(git -C "$WS2" diff HEAD^ HEAD | "$NOUN" --facts-only --no-color -C "$WS2" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "two-bump facts-only"
assert_contains "$TWOFACTS" "cli" "cli natal exists"
assert_contains "$TWOFACTS" "core" "core natal exists (lien collapsed this)"
assert_contains "$TWOFACTS" "0.3.0 → 0.7.0" "cli values"
assert_contains "$TWOFACTS" "1.2.0 → 1.3.0" "core values survived merge"

set +e
TWOOUT="$(git -C "$WS2" diff HEAD^ HEAD | "$NOUN" --no-color -C "$WS2" 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "two-bump leftover docs"
assert_contains "$TWOOUT" "0.3.0" "cli old still in README"
assert_contains "$TWOOUT" "1.2.0" "core old still in dest (lien dropped this natal)"
assert_not_contains "$TWOOUT" "crates/cli/Cargo.toml" "paid cli manifest skipped"
assert_not_contains "$TWOOUT" "crates/core/Cargo.toml" "paid core manifest skipped"

echo
echo "== FILE:LINE refused; garbage stdin; empty stdin =="
set +e
"$NOUN" --no-color -C "$FIX" core.py:1 >/dev/null 2>"$FIX/err.txt"
LOC=$?
set -e
assert_exit "$LOC" 2 "FILE:LINE exits 2"
assert_contains "$(cat "$FIX/err.txt")" "not FILE:LINE" "FILE:LINE error names the invert"

set +e
GARBAGE="$(printf 'commit deadbeef\nAuthor: x\n' | "$NOUN" --no-color -C "$FIX" 2>&1)"
st=$?
set -e
assert_exit "$st" 2 "non-diff stdin exits 2"
assert_contains "$GARBAGE" "unified diff" "non-diff names the expected object"

set +e
EMPTY="$(printf '' | "$NOUN" --no-color -C "$FIX" 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "empty diff exits 0"
if [[ -z "$EMPTY" ]]; then
  echo "  ok  empty diff is silent"
  pass=$((pass + 1))
else
  echo "  FAIL empty diff printed: $EMPTY"
  fail=$((fail + 1))
fi

if [[ -d "$KIZU/.git" ]]; then
  echo
  echo "== dogfood kizu 9349dc5: plugin.json is not a homonym =="
  set +e
  KFACTS="$(git -C "$KIZU" diff 9349dc5^ 9349dc5 | "$NOUN" --facts-only --no-color -C "$KIZU" 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "kizu 9349dc5 facts-only"
  assert_contains "$KFACTS" "kizu" "package name kizu"
  assert_contains "$KFACTS" "0.6.0 → 0.7.0" "release bump"
  assert_contains "$KFACTS" "Cargo.toml" "origin is the crate manifest, not Cargo.lock"

  set +e
  KOUT="$(git -C "$KIZU" diff 9349dc5^ 9349dc5 | "$NOUN" --no-color -C "$KIZU" 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "kizu 9349dc5 default check fails (lien was green)"
  assert_contains "$KOUT" "plugin/plugin.json:4" "stale plugin manifest"
  assert_contains "$KOUT" '"version": "0.3.0"' "plugin leftover is 0.3.0"
  assert_not_contains "$KOUT" "4.6.0" "clap dep version is not kizu.version"
  assert_not_contains "$KOUT" ": kin:" "default check is not the 28-kin flood"
  KROWS="$(grep -c . <<<"$KOUT" || true)"
  if [[ "$KROWS" -eq 1 ]]; then
    echo "  ok  9349dc5 default check is one dest-line (plugin.json)"
    pass=$((pass + 1))
  else
    echo "  FAIL 9349dc5 default rows=$KROWS (want 1 plugin.json)"
    echo "$KOUT" | sed 's/^/    /'
    fail=$((fail + 1))
  fi

  echo
  echo "== dogfood kizu 53cbd1a: plugin leftover not cleared by 0.3.0→0.3.1 =="
  set +e
  K31="$(git -C "$KIZU" diff 53cbd1a^ 53cbd1a | "$NOUN" --no-color -C "$KIZU" 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "53cbd1a still unpaid"
  assert_contains "$K31" "plugin/plugin.json:4" "plugin.json leftover of 0.3.0→0.3.1"
  assert_contains "$K31" "0.3.0" "dest still speaks 0.3.0"
else
  echo "  SKIP kizu dogfood (no repo at $KIZU)"
fi

if [[ -d "$SITBONE/.git" ]]; then
  echo
  echo "== dogfood sitbone e9b0f75: CLAUDE.md both-rows still fail =="
  set +e
  SOUT="$(git -C "$SITBONE" diff e9b0f75^ e9b0f75 | "$NOUN" --no-color -C "$SITBONE" 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "sitbone default check exits 1"
  assert_contains "$SOUT" "CLAUDE.md:329" "CLAUDE.md:329 leftover"
  assert_contains "$SOUT" "CLAUDE.md:332" "CLAUDE.md:332 leftover"
  assert_contains "$SOUT" ": both:" "both-rows remain"
  assert_not_contains "$SOUT" "v0.4" "v0.4 is not float 0.4"
  assert_not_contains "$SOUT" ": kin:" "kin-only is not a CI fail"
  SROWS="$(grep -c . <<<"$SOUT" || true)"
  if [[ "$SROWS" -eq 12 ]]; then
    echo "  ok  sitbone 12 current liens (lien v0.2 gold)"
    pass=$((pass + 1))
  else
    echo "  FAIL sitbone current liens=$SROWS (want 12)"
    echo "$SOUT" | sed 's/^/    /'
    fail=$((fail + 1))
  fi
  BOTH="$(grep -c ': both:' <<<"$SOUT" || true)"
  if [[ "$BOTH" -eq 4 ]]; then
    echo "  ok  sitbone 4 via=both"
    pass=$((pass + 1))
  else
    echo "  FAIL sitbone both-rows=$BOTH (want 4)"
    fail=$((fail + 1))
  fi
else
  echo "  SKIP sitbone dogfood (no repo at $SITBONE)"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
