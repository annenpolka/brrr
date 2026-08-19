#!/usr/bin/env bash
# Replay destroyer-21 holes against smolder. Gold must still hold.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SMOLDER="${SMOLDER:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb3a629800b3/smolder}"
TINDER="${TINDER:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-1040781e71b7/tinder}"
KIZU="${KIZU_REPO:-$HOME/ghq/github.com/annenpolka/kizu}"
SIT="${SIT_REPO:-$HOME/ghq/github.com/annenpolka/sitbone}"
FIX="${DESTROY_SMOLDER_FIX:-/tmp/destroy-smolder/fixtures}"

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
    echo "$haystack" | sed 's/^/    /'
    fail=$((fail + 1))
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

echo "== victim self-test =="
set +e
"$SMOLDER" self-test >/tmp/destroy-smolder/demo-selftest.txt 2>&1
st=$?
set -e
assert_exit "$st" 0 "smolder self-test"

echo
echo "== gold kizu / sitbone =="
set +e
KIZU_OUT="$("$SMOLDER" --no-color --no-hunk -C "$KIZU" plugin/plugin.json:4 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "kizu plugin.json leftover"
assert_contains "$KIZU_OUT" "53cbd1a" "kizu falsifier is 53cbd1a"
assert_contains "$KIZU_OUT" "Cargo.toml" "kizu origin is Cargo.toml"
if grep -Fq Cargo.lock <<<"$KIZU_OUT"; then
  echo "  FAIL kizu lockfile is not the origin"
  fail=$((fail + 1))
else
  echo "  ok  kizu lockfile is not the origin"
  pass=$((pass + 1))
fi

set +e
KIZU_LOCK="$("$SMOLDER" --no-color -C "$KIZU" Cargo.lock:168 2>&1)"
st=$?
set -e
assert_contains "$KIZU_LOCK" "regenerate" "kizu lockfile ash"

set +e
SIT_OUT="$("$SMOLDER" --no-color --no-hunk -C "$SIT" CLAUDE.md:329 2>&1)"
st=$?
set -e
assert_contains "$SIT_OUT" "e9b0f75" "sitbone hysteresis commit"
assert_contains "$SIT_OUT" "0.4 → 0.45" "sitbone 0.4→0.45"

echo
echo "== dest:84 leftover-name vs tinder none =="
set +e
DEST84="$("$SMOLDER" --no-color --no-hunk -C "$KIZU" docs/deep-research-ai-agent-hooks.md:84 2>&1)"
st=$?
set -e
assert_exit "$st" 0 "smolder dest:84 finds something"
assert_contains "$DEST84" "a75d4ea" "smolder dest:84 leftover-name a75d4ea"
assert_contains "$DEST84" "kizu hook-post-tool" "smolder dest:84 names the quote"

set +e
T84="$("$TINDER" --no-color --no-hunk -C "$KIZU" docs/deep-research-ai-agent-hooks.md:84 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "tinder dest:84 is none"
assert_contains "$T84" "none" "tinder says none"

set +e
DEAD="$("$SMOLDER" --no-color -C "$KIZU" deep-research-ai-agent-hooks.md:84 2>&1)"
st=$?
set -e
assert_exit "$st" 1 "dead dest name is missing"
assert_contains "$DEAD" "missing" "dead dest name reports missing"

if [[ -d "$FIX/lock-ash" ]]; then
  echo
  echo "== lockfile dest ash; believer leftover blames comment =="
  set +e
  LOCK="$("$SMOLDER" --no-color -C "$FIX/lock-ash" Cargo.lock:6 2>&1)"
  st=$?
  set -e
  assert_contains "$LOCK" "regenerate" "lock dest regenerate"
  set +e
  CMT="$("$SMOLDER" --no-color --no-hunk -C "$FIX/lock-ash" README.md:1 2>&1)"
  st=$?
  set -e
  assert_contains "$CMT" "src/lib.rs" "README leftover blames comment origin"
  assert_contains "$CMT" "FALSIFIED" "README leftover is FALSIFIED"
fi

if [[ -d "$FIX/workspace" ]]; then
  echo
  echo "== two packages named version =="
  set +e
  WS="$("$SMOLDER" --no-color --no-hunk -C "$FIX/workspace" pkg_b/Cargo.toml:3 2>&1)"
  st=$?
  set -e
  assert_contains "$WS" "pkg_a/Cargo.toml" "pkg_b leftover accuses pkg_a"
fi

if [[ -d "$FIX/october-named" ]]; then
  echo
  echo "== October named on dest line =="
  set +e
  OCT="$("$SMOLDER" --no-color --no-hunk -C "$FIX/october-named" docs/us.md:1 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 0 "US date is leftover timeout 10"
  assert_contains "$OCT" "HOOK_TIMEOUT" "US date names HOOK_TIMEOUT"
  set +e
  ISO="$("$SMOLDER" --no-color -C "$FIX/october-named" docs/iso.md:1 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "ISO date still none"
fi

if [[ -d "$FIX/god-wt" ]]; then
  echo
  echo "== 2MB dest is missing =="
  set +e
  GOD="$("$SMOLDER" --no-color -C "$FIX/god-wt" docs/god.md:1 2>&1)"
  st=$?
  set -e
  assert_exit "$st" 1 "2MB dest exit 1"
  assert_contains "$GOD" "missing" "2MB dest reported missing"
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
