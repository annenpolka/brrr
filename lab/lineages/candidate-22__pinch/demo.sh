#!/usr/bin/env bash
# demo.sh — pinch must classify three blocking shapes and stay runnable.
set -euo pipefail

root=$(cd "$(dirname "$0")" && pwd)
cd "$root"
chmod +x pinch fixtures/*.py

pinch=$root/pinch
assert=(python3 "$root/fixtures/assert_report.py")
tmp=$(mktemp -d "${TMPDIR:-/tmp}/pinch-demo.XXXXXX")
trap 'rm -rf "$tmp"' EXIT

echo "== pinch $(./pinch --version) =="
echo

echo "-- 1. fast producer | slow consumer  →  consumer is the pinch (others block on write)"
"$pinch" --json --report "$tmp/slowc.json" \
  --label 0=fast_producer --label 1=slow_consumer \
  -- python3 fixtures/fast_producer.py 1048576 \
  + python3 fixtures/slow_consumer.py 4096 0.002 \
  >"$tmp/slowc.out"
"${assert[@]}" "$tmp/slowc.json" \
  pinch.stage=1 \
  links.0.relation=blocked-on-write
python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["links"][0]["write_stall_s"]>0.2, r["links"][0]' "$tmp/slowc.json"
echo

echo "-- 2. slow producer | fast consumer  →  producer is the pinch (others block on read)"
"$pinch" --json --report "$tmp/slowp.json" \
  --label 0=slow_producer --label 1=fast_consumer \
  -- python3 fixtures/slow_producer.py 262144 4096 0.002 \
  + python3 fixtures/fast_consumer.py \
  >"$tmp/slowp.out"
"${assert[@]}" "$tmp/slowp.json" \
  pinch.stage=0 \
  links.0.relation=blocked-on-read
python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert r["links"][0]["read_stall_s"]>0.1, r["links"][0]' "$tmp/slowp.json"
echo

echo "-- 3. producer | cpu | consumer  →  middle is the compute pinch"
"$pinch" --json --report "$tmp/cpu.json" \
  --label 0=fast_producer --label 1=cpu_stage --label 2=fast_consumer \
  -- python3 fixtures/fast_producer.py 1048576 \
  + python3 fixtures/cpu_stage.py 25000 \
  + python3 fixtures/fast_consumer.py \
  >"$tmp/cpu.out"
"${assert[@]}" "$tmp/cpu.json" \
  pinch.stage=1 \
  pinch.kind=compute \
  links.0.relation=blocked-on-write \
  links.1.relation=blocked-on-read
echo

echo "-- 4. --sh quote-aware split + single wait-bound command"
"$pinch" --json --report "$tmp/sh.json" --sh 'python3 fixtures/fast_producer.py 65536 | python3 fixtures/fast_consumer.py' \
  >"$tmp/sh.out"
"${assert[@]}" "$tmp/sh.json" exit=0
python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert len(r["stages"])==2, r["stages"]' "$tmp/sh.json"

"$pinch" --json --report "$tmp/sleep.json" -- python3 -c 'import time; time.sleep(0.2)'
"${assert[@]}" "$tmp/sleep.json" pinch.kind=wait pinch.stage=0
echo

echo "-- 5. human report (cpu middle)"
"$pinch" --label 0=fast_producer --label 1=cpu_stage --label 2=fast_consumer \
  -- python3 fixtures/fast_producer.py 1048576 \
  + python3 fixtures/cpu_stage.py 25000 \
  + python3 fixtures/fast_consumer.py \
  >"$tmp/cpu.human.out"
echo

echo "-- 6. -- ends options, not stages (cargo test -- --list stays one command)"
"$pinch" --json --report "$tmp/passthru.json" \
  -- python3 -c 'import sys; print(len(sys.argv)-1)' -- --list --offline \
  >"$tmp/passthru.out"
"${assert[@]}" "$tmp/passthru.json" exit=0
python3 -c '
import json,sys
r=json.load(open(sys.argv[1]))
assert len(r["stages"])==1, r["stages"]
assert r["stages"][0]["argv"][-2:]==["--list","--offline"], r["stages"][0]["argv"]
print("ok   single stage argv keeps --list --offline")
' "$tmp/passthru.json"
echo
echo "-- 7. hidden child: wrapper waits, inner pinch is sleep"
"$pinch" --json --report "$tmp/inner.json" \
  -- python3 -c 'import subprocess; subprocess.check_call(["sleep", "0.35"])'
"${assert[@]}" "$tmp/inner.json" pinch.inner.comm=sleep
python3 -c '
import json,sys
r=json.load(open(sys.argv[1]))
assert r["pinch"]["inner"]["comm"]=="sleep", r["pinch"]
assert "sleep" in (r["pinch"].get("reason") or ""), r["pinch"]
print("ok   inner reason:", r["pinch"]["reason"])
' "$tmp/inner.json"
echo

echo "demo ok"
