# Additional input review (host only; not Dreamer-facing)

Reviewer: agent. Not a human review. HOLD/FAIL are not converted to PASS to fill a 3–6 count.

## Case already in HDD

- Snapshot `bd49baaa36b6999fdf9e44cf38da470c57c5f9daa6ce291e89c9084c3cce5a81`
- Deno issue 32113 reported inputs. Quality PASS / leakage PASS for reported-evidence discovery.
- Scale: **小規模試行**. This case is **not** 未知holdout.

## Candidate 35901 (already stored, not selected)

- Source revision `b82f046702b4c4a416e6732a5ee327454e34cfd66c7e840a314a24eb93cba405`
- Title: `deno run --cached-only` fails when deno.lock records `"deprecated": true`
- Different primary mechanism from 32113 (deprecated metadata vs empty package.json name).
- Quality **HOLD**: the issue quotes `deno.json` and `main.ts`, but the failing artifact is a generated `deno.lock` / `node_modules` / `DENO_DIR` that is not stored as bytes. `deno install` as a step is not a substitute for the lockfile contents. Same class of missing generated input that kept the older PR-30998 package on HOLD.
- Leakage: not assessed for a public bundle because no View was staged. Title names the suspected field `"deprecated": true`; that is a symptom claim, but without a public bundle there is nothing to export.
- Action: do not PASS for count. Do not start a second trial on this issue.

## github-pilot expansion (12:26 JST, isolated root)

See `PILOT_EXPAND_REVIEW.md`. Collection `a9328ef43806b624ae4b461fea9d53947e459228bc24bd2fe1fb90773d4ff216`, 200 requests, paused on invocation limit. 24 complete pytest roots screened; 5 bodies read; all HOLD pending a real View. No second PASS.

## Collection shortfall

- Target 3–6 independent reviewed cases: **shortfall 2–5**.
- Actual reviewed-and-exported discovery cases this run: **1**.
- github-pilot-v1 mass collect was not started in the 11:30–12:00 connection window; 35901 did not become a second PASS.
- 24-case recipe is not relaxed.

## Host 実機 vs Dream (case 001 only)

See `host-verify/case-001-deno-two-invocations/RESULT.json`.
Host Deno 2.8.1 (not reported 2.6.8): first `deno run a.js` printed `foo` and created `deno.lock`; second identical command failed with `Invalid workspace section: Invalid package requirement '@.'`.
That is host-machine evidence. It is **not** a Dreamer observation and was **not** written into trial seed/outbox.
