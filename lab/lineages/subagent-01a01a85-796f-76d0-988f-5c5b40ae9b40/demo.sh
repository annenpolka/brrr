#!/usr/bin/env bash
# Exercise wraith on the built-in fixture and on allowed real repos.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
WRAITH="$ROOT/wraith"
chmod +x "$WRAITH"

pass=0
fail=0

ok() { echo "  OK  $*"; pass=$((pass + 1)); }
bad() { echo "  FAIL $*" >&2; fail=$((fail + 1)); }

echo "== 1. built-in fixture (weird filenames, rename, leftover docs) =="
if "$WRAITH" --self-test; then
  ok "self-test"
else
  bad "self-test"
fi

dogfood() {
  local name="$1" path="$2"
  shift 2
  echo
  echo "== dogfood: $name =="
  if [[ ! -d "$path/.git" ]]; then
    echo "  skip (missing $path)"
    return
  fi
  "$WRAITH" -C "$path" --ok-exit --porcelain "$@" | tee "/tmp/wraith-demo-$name.porcelain" >/dev/null
  local n
  n=$(wc -l < "/tmp/wraith-demo-$name.porcelain" | tr -d ' ')
  echo "  porcelain lines: $n"
  ok "$name ran"
}

SKILLS=/Users/annenpolka/ghq/github.com/annenpolka/skills
SITBONE=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
KIZU=/Users/annenpolka/ghq/github.com/annenpolka/kizu
VOID=/Users/annenpolka/ghq/github.com/annenpolka/voidtrace
TENA=/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi

echo
echo "== 2. skills (must surface deleted preact-zero-mock leftover) =="
if [[ -d "$SKILLS/.git" ]]; then
  out=$("$WRAITH" -C "$SKILLS" --porcelain --ok-exit)
  echo "$out"
  if echo "$out" | grep -q 'preact-zero-mock'; then
    ok "skills: preact-zero-mock still advertised after deletion"
  else
    bad "skills: expected preact-zero-mock holdout"
  fi
else
  echo "  skip skills"
fi

dogfood sitbone "$SITBONE"
dogfood kizu "$KIZU" --max-commits 250
dogfood voidtrace "$VOID" --max-commits 80
dogfood tenaoshi "$TENA"

echo
echo "== 3. composability: porcelain is path:line:name:why:death =="
if [[ -d "$SKILLS/.git" ]]; then
  line=$("$WRAITH" -C "$SKILLS" --porcelain --ok-exit | head -1)
  echo "  sample: $line"
  if echo "$line" | grep -Eq '^[^:]+:[0-9]+:[^:]+:[^:]+:'; then
    ok "porcelain shape"
  else
    bad "porcelain shape: $line"
  fi
fi

echo
echo "passed=$pass failed=$fail"
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
exit 0
