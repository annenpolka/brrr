#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/procpath"
FIX="$ROOT/fixtures"
echo "== nearest existing operation (grep GAV vs reactor vs ~/.m2) =="
echo "omitted_fail is reactor_present and not local_repo and processorpath fail"
echo
echo "== procpath specimen-096 case B reactor fail =="
python3 "$CLI" "$FIX/096-reactor.rec" || true
echo
echo "== procpath case A local repo =="
python3 "$CLI" "$FIX/096-local.rec" || true
echo
echo "== procpath case C missing =="
python3 "$CLI" "$FIX/096-missing.rec" || true
