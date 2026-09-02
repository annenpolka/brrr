#!/usr/bin/env bash
# Record a host Red Pen JSON patch into a trial ledger under this run's HDD_ROOT.
# Usage: record_redpen.sh <trial> <json-file>
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$(cd "$SCRIPTS/.." && pwd)"
REPO="$(cd "$RUN_DIR/../.." && pwd)"
RUN_ID="$(basename "$RUN_DIR")"
HDD_PY="${HDD_PY:-$HOME/ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py}"
HDD_ROOT="${BRRR_HDD_ROOT:-$REPO/.hdd-runs/$RUN_ID}"
TRIAL="${1:?trial}"
FILE="${2:?json file}"
python3 "$HDD_PY" --root "$HDD_ROOT" record-redpen --trial "$TRIAL" --file "$FILE"
echo "recorded redpen trial=$TRIAL file=$FILE root=$HDD_ROOT"
