#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/unsay"
UNSAY="$ROOT/unsay"

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
"$UNSAY" --selftest

echo "======== 2. synthetic BLAST then spoken → --emit → apply ========"
REPO="$(mktemp -d "${TMPDIR:-/tmp}/unsay-demo.XXXXXX")"
cleanup() { rm -rf "$REPO"; }
trap cleanup EXIT
git -C "$REPO" init -q -b main
git -C "$REPO" config user.name unsay
git -C "$REPO" config user.email unsay@demo
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

echo "----- classify later: ALOUD is mic -----"
later="$("$UNSAY" -C "$REPO" --blast "$BLAST_REV" --until HEAD --header --all)"
echo "$later"
assert "ALOUD is mic 0.45, blast was TACIT" \
  grep -q $'ALOUD\tTACIT\tSHADOW\tprod\tPresenceArbiter\tpresentThreshold\t0.4→0.45\t0.45' <<<"$later"
assert "MUTE camera still omitted" \
  grep -q $'MUTE\tTACIT\tTACIT' <<<"$later"
assert "PRE lidar already spoke at blast" \
  grep -q $'PRE\tSHADOW\tSHADOW' <<<"$later"
assert "LATE new is not ALOUD" \
  grep -q $'LATE\t—\tSHADOW' <<<"$later"

echo "----- --emit is a real patch that only unsays ALOUD -----"
patch="$("$UNSAY" -C "$REPO" --blast "$BLAST_REV" --emit)"
echo "$patch"
assert "patch is a unified diff against arbiter.swift" \
  grep -Fq -- '--- a/arbiter.swift' <<<"$patch"
assert "minus line is spoken 0.45" \
  grep -q '^\-.*sensors: \["mic"\], presentThreshold: 0.45' <<<"$patch"
assert "plus line is tacit mic" \
  grep -q '^\+.*sensors: \["mic"\])' <<<"$patch"
changed="$(grep -E '^[+-]' <<<"$patch" | grep -vE '^[+-]{3}' || true)"
assert "changed lines do not rewrite lidar/new/radar" \
  bash -c '! grep -Eq "lidar|radar|\[\"new\"\]" <<<"$1"' _ "$changed"

echo "----- git apply then ALOUD became MUTE -----"
printf '%s\n' "$patch" | git -C "$REPO" apply
applied="$(cat "$REPO/arbiter.swift")"
echo "$applied"
assert "applied mic is tacit" \
  grep -q 'let spoken = PresenceArbiter(sensors: \["mic"\])' <<<"$applied"
assert "applied PRE lidar still 0.45" \
  grep -q 'let pre = PresenceArbiter(sensors: \["lidar"\], presentThreshold: 0.45)' <<<"$applied"
assert "applied LATE new still 0.45" \
  grep -q 'let late = PresenceArbiter(sensors: \["new"\], presentThreshold: 0.45)' <<<"$applied"
assert "applied FOSSIL radar still 0.4" \
  grep -q 'let fossil = PresenceArbiter(sensors: \["radar"\], presentThreshold: 0.4)' <<<"$applied"
after="$("$UNSAY" -C "$REPO" --blast "$BLAST_REV" --summary presentThreshold)"
echo "$after"
assert "after apply: ALOUD 0 MUTE 2 (mic rides again)" \
  grep -q $'PresenceArbiter\tpresentThreshold\t0\t2\t1\t1\t1' <<<"$after"
set +e
"$UNSAY" -C "$REPO" --blast "$BLAST_REV" --check presentThreshold >/dev/null
rc=$?
set -e
assert_eq "after apply --check exits 0 (no ALOUD)" "$rc" "0"

echo "----- at BLAST, --emit is empty -----"
set +e
empty="$("$UNSAY" -C "$REPO" --blast "$BLAST_REV" --until "$BLAST_REV" --emit presentThreshold 2>/tmp/unsay-empty.err)"
rc=$?
set -e
assert_eq "at-blast emit exits 0" "$rc" "0"
assert_eq "at-blast emit stdout empty" "$empty" ""
assert "at-blast stderr names MUTE still ride" \
  grep -q 'MUTE still ride' /tmp/unsay-empty.err
assert "at-blast stderr does not name LATE" \
  bash -c '! grep -q LATE /tmp/unsay-empty.err'

echo "======== 3. sitbone e9b0f75 presentThreshold ========"
if [[ -d "$SITBONE/.git" ]]; then
  now="$("$UNSAY" -C "$SITBONE" --blast e9b0f75 --summary presentThreshold)"
  echo "$now"
  assert "sitbone HEAD: 0 ALOUD 27 MUTE" \
    grep -q $'PresenceArbiter\tpresentThreshold\t0\t27\t0\t0\t0' <<<"$now"
  set +e
  sit_emit="$("$UNSAY" -C "$SITBONE" --blast e9b0f75 --emit presentThreshold 2>/tmp/unsay-sit.err)"
  rc=$?
  set -e
  assert_eq "sitbone --emit exits 0" "$rc" "0"
  assert_eq "sitbone --emit stdout empty (blast still silent)" "$sit_emit" ""
  assert "sitbone stderr names 27 MUTE still ride" \
    grep -q '27 MUTE still ride' /tmp/unsay-sit.err
  assert "sitbone stderr does not name LATE" \
    bash -c '! grep -q LATE /tmp/unsay-sit.err'
  echo "----- --pin MUTE: 27 presentThreshold: 0.45 insertions -----"
  "$UNSAY" -C "$SITBONE" --blast e9b0f75 --emit --pin presentThreshold > /tmp/unsay-sit-pin.diff
  echo "files:"
  grep '^+++' /tmp/unsay-sit-pin.diff
  plus="$(grep -c '^+.*presentThreshold: 0.45' /tmp/unsay-sit-pin.diff || true)"
  minus="$(grep -c '^-.*presentThreshold' /tmp/unsay-sit-pin.diff || true)"
  assert_eq "pin inserts 27 presentThreshold: 0.45" "$plus" "27"
  assert_eq "pin deletes no presentThreshold" "$minus" "0"
  assert "pin production SitboneCore.swift multiline" \
    grep -q 'SitboneCore.swift' /tmp/unsay-sit-pin.diff
  assert "pin hysteresis tests" \
    grep -q 'PresenceHysteresisTests.swift' /tmp/unsay-sit-pin.diff
  COPY="$(mktemp -d "${TMPDIR:-/tmp}/unsay-sit-copy.XXXXXX")"
  while IFS= read -r f; do
    f="${f#+++ b/}"
    mkdir -p "$COPY/$(dirname "$f")"
    cp "$SITBONE/$f" "$COPY/$f"
  done < <(grep '^+++' /tmp/unsay-sit-pin.diff)
  (cd "$COPY" && git apply /tmp/unsay-sit-pin.diff)
  assert "pin patch git-apply on a copy" true
  assert "applied production now speaks 0.45" \
    grep -q 'presentThreshold: 0.45' "$COPY/Sources/SitboneCore/SitboneCore.swift"
  assert "applied hysteresis one-liner speaks 0.45" \
    grep -q 'emaAlpha: 1.0, presentThreshold: 0.45' "$COPY/Tests/SitboneCoreTests/PresenceHysteresisTests.swift"
  rm -rf "$COPY"
else
  echo "  skip sitbone (not found)"
fi

echo "======== 4. kizu --agent LATE is not unsaid ========"
if [[ -d "$KIZU/.git" ]]; then
  ksum="$("$UNSAY" -C "$KIZU" --blast 3d4b543 --summary agent)"
  echo "$ksum"
  assert "kizu ALOUD is 0" \
    grep -q $'HookPostTool\tagent\t0\t0\t0\t0\t' <<<"$ksum"
  assert "kizu HookPostTool LATE restated claude-code" \
    grep -q $'HookPostTool\tagent\t0\t0\t0\t0\t' <<<"$ksum"
  set +e
  kemit="$("$UNSAY" -C "$KIZU" --blast 3d4b543 --emit agent 2>/tmp/unsay-kizu.err)"
  rc=$?
  set -e
  assert_eq "kizu --emit exits 0" "$rc" "0"
  assert_eq "kizu --emit stdout empty (LATE is not ALOUD)" "$kemit" ""
  assert "kizu emit does not delete --agent" \
    bash -c '! grep -q -- "--agent" <<<"$1"' _ "$kemit"
  assert "kizu stderr names 18 LATE born-speaking" \
    grep -q '18 LATE born-speaking, never rode' /tmp/unsay-kizu.err
  assert "kizu stderr does not claim MUTE still ride" \
    bash -c '! grep -q "MUTE still ride" /tmp/unsay-kizu.err'
  set +e
  "$UNSAY" -C "$KIZU" --blast 3d4b543 --emit --pin agent >/dev/null 2>/tmp/unsay-kizu-pin.err
  set -e
  assert "kizu --pin refuses LATE as not MUTE" \
    grep -q 'LATE is not MUTE' /tmp/unsay-kizu-pin.err
  set +e
  "$UNSAY" -C "$KIZU" --blast 3d4b543 --check agent >/dev/null
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
