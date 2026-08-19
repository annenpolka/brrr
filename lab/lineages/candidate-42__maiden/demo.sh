#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/maiden"
M="$ROOT/maiden"

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

SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"

echo "======== 1. selftest ========"
"$M" --selftest

echo "======== 2. never-red is not rg PASS ========"
J2019="$ROOT/fixtures/junit/run-2019-fail.xml"
J2024="$ROOT/fixtures/junit/run-2024-green.xml"
hist="$("$M" --no-ledger --summary --header "$J2019" "$J2024")"
echo "$hist"
assert "alpha scarred (failed in 2019)" \
  grep -q $'SCARRED\t1\t1\t0\t' <<<"$hist"
assert "beta maiden (only ever pass)" \
  grep -q $'MAIDEN\t2\t0\t0\t' <<<"$hist"
assert "gamma skipped not maiden" \
  grep -q $'SKIPPED\t0\t0\t2\t' <<<"$hist"
assert "delta maiden (born green in 2024)" \
  grep -q $'MAIDEN\t1\t0\t0\t' <<<"$hist"

latest="$("$M" --no-ledger --latest --summary "$J2019" "$J2024")"
echo "$latest"
assert "latest-only maidens the scarred test" \
  grep -q 'MAIDEN 3' <<<"$latest"
assert "latest-only has zero scarred" \
  grep -q 'SCARRED 0' <<<"$latest"

sk="$("$M" --no-ledger --skeptic --header "$J2019" "$J2024")"
echo "$sk"
assert "skeptic is alpha only" \
  grep -q $'SCARRED\t1\t1\t0\t' <<<"$sk"
assert "skeptic does not name beta" \
  bash -c '! grep -q beta <<<"$1"' _ "$sk"

echo "======== 3. skip-only is not maiden ========"
skip="$("$M" --no-ledger --summary "$ROOT/fixtures/junit/run-2019-fail.xml")"
echo "$skip"
assert "2019 gamma is SKIPPED" grep -q SKIPPED <<<"$skip"
assert "2019 has one maiden (beta)" grep -q 'MAIDEN 1' <<<"$skip"

echo "======== 4. GHA prefix + cargo ========"
gha="$("$M" --no-ledger --summary --header "$ROOT/fixtures/gha/cargo.txt")"
echo "$gha"
assert "gha undo scarred" grep -q $'SCARRED\t1\t1\t0\t' <<<"$gha"
assert "gha parse maiden" grep -q 'kizu::hook::parse' <<<"$gha"

echo "======== 5. Swift Testing display ≠ swift test list (v0.1 split) ========"
swift="$("$M" --no-alias-swift --no-ledger --summary --header --roster \
  "$ROOT/fixtures/swift/list.txt" \
  "$ROOT/fixtures/swift/testing.txt" \
  "$ROOT/fixtures/swift/xctest.txt")"
echo "$swift"
assert "list specifier formatTimeZero is UNKNOWN without alias" \
  grep -q $'UNKNOWN\t0\t0\t0\t—\t—\t—\tSitboneUITests.UILogicTests/formatTimeZero' <<<"$swift"
assert "display name is an ORPHAN pass" \
  grep -q 'formatTime: ゼロ' <<<"$swift"
assert "nested specifier is kept on the roster" \
  grep -q 'PresenceArbiterTests/EMASmoothing/firstReadingNoSmoothing' <<<"$swift"
assert "XCTest specifier joins the roster" \
  grep -q 'SitboneCoreTests.SessionProfileTests/testDefaultProfile' <<<"$swift"

echo "======== 5b. v0.2 identity: display → specifier ========"
swift2="$("$M" -C "$ROOT/fixtures/tree" --no-ledger --summary --header --roster \
  "$ROOT/fixtures/swift/list.txt" \
  "$ROOT/fixtures/swift/testing.txt" \
  "$ROOT/fixtures/swift/xctest.txt")"
echo "$swift2"
assert "alias maidens formatTimeZero" \
  grep -q $'MAIDEN\t1\t0\t0\t' <<<"$(grep formatTimeZero <<<"$swift2")"
assert "alias maidens nested EMASmoothing" \
  grep -q $'MAIDEN\t1\t0\t0\t' <<<"$(grep EMASmoothing/firstReadingNoSmoothing <<<"$swift2")"
assert "alias removes display ORPHANs" \
  bash -c '! grep -q "formatTime: ゼロ" <<<"$1" && ! grep -q "初回読み取り" <<<"$1"' _ "$swift2"

echo "======== 6. sitbone / kizu (no junit, no xcresult, CI logs 410) ========"
if [[ -d "$SITBONE/.git" ]]; then
  list_file="$(mktemp "${TMPDIR:-/tmp}/maiden-sitbone-list.XXXXXX")"
  log_file="$(mktemp "${TMPDIR:-/tmp}/maiden-sitbone-log.XXXXXX")"
  if swift test --package-path "$SITBONE" list --skip-build >"$list_file" 2>/dev/null; then
    n_list="$(grep -c '/' "$list_file" || true)"
    echo "sitbone swift test list: $n_list specifiers"
    sit_sum="$("$M" -C "$SITBONE" --no-ledger --roster --counts "$list_file")"
    echo "$sit_sum  (list lines with /: $n_list)"
    assert "sitbone roster is not MAIDEN" \
      grep -q 'MAIDEN 0' <<<"$sit_sum"
    assert "sitbone nested specifiers are not dropped" \
      grep -q "UNKNOWN $n_list" <<<"$sit_sum"
    if swift test --package-path "$SITBONE" --filter 'UILogicTests/formatTimeZero' --skip-build >"$log_file" 2>/dev/null; then
      echo "---- one green Swift Testing log + aliases from Tests/ ----"
      joined="$("$M" -C "$SITBONE" --no-ledger --roster --counts "$list_file" "$log_file")"
      echo "$joined"
      detail="$("$M" -C "$SITBONE" --no-ledger --roster --only MAIDEN,ORPHAN "$list_file" "$log_file")"
      echo "$detail"
      assert "green log maidens the list specifier via alias" \
        grep -q $'MAIDEN\t1\t0\t0\t' <<<"$(grep formatTimeZero <<<"$detail")"
      assert "display name is not an orphan after alias" \
        bash -c '! grep -q "formatTime: ゼロ" <<<"$1"' _ "$detail"
    else
      echo "skip live swift test filter (build required)"
    fi
  else
    echo "skip sitbone swift test list"
  fi
  rm -f "$list_file" "$log_file"
else
  echo "skip sitbone (missing $SITBONE)"
fi

if [[ -d "$KIZU/.git" ]]; then
  klist="$(mktemp "${TMPDIR:-/tmp}/maiden-kizu-list.XXXXXX")"
  if cargo test --manifest-path "$KIZU/Cargo.toml" --all-targets --all-features -- --list >"$klist" 2>/dev/null; then
    n_k="$(grep -c ': test$' "$klist" || true)"
    echo "kizu cargo --list: $n_k tests"
    ksum="$("$M" --no-ledger --roster --counts "$klist")"
    echo "$ksum  (list : test: $n_k)"
    assert "kizu roster is UNKNOWN" grep -q "UNKNOWN $n_k" <<<"$ksum"
    assert "kizu roster MAIDEN 0" grep -q 'MAIDEN 0' <<<"$ksum"
    klog="$(mktemp "${TMPDIR:-/tmp}/maiden-kizu-log.XXXXXX")"
    if cargo test --manifest-path "$KIZU/Cargo.toml" --lib \
      app::tests::compute_operation_diff_empty_when_identical -- --exact >"$klog" 2>/dev/null; then
      echo "---- one kizu cargo result (identity matches --list) ----"
      kjoin="$("$M" --no-ledger --roster --counts "$klist" "$klog")"
      echo "$kjoin"
      krow="$("$M" --no-ledger --roster --only MAIDEN "$klist" "$klog")"
      echo "$krow"
      assert "kizu exact test becomes MAIDEN (joined)" \
        grep -q 'app::tests::compute_operation_diff_empty_when_identical' <<<"$krow"
    fi
    rm -f "$klog"
  else
    echo "skip kizu cargo --list"
  fi
  rm -f "$klist"
else
  echo "skip kizu (missing $KIZU)"
fi

echo "======== 7. rg PASS would include the 2019 scar ========"
# skeptic of current-green: what grep PASS on the newest junit would keep
rg_pass="$(grep -c 'testcase ' "$J2024" || true)"
echo "junit 2024 testcase tags: $rg_pass (includes repaired alpha + skip gamma)"
assert "history and latest diverge on alpha" \
  bash -c '
    hist=$(grep -c SCARRED <<<"$1")
    lat=$(grep "SCARRED 0" <<<"$2")
    test "$hist" -ge 1 && test -n "$lat"
  ' _ "$hist" "$latest"

echo "======== demo $PASS passed, $FAIL failed ========"
test "$FAIL" -eq 0
