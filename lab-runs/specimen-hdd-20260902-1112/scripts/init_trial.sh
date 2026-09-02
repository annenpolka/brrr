#!/usr/bin/env bash
# Initialize one HDD trial from a compiled specimen seed. Does not invoke R1.
set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$(cd "$SCRIPTS/.." && pwd)"
REPO="$(cd "$RUN_DIR/../.." && pwd)"
RUN_ID="$(basename "$RUN_DIR")"
HDD_PY="${HDD_PY:-$HOME/ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py}"
HDD_ROOT="${BRRR_HDD_ROOT:-$REPO/.hdd-runs/$RUN_ID}"
TRIAL="${1:?trial}"
SEED="${2:?seed file}"
python3 "$HDD_PY" --root "$HDD_ROOT" init --trial "$TRIAL" --seed-file "$SEED"
python3 "$HDD_PY" --root "$HDD_ROOT" preview-dream --trial "$TRIAL" --check-meta >/dev/null
echo "initialized trial=$TRIAL seed=$SEED root=$HDD_ROOT"
