#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/snag"
SNAG="$ROOT/snag"
WEFT="${WEFT:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b68-3200-7781-bf46-49a3c771f5ff/weft}"

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
"$SNAG" --selftest

echo "======== 2. money shot: timeout bumped beside a comment ========"
MIXED='--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
 fn main() {
-    let timeout = 30; // seconds
+    let timeout = 60; // secs
 }
'
set +e
out1=$("$SNAG" --forbid number <<<"$MIXED")
rc1=$?
out1e=$("$SNAG" --forbid number --emit <<<"$MIXED")
rc1e=$?
set -e
echo "$out1"
assert_eq "mixed --forbid number exits 1" "$rc1" "1"
assert "mixed verdict is TRIP" grep -q 'snag TRIP' <<<"$out1"
assert "mixed hit 30→60" grep -q '30 → 60' <<<"$out1"
assert_not "default is not TSV" grep -q $'path\tline\tclass' <<<"$out1"
echo "$out1e"
assert_eq "emit exits 1" "$rc1e" "1"
assert "emit TSV header" grep -q $'path\tline\tclass\top\told\tnew' <<<"$out1e"
assert "emit number chg" grep -q $'number\tchg\t30\t60' <<<"$out1e"
assert_not "emit is not a verdict dump" grep -q 'snag TRIP' <<<"$out1e"
assert_not "emit is not a comment dump" grep -q 'comment' <<<"$out1e"

echo "======== 3. comment-only clears the number tripwire ========"
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
out2=$("$SNAG" --forbid number <<<"$COMMENT")
rc2=$?
set -e
echo "$out2"
assert_eq "comment-only --forbid number exits 0" "$rc2" "0"
assert "comment-only CLEAR" grep -q 'snag CLEAR' <<<"$out2"

echo "======== 4. README number still trips (not a path glob) ========"
PROSE='--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-timeout is 30
+timeout is 60
'
set +e
out3=$("$SNAG" --forbid number <<<"$PROSE")
rc3=$?
set -e
echo "$out3"
assert_eq "README 30→60 trips --forbid number" "$rc3" "1"
assert "README hit is a number" grep -q 'number' <<<"$out3"

echo "======== 5. weft --only docs vs snag --forbid number ========"
# CJK prose / docs path: weft --only docs passes. No number ply: snag also clears.
CJK='--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-契約は蒸留
+契約は資産
'
# Docs PR + timeout on a code path: both fail, but snag names only the number.
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
# Number hidden in a comment: weft --only docs passes (comment ply).
# v0.2 snag peels the interior and trips. This is the --only-pass / --forbid-fail case.
INTERIOR='--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
 fn main() {
-    let timeout = 30; // timeout 30
+    let timeout = 30; // timeout 60
 }
'
if [[ -x "$WEFT" ]]; then
  set +e
  "$WEFT" --only docs <<<"$CJK" >/dev/null
  rc_cjk_weft=$?
  "$SNAG" --forbid number <<<"$CJK" >/dev/null
  rc_cjk_snag=$?
  weft_docs=$("$WEFT" --only docs <<<"$DOCS_LEAK")
  rc_weft_docs=$?
  snag_docs=$("$SNAG" --forbid number <<<"$DOCS_LEAK")
  rc_snag_docs=$?
  "$WEFT" --only docs <<<"$INTERIOR" >/dev/null
  rc_int_weft=$?
  int_out=$("$SNAG" --forbid number <<<"$INTERIOR")
  rc_int_snag=$?
  set -e
  assert_eq "CJK prose: weft --only docs passes" "$rc_cjk_weft" "0"
  assert_eq "CJK prose: snag --forbid number clears" "$rc_cjk_snag" "0"
  echo "$weft_docs"
  echo "$snag_docs"
  assert_eq "docs+timeout: weft --only docs fails" "$rc_weft_docs" "1"
  assert_eq "docs+timeout: snag --forbid number trips" "$rc_snag_docs" "1"
  assert "snag names 30→60" grep -q '30 → 60' <<<"$snag_docs"
  echo "$int_out"
  assert_eq "comment-interior: weft --only docs passes" "$rc_int_weft" "0"
  assert_eq "comment-interior: snag --forbid number trips" "$rc_int_snag" "1"
  assert "comment-interior names 30→60" grep -q '30 → 60' <<<"$int_out"
else
  echo "  skip weft contrast (missing $WEFT)"
fi

echo "======== 6. missing --forbid is usage ========"
set +e
"$SNAG" </dev/null >/dev/null 2>/tmp/snag-demo-err.$$
rcu=$?
set -e
assert_eq "no --forbid exits 2" "$rcu" "2"
rm -f /tmp/snag-demo-err.$$

echo "======== 7. dogfood ========"
SB=/Users/annenpolka/ghq/github.com/annenpolka/sitbone
KZ=/Users/annenpolka/ghq/github.com/annenpolka/kizu
VT=/Users/annenpolka/ghq/github.com/annenpolka/voidtrace

dogfood() {
  local name="$1" repo="$2" range="$3" flag="$4"
  if [[ ! -d "$repo/.git" ]]; then
    echo "  skip $name (missing $repo)"
    return 0
  fi
  echo "----- $name $range $flag -----"
  set +e
  git -C "$repo" diff --no-color --no-ext-diff "$range" | "$SNAG" $flag
  local rc=$?
  set -e
  echo "  (exit $rc)"
}

if [[ -d "$SB/.git" ]]; then
  dogfood sitbone-hysteresis "$SB" "e9b0f75^..e9b0f75" "--forbid number"
  dogfood sitbone-readme "$SB" "77df1da^..77df1da" "--forbid number"
  dogfood sitbone-adr "$SB" "98a8009^..98a8009" "--forbid number"
  dogfood sitbone-timeout "$SB" "8b1d0f2^..8b1d0f2" "--forbid number"

  set +e
  hyst=$(git -C "$SB" diff --no-color --no-ext-diff e9b0f75^..e9b0f75 | "$SNAG" --forbid number)
  hystrc=$?
  hyste=$(git -C "$SB" diff --no-color --no-ext-diff e9b0f75^..e9b0f75 | "$SNAG" --forbid number --emit)
  readme_n=$(git -C "$SB" diff --no-color --no-ext-diff 77df1da^..77df1da -- README.md | "$SNAG" --forbid number)
  readme_nrc=$?
  set -e
  echo "$hyst" | head -20
  assert_eq "sitbone hysteresis trips --forbid number" "$hystrc" "1"
  assert "hysteresis names 0.4→0.45" grep -q '0.4' <<<"$hyst"
  assert "emit is only numbers" grep -vq $'\tident\t' <<<"$hyste" || true
  if grep -q $'\tident\t' <<<"$hyste"; then
    assert "hysteresis emit is number-only" false
  else
    assert "hysteresis emit is number-only" true
  fi
  echo "$readme_n" | head -12
  assert_eq "sitbone README fence 2048 trips after peel" "$readme_nrc" "1"
  assert "README peel names 2048" grep -q '2048' <<<"$readme_n"

  set +e
  if [[ -x "$WEFT" ]]; then
    git -C "$SB" diff --no-color --no-ext-diff 98a8009^..98a8009 | "$WEFT" --only docs -q
    adr_weft=$?
    git -C "$SB" diff --no-color --no-ext-diff 98a8009^..98a8009 | "$SNAG" --forbid number -q
    adr_snag=$?
    set -e
    assert_eq "sitbone ADR: weft --only docs passes" "$adr_weft" "0"
    assert_eq "sitbone ADR: snag --forbid number trips" "$adr_snag" "1"
  else
    set -e
  fi
fi

if [[ -d "$VT/.git" ]]; then
  dogfood voidtrace-docs-ci "$VT" "ce44c93^..ce44c93" "--forbid number"
  set +e
  if [[ -x "$WEFT" ]]; then
    git -C "$VT" diff --no-color --no-ext-diff ce44c93^..ce44c93 | "$WEFT" --only docs -q
    vt_weft=$?
    vt=$(git -C "$VT" diff --no-color --no-ext-diff ce44c93^..ce44c93 | "$SNAG" --forbid number)
    vt_snag=$?
    set -e
    echo "$vt"
    assert_eq "voidtrace docs-ci: weft --only docs passes" "$vt_weft" "0"
    assert_eq "voidtrace docs-ci: snag --forbid number trips" "$vt_snag" "1"
    assert "voidtrace hit includes a number" grep -q 'number' <<<"$vt"
  else
    set -e
  fi
fi

if [[ -d "$KZ/.git" ]]; then
  dogfood kizu-release "$KZ" "9349dc5^..9349dc5" "--forbid number"
  set +e
  if [[ -x "$WEFT" ]]; then
    git -C "$KZ" diff --no-color --no-ext-diff 9349dc5^..9349dc5 | "$WEFT" --only docs -q
    kz_weft=$?
    git -C "$KZ" diff --no-color --no-ext-diff 9349dc5^..9349dc5 | "$SNAG" --forbid number -q
    kz_snag=$?
    set -e
    # v0.2 peels 0.6→0.7 out of the version string.
    assert_eq "kizu release: weft --only docs fails (string version)" "$kz_weft" "1"
    assert_eq "kizu release: snag --forbid number trips (peeled 0.6→0.7)" "$kz_snag" "1"
  else
    set -e
  fi
fi

echo
echo "PASS=$PASS FAIL=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
echo "demo ok"
exit 0
