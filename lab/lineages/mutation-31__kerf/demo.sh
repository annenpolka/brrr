#!/usr/bin/env bash
# demo.sh — kerf: value in, cuts out, TSV.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
KERF=(python3 "$ROOT/bin/kerf")
fail() { echo "demo fail: $*" >&2; exit 1; }

echo "== 3 sits on n > 3 (exclusive) and n >= 4 (exclusive) =="
out="$("${KERF[@]}" --report-only 3 "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q $'3\tBRINK\texcl.go\t4\tn\t>\t3\texclusive' || fail "3 missed n > 3"
echo "$out" | grep -q $'3\tBRINK\tincl.go\t4\tn\t>=\t4\texclusive' || fail "3 missed n >= 4"

echo
echo "== 401 is HIT on statusCode == 401 (invert, not silent) =="
out="$("${KERF[@]}" --report-only 401 "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q $'401\tHIT\toffby.swift\t2\tstatusCode\t==\t401\texact' || fail "401 missed HIT"

echo
echo "== 400 is OFFBY on statusCode == 401 =="
out="$("${KERF[@]}" --report-only 400 "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q $'400\tOFFBY\toffby.swift\t2\tstatusCode\t==\t401\toff-by-one' || fail "400 missed OFFBY"

echo
echo "== -1 sits on err != -1 =="
out="$("${KERF[@]}" --report-only -- -1 "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q -e $'-1\tSENTINEL\tsentinel.py\t2\terr\t!=' || fail "-1 missed sentinel"

echo
echo "== unknown sits on status != unknown =="
out="$("${KERF[@]}" --report-only unknown "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q $'unknown\tSENTINEL\tsentinel.py\t10\tstatus\t!=' || fail "unknown missed excluded sentinel"

echo
echo "== running is NEIGHBOR of phase === done =="
out="$("${KERF[@]}" --report-only running "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q $'running\tNEIGHBOR\tneighbor.ts\t4\tphase' || fail "running missed neighbor"

echo
echo "== 200 / 300 sit on range endpoints =="
out="$("${KERF[@]}" --report-only 200 "$ROOT/fixtures")"
echo "$out" | grep -q $'200\tBRINK\trange.swift' || fail "200 missed range"
out="$("${KERF[@]}" --report-only 300 "$ROOT/fixtures")"
echo "$out" | grep -q $'300\tBRINK\trange.swift' || fail "300 missed range"

echo
echo "== stdin stream, TSV, no header =="
out="$(printf '3\n400\nunknown\n' | "${KERF[@]}" --report-only "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q $'3\tBRINK\texcl.go' || fail "stdin 3 missed"
echo "$out" | grep -q $'400\tOFFBY\toffby.swift' || fail "stdin 400 missed"
echo "$out" | grep -q $'unknown\tSENTINEL\tsentinel.py' || fail "stdin unknown missed"
echo "$out" | head -1 | grep -q $'^value\t' && fail "header leaked on default TSV" || true

echo
echo "== miss is silent, exit 1 without --report-only =="
"${KERF[@]}" --report-only 99999 "$ROOT/fixtures" | grep -q . && fail "99999 should be empty" || true
set +e
"${KERF[@]}" 99999 "$ROOT/fixtures" >/dev/null
rc=$?
set -e
[[ "$rc" == "1" ]] || fail "99999 exit $rc want 1"

echo
echo "== 401 does not OFFBY onto graphemes == 400 =="
out="$("${KERF[@]}" --report-only 401 "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q "grapheme.py" && fail "401 sat on graphemes == 400" || true
echo "$out" | grep -q $'401\tHIT\toffby.swift' || fail "401 HIT lost"

echo
echo "== ambient 0 is sentinel, not HIT == 0 =="
out="$("${KERF[@]}" --report-only 0 "$ROOT/fixtures")"
echo "$out"
echo "$out" | grep -q $'0\tHIT\tzero.py' && fail "bare 0 HIT on == 0" || true
echo "$out" | grep -q $'0\tSENTINEL\tzero.py' || fail "0 missed n > 0 sentinel"
echo "$out" | grep -q "loop.rs" && fail "0 sat on for i in 0..5" || true
q="$("${KERF[@]}" --report-only 'n=0' "$ROOT/fixtures")"
echo "$q"
echo "$q" | grep -q $'0\tHIT\tzero.py' || fail "n=0 missed qualified HIT"

echo
echo "== string-edit is not a class =="
"${KERF[@]}" --report-only sucess "$ROOT/fixtures" | grep -q . && fail "sucess leaked" || true
"${KERF[@]}" --report-only Success "$ROOT/fixtures" | grep -q . && fail "Success leaked" || true
"${KERF[@]}" --report-only kraken "$ROOT/fixtures" | grep -q . && fail "kraken leaked" || true
"${KERF[@]}" --report-only phoenix "$ROOT/fixtures" | grep -q . && fail "phoenix comment leaked" || true
echo "no typo/case/comment class"

echo
echo "== --scan still joins the tree's own literals =="
scan="$("${KERF[@]}" --scan --format human --report-only "$ROOT/fixtures")"
echo "$scan" | grep -q "excl.go:4" || fail "scan missed exclusive"
echo "$scan" | grep -q "offby.swift:2" || fail "scan missed offby"
echo "$scan" | grep "noise.py" | grep -q "OFFBY" && fail "0/1 count OFFBY leaked" || true
echo "$scan" | grep "timeout.swift" | grep -q "300" && fail "scan sat timeout 300 on HTTP range" || true
echo "$scan" | grep -qiE "typo|sucess|has_more" && fail "string-edit leaked in scan" || true

TENAOSHI="/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
if [[ -d "$TENAOSHI/Engine" ]]; then
  echo
  echo "== tenaoshi: 400 sits on 401; 401 is HIT =="
  ten400="$("${KERF[@]}" --report-only 400 "$TENAOSHI/Engine")"
  echo "$ten400" | grep -n "401" | head
  echo "$ten400" | grep -q $'400\tOFFBY' || fail "tenaoshi 400 not OFFBY"
  echo "$ten400" | grep -q "401" || fail "tenaoshi 400 missed 401 cut"
  ten401="$("${KERF[@]}" --report-only 401 "$TENAOSHI/Engine")"
  echo "$ten401" | grep -n "401" | head
  echo "$ten401" | grep -q $'401\tHIT' || fail "tenaoshi 401 not HIT"
  echo "$ten401" | grep -q "statusCode" || fail "tenaoshi 401 missed statusCode"
  echo "$ten401" | grep -q "contextGraphemes" && fail "401 OFFBY leaked onto graphemes" || true
fi

SITBONE="/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
if [[ -d "$SITBONE/Sources" ]]; then
  echo
  echo "== sitbone: 2 sits on parts.count > 2 =="
  sit="$("${KERF[@]}" --report-only 2 "$SITBONE/Sources")"
  echo "$sit" | grep -n "count" | head
  echo "$sit" | grep -q $'2\tBRINK' || fail "sitbone 2 not BRINK"
  echo "$sit" | grep -q "count" || fail "sitbone 2 missed count cut"
fi

echo
echo "demo ok"
exit 0
