#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises kernel slew, not a screenshot.
# ./demo.sh 0  is the default live demo.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./yaw

SCARP="${SCARP:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b60-8466-71a3-894a-7bf303f098fd/scarp}"

case "${1:-0}" in
  0) ;;
  *) echo "usage: ./demo.sh 0" >&2; exit 2 ;;
esac

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }
word() { tr -d '\n'; }

echo "== selftest =="
python3 ./yaw selftest

echo
echo "== fixtures (two named clocks) =="
got=$(python3 ./yaw --as CLOCK_MONOTONIC CLOCK_MONOTONIC_RAW < fixtures/slew.txt | word)
[[ "$got" == "SLEW" ]] || fail "slew.txt → $got"
pass "fixtures/slew.txt → SLEW"

got=$(python3 ./yaw --as CLOCK_MONOTONIC_RAW CLOCK_UPTIME_RAW < fixtures/sleep.txt | word)
[[ "$got" == "SLEEP" ]] || fail "sleep.txt → $got"
pass "fixtures/sleep.txt → SLEEP"

got=$(python3 ./yaw --as CLOCK_REALTIME CLOCK_MONOTONIC < fixtures/step.txt | word)
[[ "$got" == "STEP" ]] || fail "step.txt → $got"
pass "fixtures/step.txt → STEP"

got=$(python3 ./yaw --as python.monotonic CLOCK_UPTIME_RAW < fixtures/rest.txt | word)
[[ "$got" == "REST" ]] || fail "rest.txt → $got"
pass "fixtures/rest.txt → REST"

echo
echo "== unlabeled numbers need --as (not a second scarp) =="
got=$(printf '92.5 100\n' | python3 ./yaw --as CLOCK_MONOTONIC CLOCK_MONOTONIC_RAW | word)
[[ "$got" == "SLEW" ]] || fail "unlabeled --as → $got"
pass "92.5 100 --as MONOTONIC RAW → SLEW"

echo
echo "== monotonic means POSIX CLOCK_MONOTONIC, not python =="
got=$(python3 ./yaw --as monotonic raw <<'EOF' | word
monotonic 92.5
raw 100
EOF
)
[[ "$got" == "SLEW" ]] || fail "monotonic alias → $got"
pass "monotonic vs raw → SLEW (POSIX, not time.monotonic)"

BACKEND=$(python3 ./yaw --version)
echo
echo "== live clocks ($BACKEND) =="
python3 ./yaw clocks | sed -n '1,10p'

if [[ "$BACKEND" == *darwin* ]]; then
  echo
  echo "== object pair: POSIX CLOCK_MONOTONIC vs RAW =="
  python3 ./yaw --explain
  python3 ./yaw --require SLEW || fail "live MONOTONIC vs RAW should be SLEW"
  pass "yaw → SLEW (kernel adjtime)"

  echo
  echo "== yaw clocks | yaw is the same object (filter, no spawn) =="
  got=$(python3 ./yaw clocks | python3 ./yaw | word)
  [[ "$got" == "SLEW" ]] || fail "clocks | yaw → $got"
  pass "yaw clocks | yaw → SLEW"

  echo
  echo "== RAW vs UPTIME_RAW is SLEEP, not slew =="
  got=$(python3 ./yaw CLOCK_MONOTONIC_RAW CLOCK_UPTIME_RAW | word)
  [[ "$got" == "SLEEP" ]] || fail "RAW vs UPTIME → $got"
  pass "RAW vs UPTIME_RAW → SLEEP"

  echo
  echo "== wall vs POSIX CLOCK_MONOTONIC is REST (no true step) =="
  got=$(python3 ./yaw CLOCK_REALTIME CLOCK_MONOTONIC | word)
  [[ "$got" == "REST" ]] || fail "wall vs MONOTONIC → $got"
  pass "wall vs CLOCK_MONOTONIC → REST"

  echo
  echo "== all canonical pairs =="
  python3 ./yaw --all

  echo
  echo "== wall vs RAW: scarp's ntp pair (v0.1 named STEP; v0.2 SLEW) =="
  python3 ./yaw CLOCK_REALTIME CLOCK_MONOTONIC_RAW --explain
  python3 ./yaw CLOCK_REALTIME CLOCK_MONOTONIC_RAW --require SLEW \
    || fail "wall vs RAW should be SLEW (v0.1 called it STEP)"
  pass "wall vs RAW → SLEW (MONOTONIC witness: not a step)"

  echo
  echo "== scarp-cut shape (no CLOCK_MONOTONIC) is still SLEW, not NTP =="
  got=$(python3 ./yaw < fixtures/scarp-ntp.txt | word)
  [[ "$got" == "SLEW" ]] || fail "scarp-ntp.txt → $got want SLEW"
  pass "fixtures/scarp-ntp.txt → SLEW"

  echo
  echo "== folklore: wall vs python.monotonic is SLEEP, not STEP =="
  got=$(python3 ./yaw CLOCK_REALTIME python.monotonic | word)
  [[ "$got" == "SLEEP" ]] || fail "wall vs python.monotonic → $got"
  pass "wall vs python.monotonic → SLEEP"

  if [[ -x "$SCARP" ]]; then
    echo
    echo "== ancestor scarp names the same offset NTP; yaw names SLEW =="
    "$SCARP" cut | "$SCARP" --explain
    ntp=$("$SCARP" cut | "$SCARP" --porcelain | awk -F'\t' '$1=="clock" && $2=="ntp"{print $3}')
    yaw_pair=$(python3 ./yaw CLOCK_REALTIME CLOCK_MONOTONIC_RAW | word)
    slew=$(python3 ./yaw CLOCK_REALTIME CLOCK_MONOTONIC_RAW --porcelain | awk -F'\t' '$1=="gap" && $2=="slew"{print $3}')
    echo "scarp ntp=$ntp  (verdict SLEEP, field ntp)"
    echo "yaw  pair=$yaw_pair slew=$slew"
    [[ "$yaw_pair" == "SLEW" ]] || fail "yaw wall−RAW → $yaw_pair want SLEW"
    python3 - "$ntp" "$slew" <<'PY' || fail "scarp ntp and yaw slew should match"
import sys
ntp, slew = float(sys.argv[1]), float(sys.argv[2])
if abs(ntp - slew) > 0.05:
    raise SystemExit(f"mismatch ntp={ntp} slew={slew}")
print(f"same offset {slew:.6f}s; scarp says ntp, yaw says SLEW")
PY
    pass "scarp ntp=… / yaw SLEW (same number, different object)"
  fi
else
  python3 ./yaw --explain || true
  pass "non-Darwin live pair classified"
fi

echo
echo "demo 0 ok"
exit 0
