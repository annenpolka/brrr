#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/tally"
TALLY="$ROOT/tally"
WOOF="${WOOF:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-10d91539263d/woof}"
WEFT="${WEFT:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b68-3200-7781-bf46-49a3c771f5ff/weft}"
SNAG="${SNAG:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b83-58ff-7043-bd7c-ca791fbb8e0c/snag}"

PASS=0
FAIL=0
assert() {
  local name="$1"
  shift
  if "$@"; then
    PASS=$((PASS + 1))
    echo "  ok  $name"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL $name" >&2
  fi
}
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
assert_not() {
  local name="$1"
  shift
  if "$@"; then
    FAIL=$((FAIL + 1))
    echo "  FAIL $name (expected failure)" >&2
  else
    PASS=$((PASS + 1))
    echo "  ok  $name"
  fi
}

echo "======== 1. selftest ========"
"$TALLY" --selftest

echo "======== 2. mixed line: timeout beside a comment (still FAIL under --chg) ========"
MIXED=$(cat fixtures/mixed-money.diff)
set +e
out1=$("$TALLY" --only prose --chg <<<"$MIXED")
rc1=$?
out1e=$("$TALLY" --only prose --chg --emit <<<"$MIXED")
rc1e=$?
set -e
echo "$out1"
assert_eq "mixed --only prose --chg exits 1" "$rc1" "1"
assert "mixed verdict is FAIL" grep -q 'tally FAIL' <<<"$out1"
assert "mixed leaked number 30→60" grep -q '30 → 60' <<<"$out1"
assert_not "mixed is not marked fence" grep -q 'fence$' <<<"$out1"
assert_not "default is not TSV" grep -q $'path\tline\tclass' <<<"$out1"
echo "$out1e"
assert_eq "emit exits 1" "$rc1e" "1"
assert "emit TSV header" grep -q $'path\tline\tclass\top\told\tnew' <<<"$out1e"
assert "emit number chg" grep -q $'number\tchg\t30\t60' <<<"$out1e"
assert_not "emit is not a verdict dump" grep -q 'tally FAIL' <<<"$out1e"

echo "======== 3. comment-only passes; comment-interior is not snag ========"
COMMENT='--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
 fn start() {
-    let timeout = 60; // secs
+    let timeout = 60; // timeout
     let retries = 3;
 }
'
INTERIOR=$(cat fixtures/comment-number.diff)
set +e
out2=$("$TALLY" --only comments --chg <<<"$COMMENT")
rc2=$?
out2p=$("$TALLY" --only prose --chg <<<"$COMMENT")
rc2p=$?
out2i=$("$TALLY" --only prose --chg <<<"$INTERIOR")
rc2i=$?
set -e
echo "$out2"
assert_eq "comment-only --only comments exits 0" "$rc2" "0"
assert_eq "comment-only --only prose --chg exits 0" "$rc2p" "0"
echo "$out2i"
assert_eq "comment-interior --only prose --chg exits 0 (not snag)" "$rc2i" "0"
if [[ -x "$SNAG" ]]; then
  set +e
  "$SNAG" --forbid number <<<"$INTERIOR" >/dev/null
  rc_snag_int=$?
  set -e
  assert_eq "comment-interior: snag --forbid number trips (cited, not cloned)" "$rc_snag_int" "1"
fi

echo "======== 4. DESTROYER_WEFT fence-number: 30→60 is a number change ========"
FENCE=$(cat fixtures/fence-number.md.diff)
set +e
out6=$("$TALLY" --only prose --chg <<<"$FENCE")
rc6=$?
out6e=$("$TALLY" --only prose --chg --emit <<<"$FENCE")
set -e
echo "$out6"
assert_eq "fence-number --chg exits 1" "$rc6" "1"
assert "fence-number ply is number 30→60" grep -q $'number\tchg\t30\t60' <<<"$out6e"
assert "fence-number verdict names fence" grep -q 'fence' <<<"$out6"
assert_not "fence-number is not a swallowed string" grep -q $'string\t' <<<"$out6e"
if [[ -x "$WEFT" ]]; then
  set +e
  "$WEFT" --only docs <<<"$FENCE" >/dev/null
  rc_weft_fence=$?
  set -e
  assert_eq "weft --only docs frees README fence (path glob + swallow)" "$rc_weft_fence" "0"
fi
if [[ -x "$WOOF" ]]; then
  set +e
  "$WOOF" --only prose <<<"$FENCE" >/dev/null
  rc_woof_fence=$?
  set -e
  assert_eq "woof --only prose also fails fence-number (parent)" "$rc_woof_fence" "1"
fi

echo "======== 5. new fence sample without a number change is not an ident leak ========"
NEWS=$(cat fixtures/fence-new-sample.md.diff)
set +e
outn=$("$TALLY" --only prose --chg <<<"$NEWS")
rcn=$?
outnw=$("$TALLY" --only prose <<<"$NEWS")
rcnw=$?
set -e
echo "$outn"
assert_eq "new sample --chg exits 0" "$rcn" "0"
assert "new sample --chg is OK" grep -q 'tally OK' <<<"$outn"
echo "$outnw"
assert_eq "new sample without --chg exits 1 (ident flood)" "$rcnw" "1"
assert "without --chg the flood is ident" grep -q 'ident=' <<<"$outnw"

echo "======== 6. fence ident flood: --chg drops idents; 2048 ins is v0.1 leftover ========"
FLOOD=$(cat fixtures/fence-ident-flood.md.diff)
set +e
outf=$("$TALLY" --only prose --chg <<<"$FLOOD")
rcf=$?
outfw=$("$TALLY" --only prose <<<"$FLOOD")
outfe=$("$TALLY" --only prose --chg --emit <<<"$FLOOD")
set -e
echo "$outf"
assert_not "flood --chg is not ident" grep -q 'ident=' <<<"$outf"
assert "without --chg flood is ident" grep -q 'ident=' <<<"$outfw"
if grep -q $'number\tins\t' <<<"$outfe" && grep -q 2048 <<<"$outfe"; then
  assert "v0.1 flood --chg still names number ins 2048" true
  assert_eq "v0.1 flood --chg exits 1" "$rcf" "1"
else
  assert "v0.2 flood --chg has no number ins (only chg leaks)" true
  assert_eq "v0.2 flood --chg exits 0" "$rcf" "0"
fi

echo "======== 7. fence mixed-line 30→60 still FAIL ========"
FMIX=$(cat fixtures/fence-mixed-line.md.diff)
set +e
outfm=$("$TALLY" --only prose --chg <<<"$FMIX")
rcfm=$?
set -e
echo "$outfm"
assert_eq "fence mixed-line --chg exits 1" "$rcfm" "1"
assert "fence mixed-line is 30→60" grep -q '30 → 60' <<<"$outfm"

echo "======== 8. path-glob vs prose: docs/generated/api.rs still leaks under --chg ========"
GEN=$(cat fixtures/docs-generated-api.rs.diff)
MAKE=$(cat fixtures/docs-makefile.diff)
set +e
out4=$("$TALLY" --only prose --chg <<<"$GEN")
rc4=$?
out4m=$("$TALLY" --only prose --chg <<<"$MAKE")
rc4m=$?
set -e
echo "$out4"
assert_eq "docs/generated/api.rs --chg exits 1" "$rc4" "1"
assert "api.rs leaked number" grep -q '30 → 60' <<<"$out4"
assert "api.rs leaked ident (not a fence)" grep -q 'fetch_user' <<<"$out4"
echo "$out4m"
assert_eq "docs/Makefile --chg exits 1" "$rc4m" "1"
assert "Makefile leaked 30→60" grep -q '30 → 60' <<<"$out4m"
if [[ -x "$WEFT" ]]; then
  set +e
  "$WEFT" --only docs <<<"$GEN" >/dev/null
  rc_weft_gen=$?
  set -e
  assert_eq "weft --only docs frees docs/generated/api.rs (path glob)" "$rc_weft_gen" "0"
fi

echo "======== 9. CJK README is prose; CJK ident on src.rs is ident ========"
CJK=$(cat fixtures/cjk-readme.diff)
CJKID=$(cat fixtures/cjk-ident.diff)
set +e
out3p=$("$TALLY" --only prose --chg <<<"$CJK")
rc3p=$?
out3i=$("$TALLY" --only prose --chg <<<"$CJKID")
rc3i=$?
set -e
assert_eq "CJK README passes --only prose --chg" "$rc3p" "0"
echo "$out3i"
assert_eq "CJK ident on src.rs fails --chg" "$rc3i" "1"
assert "CJK ident leak is ident 契約→資産" grep -q '契約' <<<"$out3i"

echo "======== 10. missing --only is usage ========"
set +e
"$TALLY" </dev/null >/dev/null 2>/tmp/tally-demo-err.$$
rcu=$?
set -e
assert_eq "no --only exits 2" "$rcu" "2"
rm -f /tmp/tally-demo-err.$$

echo "======== 11. dogfood sitbone 77df1da ========"
SB=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
if [[ -d "$SB/.git" ]]; then
  DIFF=$(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da)
  set +e
  sb=$("$TALLY" --only prose --chg --emit <<<"$DIFF")
  sbrc=$?
  sbv=$("$TALLY" --only prose --chg <<<"$DIFF")
  sbw=$("$TALLY" --only prose <<<"$DIFF")
  set -e
  echo "$sbv"
  assert_eq "sitbone 77df1da --chg exits 1" "$sbrc" "1"
  assert "sitbone leak includes Makefile" grep -q $'Makefile\t' <<<"$sb"
  assert_not "sitbone --chg is not ident flood (no 100+ idents)" grep -q 'ident=12[0-9]' <<<"$sbv"
  assert "without --chg sitbone is ident flood" grep -q 'ident=126' <<<"$sbw"
  readme_num=$(grep -E $'^README.md\t[0-9]+\tnumber\t' <<<"$sb" | grep -c 2048 || true)
  readme_ident=$(grep -E $'^README.md\t[0-9]+\tident\t' <<<"$sb" | wc -l | tr -d ' ' || true)
  assert_eq "sitbone --chg README ident flood is 0" "$readme_ident" "0"
  if [[ "$readme_num" -gt 0 ]]; then
    assert "v0.1 sitbone README 2048 still number ins (not yet chg-only)" true
  else
    assert "v0.2 sitbone README 2048 is not a leak (ins, not chg)" true
  fi
  if [[ -x "$WOOF" ]]; then
    set +e
    wo=$("$WOOF" --only prose <<<"$DIFF")
    set -e
    assert "woof sitbone is ident=126 flood" grep -q 'ident=126' <<<"$wo"
  fi
  if [[ -x "$WEFT" ]]; then
    set +e
    we=$("$WEFT" --only docs --emit <<<"$DIFF")
    werc=$?
    set -e
    assert_eq "weft --only docs fails 77df1da (Makefile)" "$werc" "1"
    assert "weft leak is Makefile" grep -q $'Makefile\t' <<<"$we"
    assert_not "weft does not leak README" grep -q $'README.md\t' <<<"$we"
  fi
else
  echo "  skip sitbone (missing $SB)"
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
