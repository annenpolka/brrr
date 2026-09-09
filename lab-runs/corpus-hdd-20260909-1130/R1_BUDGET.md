# R1 budget

Updated: 2026-09-09 13:46:02 JST

## Caps

- User-specified daily cap: **$30.00** (ceiling, not a target)
- OpenRouter remaining at start: **$17.6876** (credits 35.0 − usage 17.31240384)
- Account reserve: **$1.50** (no auto top-up)
- Effective cap this run: **$16.19** — max(0, min(30.00 USD user cap, available_credit 17.6876 − 1.50 reserve))
- Stop casual new HDD (80%): **$12.95**
- Stop all new R1 (100%): **$16.19**
- Day max R1 calls: **40**
- Broad freeze: **2026-09-09 13:44:00 JST** (exceptional-jump only after)
- Hard end: **2026-09-09 13:56:00 JST** (rescheduled earlier; original ceiling 00:00 not extended)

## Totals

- Total R1 calls: **3**
- Observed spend (OpenRouter usage delta): **$0.033047**
- Conservative transcript estimate (sum): **$0.081566**
- Gate spend (max observed, estimate) + in-flight reserve: **$0.081566** + **$0.000000**
- Remaining effective budget: **$16.106030**

## Pricing used for estimates

- Input $0.7/MTok, output $2.5/MTok
- Source: live OpenRouter GET https://openrouter.ai/api/v1/models id=deepseek/deepseek-r1 at 2026-09-09 11:30:22 JST
- Missing-metadata rule: chars/2 tokens + 8192 reasoning-token buffer per call

## Calls by trial

| Trial | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| case-001-a | 3 | 0.033047 | 0.081566 |

## Calls by experiment phase

| Phase | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| counterexample | 1 | 0.005068 | 0.027196 |
| first-turn | 2 | 0.027979 | 0.054370 |

## Call log

| When JST | Trial | Iter | Phase | Status | Observed USD | Estimated USD |
| --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-09 11:31:20 JST | case-001-a | 1 | first-turn | ok | 0.015815 | 0.02653 |
| 2026-09-09 11:39:29 JST | case-001-a | 2 | first-turn | ok | 0.012164 | 0.02784 |
| 2026-09-09 11:45:16 JST | case-001-a | 3 | counterexample | ok | 0.005068 | 0.027196 |

## Notes

- Dreamer is `deepseek/deepseek-r1` only; no silent substitute.
- An R1 HTTP success is design material, not tool success.
- Host Red Pen does not count against this cap.
- Codex usage is not counted against this cap.
- This ledger lives under the current run dir; closed `lab-hdd/` and the 9/2 run are not written.
