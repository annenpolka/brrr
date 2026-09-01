#!/usr/bin/env bash
# Preservation pass evidence. Run at 08:20–09:00.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRATCH="${1:?scratch dir}"
mkdir -p "$SCRATCH/final" "$SCRATCH/selection-pack"
python3 "$ROOT/lab-hdd/scripts/r1_budget.py" render
cp "$ROOT/HDD_EVOLUTION_REPORT.md" "$ROOT/lab-hdd/R1_BUDGET.md" "$ROOT/lab-hdd/heartbeat.md" "$SCRATCH/final/"
cp "$ROOT/lab-hdd/FIRST_SELECTION.md" "$ROOT/lab-hdd/PRIOR_RUN_COMPARISON.md" "$ROOT/lab-hdd/CONVERGENCE.md" "$SCRATCH/selection-pack/" || true
# survivor demos twice
for id in gen3-01__whence-empty gen3-02__envfrom-dir gen3-03__stated-honest; do
  d="$ROOT/lab-hdd/lineages/$id"
  (cd "$d" && ./demo.sh) >"$SCRATCH/demo-${id}-1.log" 2>&1
  (cd "$d" && ./demo.sh) >"$SCRATCH/demo-${id}-2.log" 2>&1
  git -C "$HOME/.grok/worktrees/annenpolka-brrr/${id%%__*}"* log -1 --oneline 2>/dev/null || true
done
echo PRESERVE_OK
