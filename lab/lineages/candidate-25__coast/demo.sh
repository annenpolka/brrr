#!/usr/bin/env bash
# Empirical demo: unit tests + three primitives + self-dogfood.
set -euo pipefail
cd "$(dirname "$0")"
COAST=(python3 ./coast.py)

note() { printf '\n== %s ==\n' "$*"; }

check_json() {
  local file="$1"
  python3 - "$file" <<'PY'
import json, sys
from pathlib import Path
spec = Path(sys.argv[1])
# The python - filename is the json; predicates come from env.
import os
r = json.loads(spec.read_text())
g = os.environ
def need(cond, msg):
    if not cond:
        raise SystemExit("demo assertion failed: " + msg)

if g.get("EXPECT_SETTLED") == "1":
    need(r["settled"] is True, "settled")
if g.get("EXPECT_UNSETTLED") == "1":
    need(r["settled"] is False, "unsettled")
if g.get("EXPECT_COAST_MIN"):
    need(r["coast_s"] >= float(g["EXPECT_COAST_MIN"]), f"coast_s {r['coast_s']} >= {g['EXPECT_COAST_MIN']}")
if g.get("EXPECT_COAST_MAX"):
    need(r["coast_s"] <= float(g["EXPECT_COAST_MAX"]), f"coast_s {r['coast_s']} <= {g['EXPECT_COAST_MAX']}")
if g.get("EXPECT_PATH"):
    blob = json.dumps(r)
    need(g["EXPECT_PATH"] in blob, f"path {g['EXPECT_PATH']}")
if g.get("EXPECT_HAZARD") == "1":
    need(len(r.get("hazards") or []) >= 1, "hazard")
if g.get("EXPECT_REWRITTEN"):
    need(any(g["EXPECT_REWRITTEN"] in p for p in r.get("rewritten") or []), "rewritten")
if g.get("EXPECT_STRAGGLER"):
    cmds = " ".join(p.get("command") or "" for p in r.get("stragglers") or [])
    need(g["EXPECT_STRAGGLER"] in cmds, f"straggler {g['EXPECT_STRAGGLER']}")
print("ok", spec)
PY
}

note "unit tests"
python3 tests/test_coast.py
echo "unit tests ok"

note "1. clean command has ~zero coast"
d=$(mktemp -d)
mkdir -p "$d/tree"
"${COAST[@]}" run --root "$d/tree" --store "$d/store" --json-out "$d/r.json" \
  --no-passthrough --max-coast-ms 800 --quiet-ms 150 -- \
  bash fixtures/clean.sh "$d/tree"
EXPECT_SETTLED=1 EXPECT_COAST_MAX=0.2 EXPECT_PATH=out.txt check_json "$d/r.json"

note "2. late write after waitpid is a HAZARD coast"
d=$(mktemp -d)
mkdir -p "$d/tree"
"${COAST[@]}" run --root "$d/tree" --store "$d/store" --json-out "$d/r.json" \
  --no-passthrough --max-coast-ms 2500 --quiet-ms 180 -- \
  bash fixtures/late_write.sh "$d/tree"
EXPECT_SETTLED=1 EXPECT_COAST_MIN=0.25 EXPECT_PATH=late.txt EXPECT_HAZARD=1 \
  check_json "$d/r.json"
"${COAST[@]}" show --store "$d/store"

note "3. bundler rewrite records intra-run layers"
d=$(mktemp -d)
mkdir -p "$d/tree"
"${COAST[@]}" run --root "$d/tree" --store "$d/store" --json-out "$d/r.json" \
  --no-passthrough -- \
  bash fixtures/rewrite.sh "$d/tree"
EXPECT_SETTLED=1 EXPECT_REWRITTEN=bundle.js EXPECT_COAST_MAX=0.2 check_json "$d/r.json"
"${COAST[@]}" show --store "$d/store" bundle.js

note "4. isolate-tmp catches a late /tmp write"
d=$(mktemp -d)
mkdir -p "$d/tree"
"${COAST[@]}" run --root "$d/tree" --store "$d/store" --json-out "$d/r.json" \
  --no-passthrough --isolate-tmp --max-coast-ms 2500 -- \
  python3 fixtures/tmp_late.py
EXPECT_SETTLED=1 EXPECT_COAST_MIN=0.25 EXPECT_PATH=secret.bin EXPECT_HAZARD=1 \
  check_json "$d/r.json"

note "5. coast wait exits 124 on a leftover sleep"
d=$(mktemp -d)
mkdir -p "$d/tree"
set +e
"${COAST[@]}" wait --root "$d/tree" --store "$d/store" --json-out "$d/r.json" \
  --no-passthrough --max-coast-ms 400 --quiet-ms 80 -- \
  bash fixtures/straggler.sh "$d/tree"
rc=$?
set -e
test "$rc" = 124
EXPECT_UNSETTLED=1 EXPECT_STRAGGLER=sleep check_json "$d/r.json"
python3 - "$d/store/last.json" <<'PY'
import json, os, sys
r = json.loads(open(sys.argv[1]).read())
for p in r.get("leftover") or []:
    try:
        os.kill(p["pid"], 9)
    except OSError:
        pass
print("killed leftovers")
PY

note "6. dogfood: py_compile writes bytecode during the run, not after"
d=$(mktemp -d)
mkdir -p "$d/tree"
cp coast.py "$d/tree/mod.py"
"${COAST[@]}" run --root "$d/tree" --store "$d/store" --json-out "$d/r.json" \
  --no-passthrough --max-coast-ms 1500 -- \
  python3 -m py_compile "$d/tree/mod.py"
EXPECT_SETTLED=1 EXPECT_COAST_MAX=0.2 EXPECT_PATH=__pycache__/mod check_json "$d/r.json"

note "7. dogfood: isolate-tmp around a tiny nested tempfile user"
d=$(mktemp -d)
mkdir -p "$d/empty"
"${COAST[@]}" run --root "$d/empty" --store "$d/store" --json-out "$d/r.json" \
  --no-passthrough --isolate-tmp --max-coast-ms 1500 -- \
  python3 -c 'import tempfile, pathlib; p=pathlib.Path(tempfile.mkdtemp())/"x"; p.write_text("hi"); print(p)'
EXPECT_SETTLED=1 EXPECT_PATH=x check_json "$d/r.json"

echo
echo "demo: all checks passed"
exit 0
