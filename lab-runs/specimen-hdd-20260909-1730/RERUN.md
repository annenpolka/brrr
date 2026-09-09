# 再実行方法

cwd: repository root `/Users/annenpolka/ghq/github.com/annenpolka/brrr`

1. Do not start before 17:30 JST on 2026-09-09 without this run id `specimen-hdd-20260909-1730`.
2. Export the same snapshot:

       python3 scripts/corpus.py --root .brrr-corpus/mini-followup export bd49baaa36b6999fdf9e44cf38da470c57c5f9daa6ce291e89c9084c3cce5a81 --output .brrr-corpus/mini-followup/exports/reported-discovery-v1

   Public 6 file hashes must match `docs/preparation/evidence-pilot-receipt.json` `export.files` and `lab-runs/specimen-hdd-20260909-1730/INPUTS.json`.
3. Copy only the public 6 files. Do not pass collector root, PRIVATE reviews, past runs, or the execplan to the Dreamer.
4. HDD:

       python3 /Users/annenpolka/.codex/skills/hdd-loop/scripts/hdd.py --root .hdd-runs/specimen-hdd-20260909-1730 status --trial case-001-a

   Resume with `status`, not `init`, for the same trial. Do not re-init `corpus-hdd-20260909-1130` or `specimen-hdd-20260902-1112`.
5. Dreamer remains `deepseek/deepseek-r1`. No silent substitute.
6. Candidate worktrees go outside the run directory and are removed before HARD_STOP.
7. Host 実機 leftovers live under `lab-runs/specimen-hdd-20260909-1730/host-verify/`. HOLD stays HOLD.
