#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the stream primitive, not a screenshot.
# ./demo.sh 0  is the default live demo.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./twixt

case "${1:-0}" in
  0) ;;
  *) echo "usage: ./demo.sh 0" >&2; exit 2 ;;
esac

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }
names() { awk '{print $1}' | tr '\n' ' ' | sed 's/ *$//'; }

ANCESTOR="${ANCESTOR:-/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b60-8466-71a3-894a-7bf303f098fd/scarp}"

echo "== selftest =="
python3 ./twixt selftest

echo
echo "== fixtures: one-pair names match scarp =="
for pair in sleep:SLEEP step:STEP dilate:DILATE rest:REST slew:SLEEP; do
  f=${pair%%:*}; want=${pair##*:}
  got=$(python3 ./twixt < "fixtures/${f}.txt" | names)
  [[ "$got" == "$want" ]] || fail "fixtures/${f}.txt → $got want $want"
  pass "fixtures/${f}.txt → $want"
done

echo
echo "== stream.jsonl: 4 cuts → SLEEP DILATE REST =="
got=$(python3 ./twixt < fixtures/stream.jsonl | names)
[[ "$got" == "SLEEP DILATE REST" ]] || fail "stream.jsonl → $got"
pass "stream.jsonl → SLEEP DILATE REST"
if [[ -x "$ANCESTOR" ]]; then
  scarp_got=$(python3 "$ANCESTOR" < fixtures/stream.jsonl | tr -d '\n')
  [[ "$scarp_got" == "SLEEP" ]] || fail "ancestor stream.jsonl → $scarp_got want SLEEP (first pair only)"
  pass "ancestor scarp on the same log → SLEEP (throws away DILATE REST)"
fi

echo
echo "== two timestamps (one clock) are REST =="
got=$(printf '1000\n1001\n' | python3 ./twixt | names)
[[ "$got" == "REST" ]] || fail "two timestamps → $got"
pass "1000 1001 → REST"

echo
echo "== JSONL two cuts: host sleep =="
got=$(printf '%s\n%s\n' \
  '{"wall":1000,"machine":100,"awake":80,"proper":1}' \
  '{"wall":1010,"machine":110,"awake":81,"proper":1}' \
  | python3 ./twixt | names)
[[ "$got" == "SLEEP" ]] || fail "jsonl sleep → $got"
pass "JSONL two cuts → SLEEP"

if [[ -x "$ANCESTOR" ]]; then
  echo
  echo "== live stream vs ancestor (scarp never sees pair 2) =="
  STREAM=$(mktemp)
  trap 'rm -f "$STREAM"' EXIT
  { python3 "$ANCESTOR" cut --json
    python3 -c 'import time; time.sleep(0.3)'
    python3 "$ANCESTOR" cut --json
    python3 "$ANCESTOR" cut --json
  } > "$STREAM"
  echo "--- cuts ---"
  python3 - "$STREAM" <<'PY'
import json, sys
for i, line in enumerate(open(sys.argv[1])):
    d = json.loads(line)
    print(
        f"  cut{i} wall={d['wall']:.6f} machine={d['machine']:.3f} "
        f"awake={d['awake']:.3f} proper={d['proper']:.4f} pid={d['pid']}"
    )
PY
  echo "--- ancestor scarp (whole stream) ---"
  python3 "$ANCESTOR" --explain < "$STREAM" | sed -n '1,12p'
  echo "--- twixt (adjacent pairs) ---"
  python3 ./twixt --explain < "$STREAM"
  echo "--- ancestor on each adjacent pair ---"
  python3 - "$ANCESTOR" "$STREAM" <<'PY'
import json, subprocess, sys
anc, path = sys.argv[1], sys.argv[2]
cuts = [json.loads(l) for l in open(path)]
for i in range(len(cuts)-1):
    blob = json.dumps(cuts[i]) + "\n" + json.dumps(cuts[i+1]) + "\n"
    r = subprocess.run([sys.executable, anc], input=blob, text=True, capture_output=True)
    print(f"  pair {i}: {r.stdout.strip()}")
PY
  got=$(python3 ./twixt < "$STREAM" | names)
  # pair0 is the sleep sandwich → DILATE; pair1 is back-to-back → REST (dt < 50ms)
  [[ "$got" == "DILATE REST" ]] || fail "live 3 cuts → $got want DILATE REST"
  scarp_got=$(python3 "$ANCESTOR" < "$STREAM" | tr -d '\n')
  [[ "$scarp_got" == "DILATE" ]] || fail "ancestor live stream → $scarp_got want DILATE"
  pass "{cut; sleep 0.3; cut; cut} | twixt → DILATE REST"
  pass "same bytes | scarp → DILATE (first pair only)"
  word=$(python3 ./twixt < "$STREAM")
  echo "$word" | grep -q 'host_sleep=' || fail "live stream should carry host_sleep (lid-close since boot)"
  pass "live DILATE REST rows carry host_sleep=$(echo "$word" | awk -F'host_sleep=' 'NF>1{print $2; exit}' | awk '{print $1}')"
  origin_got=$(python3 ./twixt --origin boot < "$STREAM" | names)
  [[ "$origin_got" == "SLEEP DILATE REST" ]] || fail "--origin boot → $origin_got want SLEEP DILATE REST"
  pass "{cut; sleep 0.3; cut; cut} | twixt --origin boot → SLEEP DILATE REST"

  echo
  echo "== Darwin lid-close: singleton cut vs boot,then stream =="
  python3 "$ANCESTOR" cut | python3 ./twixt --explain | sed -n '1,12p'
  python3 "$ANCESTOR" cut | python3 ./twixt --require SLEEP >/dev/null \
    || fail "singleton Darwin cut should be SLEEP (host since boot)"
  pass "scarp cut | twixt → SLEEP (one snapshot, origin=boot)"

  got=$({ python3 "$ANCESTOR" cut --json --boot
          python3 "$ANCESTOR" cut --json
        } | python3 ./twixt | names)
  [[ "$got" == "SLEEP" ]] || fail "boot→now → $got"
  pass "{cut --boot; cut} | twixt → SLEEP"
fi

echo
echo "== in-process busy loop: several REST pairs (same pid) =="
got=$(python3 - <<'PY' | python3 ./twixt | names
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

echo
echo "== unlabeled timestamps are a stream of wall ticks =="
echo "--- 1000 1001 1005 1010 ---"
python3 ./twixt --explain < fixtures/unlabeled.txt
got=$(python3 ./twixt < fixtures/unlabeled.txt | names)
[[ "$got" == "REST REST REST" ]] || fail "unlabeled → $got want REST REST REST"
pass "unlabeled 1000,1001,1005,1010 → REST REST REST (1s, 4s, 5s)"
if [[ -x "$ANCESTOR" ]]; then
  scarp_got=$(python3 "$ANCESTOR" < fixtures/unlabeled.txt | tr -d '\n')
  echo "--- ancestor scarp on the same unlabeled file: $scarp_got ---"
  [[ "$scarp_got" == "STEP" ]] || fail "ancestor unlabeled → $scarp_got want STEP (duration bag)"
  pass "ancestor scarp on the same ticks → STEP (bag of durations)"
fi

echo
echo "demo 0 ok"
exit 0
