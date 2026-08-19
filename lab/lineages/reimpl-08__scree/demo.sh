#!/usr/bin/env bash
# Gold oracle for scree. Optional arg is ignored (ancestor demo.sh 0).
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./scree
S=./scree
pass=0
fail=0

ok() { echo "PASS: $*"; pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }

want() {
  local label="$1" expected="$2" got
  got=$(cat)
  if [ "$got" = "$expected" ]; then
    ok "$label → $expected"
  else
    bad "$label → got ${got:-<empty>} want $expected"
  fi
}

echo "== selftest =="
"$S" selftest

echo
echo "== fixtures: which clock explains the gap =="
want "fixtures/sleep.txt" SLEEP < <("$S" < fixtures/sleep.txt)
want "fixtures/step.txt" STEP < <("$S" < fixtures/step.txt)
want "fixtures/dilate.txt" DILATE < <("$S" < fixtures/dilate.txt)
want "fixtures/rest.txt" REST < <("$S" < fixtures/rest.txt)
want "fixtures/slew.txt" SLEEP < <("$S" < fixtures/slew.txt)

echo
echo "== two timestamps (one clock) are REST, not DILATE =="
want "1000 1001" REST < <(printf '1000\n1001\n' | "$S")

echo
echo "== JSONL two cuts: host sleep =="
want "JSONL two cuts" SLEEP < <(printf '%s\n' \
  '{"wall":1000,"machine":0,"awake":0,"proper":0,"pid":1}' \
  '{"wall":1010,"machine":10,"awake":1,"proper":1,"pid":1}' | "$S")

echo
echo "== scree never spawns; the shell sleeps =="
want "{cut; sleep 0.35; cut} | scree" DILATE < <({ "$S" cut --json; sleep 0.35; "$S" cut --json; } | "$S")

echo
echo "== in-process busy loop: proper tracks awake (REST) =="
want "busy 0.28s two cuts" REST < <(printf '%s\n' \
  '{"wall":1000.0,"machine":0.0,"awake":0.0,"proper":0.0,"pid":7}' \
  '{"wall":1000.28,"machine":0.28,"awake":0.28,"proper":0.28,"pid":7}' | "$S")

echo
echo "== live cut (this Darwin host) =="
"$S" cut | "$S" --explain | sed -n '1,12p'
live=$("$S" cut | "$S")
echo "$live"
if [ "$live" = STEP ]; then
  bad "scree cut | scree → STEP (should be SLEEP, not NTP)"
elif [ "$live" = SLEEP ]; then
  ok "scree cut | scree → SLEEP (lid-close, not NTP)"
else
  bad "scree cut | scree → $live (this host has slept; want SLEEP)"
fi

echo
echo "== same question as two cuts: boot origin then now =="
want "{cut --boot; cut} | scree" SLEEP < <({ "$S" cut --json --boot; "$S" cut --json; } | "$S")

echo
echo "== folklore trap: wall vs time.monotonic() since boot =="
boot=$("$S" cut --json --boot)
now=$("$S" cut --json)
folk_in=$(NOW="$now" BOOT="$boot" python3 - <<'PY'
import json, os
boot = json.loads(os.environ["BOOT"])
now = json.loads(os.environ["NOW"])
print(f"wall {boot['wall']:.9f} {now['wall']:.9f}")
print(f"monotonic {boot['python_monotonic']:.9f} {now['python_monotonic']:.9f}")
PY
)
echo "$folk_in"
folk=$("$S" --explain <<<"$folk_in")
echo "$folk" | sed -n '1,12p'
folk_v=$(printf '%s\n' "$folk" | awk 'NR==1{print $1}')
if [ "$folk_v" = SLEEP ]; then
  ok "wall + python.monotonic since boot → SLEEP, not STEP"
elif [ "$folk_v" = STEP ]; then
  bad "wall + python.monotonic since boot → STEP (the Darwin lie)"
else
  bad "wall + python.monotonic since boot → $folk_v want SLEEP"
fi

echo
echo "== 50 ppm slew is not STEP =="
"$S" --require SLEEP < fixtures/slew.txt >/dev/null
ok "--require SLEEP on slew.txt"
if "$S" --require STEP < fixtures/slew.txt >/dev/null; then
  bad "--require STEP on slew.txt should miss"
else
  ok "--require STEP on slew.txt misses (exit 1)"
fi

echo
echo "== python.monotonic does not clobber CLOCK_MONOTONIC_RAW =="
want "JSON python_monotonic + machine" SLEEP < <(printf '%s\n' \
  '{"wall":1000.0,"machine":0.0,"python_monotonic":0.0,"pid":1}' \
  '{"wall":1010.0,"machine":10.0,"python_monotonic":1.0,"pid":1}' | "$S")

echo
echo "== beat: repeated key=value lines are two cuts, not a overwrite-REST =="
rep=$("$S" <<'EOF'
wall=0
wall=10
machine=0
machine=10
awake=0
awake=1
EOF
)
if [ "$rep" = SLEEP ]; then
  ok "repeated key=value → SLEEP (ancestor REST; we keep both timestamps)"
else
  bad "repeated key=value → $rep want SLEEP"
fi

echo
echo "demo $pass passed, $fail failed"
if [ "$fail" -ne 0 ]; then
  exit 1
fi
echo "demo 0 ok"
exit 0
