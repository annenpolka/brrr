# DESTROYER startimer

Date: 2026-09-02 13:52 JST

Target: `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-startimer/startimer`

Origin: timer armed while starting vs remaining at StartPeriod vs first counted failure. Specimen-066. Happy path is real.

```
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-startimer/startimer
```

## What still works

Owned `2s / 30s / 2s / retries 1`:

```
armed	start-interval	30s
period_end	2s
remaining_at_period_end	28s
reset_at_period_end	no
first_probe	30s
unhealthy_at	30s
expected_unhealthy	4s
gap	26s
```

ms units match seconds. Negative duration rc=1. retries 0 rc=1. Missing flags rc=2.

## Implementation

### 1. remaining_at_period_end disagrees with first_probe when StartInterval < StartPeriod

```
python3 "$CLI" --start-period 30s --start-interval 2s --interval 2s --retries 1
```

```
armed	start-interval	2s
period_end	30s
remaining_at_period_end	0s
first_probe	2s
first_counted	30s
unhealthy_at	30s
expected_unhealthy	32s
gap	-2s
```

`remaining_at_period_end` is `max(armed - period_end, 0)` so 0s, while `first_probe` is 2s (inside the period). `first_counted` then jumps to period_end. The four output times are not one timer.

### 2. reset_at_period_end is a constant

Always `no`. The CLI replays only the failing getInterval (arm start-interval at t=0, never reset). It cannot name the policy that *would* reset at period end; `expected_unhealthy` is a second formula, not a second arming.

When start_interval == start_period (10s) and retries=3: `remaining 0s`, `first_probe 10s`, `unhealthy_at 14s`, `expected_unhealthy 16s`, `gap -2s`.

## Decision

MUTATE. Keep owned 066 remaining 28s / unhealthy 30s vs expected 4s. remaining must match armed−elapsed at period_end only when first_probe is after that instant; negative gap is a lie if the counted probe is the original fire.
