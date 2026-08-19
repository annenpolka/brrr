#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the stream primitive, not a screenshot.
# ./demo.sh 0  is the default live demo.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./lurch

case "${1:-0}" in
  0) ;;
  *) echo "usage: ./demo.sh 0" >&2; exit 2 ;;
esac

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }
names() { awk '{print $1}' | tr '\n' ' ' | sed 's/ *$//'; }

ANCESTOR="${ANCESTOR:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b60-8466-71a3-894a-7bf303f098fd/scarp}"
DESTROY="${DESTROY:-/tmp/destroy-scarp/fixtures}"

echo "== selftest =="
python3 ./lurch selftest

echo
echo "== fixtures: one-pair names match scarp =="
for pair in sleep:SLEEP step:STEP dilate:DILATE rest:REST slew:SLEEP; do
  f=${pair%%:*}; want=${pair##*:}
  got=$(python3 ./lurch < "fixtures/${f}.txt" | names)
  [[ "$got" == "$want" ]] || fail "fixtures/${f}.txt → $got want $want"
  pass "fixtures/${f}.txt → $want"
done

echo
echo "== stream: 3 cuts are two names, not cuts[0],cuts[1] =="
got=$(python3 ./lurch < fixtures/stream-sleep-then-dilate.jsonl | names)
[[ "$got" == "SLEEP DILATE" ]] || fail "sleep-then-dilate → $got"
pass "sleep-then-dilate → SLEEP DILATE"
got=$(python3 ./lurch < fixtures/stream-dilate-then-sleep.jsonl | names)
[[ "$got" == "DILATE SLEEP" ]] || fail "dilate-then-sleep → $got"
pass "dilate-then-sleep → DILATE SLEEP"
got=$(python3 ./lurch < fixtures/stream.jsonl | names)
[[ "$got" == "SLEEP DILATE REST" ]] || fail "stream.jsonl → $got"
pass "stream.jsonl → SLEEP DILATE REST"

word=$(python3 ./lurch < fixtures/stream-dilate-then-sleep.jsonl)
echo "$word" | grep -q $'DILATE\t' || fail "DILATE row missing"
echo "$word" | grep -q 'sleep=' || fail "scarp name sleep= missing on stream"
echo "$word" | grep -q 'ntp=' || fail "scarp name ntp= missing on stream"
pass "every pair carries sleep= and ntp="

echo
echo "== missing proper is lid-close, not 22d DILATE =="
got=$(python3 ./lurch < fixtures/slew-noproper.txt | names)
[[ "$got" == "SLEEP" ]] || fail "slew-noproper → $got want SLEEP"
pass "22-day dump without rusage → SLEEP (1d lid-close)"
got=$(python3 ./lurch < fixtures/wait61.txt | names)
[[ "$got" == "DILATE" ]] || fail "wait61 → $got want DILATE"
pass "61s zero-origin wait → DILATE (not kind=host REST)"
if [[ -x "$ANCESTOR" ]]; then
  scarp_got=$(python3 "$ANCESTOR" < fixtures/slew-noproper.txt | tr -d '\n')
  [[ "$scarp_got" == "DILATE" ]] || fail "ancestor noproper → $scarp_got want DILATE"
  pass "ancestor scarp on the same dump → DILATE (awake−0 beats sleep)"
  scarp_got=$(python3 "$ANCESTOR" < fixtures/wait61.txt | tr -d '\n')
  [[ "$scarp_got" == "REST" ]] || fail "ancestor wait61 → $scarp_got want REST"
  pass "ancestor scarp on 61s wait → REST (fake host marker)"
fi

if [[ -x "$ANCESTOR" ]]; then
  scarp_got=$(python3 "$ANCESTOR" < fixtures/stream-dilate-then-sleep.jsonl | tr -d '\n')
  [[ "$scarp_got" == "DILATE" ]] || fail "ancestor dilate-then-sleep → $scarp_got want DILATE"
  pass "ancestor scarp on dilate-then-sleep → DILATE (throws away SLEEP)"
  scarp_got=$(python3 "$ANCESTOR" < fixtures/stream-sleep-then-dilate.jsonl | tr -d '\n')
  [[ "$scarp_got" == "SLEEP" ]] || fail "ancestor sleep-then-dilate → $scarp_got want SLEEP"
  pass "ancestor scarp on sleep-then-dilate → SLEEP (throws away DILATE)"
fi

echo
echo "== two timestamps (one clock) are REST =="
got=$(printf '1000\n1001\n' | python3 ./lurch | names)
[[ "$got" == "REST" ]] || fail "two timestamps → $got"
pass "1000 1001 → REST"

echo
echo "== unlabeled timestamps are a stream of wall ticks =="
got=$(python3 ./lurch < fixtures/unlabeled.txt | names)
[[ "$got" == "REST REST REST" ]] || fail "unlabeled → $got want REST REST REST"
pass "unlabeled 1000,1001,1005,1010 → REST REST REST (1s, 4s, 5s)"
if [[ -x "$ANCESTOR" ]]; then
  scarp_got=$(python3 "$ANCESTOR" < fixtures/unlabeled.txt | tr -d '\n')
  echo "--- ancestor scarp on the same unlabeled file: $scarp_got ---"
  [[ "$scarp_got" == "STEP" ]] || fail "ancestor unlabeled → $scarp_got want STEP (duration bag)"
  pass "ancestor scarp on the same ticks → STEP (bag of durations)"
fi

if [[ -f "$DESTROY/huge-1000.jsonl" ]]; then
  echo
  echo "== destroyer huge-1000.jsonl: 999 pairs, last is SLEEP =="
  got=$(python3 ./lurch < "$DESTROY/huge-1000.jsonl" | names)
  n=$(printf '%s\n' "$got" | awk '{print NF}')
  last=$(printf '%s\n' "$got" | awk '{print $NF}')
  [[ "$n" == "999" ]] || fail "huge-1000 pairs → $n want 999"
  [[ "$last" == "SLEEP" ]] || fail "huge-1000 last → $last want SLEEP"
  pass "1000 JSONL cuts → 999 names, last SLEEP"
  if [[ -x "$ANCESTOR" ]]; then
    scarp_got=$(python3 "$ANCESTOR" < "$DESTROY/huge-1000.jsonl" | tr -d '\n')
    [[ "$scarp_got" == "REST" ]] || fail "ancestor huge-1000 → $scarp_got want REST (first pair)"
    pass "ancestor scarp on the same 1000 cuts → REST (first pair only)"
  fi
fi

if [[ -f "$DESTROY/huge-1000-unlabeled.txt" ]]; then
  echo
  echo "== destroyer 1000 unlabeled ticks: 999 REST, not first-eight fields =="
  got=$(python3 ./lurch < "$DESTROY/huge-1000-unlabeled.txt" | names)
  n=$(printf '%s\n' "$got" | awk '{print NF}')
  first=$(printf '%s\n' "$got" | awk '{print $1}')
  [[ "$n" == "999" ]] || fail "1000 ticks → $n intervals"
  [[ "$first" == "REST" ]] || fail "first unlabeled interval → $first"
  pass "1000 unlabeled ticks → 999 REST"
fi

echo
echo "== lurch never spawns; the shell sleeps =="
got=$({ python3 ./lurch cut --json
        python3 -c 'import time; time.sleep(0.35)'
        python3 ./lurch cut --json
      } | python3 ./lurch | names)
[[ "$got" == "DILATE" ]] || fail "sleep sandwich → $got want DILATE"
pass "{cut; sleep 0.35; cut} | lurch → DILATE"

echo
echo "== in-process busy loop: proper tracks awake (REST REST) =="
got=$(python3 - <<'PY' | python3 ./lurch | names
import json, time, os
def cut():
    clocks = {}
    if hasattr(time, "CLOCK_MONOTONIC_RAW"):
        clocks["machine"] = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
        clocks["awake"] = time.clock_gettime(time.CLOCK_UPTIME_RAW)
    elif hasattr(time, "CLOCK_BOOTTIME"):
        clocks["machine"] = time.clock_gettime(time.CLOCK_BOOTTIME)
        clocks["awake"] = time.clock_gettime(time.CLOCK_MONOTONIC)
    else:
        clocks["machine"] = time.monotonic()
        clocks["awake"] = time.monotonic()
    clocks["wall"] = time.time()
    clocks["proper"] = time.process_time()
    clocks["pid"] = os.getpid()
    return clocks
print(json.dumps(cut()))
end = time.perf_counter() + 0.28
n = 0
while time.perf_counter() < end:
    n += 1
print(json.dumps(cut()))
end = time.perf_counter() + 0.12
while time.perf_counter() < end:
    n += 1
print(json.dumps(cut()))
PY
)
[[ "$got" == "REST REST" ]] || fail "busy cuts → $got want REST REST"
pass "busy 0.28s+0.12s three cuts → REST REST"

BACKEND=$(python3 ./lurch --version)
echo
echo "== live cut ($BACKEND) =="
CUT=$(python3 ./lurch cut)
echo "$CUT" | sed -n '1,8p'
echo "$CUT" | grep -q $'python.monotonic\t' || fail "cut should emit python.monotonic"
if [[ "$BACKEND" == *darwin* ]]; then
  echo "$CUT" | grep -q $'python_monotonic_role\tawake' || fail "python.monotonic maps to awake"
  echo "$CUT" | python3 ./lurch --explain
  echo "$CUT" | python3 ./lurch --require SLEEP >/dev/null || fail "live Darwin cut should be SLEEP (lid-close)"
  pass "lurch cut | lurch → SLEEP (lid-close, not NTP)"

  echo
  echo "== live 3-cut stream vs first pair =="
  STREAM=$(mktemp)
  trap 'rm -f "$STREAM"' EXIT
  { python3 ./lurch cut --json
    python3 -c 'import time; time.sleep(0.35)'
    python3 ./lurch cut --json
    python3 ./lurch cut --json
  } > "$STREAM"
  echo "--- lurch (adjacent pairs) ---"
  python3 ./lurch --explain < "$STREAM"
  got=$(python3 ./lurch < "$STREAM" | names)
  [[ "$got" == "DILATE REST" ]] || fail "live 3 cuts → $got want DILATE REST"
  pass "{cut; sleep 0.35; cut; cut} | lurch → DILATE REST"
  if [[ -x "$ANCESTOR" ]]; then
    scarp_got=$(python3 "$ANCESTOR" < "$STREAM" | tr -d '\n')
    [[ "$scarp_got" == "DILATE" ]] || fail "ancestor live stream → $scarp_got want DILATE"
    pass "same bytes | scarp → DILATE (first pair only)"
  fi
  word=$(python3 ./lurch < "$STREAM")
  echo "$word" | grep -q 'sleep=' || fail "live rows should carry sleep="
  echo "$word" | grep -q 'ntp=' || fail "live rows should carry ntp="
  pass "live DILATE REST rows carry sleep= ntp= (scarp names, pair-delta)"

  echo
  echo "== folklore trap: wall vs time.monotonic() since boot =="
  TRAP=$(python3 - <<'PY'
import time, ctypes
libc = ctypes.CDLL(None)
class timeval(ctypes.Structure):
    _fields_ = [("tv_sec", ctypes.c_int64), ("tv_usec", ctypes.c_int32)]
tv = timeval(); size = ctypes.c_size_t(ctypes.sizeof(tv))
rc = libc.sysctlbyname(b"kern.boottime", ctypes.byref(tv), ctypes.byref(size), None, 0)
if rc != 0:
    raise SystemExit("sysctlbyname kern.boottime failed")
boot = tv.tv_sec + tv.tv_usec / 1e6
print(f"wall {boot:.9f} {time.time():.9f}")
print(f"monotonic {0:.9f} {time.monotonic():.9f}")
PY
)
  echo "$TRAP"
  got=$(printf '%s\n' "$TRAP" | python3 ./lurch | names)
  echo "$TRAP" | python3 ./lurch --explain
  [[ "$got" == "SLEEP" ]] || fail "wall vs monotonic → $got (must not be STEP)"
  pass "wall + python.monotonic since boot → SLEEP, not STEP"

  got=$({ python3 ./lurch cut --json --boot
          python3 ./lurch cut --json
        } | python3 ./lurch | names)
  [[ "$got" == "SLEEP" ]] || fail "boot→now → $got"
  pass "{cut --boot; cut} | lurch → SLEEP"
else
  echo "$CUT" | python3 ./lurch --explain || true
  pass "non-Darwin live cut classified"
fi

echo
echo "demo 0 ok"
exit 0
