# github-pilot expansion screen (host; not Dreamer-facing)

Reviewer: agent. Not human. HOLD is not converted to PASS to fill a quota.

Source corpus: `.brrr-corpus/pilot-expand-20260909` collection `a9328ef43806b624ae4b461fea9d53947e459228bc24bd2fe1fb90773d4ff216`.
This run does not re-init that collection; it resumes and screens. 1130 already screened 13755/13784/13885/14048/14971 as HOLD.

## Newly screened complete issues (read bodies)

| Issue | Quality | Why |
| --- | --- | --- |
| 14608 nested addoption | HOLD | Directory sketch only; no file bytes; no command transcript. |
| 13913 conftest load vs custom CLI | HOLD | Reproducer is `git clone sqlalchemy` plus xdist; not a sealed mini bundle. |
| 14635 order-dependent fixture closure | HOLD | Requires Home Assistant tree; reporter says no standalone conftest. Causal/AI diagnosis must not go to a Dreamer. |
| 13479 class fixture + freezegun | HOLD | Mini snippet exists but depends on third-party `freezegun`. Host 実機 pytest 8.4.1 and 9.1.1 + freezegun 1.5.2: `fixture 'ff' not found`. No View. |
| 14591 indirect parametrize override | HOLD | Complete single-file example + 9.0.3 vs 9.1.0 transcripts. Bisect SHA is 正解 and stays off the consumer. Host 実機: 9.0.3 4 passed; 9.1.0 collection error `duplicate parametrization of 'myfixture'`; 9.1.1 4 passed (regression gone). No View/export. |
| 14011 class-scoped inherited fixture | HOLD | Complete snippet + pip list + pytest 9.0.1. Host 実機: 9.0.1 both tests fail (`self.variable is None`). No View staged. |

Reconfirmed 1130 HOLD 13885: pytest 8.4.1 and 9.0.1 autouse `assert 0` still runs under `@skipIf(True, ...)`; pytest 9.1.1 skips (rc=0). Still HOLD; no View. 14011 still fails on 9.1.1 (`self.variable is None`).

| 12689 | HOLD | No sealed mini bundle. HOLD. |
| 13699 | HOLD | No sealed mini bundle. HOLD. |
| 13724 | HOLD | PR. Repair/feature. HOLD. |
| 13727 | HOLD | PR. Repair/feature. HOLD. |
| 13754 | HOLD | Has a snippet but no sealed View/export. HOLD. |
| 13778 | HOLD | PR. Repair/feature. HOLD. |
| 13796 | HOLD | PR. Repair/feature. HOLD. |
| 13834 | HOLD | No sealed mini bundle. HOLD. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

32113 public files remain discovery. Related PRs in mini-followup remain 正解 and stay off the consumer.

## Acquisition vs eligibility

Fetching can succeed while eligibility for HDD stays quality+漏洩 PASS bound to a View hash. This screen does not mint PASS.
