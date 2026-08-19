#!/usr/bin/env bash
# Empirical demo: knot must exit 0.
# Fixtures prove pipe conversation, tree waits, and the joint walk;
# cargo / node / python dogfood prove it survives real command lines.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
KNOT="$ROOT/knot"
ASSERT=(python3 "$ROOT/fixtures/assert_report.py")
TMP="$(mktemp -d "${TMPDIR:-/tmp}/knot-demo.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

chmod +x "$KNOT" "$ROOT"/fixtures/*.py

need() { command -v "$1" >/dev/null || { echo "missing $1" >&2; exit 1; }; }
need python3
need lsof
need ps

echo "== knot $(python3 "$KNOT" --version) =="
echo

echo "-- 0. selftest"
python3 "$KNOT" selftest
echo

echo "-- 1. pipe-read (child blocked on parent writer)  →  knot is the writer"
python3 "$KNOT" --json --report "$TMP/pipe.json" --ignore-exit \
  --expect-kind pipe-read --interval 0.08 \
  -- python3 "$ROOT/fixtures/pipe_block.py" 0.65 \
  >"$TMP/pipe.out"
"${ASSERT[@]}" "$TMP/pipe.json" conversation.kinds=pipe-read
echo

echo "-- 2. fast producer | slow consumer  →  consumer is the knot (pipe-full)"
python3 "$KNOT" --json --report "$TMP/slowc.json" --ignore-exit \
  --label 0=fast_producer --label 1=slow_consumer \
  -- python3 "$ROOT/fixtures/fast_producer.py" 1048576 \
  + python3 "$ROOT/fixtures/slow_consumer.py" 4096 0.002 \
  >"$TMP/slowc.out"
"${ASSERT[@]}" "$TMP/slowc.json" conversation.kinds=pipe-full
python3 - "$TMP/slowc.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
kinds = {e["kind"] for e in r.get("conversation") or []}
assert "pipe-full" in kinds, kinds
# knot should be the slow consumer, not the producer
blob = ((r.get("knot") or {}).get("cmd") or "") + ((r.get("knot") or {}).get("comm") or "")
assert "slow_consumer" in blob or "slow_consumer" in json.dumps(r.get("knot")), r.get("knot")
print("ok   knot is slow_consumer", r["knot"].get("cmd"), r["knot"].get("via"))
PY
echo

echo "-- 3. slow producer | fast consumer  →  producer is the knot (pipe-empty)"
python3 "$KNOT" --json --report "$TMP/slowp.json" --ignore-exit \
  --label 0=slow_producer --label 1=fast_consumer \
  -- python3 "$ROOT/fixtures/slow_producer.py" 262144 4096 0.002 \
  + python3 "$ROOT/fixtures/fast_consumer.py" \
  >"$TMP/slowp.out"
"${ASSERT[@]}" "$TMP/slowp.json" conversation.kinds=pipe-empty
python3 - "$TMP/slowp.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
blob = json.dumps(r.get("knot") or {})
assert "slow_producer" in blob, r.get("knot")
print("ok   knot is slow_producer", r["knot"].get("cmd"), r["knot"].get("via"))
PY
echo

echo "-- 4. producer | cpu | consumer  →  middle is the compute knot"
python3 "$KNOT" --json --report "$TMP/cpu.json" --ignore-exit \
  --label 0=fast_producer --label 1=cpu_stage --label 2=fast_consumer \
  -- python3 "$ROOT/fixtures/fast_producer.py" 1048576 \
  + python3 "$ROOT/fixtures/cpu_stage.py" 25000 \
  + python3 "$ROOT/fixtures/fast_consumer.py" \
  >"$TMP/cpu.out"
"${ASSERT[@]}" "$TMP/cpu.json" knot.kind=compute conversation.kinds=pipe-full
python3 - "$TMP/cpu.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
blob = json.dumps(r.get("knot") or {})
assert "cpu_stage" in blob, r.get("knot")
print("ok   knot is cpu_stage", r["knot"].get("kind"), r["knot"].get("via"))
PY
echo

echo "-- 5. hidden child: wrapper waits, knot is sleep (tree wait-source)"
python3 "$KNOT" --json --report "$TMP/inner.json" --ignore-exit \
  --expect-comm sleep --interval 0.06 \
  -- python3 "$ROOT/fixtures/hidden_child.py" 0.4
"${ASSERT[@]}" "$TMP/inner.json" knot.comm=sleep conversation.kinds=child-wait
echo

echo "-- 6. JOINT: hidden producer | fast consumer"
echo "    pinch would name the parent stage; hitch would name child-wait."
echo "    knot walks pipe-empty through child-wait to the inner writer."
python3 "$KNOT" --json --report "$TMP/joint.json" --ignore-exit \
  --interval 0.06 \
  -- python3 "$ROOT/fixtures/hidden_producer.py" 24 0.03 \
  + python3 "$ROOT/fixtures/fast_consumer.py" \
  >"$TMP/joint.out"
python3 - "$TMP/joint.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
kinds = {e["kind"] for e in r.get("conversation") or []}
via = r.get("knot", {}).get("via") or []
stage0 = (r.get("stages") or [{}])[0].get("pid")
knot_pid = (r.get("knot") or {}).get("pid")
print("  kinds", sorted(kinds))
print("  via  ", via)
print("  knot ", r.get("knot", {}).get("comm"), r.get("knot", {}).get("cmd"))
print("  pids stage0", stage0, "knot", knot_pid)
assert "pipe-empty" in kinds or "pipe-read" in kinds, kinds
assert "child-wait" in kinds or "child-wait" in via or any(
    "child-wait" in str((e or {}).get("detail") or "") for e in r.get("conversation") or []
), (kinds, via, r.get("knot"))
# Synthesis: knot is the inner writer, not the pipeline-stage parent.
assert knot_pid and stage0 and knot_pid != stage0, (stage0, knot_pid, r.get("knot"))
cmd = (r.get("knot") or {}).get("cmd") or ""
assert "hidden_producer" in cmd or "[child]" in cmd or "Python" in cmd, cmd
print("ok   joint knot is inner writer, conversation spans pipe + child-wait")
PY
echo

echo "-- 7. fifo (reader blocked on empty fifo)"
python3 "$KNOT" --json --report "$TMP/fifo.json" --ignore-exit \
  --expect-kind fifo --interval 0.08 \
  -- python3 "$ROOT/fixtures/fifo_block.py" 0.65
"${ASSERT[@]}" "$TMP/fifo.json" conversation.kinds=fifo
echo

echo "-- 8. -- ends options, not stages"
python3 "$KNOT" --json --report "$TMP/passthru.json" --ignore-exit \
  -- python3 -c 'import sys; print(len(sys.argv)-1)' -- --list --offline \
  >"$TMP/passthru.out"
python3 - "$TMP/passthru.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
assert len(r["stages"]) == 1, r["stages"]
assert r["stages"][0]["argv"][-2:] == ["--list", "--offline"], r["stages"][0]["argv"]
print("ok   single stage argv keeps --list --offline")
PY
echo

echo "-- 9. --sh quote-aware split"
python3 "$KNOT" --json --report "$TMP/sh.json" --ignore-exit \
  --sh "python3 '$ROOT/fixtures/fast_producer.py' 65536 | python3 '$ROOT/fixtures/fast_consumer.py'" \
  >"$TMP/sh.out"
python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); assert len(r["stages"])==2, r["stages"]' "$TMP/sh.json"
echo "ok   --sh two stages"
echo

echo "-- 10. human report (cpu middle)"
python3 "$KNOT" --label 0=fast_producer --label 1=cpu_stage --label 2=fast_consumer \
  -- python3 "$ROOT/fixtures/fast_producer.py" 1048576 \
  + python3 "$ROOT/fixtures/cpu_stage.py" 25000 \
  + python3 "$ROOT/fixtures/fast_consumer.py" \
  >"$TMP/cpu.human.out"
echo

echo "demo ok  reports in $TMP (cleaned on exit)"
