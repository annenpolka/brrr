#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/aloud"
ALOUD="$ROOT/aloud"

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
    echo "  FAIL $name got=$(printf %q "$got") want=$(printf %q "$want")" >&2
  fi
}

SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"

echo "======== 1. selftest ========"
"$ALOUD" --selftest

echo "======== 2. synthetic BLAST then spoken ========"
REPO="$(mktemp -d "${TMPDIR:-/tmp}/aloud-demo.XXXXXX")"
cleanup() { rm -rf "$REPO"; }
trap cleanup EXIT
git -C "$REPO" init -q -b main
git -C "$REPO" config user.name aloud
git -C "$REPO" config user.email aloud@demo
git -C "$REPO" config commit.gpgsign false
cp "$ROOT/fixtures/old.swift" "$REPO/arbiter.swift"
git -C "$REPO" add arbiter.swift
git -C "$REPO" commit -q -m "threshold 0.4"
cp "$ROOT/fixtures/blast.swift" "$REPO/arbiter.swift"
git -C "$REPO" add arbiter.swift
git -C "$REPO" commit -q -m "rename to presentThreshold 0.45"
BLAST_REV="$(git -C "$REPO" rev-parse HEAD)"
cp "$ROOT/fixtures/later.swift" "$REPO/arbiter.swift"
git -C "$REPO" add arbiter.swift
git -C "$REPO" commit -q -m "speak 0.45 at mic"

echo "----- at BLAST (until=blast): ALOUD must be 0 -----"
at_blast="$("$ALOUD" -C "$REPO" --blast "$BLAST_REV" --until "$BLAST_REV" --header --all)"
echo "$at_blast"
assert "no ALOUD at the blast itself" \
  bash -c '! grep -q $'\''^ALOUD\t'\'' <<<"$1"' _ "$at_blast"
assert "two MUTE riders at blast" \
  bash -c '[[ "$(grep -c $'\''^MUTE\t'\'' <<<"$1")" == "2" ]]' _ "$at_blast"
assert "FOSSIL 0.4 at blast" \
  grep -q $'FOSSIL\tOVERRIDE\tOVERRIDE' <<<"$at_blast"
assert "PRE 0.45 at blast" \
  grep -q $'PRE\tSHADOW\tSHADOW' <<<"$at_blast"

echo "----- later: omitted-then-spoken is distinct -----"
later="$("$ALOUD" -C "$REPO" --blast "$BLAST_REV" --until HEAD --header --all)"
echo "$later"
assert "ALOUD is mic 0.45, blast was TACIT" \
  grep -q $'ALOUD\tTACIT\tSHADOW\tprod\tPresenceArbiter\tpresentThreshold\t0.4→0.45\t0.45' <<<"$later"
assert "MUTE stayed camera omitted" \
  grep -q $'MUTE\tTACIT\tTACIT' <<<"$later"
assert "FOSSIL still radar 0.4 not 0.45" \
  grep -q $'FOSSIL' <<<"$later" && grep -q $'\t0.4\tarbiter.swift' <<<"$later"
assert "PRE lidar already spoke at blast" \
  grep -q $'PRE\tSHADOW\tSHADOW' <<<"$later"
assert "LATE new site born speaking 0.45 is not ALOUD" \
  grep -q $'LATE\t—\tSHADOW' <<<"$later"
sum="$("$ALOUD" -C "$REPO" --blast "$BLAST_REV" --until HEAD --summary presentThreshold)"
echo "$sum"
assert "summary 1 ALOUD / 1 MUTE / 1 FOSSIL / 1 PRE / 1 LATE" \
  grep -q $'PresenceArbiter\tpresentThreshold\t1\t1\t1\t1\t1' <<<"$sum"
set +e
"$ALOUD" -C "$REPO" --blast "$BLAST_REV" --until HEAD --check >/dev/null
rc=$?
set -e
assert_eq "later --check exits 1 (ALOUD found)" "$rc" "1"
set +e
"$ALOUD" -C "$REPO" --blast "$BLAST_REV" --until "$BLAST_REV" --check >/dev/null
rc=$?
set -e
assert_eq "at-blast --check exits 0 (no ALOUD yet)" "$rc" "0"

echo "======== 3. sitbone e9b0f75 presentThreshold ========"
if [[ -d "$SITBONE/.git" ]]; then
  at="$("$ALOUD" -C "$SITBONE" --blast e9b0f75 --until e9b0f75 --summary presentThreshold)"
  echo "$at"
  assert "sitbone at blast: 0 ALOUD 27 MUTE" \
    grep -q $'PresenceArbiter\tpresentThreshold\t0\t27\t0\t0\t0' <<<"$at"
  now="$("$ALOUD" -C "$SITBONE" --blast e9b0f75 --summary presentThreshold)"
  echo "$now"
  assert "sitbone HEAD: still 0 ALOUD 27 MUTE" \
    grep -q $'PresenceArbiter\tpresentThreshold\t0\t27\t0\t0\t0' <<<"$now"
  abs="$("$ALOUD" -C "$SITBONE" --blast e9b0f75 --summary PresenceArbiter)"
  echo "$abs"
  assert "sitbone absentThreshold born-slot also MUTE 27" \
    grep -q $'PresenceArbiter\tabsentThreshold\t0\t27\t0\t0\t0' <<<"$abs"
  hyst="$("$ALOUD" -C "$SITBONE" --blast e9b0f75 --header --only mute presentThreshold)"
  assert "hysteresis tests still omit presentThreshold" \
    grep -q 'PresenceHysteresisTests.swift' <<<"$hyst"
  assert "production SitboneCore.swift still MUTE" \
    grep -q 'SitboneCore.swift' <<<"$hyst"
  set +e
  "$ALOUD" -C "$SITBONE" --blast e9b0f75 --check presentThreshold >/dev/null
  rc=$?
  set -e
  assert_eq "sitbone --check exits 0 (nobody spoke)" "$rc" "0"
else
  echo "  skip sitbone (not found)"
fi

echo "======== 4. kizu --agent born speaking is LATE, not ALOUD ========"
if [[ -d "$KIZU/.git" ]]; then
  ksum="$("$ALOUD" -C "$KIZU" --blast 3d4b543 --summary agent)"
  echo "$ksum"
  assert "kizu ALOUD is 0 (no blast survivor later spoke)" \
    bash -c '! grep -q $'\''\t[1-9][0-9]*\t'\'' <<<"$(echo "$1" | awk -F"\t" '\''NR>2 && $3+0>0 {print}'\'')"' _ "$ksum"
  assert "kizu HookPostTool LATE restated claude-code" \
    grep -q $'HookPostTool\tagent\t0\t0\t0\t0\t' <<<"$ksum"
  kall="$("$ALOUD" -C "$KIZU" --blast 3d4b543 --all --summary agent)"
  echo "$kall"
  assert "kizu LATE count is SHADOW-of-new only (not cursor OVERRIDE)" \
    grep -q $'^LATE\t' <<<"$kall"
  ktsv="$("$ALOUD" -C "$KIZU" --blast 3d4b543 --header --only late HookPostTool agent)"
  assert "kizu LATE later=SHADOW claude-code" \
    grep -q $'LATE\t—\tSHADOW\ttest\tHookPostTool\tagent' <<<"$ktsv"
  assert "kizu LATE is not ALOUD" \
    bash -c '! grep -q $'\''^ALOUD\t'\'' <<<"$1"' _ "$ktsv"
  set +e
  "$ALOUD" -C "$KIZU" --blast 3d4b543 --check agent >/dev/null
  rc=$?
  set -e
  assert_eq "kizu --check exits 0 (LATE is not ALOUD)" "$rc" "0"
else
  echo "  skip kizu (not found)"
fi

echo
echo "passed=$PASS failed=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
