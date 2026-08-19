#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/badge"
B="$ROOT/badge"

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

echo "======== 1. selftest ========"
"$B" --selftest

echo "======== 2. never-red is not rg PASS ========"
J2019="$ROOT/fixtures/junit/run-2019-fail.xml"
J2024="$ROOT/fixtures/junit/run-2024-green.xml"
hist="$("$B" --no-ledger --summary --header "$J2019" "$J2024")"
echo "$hist"
assert "alpha scarred (failed in 2019)" \
  grep -q $'SCARRED\t1\t1\t0\t' <<<"$hist"
assert "beta maiden (only ever pass)" \
  grep -q $'MAIDEN\t2\t0\t0\t' <<<"$hist"
assert "gamma skipped not maiden" \
  grep -q $'SKIPPED\t0\t0\t2\t' <<<"$hist"
assert "delta maiden (born green in 2024)" \
  grep -q $'MAIDEN\t1\t0\t0\t' <<<"$hist"
assert "triple is in json" \
  grep -q '"method": "alpha"' <<<"$("$B" --no-ledger --json "$J2019" "$J2024")"

latest="$("$B" --no-ledger --latest --summary "$J2019" "$J2024")"
echo "$latest"
assert "latest-only maidens the scarred test" \
  grep -q 'MAIDEN 3' <<<"$latest"
assert "latest-only has zero scarred" \
  grep -q 'SCARRED 0' <<<"$latest"

sk="$("$B" --no-ledger --skeptic --header "$J2019" "$J2024")"
echo "$sk"
assert "skeptic is alpha only" \
  grep -q $'SCARRED\t1\t1\t0\t' <<<"$sk"
assert "skeptic does not name beta" \
  bash -c '! grep -q beta <<<"$1"' _ "$sk"

set +e
"$B" --no-ledger --latest --skeptic "$J2019" "$J2024" >/dev/null 2>&1
lc=$?
set -e
assert "latest+skeptic refuses (not rg PASS)" test "$lc" -eq 2

echo "======== 3. skip-only is not maiden ========"
skip="$("$B" --no-ledger --counts "$ROOT/fixtures/junit/skip-only.xml")"
echo "$skip"
assert "skip-only SKIPPED 1" grep -q 'SKIPPED 1' <<<"$skip"
assert "skip-only MAIDEN 0" grep -q 'MAIDEN 0' <<<"$skip"
set +e
"$B" --no-ledger --check MAIDEN "$ROOT/fixtures/junit/skip-only.xml"
sc=$?
set -e
assert "skip-only --check MAIDEN rc=0" test "$sc" -eq 0

echo "======== 4. flakyFailure is a red ========"
flaky="$("$B" --no-ledger --summary --header "$ROOT/fixtures/junit/flaky-then-green.xml")"
echo "$flaky"
assert "flakyFailure SCARRED alpha" \
  grep -q $'SCARRED\t0\t1\t0\t' <<<"$(grep 'pkg.T::alpha' <<<"$flaky")"
assert "flaky sibling beta still MAIDEN" \
  grep -q $'MAIDEN\t1\t0\t0\t' <<<"$(grep 'pkg.T::beta' <<<"$flaky")"
rerun="$("$B" --no-ledger --counts "$ROOT/fixtures/junit/rerun-failure.xml")"
echo "$rerun"
assert "rerunFailure SCARRED" grep -q 'SCARRED 1' <<<"$rerun"
stattr="$("$B" --no-ledger --summary --header "$ROOT/fixtures/junit/status-attr-failed.xml")"
echo "$stattr"
assert "status=failed SCARRED" \
  grep -q $'SCARRED\t0\t1\t0\t' <<<"$(grep 'pkg.T::alpha' <<<"$stattr")"

echo "======== 5. renamed test pair is one identity ========"
raw="$("$B" --no-unify --no-ledger --counts \
  "$ROOT/fixtures/junit/rename-fail.xml" \
  "$ROOT/fixtures/junit/rename-pass.xml")"
echo "raw-id: $raw"
assert "--no-unify still splits (SCARRED 1 MAIDEN 1)" \
  bash -c 'grep -q "SCARRED 1" <<<"$1" && grep -q "MAIDEN 1" <<<"$1"' _ "$raw"
ren="$("$B" --no-ledger --summary --header \
  "$ROOT/fixtures/junit/rename-fail.xml" \
  "$ROOT/fixtures/junit/rename-pass.xml")"
echo "$ren"
assert "rename is one identity (SCARRED 1, no MAIDEN)" \
  bash -c 'grep -q "SCARRED 1" <<<"$1" && grep -q "MAIDEN 0" <<<"$1"' _ "$ren"
assert "folded spelling is compute_operation_diff" \
  grep -q 'pkg.T::compute_operation_diff' <<<"$ren"
assert "aka keeps compute_diff" \
  grep -q 'compute_diff' <<<"$ren"
assert "folded n_fail=1 n_pass=1" \
  grep -q $'SCARRED\t1\t1\t0\t' <<<"$ren"
rsk="$("$B" --no-ledger --skeptic --counts \
  "$ROOT/fixtures/junit/rename-fail.xml" \
  "$ROOT/fixtures/junit/rename-pass.xml")"
echo "$rsk"
assert "rename pair is skeptic (was 0 under string id)" \
  grep -q 'SKEPTIC 1' <<<"$rsk"
why="$("$B" --no-ledger --why pkg.T::compute_diff \
  "$ROOT/fixtures/junit/rename-fail.xml" \
  "$ROOT/fixtures/junit/rename-pass.xml")"
echo "$why"
assert "why old spelling finds the badge" \
  grep -q 'compute_operation_diff' <<<"$why"
cls="$("$B" --no-ledger --counts \
  "$ROOT/fixtures/junit/classname-changed-fail.xml" \
  "$ROOT/fixtures/junit/classname-changed-pass.xml")"
echo "$cls"
assert "class move is one identity SCARRED" \
  bash -c 'grep -q "SCARRED 1" <<<"$1" && grep -q "MAIDEN 0" <<<"$1"' _ "$cls"

echo "======== 6. sitbone roster is UNKNOWN, not maiden ========"
sit_sum="$("$B" --no-ledger --roster --counts "$ROOT/fixtures/roster/sitbone-list.txt")"
echo "$sit_sum"
assert "sitbone MAIDEN 0" grep -q 'MAIDEN 0' <<<"$sit_sum"
assert "sitbone UNKNOWN 213" grep -q 'UNKNOWN 213' <<<"$sit_sum"
set +e
"$B" --no-ledger --roster --counts --check MAIDEN "$ROOT/fixtures/roster/sitbone-list.txt"
sitc=$?
set -e
assert "sitbone --check MAIDEN rc=0" test "$sitc" -eq 0

if [[ -d "$SITBONE/.git" ]]; then
  list_file="$(mktemp "${TMPDIR:-/tmp}/badge-sitbone-list.XXXXXX")"
  if swift test --package-path "$SITBONE" list --skip-build >"$list_file" 2>/dev/null; then
    n_list="$(grep -c '/' "$list_file" || true)"
    live="$("$B" -C "$SITBONE" --no-ledger --roster --counts "$list_file")"
    echo "live sitbone list: $n_list  $live"
    assert "live sitbone not MAIDEN" grep -q 'MAIDEN 0' <<<"$live"
  else
    echo "skip live sitbone swift test list"
  fi
  rm -f "$list_file"
fi

echo "======== 7. ingest --run ID FILE (argparse order maiden broke) ========"
tmpd="$(mktemp -d "${TMPDIR:-/tmp}/badge-ledger.XXXXXX")"
ing="$("$B" --ledger "$tmpd/ledger.jsonl" ingest --run ci-2024 "$J2024")"
echo "$ing"
assert "ingest --run ID FILE works" grep -q 'ingested' <<<"$ing"
rm -rf "$tmpd"

echo "======== 8. GHA prefix + cargo ========"
gha="$("$B" --no-ledger --summary --header "$ROOT/fixtures/gha/cargo.txt")"
echo "$gha"
assert "gha undo scarred" grep -q $'SCARRED\t1\t1\t0\t' <<<"$gha"
assert "gha parse maiden" grep -q 'kizu::hook::parse' <<<"$gha"

echo "======== demo $PASS passed, $FAIL failed ========"
test "$FAIL" -eq 0
