#!/usr/bin/env bash
# demo.sh — exercise nigh on fixtures and a real repo slice.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
NIGH=(python3 "$ROOT/bin/nigh")
fail() { echo "demo fail: $*" >&2; exit 1; }

echo "== fixtures: NIGH / CLOSED =="
out="$("${NIGH[@]}" --report-only "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q "NIGH       nigh_typo.py:2  status == 'success'" || fail "missing typo NIGH"
echo "$out" | grep -q "sucess" || fail "missing typo evidence"
echo "$out" | grep -q "(typo d=1)" || fail "missing typo reason"
echo "$out" | grep -q "NIGH       nigh_inflect.ts:2  flag === 'has_more'" || fail "missing inflection NIGH"
echo "$out" | grep -q "CLOSED     closed.py:4  kind == 'phoenix'" || fail "missing CLOSED phoenix"
echo "$out" | grep -q "CLOSED     family.ts:2  action.kind === 'action.never-built'" || fail "missing family CLOSED"
echo "$out" | grep -q "action.resolved-beam" || fail "missing family context"
# v0.2: rust lifetimes / templates / embedded JSON / typo field-scope
echo "$out" | grep -q "SelectState" && fail "rust lifetime leaked as gate" || true
echo "$out" | grep -q "forced-slash" && fail "template assignment should satisfy forced-slash" || true
echo "$out" | grep -q "claude-haiku-4-5" && fail "embedded JSON should produce claude-haiku-4-5" || true
echo "$out" | grep "ENOENT" | grep -q "event" && fail "ENOENT should not NIGH against event" || true
echo "$out" | grep -q "会議" && fail "oracle prose leaked" || true
echo "$out" | grep -q "typeof" && fail "typeof leaked" || true

echo
echo "== fixtures: BRINK (opt-in) =="
brink="$("${NIGH[@]}" --brink --report-only "$ROOT/fixtures")"
echo "$brink"
echo "$brink" | grep -q "BRINK      brink.go:4  n > 3" || fail "missing BRINK"

echo
echo "== --probe success =="
probe="$("${NIGH[@]}" --probe success --report-only "$ROOT/fixtures")"
echo "$probe"
echo "$probe" | grep -q "nigh_typo.py:2" || fail "probe missed success gate"

echo
echo "== tsv pipeline =="
"${NIGH[@]}" --format tsv --nigh --report-only --quiet "$ROOT/fixtures" | awk -F'\t' 'NR==1 || $1=="NIGH"' | head

echo
echo "== sitbone: CLOSED flag that is never constructed =="
sit="$("${NIGH[@]}" --closed --report-only /Users/annenpolka/ghq/github.com/annenpolka/sitbone/Sources)"
echo "$sit" | grep -n "auto-start" | head
echo "$sit" | grep -q -- "--auto-start" || fail "sitbone --auto-start not CLOSED"

echo
echo "demo ok"
exit 0
