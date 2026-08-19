#!/usr/bin/env bash
# demo.sh — exercise cusp on fixtures and a real repo slice.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CUSP=(python3 "$ROOT/bin/cusp")
fail() { echo "demo fail: $*" >&2; exit 1; }

echo "== fixtures: numeric / enum brink =="
out="$("${CUSP[@]}" --report-only "$ROOT/fixtures")"
echo "$out"

echo "$out" | grep -q "BRINK      excl.go:4  n > 3" || fail "missing exclusive BRINK"
echo "$out" | grep -q "exclusive bound" || fail "missing exclusive note"
echo "$out" | grep -qE "CUT +3  excl.go:8" || fail "missing exclusive evidence 3"

echo "$out" | grep -q "BRINK      incl.go:4  n >= 4" || fail "missing inclusive BRINK"
echo "$out" | grep -q "inclusive bound" || fail "missing inclusive note"

echo "$out" | grep -q "OFFBY      offby.swift:2  statusCode == 401" || fail "missing OFFBY 401"
echo "$out" | grep -qE "CUT +400" || fail "missing 400 evidence"

echo "$out" | grep -q "SENTINEL   sentinel.py:2  err != -1" || fail "missing numeric sentinel"
echo "$out" | grep -q "SENTINEL   sentinel.py:10  status != 'unknown'" || fail "missing string sentinel"

echo "$out" | grep -q "NEIGHBOR   neighbor.ts:4  phase === 'done'" || fail "missing enum NEIGHBOR"
echo "$out" | grep -q "running" || fail "missing neighbor evidence"

echo "$out" | grep -q "range.swift" || fail "missing range brink"
echo "$out" | grep -q "200" || fail "missing range endpoint 200"

echo "$out" | grep -q "enum_swift.swift" || fail "missing Swift enum brink"

echo "$out" | grep "noise.py" | grep -q "OFFBY" && fail "0/1 count OFFBY leaked" || true
echo "$out" | grep "timeout.swift" | grep -q "300" && fail "HTTP range sat on timeout 300" || true

echo
echo "== string-edit NIGH is dead =="
echo "$out" | grep -qiE "typo|nigh|sucess|has_more|Success" && fail "string-edit NIGH leaked" || true
echo "$out" | grep -q "kraken" && fail "non-enum string gate leaked" || true
echo "$out" | grep -q "phoenix" && fail "comment leaked" || true
echo "no typo/case/inflection class in default report"

echo
echo "== --probe 3 sits on n > 3 =="
probe="$("${CUSP[@]}" --probe 3 --report-only "$ROOT/fixtures")"
echo "$probe"
echo "$probe" | grep -q "excl.go:4" || fail "probe 3 missed exclusive cut"

echo
echo "== tsv pipeline =="
"${CUSP[@]}" --format tsv --offby --report-only --quiet "$ROOT/fixtures" | awk -F'\t' 'NR==1 || $1=="OFFBY"' | head

TENAOSHI="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
if [[ -d "$TENAOSHI/Engine/Sources" ]]; then
  echo
  echo "== tenaoshi: 401 vs constructed 400 =="
  ten="$("${CUSP[@]}" --offby --report-only "$TENAOSHI/Engine")"
  echo "$ten" | grep -n "401" | head
  echo "$ten" | grep -q "401" || fail "tenaoshi 401 not OFFBY"
  echo "$ten" | grep -q "400" || fail "tenaoshi missing 400 evidence"
fi

SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/Sources" ]]; then
  echo
  echo "== sitbone: count > 2 with constructed 2 =="
  sit="$("${CUSP[@]}" --brink --report-only "$SITBONE/Sources")"
  echo "$sit" | grep -n "count" | head
  echo "$sit" | grep -q "count > 2" || fail "sitbone parts.count > 2 not BRINK"
fi

echo
echo "demo ok"
exit 0
