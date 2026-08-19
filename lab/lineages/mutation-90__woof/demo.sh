#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/woof"
WOOF="$ROOT/woof"
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
"$WOOF" --selftest

echo "======== 2. mixed line: timeout beside a comment ========"
MIXED=$(cat fixtures/mixed-money.diff)
set +e
out1=$("$WOOF" --only prose <<<"$MIXED")
rc1=$?
out1e=$("$WOOF" --only prose --emit <<<"$MIXED")
rc1e=$?
set -e
echo "$out1"
assert_eq "mixed --only prose exits 1" "$rc1" "1"
assert "mixed verdict is FAIL" grep -q 'woof FAIL' <<<"$out1"
assert "mixed leaked number 30→60" grep -q '30 → 60' <<<"$out1"
assert_not "default is not TSV" grep -q $'path\tline\tclass' <<<"$out1"
echo "$out1e"
assert_eq "emit exits 1" "$rc1e" "1"
assert "emit TSV header" grep -q $'path\tline\tclass\top\told\tnew' <<<"$out1e"
assert "emit number chg" grep -q $'number\tchg\t30\t60' <<<"$out1e"
assert_not "emit is not a verdict dump" grep -q 'woof FAIL' <<<"$out1e"

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
out2=$("$WOOF" --only comments <<<"$COMMENT")
rc2=$?
out2p=$("$WOOF" --only prose <<<"$COMMENT")
rc2p=$?
out2i=$("$WOOF" --only prose <<<"$INTERIOR")
rc2i=$?
set -e
echo "$out2"
assert_eq "comment-only --only comments exits 0" "$rc2" "0"
assert_eq "comment-only --only prose exits 0" "$rc2p" "0"
echo "$out2i"
assert_eq "comment-interior --only prose exits 0 (not snag)" "$rc2i" "0"
if [[ -x "$SNAG" ]]; then
  set +e
  "$SNAG" --forbid number <<<"$INTERIOR" >/dev/null
  rc_snag_int=$?
  set -e
  assert_eq "comment-interior: snag --forbid number trips (cited, not cloned)" "$rc_snag_int" "1"
fi

echo "======== 4. CJK README is prose; CJK ident on src.rs is ident ========"
CJK=$(cat fixtures/cjk-readme.diff)
CJKID=$(cat fixtures/cjk-ident.diff)
set +e
out3=$("$WOOF" --only comments <<<"$CJK")
rc3=$?
out3p=$("$WOOF" --only prose <<<"$CJK")
rc3p=$?
out3i=$("$WOOF" --only prose <<<"$CJKID")
rc3i=$?
set -e
assert_eq "CJK README fails --only comments" "$rc3" "1"
assert_eq "CJK README passes --only prose" "$rc3p" "0"
echo "$out3i"
assert_eq "CJK ident on src.rs fails --only prose" "$rc3i" "1"
assert "CJK ident leak is ident 契約→資産" grep -q '契約' <<<"$out3i"

echo "======== 5. path-glob vs prose: docs/generated/api.rs ========"
GEN=$(cat fixtures/docs-generated-api.rs.diff)
MAKE=$(cat fixtures/docs-makefile.diff)
set +e
out4=$("$WOOF" --only prose <<<"$GEN")
rc4=$?
out4d=$("$WOOF" --only docs <<<"$GEN")
rc4d=$?
out4m=$("$WOOF" --only prose <<<"$MAKE")
rc4m=$?
set -e
echo "$out4"
assert_eq "docs/generated/api.rs --only prose exits 1" "$rc4" "1"
assert "api.rs leaked number" grep -q '30 → 60' <<<"$out4"
assert "api.rs leaked ident" grep -q 'fetch_user' <<<"$out4"
assert_eq "--only docs is the same token alias (not a glob)" "$rc4d" "1"
echo "$out4m"
assert_eq "docs/Makefile --only prose exits 1" "$rc4m" "1"
assert "Makefile leaked 30→60" grep -q '30 → 60' <<<"$out4m"
if [[ -x "$WEFT" ]]; then
  set +e
  "$WEFT" --only docs <<<"$GEN" >/dev/null
  rc_weft_gen=$?
  "$WEFT" --only docs <<<"$MAKE" >/dev/null
  rc_weft_make=$?
  set -e
  assert_eq "weft --only docs frees docs/generated/api.rs (path glob)" "$rc_weft_gen" "0"
  assert_eq "weft --only docs frees docs/Makefile (path glob)" "$rc_weft_make" "0"
fi

echo "======== 6. README.md at repo root counts ========"
VER=$(cat fixtures/readme-ver.diff)
set +e
out5=$("$WOOF" --only prose <<<"$VER")
rc5=$?
set -e
echo "$out5"
assert_eq "README 0.6.0→0.7.0 --only prose exits 1" "$rc5" "1"
assert "README number ply is visible" grep -q 'README.md' <<<"$out5"
if [[ -x "$WEFT" ]]; then
  set +e
  "$WEFT" --only docs <<<"$VER" >/dev/null
  rc_weft_ver=$?
  set -e
  assert_eq "weft --only docs frees README version (path glob)" "$rc_weft_ver" "0"
fi

echo "======== 7. fence-number fixture (v0.2: number ply, not swallowed string) ========"
FENCE=$(cat fixtures/fence-number.md.diff)
set +e
out6=$("$WOOF" --only prose <<<"$FENCE")
rc6=$?
out6e=$("$WOOF" --only prose --emit <<<"$FENCE")
set -e
echo "$out6"
assert_eq "fence-number --only prose exits 1" "$rc6" "1"
# v0.1: fence is one string. v0.2 will name 30→60 as number.
if grep -q $'number\tchg\t30\t60' <<<"$out6e"; then
  assert "fence-number ply is number 30→60" true
  assert_not "fence-number is not a swallowed string" grep -q $'string\t' <<<"$out6e"
else
  assert "v0.1 fence-number is a swallowed string" grep -q 'string' <<<"$out6"
  assert_not "v0.1 fence-number is not yet a number ply" grep -q 'number=1' <<<"$out6"
fi
if [[ -x "$WEFT" ]]; then
  set +e
  "$WEFT" --only docs <<<"$FENCE" >/dev/null
  rc_weft_fence=$?
  set -e
  assert_eq "weft --only docs frees README fence (path glob + swallow)" "$rc_weft_fence" "0"
fi

echo "======== 8. missing --only is usage ========"
set +e
"$WOOF" </dev/null >/dev/null 2>/tmp/woof-demo-err.$$
rcu=$?
set -e
assert_eq "no --only exits 2" "$rcu" "2"
rm -f /tmp/woof-demo-err.$$

echo "======== 9. dogfood sitbone 77df1da ========"
SB=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
if [[ -d "$SB/.git" ]]; then
  set +e
  sb=$("$WOOF" --only prose --emit < <(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da))
  sbrc=$?
  sbv=$("$WOOF" --only prose < <(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da))
  set -e
  echo "$sbv" | head -20
  assert_eq "sitbone 77df1da fails --only prose" "$sbrc" "1"
  assert "sitbone leak includes Makefile" grep -q $'Makefile\t' <<<"$sb"
  assert "sitbone README fence 2048 is number ply" grep -q $'README.md\t' <<<"$sb"
  if grep -E $'^README.md\t[0-9]+\tnumber\t' <<<"$sb" | grep -q 2048; then
    assert "README cert 2048 is class number (not swallowed string)" true
  else
    echo "$sb" | grep README | head
    assert "README cert 2048 is class number (not swallowed string)" false
  fi
  if [[ -x "$WEFT" ]]; then
    set +e
    we=$("$WEFT" --only docs --emit < <(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da))
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
