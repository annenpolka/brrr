#!/usr/bin/env bash
# Run keyorder on the owned {1: 0, 0: 0} sorted vs insertion prints.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/keyorder"
FIXTURE="$ROOT/fixtures/two_prints.py"

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== owned fixture $FIXTURE =="
python3 "$FIXTURE"
echo

echo "== nearest existing operation: print(d) vs print(list(d)) vs sorted(d) =="
python3 -c 'd={1: 0, 0: 0}; print("print(d)", d); print("list(d)", list(d)); print("sorted(d)", sorted(d))'
echo

echo "== keyorder --obj of those two prints =="
python3 "$CLI" --obj '{1: 0, 0: 0}' --file "$ROOT/fixtures/two_prints.txt"
echo

echo "== keyorder --fixture (same owned dict, both printers) =="
python3 "$CLI" --fixture
echo

echo "== keyorder already-sorted {0: 0, 1: 0} (printers agree) =="
python3 "$CLI" --obj '{0: 0, 1: 0}' --file "$ROOT/fixtures/agree.txt"
echo

echo "== keyorder prefixed views of the same owned dict =="
python3 "$CLI" --file "$ROOT/fixtures/three_views.txt"
