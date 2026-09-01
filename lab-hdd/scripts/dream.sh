#!/usr/bin/env bash
# Run one diegetic HDD Dreamer turn through the real hdd-loop runner.
# Usage: dream.sh <trial> <phase>
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HDD_PY="${HDD_PY:-$HOME/ghq/github.com/annenpolka/skills/hdd-loop/scripts/hdd.py}"
TRIAL="${1:?trial name}"
PHASE="${2:-cambrian}"
LAB="$ROOT/lab-hdd"
SCRIPTS="$LAB/scripts"
LOG_DIR="$LAB/dream-logs"
mkdir -p "$LOG_DIR"

export HDD_DREAMER_HTTP_TIMEOUT="${HDD_DREAMER_HTTP_TIMEOUT:-900}"

GATE_JSON="$LOG_DIR/${TRIAL}-gate.json"
if ! python3 "$SCRIPTS/r1_budget.py" gate "$PHASE" >"$GATE_JSON"; then
  echo "BUDGET GATE refused new R1 for trial=$TRIAL phase=$PHASE"
  cat "$GATE_JSON"
  exit 3
fi

set -a
# shellcheck disable=SC1091
source "$ROOT/.env.hdd"
set +a

BEFORE="$LOG_DIR/${TRIAL}-$(date +%Y%m%d%H%M%S)-before.json"
AFTER="$LOG_DIR/${TRIAL}-after.json"
python3 "$SCRIPTS/credits.py" | tee "$BEFORE"

STARTED_AT="$(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S %Z')"
OUT="$LOG_DIR/${TRIAL}-dream.out"
ERR="$LOG_DIR/${TRIAL}-dream.err"

set +e
python3 "$HDD_PY" --root "$ROOT/.hdd" dream --trial "$TRIAL" >"$OUT" 2>"$ERR"
STATUS=$?
set -e
ENDED_AT="$(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S %Z')"

python3 "$SCRIPTS/credits.py" | tee "$AFTER"

python3 - "$ROOT" "$TRIAL" "$PHASE" "$STATUS" "$STARTED_AT" "$ENDED_AT" "$BEFORE" "$AFTER" "$OUT" "$ERR" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
trial, phase = sys.argv[2], sys.argv[3]
status = int(sys.argv[4])
started, ended = sys.argv[5], sys.argv[6]
before = json.loads(Path(sys.argv[7]).read_text())
after = json.loads(Path(sys.argv[8]).read_text())
out = Path(sys.argv[9]).read_text(errors="replace")
err = Path(sys.argv[10]).read_text(errors="replace")

sys.path.insert(0, str(root / "lab-hdd" / "scripts"))
import r1_budget

lab = root / "lab-hdd"
ledger = r1_budget.load_ledger()
ws = root / ".hdd" / trial
prompt_chars = 0
dream_chars = 0
iteration = None
# latest prompt + dreamer files
outbox = ws / "outbox"
iters = ws / "iterations"
if outbox.exists():
    prompts = sorted(outbox.glob("*-dreamer-prompt.md"))
    if prompts:
        prompt_chars = prompts[-1].stat().st_size
        iteration = int(prompts[-1].name.split("-")[0])
if iters.exists():
    dreams = sorted(iters.glob("*-dreamer.md"))
    if dreams:
        dream_chars = dreams[-1].stat().st_size
        iteration = int(dreams[-1].name.split("-")[0])

est = r1_budget.estimate_cost_usd(prompt_chars, dream_chars, ledger["pricing"])
obs = after["total_usage"] - before["total_usage"]
call = {
    "at_jst": started,
    "ended_jst": ended,
    "trial": trial,
    "phase": phase,
    "iteration": iteration,
    "status": "ok" if status == 0 else f"exit-{status}",
    "credits_before": {k: before[k] for k in ("at_jst", "total_credits", "total_usage", "remaining")},
    "credits_after": {k: after[k] for k in ("at_jst", "total_credits", "total_usage", "remaining")},
    "observed_usd": round(obs, 8),
    "prompt_chars": prompt_chars,
    "dream_chars": dream_chars,
    "estimated_usd": est["estimated_usd"],
    "token_estimate": est,
    "stdout_tail": out[-2000:],
    "stderr_tail": err[-2000:],
}
ledger.setdefault("calls", []).append(call)
ledger["total_calls"] = len(ledger["calls"])
ledger["estimated_spend_usd"] = round(sum(c.get("estimated_usd") or 0 for c in ledger["calls"]), 6)
ledger["observed_spend_usd"] = r1_budget.reported_spend(ledger)
r1_budget.save_ledger(ledger)
r1_budget.rewrite_budget_md()
print(json.dumps({"trial": trial, "status": call["status"], "observed_usd": call["observed_usd"], "estimated_usd": call["estimated_usd"], "iteration": iteration}, indent=2))
raise SystemExit(status)
PY
