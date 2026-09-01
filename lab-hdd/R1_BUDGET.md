# R1 budget

Updated: 2026-09-02 02:16:35 JST

## Caps

- Experiment hard cap: **$50.00** (ceiling, not a target)
- OpenRouter remaining at start: **$11.1591** (credits 25.0 − usage 13.84092774)
- Effective cap this night: **$10.00** — min($50 experiment cap, OpenRouter remaining ~$11.16 minus $1.16 account reserve). If credits are added later, raise toward $50.
- Stop casual new HDD: **$9.00**
- Stop all new R1: **$10.00**

## Totals

- Total R1 calls: **38**
- Observed spend (OpenRouter usage delta): **$0.398488**
- Conservative transcript estimate (sum): **$1.045419**
- Remaining effective budget: **$9.601512**
- Remaining vs $50 experiment cap: **$49.601512**

## Pricing used for estimates

- Input $0.7/MTok, output $2.5/MTok
- Source: OpenRouter list price for deepseek/deepseek-r1 on 2026-09-01; used only when generation usage metadata is missing
- Missing-metadata rule: chars/2 tokens + 8192 reasoning-token buffer per call

## Calls by trial

| Trial | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| hdd-agent | 3 | 0.052133 | 0.080802 |
| hdd-build | 1 | 0.059711 | 0.025966 |
| hdd-ci | 2 | 0.038736 | 0.052578 |
| hdd-config | 2 | 0.065822 | 0.051765 |
| hdd-cross | 1 | 0.034579 | 0.027378 |
| hdd-debug | 2 | 0.073979 | 0.050014 |
| hdd-docs | 1 | 0.044843 | 0.026205 |
| hdd-empty | 2 | 0.000000 | 0.050743 |
| hdd-env | 2 | 0.044036 | 0.051316 |
| hdd-flake | 1 | 0.018459 | 0.025190 |
| hdd-history | 2 | 0.002857 | 0.054577 |
| hdd-ident | 2 | 0.018411 | 0.051766 |
| hdd-jump-nopath | 1 | 0.000000 | 0.025498 |
| hdd-log | 1 | 0.038052 | 0.026376 |
| hdd-merge | 2 | 0.099901 | 0.053648 |
| hdd-order | 2 | 0.029395 | 0.051827 |
| hdd-partial | 1 | 0.014263 | 0.082269 |
| hdd-patch | 1 | 0.021350 | 0.026027 |
| hdd-perf | 1 | 0.021350 | 0.025247 |
| hdd-pipe | 1 | 0.060584 | 0.025461 |
| hdd-review | 1 | 0.010590 | 0.026240 |
| hdd-silence | 1 | 0.005918 | 0.025555 |
| hdd-test | 1 | 0.063164 | 0.025605 |
| hdd-type | 1 | 0.074918 | 0.024946 |
| hdd-wait | 2 | 0.034579 | 0.053091 |
| unfamiliar-cli | 1 | 0.010590 | 0.025329 |

## Calls by experiment phase

| Phase | Calls | Observed USD | Estimated USD |
| --- | ---: | ---: | ---: |
| cambrian | 25 | 0.615736 | 0.697171 |
| deepen | 12 | 0.322487 | 0.322750 |
| jump | 1 | 0.000000 | 0.025498 |

## Call log

| When JST | Trial | Iter | Phase | Status | Observed USD | Estimated USD |
| --- | --- | ---: | --- | --- | ---: | ---: |
| 2026-09-01 22:00:06 JST | hdd-history | 1 | cambrian | ok | 0.000000 | 0.026398 |
| 2026-09-01 22:00:06 JST | hdd-debug | 1 | cambrian | ok | 0.003452 | 0.024528 |
| 2026-09-01 22:00:06 JST | hdd-agent | 1 | cambrian | ok | 0.010590 | 0.025937 |
| 2026-09-01 22:00:06 JST | unfamiliar-cli | 1 | cambrian | ok | 0.010590 | 0.025329 |
| 2026-09-01 22:00:06 JST | hdd-review | 1 | cambrian | ok | 0.010590 | 0.02624 |
| 2026-09-01 22:00:06 JST | hdd-merge | 1 | cambrian | ok | 0.029374 | 0.026856 |
| 2026-09-01 22:00:06 JST | hdd-log | 1 | cambrian | ok | 0.038052 | 0.026376 |
| 2026-09-01 22:03:09 JST | hdd-build | 1 | cambrian | ok | 0.059711 | 0.025966 |
| 2026-09-01 22:00:06 JST | hdd-test | 1 | cambrian | ok | 0.063164 | 0.025605 |
| 2026-09-01 22:06:21 JST | hdd-config | 1 | cambrian | ok | 0.016050 | 0.025118 |
| 2026-09-01 22:06:21 JST | hdd-ci | 1 | cambrian | ok | 0.016050 | 0.025329 |
| 2026-09-01 22:06:21 JST | hdd-perf | 1 | cambrian | ok | 0.021350 | 0.025247 |
| 2026-09-01 22:08:31 JST | hdd-history | 2 | deepen | ok | 0.002857 | 0.028179 |
| 2026-09-01 22:06:21 JST | hdd-env | 1 | cambrian | ok | 0.021350 | 0.025081 |
| 2026-09-01 22:06:21 JST | hdd-patch | 1 | cambrian | ok | 0.021350 | 0.026027 |
| 2026-09-01 22:06:21 JST | hdd-docs | 1 | cambrian | ok | 0.044843 | 0.026205 |
| 2026-09-01 22:08:31 JST | hdd-agent | 2 | deepen | ok | 0.026350 | 0.027085 |
| 2026-09-01 22:06:21 JST | hdd-type | 1 | cambrian | ok | 0.074918 | 0.024946 |
| 2026-09-01 22:08:31 JST | hdd-merge | 2 | deepen | ok | 0.070527 | 0.026792 |
| 2026-09-01 22:08:31 JST | hdd-debug | 2 | deepen | ok | 0.070527 | 0.025486 |
| 2026-09-01 22:15:17 JST | hdd-agent | 3 | deepen | ok | 0.015193 | 0.02778 |
| 2026-09-01 22:15:17 JST | hdd-env | 2 | deepen | ok | 0.022686 | 0.026235 |
| 2026-09-01 22:15:17 JST | hdd-ci | 2 | deepen | ok | 0.022686 | 0.027249 |
| 2026-09-01 22:18:03 JST | hdd-flake | 1 | cambrian | ok | 0.018459 | 0.02519 |
| 2026-09-01 22:18:03 JST | hdd-wait | 1 | cambrian | ok | 0.034579 | 0.025813 |
| 2026-09-01 22:15:17 JST | hdd-config | 2 | deepen | ok | 0.049772 | 0.026647 |
| 2026-09-01 22:18:03 JST | hdd-cross | 1 | cambrian | ok | 0.034579 | 0.027378 |
| 2026-09-01 22:18:03 JST | hdd-pipe | 1 | cambrian | ok | 0.060584 | 0.025461 |
| 2026-09-01 22:23:21 JST | hdd-wait | 2 | deepen | ok | 0.000000 | 0.027278 |
| 2026-09-01 22:40:04 JST | hdd-order | 1 | cambrian | ok | 0.000000 | 0.024636 |
| 2026-09-01 22:40:04 JST | hdd-silence | 1 | cambrian | ok | 0.005918 | 0.025555 |
| 2026-09-01 22:40:04 JST | hdd-ident | 1 | cambrian | ok | 0.005918 | 0.025044 |
| 2026-09-01 22:45:33 JST | hdd-ident | 2 | deepen | ok | 0.012493 | 0.026722 |
| 2026-09-01 22:44:12 JST | hdd-order | 2 | deepen | ok | 0.029395 | 0.027191 |
| 2026-09-01 22:57:48 JST | hdd-empty | 1 | cambrian | ok | 0.000000 | 0.024637 |
| 2026-09-01 23:07:22 JST | hdd-empty | 2 | deepen | ok | 0.000000 | 0.026106 |
| 2026-09-01 22:57:48 JST | hdd-partial | 1 | cambrian | ok | 0.014263 | 0.082269 |
| 2026-09-02 02:00:47 JST | hdd-jump-nopath | 1 | jump | ok | 0.000000 | 0.025498 |

## Notes

- R1 is for conceptual Dreamer mutation, not routine coding.
- A Red Pen turn does not imply another R1 turn.
- If OpenRouter is down, Dreaming degrades; grounding/implementation/judging continue.
