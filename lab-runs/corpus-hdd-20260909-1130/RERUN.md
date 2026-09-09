# 再実行方法

cwd: repository root `/Users/annenpolka/ghq/github.com/annenpolka/brrr`

1. Do not start before 11:30 JST on a new day without a new run id.
2. Export the same snapshot:

       python3 scripts/corpus.py --root .brrr-corpus/mini-followup export bd49baaa36b6999fdf9e44cf38da470c57c5f9daa6ce291e89c9084c3cce5a81 --output .brrr-corpus/mini-followup/exports/reported-discovery-v1

3. Copy only the public 6 files. Do not pass collector root, PRIVATE reviews, past runs, or the execplan to the Dreamer.
4. HDD:

       python3 /Users/annenpolka/.codex/skills/hdd-loop/scripts/hdd.py --root .hdd-runs/corpus-hdd-20260909-1130 status --trial case-001-a

   Resume with `status`, not `init`, for the same trial.
5. Dreamer remains `deepseek/deepseek-r1`. No silent substitute.
6. Candidate tool:

       python3 scripts/runpair.py --cwd DIR -- deno run a.js
