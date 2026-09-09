# R1 budget

Updated: 2026-09-09 17:40:54 JST

## Caps

- User-specified daily cap: **$50.00** (ceiling, not a target)
- OpenRouter remaining at start: **$17.6545** (credits 35.0 − usage 17.34545104)
- Account reserve: **$1.50** (no auto top-up)
- Effective cap this run: **$16.15** — max(0, min(50.00 USD user cap, available_credit 17.6545 − 1.50 reserve))
- Stop casual new HDD (80%): **$12.92**
- Stop all new R1 (100%): **$16.15**
- Day max R1 calls: **40**
- Broad freeze: **2026-09-10 06:40:00 JST** (exceptional-jump only after)
- Preservation start: **2026-09-10 08:00:00 JST**
- Hard end: **2026-09-10 09:00:00 JST** (not extended)

## Totals

- Total R1 calls: **1**
- Observed spend (OpenRouter usage delta): **$0.000000**
- Conservative transcript estimate (sum): **$0.027377**
- Gate spend (max observed, estimate) + in-flight reserve: **$0.027377** + **$0.000000**
- Remaining effective budget: **$16.127172**

## Pricing used for estimates

- Input $0.7/MTok, output $2.5/MTok
- Source: live OpenRouter GET https://openrouter.ai/api/v1/models id=deepseek/deepseek-r1 at 2026-09-09 17:30:02 JST
- Missing-metadata rule: chars/2 tokens + 8192 reasoning-token buffer per call

## Calls by trial

| Trial | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| case-001-a | 1 | 0.000000 | 0.027377 |

## Calls by experiment phase

| Phase | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| first-turn | 1 | 0.000000 | 0.027377 |

## Call log

| When JST | Trial | Iter | Phase | Status | HTTP | Tool | Observed USD | Estimated USD |
| --- | --- | ---: | --- | --- | --- | --- | ---: | ---: |
| 2026-09-09 17:33:23 JST | case-001-a | 1 | first-turn | http-ok | True | False | 0.000000 | 0.027377 |

## Notes

- Dreamer is `deepseek/deepseek-r1` only; no silent substitute.
- An R1 HTTP success is design material, not tool success.
- Host Red Pen does not count against this cap.
- Codex usage is not counted against this cap.
- This ledger lives under the current run dir; closed `lab-hdd/` and the 9/2 and 1130 runs are not written.
- No auto top-up.
