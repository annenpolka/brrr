#!/usr/bin/env bash
# Extra args (e.g. ./demo.sh 0) are ignored.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
chmod +x "$ROOT/preen"
PREEN="$ROOT/preen"

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
TENAOSHI="${TENAOSHI:-/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi}"

echo "======== 1. selftest ========"
"$PREEN" --selftest

echo "======== 2. fixtures: constructed default ≠ signature default ========"
fix_out="$("$PREEN" -C "$ROOT/fixtures" --header --all)"
echo "$fix_out" | head -30
assert "fixture tacit presentThreshold" \
  grep -q $'TACIT\tprod\tPresenceArbiter\tpresentThreshold\t0.45\t—' <<<"$fix_out"
assert "fixture shadow presentThreshold" \
  grep -q $'SHADOW\tprod\tPresenceArbiter\tpresentThreshold\t0.45\t0.45' <<<"$fix_out"
assert "fixture override presentThreshold" \
  grep -q $'OVERRIDE\tprod\tPresenceArbiter\tpresentThreshold\t0.45\t0.50' <<<"$fix_out"
assert "fixture SessionProfile omitted driftDelay TACIT 15" \
  grep -q $'TACIT\tprod\tSessionProfile\tthresholds.driftDelay\t15\t—' <<<"$fix_out"
assert "fixture passed Thresholds(driftDelay: 15) nested SHADOW" \
  grep -q $'SHADOW\tprod\tSessionProfile\tthresholds.driftDelay\t15\t15' <<<"$fix_out"
assert "fixture passed Thresholds(driftDelay: 20) nested OVERRIDE" \
  grep -q $'OVERRIDE\tprod\tSessionProfile\tthresholds.driftDelay\t15\t20' <<<"$fix_out"
assert "PinProfile constructed default is OVERRIDE 20 not TACIT 15" \
  grep -q $'OVERRIDE\tprod\tPinProfile\tthresholds.driftDelay\t15\t20' <<<"$fix_out"
assert "PinProfile is not signature-TACIT 15" \
  bash -c '! grep -q $'"'"'TACIT\tprod\tPinProfile\tthresholds.driftDelay'"'"' <<<"$1"' _ "$fix_out"
assert "DotInit .init() unfolds TACIT 15" \
  grep -q $'TACIT\tprod\tDotInit\tthresholds.driftDelay\t15' <<<"$fix_out"
assert "fixture clap omit is TACIT" \
  grep -q $'TACIT\tprod\tHookPostTool\tagent' <<<"$fix_out"
assert "fixture clap HookPostTool shadow" \
  grep -q $'SHADOW\tprod\tHookPostTool\tagent' <<<"$fix_out"
assert "fixture clap HookStop override" \
  grep -q $'OVERRIDE\tprod\tHookStop\tagent' <<<"$fix_out"
assert "fixture clap interpolation bound" \
  grep -q $'BOUND\tprod\tHookPostTool\tagent' <<<"$fix_out"
assert "fixture clap long= agent-id" \
  grep -q $'SHADOW\tprod\tHookNamed\tagent' <<<"$fix_out"
assert "fixture clap shebang --agent cline is OVERRIDE" \
  grep -q $'OVERRIDE\tprod\tHookPostTool\tagent\t"claude-code"\t"cline"' <<<"$fix_out"
assert "fixture clap contains/prose is not extra TACIT" \
  bash -c 'n=$(grep -c $'"'"'TACIT\tprod\tHookPostTool\tagent'"'"' <<<"$1"); [[ "$n" == "1" ]]' _ "$fix_out"

echo "======== 3. rename as git --git BLAST/FOSSIL ========"
REPO="$(mktemp -d "${TMPDIR:-/tmp}/preen-demo.XXXXXX")"
cleanup() { rm -rf "$REPO"; }
trap cleanup EXIT
git -C "$REPO" init -q -b main
git -C "$REPO" config user.name preen
git -C "$REPO" config user.email preen@demo
git -C "$REPO" config commit.gpgsign false
cp "$ROOT/fixtures/old_arbiter.swift" "$REPO/arbiter.swift"
git -C "$REPO" add arbiter.swift
git -C "$REPO" commit -q -m "threshold 0.4"
cp "$ROOT/fixtures/new_arbiter.swift" "$REPO/arbiter.swift"
git -C "$REPO" add arbiter.swift
git -C "$REPO" commit -q -m "rename to presentThreshold 0.45"
diff_out="$("$PREEN" -C "$REPO" --git HEAD^ HEAD --header --all)"
echo "$diff_out"
assert "rename BLAST tacit" \
  grep -q $'BLAST\tTACIT\tprod\tPresenceArbiter\tpresentThreshold' <<<"$diff_out"
assert "rename FOSSIL 0.4" \
  grep -q $'FOSSIL\tOVERRIDE\tprod\tPresenceArbiter\tpresentThreshold' <<<"$diff_out"
set +e
"$PREEN" -C "$REPO" --git HEAD^ HEAD --check >/dev/null
rc=$?
set -e
assert_eq "rename --check exits 1" "$rc" "1"

echo "======== 4. sitbone ========"
if [[ -d "$SITBONE/.git" ]]; then
  sum="$("$PREEN" -C "$SITBONE" --summary PresenceArbiter)"
  echo "$sum"
  assert "sitbone summary is only PresenceArbiter" \
    bash -c '! grep -qv "^callee\|^PresenceArbiter" <<<"$1"' _ "$sum"
  pt="$("$PREEN" -C "$SITBONE" presentThreshold | wc -l | tr -d ' ')"
  assert "sitbone 27 tacit presentThreshold" \
    bash -c '[[ "$1" == "27" ]]' _ "$pt"
  hyst="$("$PREEN" -C "$SITBONE" --header PresenceArbiter presentThreshold)"
  assert "hysteresis tests ride presentThreshold" \
    grep -q 'PresenceHysteresisTests.swift' <<<"$hyst"
  shadow="$("$PREEN" -C "$SITBONE" --only shadow SessionProfile colorHue)"
  echo "$shadow"
  assert "makeDefault SHADOW colorHue 0.45" \
    grep -q 'SessionProfile.swift' <<<"$shadow"
  nest="$("$PREEN" -C "$SITBONE" --all --header SessionProfile driftDelay)"
  echo "$nest"
  assert "sitbone SessionProfile unfolds constructed Thresholds() as TACIT 15" \
    grep -q $'TACIT\tprod\tSessionProfile\tthresholds.driftDelay\t15' <<<"$nest"
  blast="$("$PREEN" -C "$SITBONE" --git e9b0f75^ e9b0f75 --summary PresenceArbiter)"
  echo "$blast"
  assert "hysteresis commit BLAST presentThreshold" \
    grep -q $'PresenceArbiter\tpresentThreshold\t27' <<<"$blast"
  assert "hysteresis commit BLAST absentThreshold" \
    grep -q $'PresenceArbiter\tabsentThreshold\t27' <<<"$blast"
  set +e
  "$PREEN" -C "$SITBONE" --git e9b0f75^ e9b0f75 --check PresenceArbiter >/dev/null
  rc=$?
  set -e
  assert_eq "sitbone --check BLAST exits 1" "$rc" "1"
else
  echo "  skip sitbone (not found)"
fi

echo "======== 5. kizu clap --agent is an invocation, not a command-shaped line ========"
if [[ -d "$KIZU/.git" ]]; then
  ksum="$("$PREEN" -C "$KIZU" --all --summary agent)"
  echo "$ksum"
  assert "kizu HookPostTool harvested" \
    grep -q HookPostTool <<<"$ksum"
  assert "kizu HookStop harvested" \
    grep -q HookStop <<<"$ksum"
  ktsv="$("$PREEN" -C "$KIZU" --all --header HookPostTool agent)"
  assert "kizu tests SHADOW claude-code" \
    grep -q $'SHADOW\ttest\tHookPostTool\tagent' <<<"$ktsv"
  assert "kizu install {agent_arg} is BOUND" \
    grep -q $'BOUND\tprod\tHookPostTool\tagent' <<<"$ktsv"
  assert "kizu cline is OVERRIDE" \
    grep -q $'OVERRIDE\tprod\tHookPostTool\tagent\t"claude-code"\t"cline"' <<<"$ktsv"
  assert "kizu shebang cline OVERRIDE restored" \
    grep -q $'install.rs\t345' <<<"$ktsv"
  # gold lie gone: clap TACIT is omitted flags of an invoked command
  ktacit=$(grep -c $'TACIT\t' <<<"$ktsv" || true)
  assert_eq "kizu HookPostTool TACIT is 0 (not 6 mentions)" "$ktacit" "0"
  kstop="$("$PREEN" -C "$KIZU" --only tacit HookStop agent)"
  assert_eq "kizu HookStop TACIT is 0" "$kstop" ""
  # old gold lie: doc-comment / "older kizu install" are not riders
  assert "kizu doc-comment settings_json.rs:15 is not TACIT" \
    bash -c '! grep -q $'"'"'settings_json.rs\t15'"'"' <<<"$1"' _ "$ktsv"
  assert "kizu comment settings_json.rs:152 is not TACIT" \
    bash -c '! grep -q $'"'"'settings_json.rs\t152'"'"' <<<"$1"' _ "$ktsv"
else
  echo "  skip kizu (not found)"
fi

echo "======== 6. tenaoshi reopenUnit ========"
if [[ -d "$TENAOSHI/.git" ]]; then
  rtsv="$("$PREEN" -C "$TENAOSHI" --all --header reopenUnit)"
  echo "$rtsv"
  assert "signature not a call" \
    bash -c '! grep -q "Bool = true" <<<"$1"' _ "$rtsv"
  assert "reopenFocusedFinalUnit SHADOW true" \
    grep -q $'SHADOW\tprod\treopenUnit\treturningToFinal\ttrue\ttrue\tEngine/Sources/TenaoshiEngine/ReviewSession.swift\t267' <<<"$rtsv"
  assert "PanelView TACIT returningToFinal" \
    grep -q 'PanelView.swift' <<<"$rtsv"
else
  echo "  skip tenaoshi (not found)"
fi

echo
echo "passed=$PASS failed=$FAIL"
if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi
exit 0
