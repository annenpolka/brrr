#!/usr/bin/env bash
# Exercise kiln on a synthetic firing, then dogfood nearby repos when present.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
KILN="$ROOT/kiln"
chmod +x "$KILN"

PASS=0
FAIL=0

ok() { PASS=$((PASS + 1)); echo "  PASS  $1"; }
bad() { FAIL=$((FAIL + 1)); echo "  FAIL  $1"; echo "        $2" >&2; }

echo "== selftest =="
if python3 "$KILN" --selftest; then
  ok "selftest"
else
  bad "selftest" "kiln --selftest failed"
fi

echo "== help =="
if python3 "$KILN" --help | grep -q 'SPLIT'; then
  ok "help names SPLIT"
else
  bad "help names SPLIT" "missing primitive in --help"
fi

dogfood() {
  local name="$1"
  local path="$2"
  shift 2
  echo "== dogfood $name =="
  if [[ ! -d "$path" ]]; then
    echo "  skip  $name (not present)"
    return 0
  fi
  local out
  if ! out="$(python3 "$KILN" -C "$path" --tsv 2>&1)"; then
    bad "$name kiln exit" "$out"
    return 0
  fi
  local n
  n="$(echo "$out" | awk 'NR>1 && NF{c++} END{print c+0}')"
  echo "  artifacts $n"
  local arg
  for arg in "$@"; do
    local label="${arg%%:*}"
    local needle="${arg#*:}"
    if echo "$out" | grep -q -- "$needle"; then
      ok "$name $label"
    else
      bad "$name $label" "expected /$needle/ in tsv (first lines): $(echo "$out" | head -5)"
    fi
  done
}

GHQ="${GHQ:-$HOME/ghq/github.com/annenpolka}"

dogfood relico "$GHQ/relico" \
  "split-lot:SPLIT" \
  "dated-unit:oracles_generated.test.ts" \
  "blind-patterns:patterns.pkl"

dogfood tenaoshi "$GHQ/tenaoshi" \
  "oracle:OraclesGenerated.swift" \
  "recipe-json:contracts/testcases/" \
  "blind:patterns.pkl"

dogfood voidtrace "$GHQ/voidtrace" \
  "split:SPLIT" \
  "contracts:docs/generated/CONTRACTS.md" \
  "blind-imports:specs/patterns/base.pkl"

dogfood koyomi "$GHQ/koyomi-trace" \
  "tz-bound:BOUND" \
  "corpus-gen:generate_corpus.py"

dogfood kizu "$GHQ/kizu"
dogfood sitbone "$GHQ/sitbone"

echo
echo "demo: $PASS passed, $FAIL failed"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
