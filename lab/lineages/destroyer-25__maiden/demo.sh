#!/usr/bin/env bash
# Replay the load-bearing maiden attacks. Extra args ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
MAIDEN="${MAIDEN:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/maiden}"
FIX="${FIX:-/tmp/destroy-maiden/fixtures}"
SITBONE="${SITBONE:-/Users/annenpolka/ghq/github.com/annenpolka/sitbone}"
KIZU="${KIZU:-/Users/annenpolka/ghq/github.com/annenpolka/kizu}"

if [[ ! -x "$MAIDEN" && -f "$MAIDEN" ]]; then
  chmod +x "$MAIDEN"
fi
if [[ ! -f "$MAIDEN" ]]; then
  echo "demo: maiden not found at $MAIDEN" >&2
  exit 2
fi
if [[ ! -d "$FIX/junit" ]]; then
  echo "demo: generating fixtures via attack.py"
  python3 "$ROOT/attack.py"
fi

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

M=("$MAIDEN" --no-ledger)
J2019="$FIX/junit/run-2019-fail.xml"
J2024="$FIX/junit/run-2024-green.xml"

echo "======== 0. victim selftest (no rewrite) ========"
"$MAIDEN" --selftest
"$MAIDEN" --version

echo "======== 1. gold: never-red is not rg PASS ========"
hist="$("${M[@]}" --summary --header "$J2019" "$J2024")"
echo "$hist"
assert "alpha scarred" grep -q $'SCARRED\t1\t1\t0\t' <<<"$hist"
assert "beta maiden" grep -q $'MAIDEN\t2\t0\t0\t' <<<"$hist"
assert "gamma skipped" grep -q $'SKIPPED\t0\t0\t2\t' <<<"$hist"
latest="$("${M[@]}" --latest --counts "$J2019" "$J2024")"
echo "$latest"
assert "latest maidens the scar" grep -q 'MAIDEN 3' <<<"$latest"
assert "latest has zero scarred" grep -q 'SCARRED 0' <<<"$latest"
sk="$("${M[@]}" --skeptic --header "$J2019" "$J2024")"
echo "$sk"
assert "skeptic is alpha" grep -q $'SCARRED\t1\t1\t0\t' <<<"$sk"
assert "skeptic omits beta" bash -c '! grep -q beta <<<"$1"' _ "$sk"

echo "======== 2. SKIP-only is not maiden ========"
skip="$("${M[@]}" --counts "$FIX/junit/skip-only.xml")"
echo "$skip"
assert "skip-only SKIPPED" grep -q 'SKIPPED 1' <<<"$skip"
assert "skip-only MAIDEN 0" grep -q 'MAIDEN 0' <<<"$skip"
set +e
"${M[@]}" --check MAIDEN "$FIX/junit/skip-only.xml" >/dev/null
rc=$?
set -e
assert "check MAIDEN on skip-only is 0" test "$rc" -eq 0

echo "======== 3. --latest --skeptic cancels skeptic ========"
combo="$("${M[@]}" --latest --skeptic --counts "$J2019" "$J2024")"
echo "$combo"
assert "latest+skeptic is SKEPTIC 0" grep -q 'SKEPTIC 0' <<<"$combo"

echo "======== 4. rename launders a scar ========"
ren="$("${M[@]}" --header "$FIX/junit/rename-fail.xml" "$FIX/junit/rename-pass.xml")"
echo "$ren"
assert "old name scarred" grep -q compute_diff <<<"$ren"
assert "new name maiden" grep -q compute_operation_diff <<<"$ren"
rsk="$("${M[@]}" --skeptic --counts "$FIX/junit/rename-fail.xml" "$FIX/junit/rename-pass.xml")"
assert "rename is not skeptic" grep -q 'SKEPTIC 0' <<<"$rsk"

echo "======== 5. ledger status=red maidens ========"
red="$("${M[@]}" --counts "$FIX/ledger/status-red.jsonl")"
echo "$red"
assert "red-status dropped → MAIDEN" grep -q 'MAIDEN 1' <<<"$red"
assert "red-status SCARRED 0" grep -q 'SCARRED 0' <<<"$red"

echo "======== 6. junit flaky then green is MAIDEN ========"
fl="$("${M[@]}" --header "$FIX/junit/flaky-then-green.xml")"
echo "$fl"
assert "flakyFailure maidens alpha" grep -q $'MAIDEN\t1\t0\t0\t' <<<"$(grep alpha <<<"$fl")"
st="$("${M[@]}" --header "$FIX/junit/status-attr-failed.xml")"
echo "$st"
assert "status=failed maidens alpha" grep -q $'MAIDEN\t1\t0\t0\t' <<<"$(grep alpha <<<"$st")"

echo "======== 7. xcresult missing is empty ========"
xc="$("${M[@]}" --counts "$FIX/xcresult/Missing.xcresult")"
echo "$xc"
assert "missing xcresult is zero" grep -q 'SCARRED 0' <<<"$xc"
assert "missing xcresult not maiden" grep -q 'MAIDEN 0' <<<"$xc"

echo "======== 8. unparsed fail dialects are empty ========"
for kind in go-fail bun-fail nextest-fail; do
  z="$("${M[@]}" --counts "$FIX/ci/$kind.txt")"
  echo "$kind  $z"
  assert "$kind empty fold" grep -q 'MAIDEN 0' <<<"$z"
  assert "$kind not scarred" grep -q 'SCARRED 0' <<<"$z"
done

echo "======== 9. sitbone / kizu UNKNOWN (not maiden) ========"
if [[ -f /tmp/destroy-maiden/logs/sitbone-list.txt ]]; then
  sc="$("${M[@]}" -C "$SITBONE" --roster --counts /tmp/destroy-maiden/logs/sitbone-list.txt)"
  echo "$sc"
  assert "sitbone MAIDEN 0" grep -q 'MAIDEN 0' <<<"$sc"
  assert "sitbone UNKNOWN 213" grep -q 'UNKNOWN 213' <<<"$sc"
else
  echo "skip sitbone list (run attack dogfood first)"
fi
if [[ -f /tmp/destroy-maiden/logs/kizu-list.txt ]]; then
  kc="$("${M[@]}" --roster --counts /tmp/destroy-maiden/logs/kizu-list.txt)"
  echo "$kc"
  assert "kizu MAIDEN 0" grep -q 'MAIDEN 0' <<<"$kc"
  assert "kizu UNKNOWN 489" grep -q 'UNKNOWN 489' <<<"$kc"
else
  echo "skip kizu list (run attack dogfood first)"
fi

echo "======== demo $PASS passed, $FAIL failed ========"
test "$FAIL" -eq 0
