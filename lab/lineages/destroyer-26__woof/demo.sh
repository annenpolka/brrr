#!/usr/bin/env bash
# DESTROYER_WOOF money shots. Extra args ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
WOOF="${WOOF:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-10d91539263d/woof}"
TALLY="${TALLY:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7db4d4bb2bf3/tally}"
WEFT="${WEFT:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b68-3200-7781-bf46-49a3c771f5ff/weft}"
SNAG="${SNAG:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b83-58ff-7043-bd7c-ca791fbb8e0c/snag}"
SB="${SB:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
FIX="${DESTROY_ROOT:-/tmp/destroy-woof}/fixtures"

PASS=0
FAIL=0
assert_eq() {
  local name="$1" got="$2" want="$3"
  if [[ "$got" == "$want" ]]; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name (got $got want $want)" >&2
  fi
}

chmod +x "$WOOF" "$TALLY" "$WEFT" "$SNAG" 2>/dev/null || true
echo "======== 0. victim selftest (do not rewrite) ========"
"$WOOF" --selftest
"$WOOF" --version

echo "======== 1. gold mixed-line / comment-interior / api.rs / fence ========"
python3 attack.py >/tmp/destroy-woof-demo.log 2>&1 || true
set +e
"$WOOF" --only prose < "$FIX/mixed-money.diff" >/dev/null
assert_eq "mixed-line rc=1" "$?" "1"
"$WOOF" --only prose < "$FIX/comment-number.diff" >/dev/null
assert_eq "comment-interior rc=0" "$?" "0"
"$SNAG" --forbid number < "$FIX/comment-number.diff" >/dev/null
assert_eq "snag --forbid number trips (cited, not cloned)" "$?" "1"
"$WOOF" --only prose < "$FIX/docs-generated-api.rs.diff" >/dev/null
assert_eq "docs/generated/api.rs rc=1" "$?" "1"
"$WEFT" --only docs < "$FIX/docs-generated-api.rs.diff" >/dev/null
assert_eq "weft --only docs still frees api.rs (glob, cited)" "$?" "0"
"$WOOF" --only prose < "$FIX/fence-number.md.diff" >/dev/null
assert_eq "fence-number rc=1" "$?" "1"
"$WOOF" --only prose < "$FIX/cjk-ident.diff" >/dev/null
assert_eq "CJK ident on src.rs rc=1" "$?" "1"
"$WOOF" --only prose < "$FIX/cjk-readme.diff" >/dev/null
assert_eq "CJK README rc=0" "$?" "0"
set -e

echo "======== 2. 114 ident inserts vs tally --chg ========"
set +e
"$WOOF" --only prose < "$FIX/fence-new-sample.md.diff" >/dev/null
assert_eq "new bash sample woof rc=1" "$?" "1"
"$TALLY" --only prose --chg < "$FIX/fence-new-sample.md.diff" >/dev/null
assert_eq "new bash sample tally --chg rc=0" "$?" "0"
if [[ -d "$SB/.git" ]]; then
  woof_out=$("$WOOF" --only prose --emit < <(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da))
  n114=$(printf '%s\n' "$woof_out" | awk -F'\t' '$1=="README.md" && $3=="ident" && $4=="ins"{c++} END{print c+0}')
  assert_eq "sitbone 77df1da README ident ins=114" "$n114" "114"
  "$TALLY" --only prose --chg < <(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da) >/dev/null
  assert_eq "sitbone 77df1da tally --chg still rc=1 (Makefile)" "$?" "1"
fi
set -e

echo "======== 3. SHA split / indented CJK / binary stdin / rename ========"
set +e
out=$("$WOOF" --only prose < "$FIX/sha-digit.md.diff")
assert_eq "SHA 77df1da→98a8009 rc=1" "$?" "1"
assert_eq "SHA leak is 77 → 98" "$(grep -c '77 → 98' <<<"$out" || true)" "1"
"$WOOF" --only prose < "$FIX/sha-letter.md.diff" >/dev/null
assert_eq "letter-prefix SHA rc=0" "$?" "0"
"$WOOF" --only prose < "$FIX/cjk-indented.md.diff" >/dev/null
assert_eq "indented CJK ident rc=0 (text)" "$?" "0"
"$WOOF" --only prose < "$FIX/rename-only.diff" >/dev/null
assert_eq "100% rename rc=0" "$?" "0"
printf '\x00\xff' | "$WOOF" --only prose >/dev/null 2>/tmp/woof-bin-err.$$
assert_eq "binary stdin rc=1 (traceback)" "$?" "1"
grep -q UnicodeDecodeError /tmp/woof-bin-err.$$
assert_eq "binary stdin is UnicodeDecodeError" "$?" "0"
rm -f /tmp/woof-bin-err.$$
"$WOOF" --only prose < "$FIX/fence-body-swap.md.diff" >/dev/null
assert_eq "fence/body swap woof rc=0 (move)" "$?" "0"
"$TALLY" --only prose --chg < "$FIX/fence-body-swap.md.diff" >/dev/null
assert_eq "fence/body swap tally --chg rc=1" "$?" "1"
set -e

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
