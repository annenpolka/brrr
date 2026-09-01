#!/usr/bin/env bash
# Record a host Red Pen JSON patch into a trial ledger.
# Usage: record_redpen.sh <trial> <json-file>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HDD_PY="${HDD_PY:-$HOME/ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py}"
TRIAL="${1:?trial}"
FILE="${2:?json file}"
python3 "$HDD_PY" --root "$ROOT/.hdd" record-redpen --trial "$TRIAL" --file "$FILE"
echo "recorded redpen trial=$TRIAL file=$FILE"
