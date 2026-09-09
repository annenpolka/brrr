#!/usr/bin/env bash
# Run one diegetic HDD Dreamer turn through the real hdd-loop runner.
# Usage: dream.sh <trial> <phase>
set -euo pipefail

SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$(cd "$SCRIPTS/.." && pwd)"
REPO="$(cd "$RUN_DIR/../.." && pwd)"
RUN_ID="$(basename "$RUN_DIR")"
HDD_PY="${HDD_PY:-$HOME/.codex/skills/hdd-loop/scripts/hdd.py}"
HDD_ROOT="${BRRR_HDD_ROOT:-$REPO/.hdd-runs/$RUN_ID}"
TRIAL="${1:?trial name}"
PHASE="${2:-first-turn}"
LOG_DIR="$RUN_DIR/dream-logs"
mkdir -p "$LOG_DIR"

export HDD_DREAMER_TRANSPORT="${HDD_DREAMER_TRANSPORT:-openrouter}"
export HDD_DREAMER_MODEL="${HDD_DREAMER_MODEL:-deepseek/deepseek-r1}"
export HDD_DREAMER_HTTP_TIMEOUT="${HDD_DREAMER_HTTP_TIMEOUT:-900}"
export HDD_APP_TITLE="${HDD_APP_TITLE:-hdd-loop-specimen-hdd-20260909-1730}"
export PYTHONPATH="$SCRIPTS${PYTHONPATH:+:$PYTHONPATH}"

if [[ "$HDD_DREAMER_MODEL" != "deepseek/deepseek-r1" ]]; then
  echo "REFUSING silent Dreamer substitute: HDD_DREAMER_MODEL=$HDD_DREAMER_MODEL" >&2
  exit 5
fi

GATE_JSON="$LOG_DIR/${TRIAL}-gate.json"
if ! python3 "$SCRIPTS/r1_budget.py" gate "$PHASE" >"$GATE_JSON"; then
  echo "BUDGET GATE refused new R1 for trial=$TRIAL phase=$PHASE"
  cat "$GATE_JSON"
  exit 3
fi

if ! python3 "$SCRIPTS/contamination_check.py"; then
  echo "CONTAMINATION GATE refused Dreamer launch"
  exit 4
fi

set -a
# shellcheck disable=SC1091
source "$REPO/.env.hdd"
set +a
export HDD_DREAMER_TRANSPORT="${HDD_DREAMER_TRANSPORT:-openrouter}"
export HDD_DREAMER_MODEL="deepseek/deepseek-r1"

BEFORE="$LOG_DIR/${TRIAL}-$(TZ=Asia/Tokyo date +%Y%m%d%H%M%S)-before.json"
AFTER="$LOG_DIR/${TRIAL}-after.json"
python3 "$SCRIPTS/credits.py" | tee "$BEFORE"

STARTED_AT="$(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S %Z')"
STAMP="$(TZ=Asia/Tokyo date +%Y%m%d%H%M%S)"
OUT="$LOG_DIR/${TRIAL}-${STAMP}-dream.out"
ERR="$LOG_DIR/${TRIAL}-${STAMP}-dream.err"

set +e
python3 "$HDD_PY" --root "$HDD_ROOT" dream --trial "$TRIAL" >"$OUT" 2>"$ERR"
STATUS=$?
set -e
ENDED_AT="$(TZ=Asia/Tokyo date '+%Y-%m-%d %H:%M:%S %Z')"

python3 "$SCRIPTS/credits.py" | tee "$AFTER"

python3 - "$RUN_DIR" "$TRIAL" "$PHASE" "$STATUS" "$STARTED_AT" "$ENDED_AT" "$BEFORE" "$AFTER" "$OUT" "$ERR" "$HDD_ROOT" <<'PY'
import json, sys
from pathlib import Path

run_dir = Path(sys.argv[1])
trial, phase = sys.argv[2], sys.argv[3]
status = int(sys.argv[4])
started, ended = sys.argv[5], sys.argv[6]
before = json.loads(Path(sys.argv[7]).read_text())
after = json.loads(Path(sys.argv[8]).read_text())
out = Path(sys.argv[9]).read_text(errors="replace")
err = Path(sys.argv[10]).read_text(errors="replace")
hdd_root = Path(sys.argv[11])

sys.path.insert(0, str(run_dir / "scripts"))
import r1_budget

ledger = r1_budget.load_ledger()
ws = hdd_root / trial
prompt_chars = 0
dream_chars = 0
iteration = None
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
http_success = status == 0
call = {
    "at_jst": started,
    "ended_jst": ended,
    "trial": trial,
    "phase": phase,
    "iteration": iteration,
    "status": "http-ok" if http_success else f"exit-{status}",
    "http_success": http_success,
    "tool_success": False,
    "model": "deepseek/deepseek-r1",
    "credits_before": {k: before[k] for k in ("at_jst", "total_credits", "total_usage", "remaining")},
    "credits_after": {k: after[k] for k in ("at_jst", "total_credits", "total_usage", "remaining")},
    "observed_usd": round(obs, 8),
    "prompt_chars": prompt_chars,
    "dream_chars": dream_chars,
    "estimated_usd": est["estimated_usd"],
    "token_estimate": est,
    "stdout_path": str(Path(sys.argv[9])),
    "stderr_path": str(Path(sys.argv[10])),
    "stdout_tail": out[-2000:],
    "stderr_tail": err[-2000:],
    "note": "R1 HTTP success is design material, not tool success.",
}
ledger.setdefault("calls", []).append(call)
ledger["in_flight_reserve_usd"] = 0.0
ledger["total_calls"] = len(ledger["calls"])
ledger["estimated_spend_usd"] = round(sum(c.get("estimated_usd") or 0 for c in ledger["calls"]), 6)
ledger["observed_spend_usd"] = r1_budget.reported_spend(ledger)
r1_budget.save_ledger(ledger)
r1_budget.append_jsonl(call)
r1_budget.rewrite_budget_md()
print(json.dumps({
    "trial": trial,
    "status": call["status"],
    "http_success": http_success,
    "tool_success": False,
    "observed_usd": call["observed_usd"],
    "estimated_usd": call["estimated_usd"],
    "iteration": iteration,
}, indent=2))
raise SystemExit(status)
PY
