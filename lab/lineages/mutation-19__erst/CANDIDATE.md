# mutation-19 — erst

## Primitive
Given a **commit or a diff** (never FILE:LINE), recover every **birth cohort** that change touches — and treat natal keys as identities that **inflect** (`t1` ↔ `driftDelay` from the same line's history; `present_threshold` ↔ `presentThreshold` by snake/camel) so renamed siblings still count as unpaid kin.

## Why this might not exist
`also` answers once you already know `FILE:LINE`. `owe` takes a change but matches natal keys as exact bytes, so a rename of `t1` → `driftDelay` looks like a no-op (the `15` never moved) and leftover `T1` docs stay invisible. `aka` catalogs every inflection pact in a tree and checks one-sided patches; it has no birth cohort and cannot pair `t1` with `driftDelay` because they share no stem. Reviewers have a SHA. The leftover mention may have been last-touched by a formatter, may no longer look like a clone, and may now be spelled `T1` or `present_threshold`.

## How to run
From this worktree:

```bash
./erst --selftest
./demo.sh
./erst HEAD
./erst -C /path/to/repo e9b0f75 --json --check
git diff | ./erst -
```

## Empirical transcript
v0.1 is the first commit of `erst`. Transcript filled after the first dogfood pass.

## Dogfood targets
- Synthetic ugly fixture (spaces, parens, nested git, `t1`/`T1`/`present_threshold`) — `./demo.sh`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — PresenceArbiter `e9b0f75`, rename `1fcdec6`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu`

## Surprises
(to fill)

## Failures
(to fill)

## Suggested mutations
(to fill)

## Kill / keep
(to fill)
