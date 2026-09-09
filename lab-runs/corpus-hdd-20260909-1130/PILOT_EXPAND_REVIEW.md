# github-pilot expansion screen (host; not Dreamer-facing)

Pulled into 12:26–12:30 JST so the 12:00–14:00 slot is not idle.
Isolated root: `.brrr-corpus/pilot-expand-20260909`
Collection: `a9328ef43806b624ae4b461fea9d53947e459228bc24bd2fe1fb90773d4ff216`
Stop: `INVOCATION_REQUEST_LIMIT` after 200 requests (recipe slice, not auto-raised).
Resume: `python3 scripts/corpus.py --root .brrr-corpus/pilot-expand-20260909 resume --collection a9328ef43806b624ae4b461fea9d53947e459228bc24bd2fe1fb90773d4ff216 --max-requests 200 --max-seconds 600`

Slice 1: 200 requests, 24 complete, pytest only.
Slice 2 resume: +200 requests (total reserved 400), 42 complete, still pytest only. Search job `RESOURCE_OR_LANE_LIMIT` — pytest lane filled before cargo/uv/npm/gradle/TypeScript/nix/buildkit were reached. A third slice would mostly deepen pytest PRs, not add repositories, so it is not started.
Coverage is bounded search, not a census.

Reviewer: agent. Not human. HOLD is not converted to PASS to fill 3–6.

## Screened complete issues (read bodies)

| Issue | Quality | Leakage | Why |
| --- | --- | --- | --- |
| 13755 session fixture re-init | HOLD | not exported | Long reported test module exists, but no sealed View/byte-range artifacts yet; do not improvise a bundle. |
| 13784 capteesys doubled prints | HOLD | not exported | Has `test.py` + `pytest -svv` transcript (8.4.1). Still no View. Transcript mentions extra plugins/`pytest.ini` not supplied. |
| 13885 skipIf vs autouse fixture | HOLD | not exported | Small complete snippet + pytest 8.4.2. Strong mini candidate. No View staged this hour. |
| 14048 --pyargs + tox 3.14.2 | HOLD | n/a | Tree listed; `__init__.py` bytes missing; tox-only; `test_some.py` indent in markdown is untrusted. |
| 14971 nested conftest vs file order | HOLD | not exported | Best extra candidate: five quoted files + exact command + 8.4.2 vs 9.1.1. Reporter also includes a causal trace of pytest internals — that paragraph must not go to a Dreamer. Host 実機 (Python 3.14 venvs): 9.1.1 `..E` nested_fixture missing on test_b; 8.4.2 3 passed. runpair around 9.1.1: rc 1/1, added []. No View/export. |

No second public PASS snapshot. HDD consumer still has 1 discovery case. 小規模試行. Not holdout.

32113-related PRs in mini-followup remain 正解 and stay off the consumer.

## Acquisition vs eligibility

Fetching succeeded for 24 roots. Eligibility for HDD is quality+漏洩 PASS bound to a View hash. This screen does not mint PASS.
