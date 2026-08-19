#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/weft"
WEFT="$ROOT/weft"

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
"$WEFT" --selftest

echo "======== 2. stdin gate: docs PR that leaked a number ========"
MIXED='--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
 fn main() {
-    let timeout = 30; // seconds
+    let timeout = 60; // secs
 }
'
set +e
out1=$("$WEFT" --only docs <<<"$MIXED")
rc1=$?
out1e=$("$WEFT" --only comments --emit <<<"$MIXED")
rc1e=$?
out1c=$("$WEFT" --only comments <<<"$MIXED")
rc1c=$?
set -e
echo "$out1"
assert_eq "mixed --only docs exits 1" "$rc1" "1"
assert "mixed verdict is FAIL" grep -q 'weft FAIL' <<<"$out1"
assert "mixed leaked number 30→60" grep -q '30 → 60' <<<"$out1"
assert_not "default is not TSV" grep -q $'path\tline\tclass' <<<"$out1"
assert_eq "mixed --only comments exits 1" "$rc1c" "1"
echo "$out1e"
assert_eq "emit exits 1" "$rc1e" "1"
assert "emit TSV header" grep -q $'path\tline\tclass\top\told\tnew' <<<"$out1e"
assert "emit number chg" grep -q $'number\tchg\t30\t60' <<<"$out1e"
assert_not "emit is not a verdict dump" grep -q 'weft FAIL' <<<"$out1e"

echo "======== 3. comment-only passes ========"
COMMENT='--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
 fn start() {
-    let timeout = 60; // secs
+    let timeout = 60; // timeout
     let retries = 3;
 }
'
set +e
out2=$("$WEFT" --only comments <<<"$COMMENT")
rc2=$?
out2d=$("$WEFT" --only docs <<<"$COMMENT")
rc2d=$?
set -e
echo "$out2"
assert_eq "comment-only --only comments exits 0" "$rc2" "0"
assert "comment-only OK" grep -q 'weft OK' <<<"$out2"
assert_eq "comment-only --only docs exits 0" "$rc2d" "0"

echo "======== 4. --only comments rejects README prose (text ≠ comment) ========"
PROSE='--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-契約は蒸留
+契約は資産
'
set +e
out3=$("$WEFT" --only comments <<<"$PROSE")
rc3=$?
out3d=$("$WEFT" --only docs <<<"$PROSE")
rc3d=$?
set -e
assert_eq "CJK prose fails --only comments" "$rc3" "1"
assert_eq "CJK prose passes --only docs" "$rc3d" "0"

echo "======== 5. docs PR that leaked a number (README + timeout) ========"
DOCS_LEAK='diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,2 +1,2 @@
 # retry
-timeout is 30 seconds
+timeout is 30 seconds (documented)
diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
 fn main() {
-    let timeout = 30; // documented
+    let timeout = 60; // documented
 }
'
set +e
out4=$("$WEFT" --only docs <<<"$DOCS_LEAK")
rc4=$?
out4e=$("$WEFT" --only docs --emit <<<"$DOCS_LEAK")
rc4e=$?
set -e
echo "$out4"
assert_eq "docs PR + number exits 1" "$rc4" "1"
assert "docs PR leaked number" grep -q 'number' <<<"$out4"
assert_not "docs PR does not leak README prose" grep -q 'README.md' <<<"$out4"
assert "docs PR emit 30→60" grep -q $'number\tchg\t30\t60' <<<"$out4e"
assert_eq "emit also exits 1" "$rc4e" "1"

echo "======== 6. missing --only is usage ========"
set +e
"$WEFT" </dev/null >/dev/null 2>/tmp/weft-demo-err.$$
rcu=$?
set -e
assert_eq "no --only exits 2" "$rcu" "2"
rm -f /tmp/weft-demo-err.$$

echo "======== 7. dogfood ========"
dogfood() {
  local name="$1" repo="$2" range="$3"
  shift 3
  if [[ ! -d "$repo/.git" ]]; then
    echo "  skip $name (missing $repo)"
    return 0
  fi
  echo "----- $name $range --only docs -----"
  set +e
  git -C "$repo" diff --no-color --no-ext-diff "$range" | "$WEFT" --only docs
  local rc=$?
  set -e
  echo "  (exit $rc)"
  echo "$rc" > "/tmp/weft-dogfood-$name.rc"
}

SB=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
KZ=/Users/annenpolka/ghq/github.com/annenpolka/kizu
TN=/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
VT=/Users/annenpolka/ghq/github.com/annenpolka/voidtrace

# README update that also rewrote Makefile codesign (not a number, but a class leak)
dogfood sitbone-readme "$SB" "77df1da^..77df1da"
# ADR-only add: genuine docs file, but markdown numbers
dogfood sitbone-adr "$SB" "98a8009^..98a8009"
# docs: record ci — markdown with GitHub run ids (numbers)
dogfood voidtrace-docs-ci "$VT" "ce44c93^..ce44c93"
# restoration commit that also touched Swift tests / pkl
dogfood tenaoshi-restore "$TN" "838c078^..838c078"
# hysteresis number change (not a docs PR)
dogfood sitbone-hysteresis "$SB" "e9b0f75^..e9b0f75"
# kizu version bump (lockfile skipped; Cargo.toml string/number)
dogfood kizu-release "$KZ" "9349dc5^..9349dc5"

if [[ -d "$SB/.git" ]]; then
  set +e
  sb=$(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da | "$WEFT" --only docs --emit)
  sbrc=$?
  set -e
  assert_eq "sitbone README+Makefile fails --only docs" "$sbrc" "1"
  assert "sitbone leak is Makefile, not README" grep -q $'Makefile\t' <<<"$sb"
  assert_not "sitbone README numbers are not leaks" grep -q $'README.md\t' <<<"$sb"
fi

if [[ -d "$SB/.git" ]]; then
  set +e
  git -C "$SB" diff --no-color --no-ext-diff 98a8009^..98a8009 | "$WEFT" --only docs -q
  adrrc=$?
  set -e
  assert_eq "sitbone ADR-only docs commit passes" "$adrrc" "0"
fi

if [[ -d "$VT/.git" ]]; then
  set +e
  vt=$(git -C "$VT" diff --no-color --no-ext-diff ce44c93^..ce44c93 | "$WEFT" --only docs)
  vtrc=$?
  set -e
  echo "$vt"
  assert_eq "voidtrace docs-ci markdown passes --only docs" "$vtrc" "0"
fi

if [[ -d "$TN/.git" ]]; then
  set +e
  tn=$(git -C "$TN" diff --no-color --no-ext-diff 838c078^..838c078 | "$WEFT" --only docs --emit)
  tnrc=$?
  set -e
  assert_eq "tenaoshi restoration fails (tests/pkl leaked)" "$tnrc" "1"
  assert_not "tenaoshi AGENTS.md is not a leak under --only docs" grep -q $'AGENTS.md\t' <<<"$tn"
  if grep -q $'.swift\t' <<<"$tn" || grep -q $'.pkl\t' <<<"$tn" || grep -q $'.json\t' <<<"$tn"; then
    assert "tenaoshi leaked a code path" true
  else
    echo "$tn" | head
    assert "tenaoshi leaked a code path" false
  fi
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
