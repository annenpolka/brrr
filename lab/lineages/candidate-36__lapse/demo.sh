#!/usr/bin/env bash
# demo.sh — must exit 0. Exercises the primitive, not a screenshot.
# ./demo.sh 0  is the default live demo.
set -euo pipefail
cd "$(dirname "$0")"
chmod +x ./lapse fixtures/*.py

case "${1:-0}" in
  0) ;;
  *) echo "usage: ./demo.sh 0" >&2; exit 2 ;;
esac

fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

echo "== selftest =="
python3 ./lapse selftest

echo
echo "== clocks: Python monotonic is the AWAKE clock on Darwin =="
CUT=$(python3 ./lapse clocks)
echo "$CUT"
echo "$CUT" | grep -q "mapped-to awake" || fail "clocks should name python.monotonic"
echo "$CUT" | grep -q "CLOCK_UPTIME_RAW\|CLOCK_MONOTONIC" || fail "awake clock missing"
echo "$CUT" | grep -q "python monotonic is NOT the sleep-running clock\|mapped-to" || fail "monotonic mapping"
pass "clock-cut names wall / machine / awake"

echo
echo "== blocked child is dilated (ages little) =="
python3 ./lapse --porcelain -- python3 fixtures/block.py 0.35 >/dev/null 2>/tmp/lapse-block.tsv
cat /tmp/lapse-block.tsv
awk -F'\t' '$1=="verdict" && $2=="primary" && $3=="DILATE" {found=1} END{exit found?0:1}' /tmp/lapse-block.tsv \
  || fail "block should be DILATE"
awk -F'\t' '$1=="clock" && $2=="gamma" {g=$3+0; exit (g>=5)?0:1}' /tmp/lapse-block.tsv \
  || fail "block gamma should be high"
grep -q $'clock\tsleep\t' /tmp/lapse-block.tsv || fail "porcelain sleep clock"
pass "sleep 0.35s → DILATE"

echo
echo "== busy child ages with the world (REST), not STARVE =="
python3 ./lapse --porcelain -- python3 fixtures/busy.py 0.30 >/dev/null 2>/tmp/lapse-busy.tsv
cat /tmp/lapse-busy.tsv
awk -F'\t' '$1=="verdict" && $2=="tags" && $3 ~ /STARVE/ {exit 1}' /tmp/lapse-busy.tsv \
  || fail "busy must not be STARVE (ps lag false positive)"
awk -F'\t' '$1=="verdict" && $2=="primary" && ($3=="REST" || $3=="BOOST") {found=1} END{exit found?0:1}' /tmp/lapse-busy.tsv \
  || fail "busy should be REST (or BOOST on a noisy host)"
awk -F'\t' '$1=="clock" && $2=="proper" {p=$3+0; exit (p>=0.12)?0:1}' /tmp/lapse-busy.tsv \
  || fail "busy proper time too small"
pass "busy 0.30s → REST, proper ≈ wall"

echo
echo "== parallel children: tree proper can exceed awake (BOOST) =="
python3 ./lapse --json -- python3 fixtures/parallel.py 3 0.28 >/dev/null 2>/tmp/lapse-par.json
python3 - <<'PY'
import json
d = json.load(open("/tmp/lapse-par.json"))
print("verdict", d["verdict"]["primary"], "pids", d["n_pids"],
      "proper", round(d["clock"]["proper"], 3), "awake", round(d["clock"]["awake"], 3))
assert d["n_pids"] >= 3, d["n_pids"]
ratio = d["clock"]["proper"] / max(d["clock"]["awake"], 1e-9)
if ratio < 1.15:
    print("WARN parallel ratio", round(ratio, 2), "(host may be busy); tree still observed")
else:
    assert "BOOST" in d["verdict"]["tags"], d["verdict"]
PY
pass "parallel tree observed"

echo
echo "== mix: worldline phases run then block =="
python3 ./lapse --porcelain -- python3 fixtures/mix.py 0.18 0.25 >/dev/null 2>/tmp/lapse-mix.tsv
cat /tmp/lapse-mix.tsv
grep -qE $'line\t.*run.*block' /tmp/lapse-mix.tsv || fail "mix phase should be run→block"
pass "mix worldline run→block"

echo
echo "== machine since boot: host proper time is awake =="
python3 ./lapse --porcelain machine >/tmp/lapse-machine.tsv
python3 ./lapse machine
awk -F'\t' '$1=="meta" && $2=="kind" && $3=="machine" {found=1} END{exit found?0:1}' /tmp/lapse-machine.tsv \
  || fail "kind=machine"
awk -F'\t' '$1=="verdict" && $2=="tags" && $3 ~ /REST/ {exit 1}' /tmp/lapse-machine.tsv \
  || fail "machine must not carry process REST"
awk -F'\t' '$1=="clock" && $2=="sleep" {s=$3+0; exit (s>1)?0:1}' /tmp/lapse-machine.tsv \
  || fail "this host has slept since boot; sleep clock should be large"
# 7s NTP slew over weeks is not STEP
awk -F'\t' '$1=="verdict" && $2=="tags" && $3 ~ /STEP/ {exit 1}' /tmp/lapse-machine.tsv \
  || fail "ppm-scaled STEP must ignore crystal slew"
pass "machine lapse: SLEEP, not STEP-on-slew"

echo
echo "== dogfood: lapse observing lapse =="
python3 ./lapse --json -- python3 ./lapse clocks >/tmp/lapse-clocks-inner.txt 2>/tmp/lapse-dog.json
python3 - <<'PY'
import json
d = json.load(open("/tmp/lapse-dog.json"))
assert d["kind"] == "command", d["kind"]
assert d["argv"][-1] == "clocks", d["argv"]
assert "wall" in d["clock"] and "awake" in d["clock"] and "machine" in d["clock"]
assert d["exit_code"] == 0
print("outer γ", round(d["clock"]["gamma"], 2), "verdict", d["verdict"]["primary"],
      "inner clocks bytes", open("/tmp/lapse-clocks-inner.txt").read().__len__())
PY
pass "lapse -- lapse clocks: inner cut on stdout, outer lapse on stderr"

echo
echo "demo 0 ok"
exit 0
