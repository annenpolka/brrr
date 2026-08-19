#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the primitive, not a screenshot.
# ./demo.sh 0  is the default live demo.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./scarp

case "${1:-0}" in
  0) ;;
  *) echo "usage: ./demo.sh 0" >&2; exit 2 ;;
esac

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }
word() { tr -d '\n'; }

echo "== selftest =="
python3 ./scarp selftest

echo
echo "== fixtures: which clock explains the gap =="
for pair in sleep:SLEEP step:STEP dilate:DILATE rest:REST slew:SLEEP; do
  f=${pair%%:*}; want=${pair##*:}
  got=$(python3 ./scarp < "fixtures/${f}.txt" | word)
  [[ "$got" == "$want" ]] || fail "fixtures/${f}.txt → $got want $want"
  pass "fixtures/${f}.txt → $want"
done

echo
echo "== two timestamps (one clock) are REST, not DILATE =="
got=$(printf '1000\n1001\n' | python3 ./scarp | word)
[[ "$got" == "REST" ]] || fail "two timestamps → $got"
pass "1000 1001 → REST"

echo
echo "== JSONL two cuts: host sleep =="
got=$(printf '%s\n%s\n' \
  '{"wall":1000,"machine":100,"awake":80,"proper":1}' \
  '{"wall":1010,"machine":110,"awake":81,"proper":1}' \
  | python3 ./scarp | word)
[[ "$got" == "SLEEP" ]] || fail "jsonl sleep → $got"
pass "JSONL two cuts → SLEEP"

echo
echo "== scarp never spawns; the shell sleeps =="
got=$({ python3 ./scarp cut --json
        python3 -c 'import time; time.sleep(0.35)'
        python3 ./scarp cut --json
      } | python3 ./scarp | word)
[[ "$got" == "DILATE" ]] || fail "sleep sandwich → $got want DILATE"
pass "{cut; sleep 0.35; cut} | scarp → DILATE"

echo
echo "== in-process busy loop: proper tracks awake (REST) =="
got=$(python3 - <<'PY' | python3 ./scarp | word
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
PY
)
[[ "$got" == "REST" ]] || fail "busy cuts → $got want REST"
pass "busy 0.28s two cuts → REST"

BACKEND=$(python3 ./scarp --version)
echo
echo "== live cut ($BACKEND) =="
CUT=$(python3 ./scarp cut)
echo "$CUT" | sed -n '1,8p'
echo "$CUT" | grep -q $'python.monotonic\t' || fail "cut should emit python.monotonic"
if [[ "$BACKEND" == *darwin* ]]; then
  echo "$CUT" | grep -q $'python_monotonic_role\tawake' || fail "python.monotonic maps to awake"
  echo "$CUT" | python3 ./scarp --explain
  echo "$CUT" | python3 ./scarp --require SLEEP || fail "live Darwin cut should be SLEEP (lid-close)"
  pass "scarp cut | scarp → SLEEP (lid-close, not NTP)"

  echo
  echo "== same question as two cuts: boot origin then now =="
  got=$({ python3 ./scarp cut --json --boot
          python3 ./scarp cut --json
        } | python3 ./scarp | word)
  [[ "$got" == "SLEEP" ]] || fail "boot→now → $got"
  pass "{cut --boot; cut} | scarp → SLEEP"

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
  got=$(printf '%s\n' "$TRAP" | python3 ./scarp | word)
  echo "$TRAP" | python3 ./scarp --explain
  [[ "$got" == "SLEEP" ]] || fail "wall vs monotonic → $got (v0.1 called this STEP)"
  pass "wall + python.monotonic since boot → SLEEP, not STEP"
else
  echo "$CUT" | python3 ./scarp --explain || true
  pass "non-Darwin live cut classified"
fi

echo
echo "demo 0 ok"
exit 0
