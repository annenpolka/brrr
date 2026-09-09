# uv issues from expand corpus (host; not Dreamer-facing)

Reviewer: agent. Not human. HOLD is not converted to PASS.

Source: `.brrr-corpus/pilot-expand-20260909` after resume slices. 17 uv roots `complete_for_policy`.

| Issue | Quality | Why |
| --- | --- | --- |
| 18801 parallel rustc clash | HOLD | Environmental race while building multiple rust crates; no sealed mini files. |
| 17487 build during lock | HOLD | Question plus CUDA-only package; no public wheel-less mini bundle. |
| 21551 uv check vs ty exclude | HOLD | Workspace/vendor layout not supplied as a View. |
| 17642 platform exclude-dependencies | HOLD | Feature request. |
| 19622 dangling Windows junction | HOLD | Windows-only recovery; no portable files. |
| 16402 private index auth | HOLD | Token/private Gitlab; leakage risk; no public repro. |
| 18221 exclude-dependencies × dev groups | HOLD | Feature request. |
| 19791 custom ty config | HOLD | Feature request. |
| 9684 atom feed metadata | HOLD | Investigation, not a failing input. |
| 16139 | HOLD | Repair PR. 正解 risk. No sealed failing public input. |
| 18406 | HOLD | Repair/feature PR. No View. |
| 18979 | HOLD | Repair/feature PR. No View. |
| 19114 empty top_level.txt | HOLD | Repair PR. 正解 risk. |
| 19330 | HOLD | Repair/feature PR. No View. |
| 19370 | HOLD | Repair/feature PR. No View. |
| 19613 | HOLD | Repair/feature PR. No View. |
| 21265 | HOLD | Repair/feature PR. No View. |

17/17 uv complete roots screened HOLD. Partial uv#19603 and uv#19770 stay partial (binary/incomplete patches); not PASS.

Leftover uv PRs re-screened 2026-09-09 22:03 JST: 16139/18406/18979/19114/19330/19370/19613/21265 all `n_fences=0` `snippet_len=0`. Still HOLD. Do not apply. No View.

None exported. No quality PASS. Consumer still 1 discovery case. **小規模試行**.
