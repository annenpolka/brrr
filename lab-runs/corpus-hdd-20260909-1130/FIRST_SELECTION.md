# First selection — 2026-09-09

Saved before 15:30 JST. Host selection, not a human jury. Disagreement is not averaged because there is a single host Red Pen.

Input scale: **小規模試行** (1 discovery case). That case is not 未知holdout.

Dreamer trial `case-001-a` is stopped after 3 turns. Further paraphrase of an unfamiliar-cli is not continued for count.

## KEEP

### runpair (USEFUL_COMPOSITION)

- Operation: run the same command twice in one directory; report regular files added/removed/changed after each invocation; do not open those files.
- 実装: isolated worktree `lab-runs/corpus-hdd-20260909-1130/worktrees/runpair` on branch `hdd-20260909-runpair`. Not merged to coordinator `main`.
- 実機: on the public 32113 file copy, `python3 -m runpair --cwd DIR -- deno run a.js` → first rc 0 stdout `foo`, added `deno.lock` size 727; second rc 1 stderr contains `Invalid package requirement '@.'`.
- Tests: `tests/test_runpair.py` drives the shipped `runpair` functions and CLI (true/true, writer, first-fail, grow, remove, unicode/binary, stamp transfer, nested ignore, deno bundle).
- 反例 already run: `true` (no sidecar), `false` still runs second, writer, grow, remove, symlink not listed, nested ignored, FIFO ignored, spaces, unicode/binary, stamp.py transfer (not 32113).
- Why keep: binds first-run sidecar appearance to second-run exit in one contract. Ordinary `cmd; ls; cmd` does not.
- Limits: non-recursive; no symlink follow; does not interpret sidecar bytes; host Deno is 2.8.1 not reported 2.6.8.

## KILL

### fictional unfamiliar-cli / verify-lock / cli facade

- Dream turns 1–3 used Deno or a renamed Deno and treated generated stdout as observations.
- Turn 3 copied the supplied transcript including `[reporter-local-path-omitted]`.
- No untested observable delta remains that a further Dream could supply without leaking host 正解. Stop.

## MUTATE

None. Do not mutate runpair into a lockfile parser or Deno-specific diagnostic; that would collapse into the 正解 of issue 32113.

## Not selected

- Issue 35901: quality HOLD (generated lockfile / DENO_DIR / node_modules not stored as bytes). Not a second independent PASS. Not holdout.

## Isolation

`FIRST_SELECTION.md` does **not** disable `scripts/contamination_check.py`.
