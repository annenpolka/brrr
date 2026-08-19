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

v0.1 is commit `95e67d8`. v0.2 is the improvement driven by sitbone dogfood.

### Before (v0.1) — fixture

Birth: `t1 = 15` and `present_threshold = 0.4` introduced together with a weird markdown path, yaml, tests, and `src/foo bar/t1.py`. Mutation commit renames only `core.py`.

```
$ ./erst --no-color -C "$FIX" HEAD
change commit  …  rename t1→driftDelay and present_threshold→presentThreshold

owing  5 unpaid  ·  …  introduce t1=15 present_threshold=0.4 port=8080
nee    t1↔driftDelay
keys   t1
delta  t1 → driftDelay
paid   core.py:1: driftDelay = 15
owing  deploy/timing.yaml:1: t1: 15
owing  docs/how to set (t1).md:3: T1 is 15 seconds.
owing  src/foo bar/t1.py:1: t1 = 15  # keep in sync with core.py
owing  tests/test_core.py:4: assert t1 == 15

owing  4 unpaid  ·  …  introduce t1=15 present_threshold=0.4 port=8080
nee    present_threshold↔presentThreshold
keys   present_threshold, 0.4
delta  present_threshold, 0.4 → presentThreshold, 0.45
paid   core.py:2: presentThreshold = 0.45
owing  deploy/timing.yaml:2: present_threshold: 0.4
owing  docs/how to set (t1).md:4: The present_threshold is 0.4.
```

`FILE:LINE` exits 2. `--check` exits 1. Intact `PORT=8080` stays quiet. `T1` in the docs holds natal `t1`.

### Before (v0.1) — dogfood

sitbone `e9b0f75` (PresenceArbiter `threshold`/`0.4` → `presentThreshold`/`0.45`), invoked as a commit:

```
nee    threshold↔presentThreshold
keys   threshold, 0.4
delta  threshold, 0.4 → presentThreshold, 0.45
paid   Sources/SitboneCore/PresenceArbiter.swift:33: presentThreshold: Double = 0.45,
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
owing  docs/adr/0019-presence-hysteresis.md:76: 既存の `threshold: Double = 0.4` …
owing  Sources/SitboneCore/SiteObserver.swift:45: private let threshold: Double = 0.7
```

The inversion works: no line number, leftover 0.4 tests *and* the erstwhile name `threshold` surface. False owing: `SiteObserver.threshold = 0.7` is a different domain.

sitbone `1fcdec6` (lint commit that also renamed `t1` → `driftDelay`, `t2` → `awayDelay`):

The intended hit is real — leftover `T1`/`T2` in SPEC/README/CLAUDE. But a large rewrite also 1:1-paired locals: `counters↔updatedCounters`, `radius↔cornerRadius`, `window↔focusedWindow`, `geo↔geometry`. Unusable as a rename report.

### After (v0.2)

Pair declaration-slot names first. 1:1 leftover pairing only when the abandoned name is distinctive (`t1`). Stem containment is slot-only and rejects prefix noise (`updated`+`Counters`). Generic idents (`threshold`) locate/echo only when bound to a natal literal or leftover in docs/tests.

Same PresenceArbiter commit. SiteObserver is gone. ADR leftover `threshold` and 0.4 tests remain:

```
$ ./erst --no-color -C sitbone e9b0f75
change commit  e9b0f75deabd  Implement dual-threshold hysteresis in PresenceArbiter

owing  3 unpaid  ·  a95da435efe6  Add PresenceArbiter …
nee    threshold↔presentThreshold
keys   threshold, 0.4
delta  threshold, 0.4 → presentThreshold, 0.45
paid   Sources/SitboneCore/PresenceArbiter.swift:33: presentThreshold: Double = 0.45,
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:216: // … 0.214 < 0.4
owing  docs/adr/0019-presence-hysteresis.md:76: 既存の `threshold: Double = 0.4` パラメータを削除し…
echo   docs/adr/0019-presence-hysteresis.md:12: smoothedScore >= threshold ? .present : .absent
echo   CLAUDE.md:329: @Test("… threshold 0.4")
echo   SPEC.md:145: `normalized > 0.4` → `.present`。
```

Same lint commit. Only the natal renames remain:

```
$ ./erst --no-color -C sitbone 1fcdec6
owing  …  nee t2↔awayDelay
owing  SPEC.md:111: - `T2` = 90秒（DRIFT→AWAY閾値）
owing  Tests/…/FocusStateMachineEdgeCaseTests.swift:25: // > t2(90)

owing  …  nee t1↔driftDelay
owing  SPEC.md:110: - `T1` = 15秒（FLOW→DRIFT閾値）
owing  README.md:130: | FocusStateMachine | … T1=15s, T2=90s |
owing  CLAUDE.md:506: - 境界値テスト: T1(15s), T2(90s)
```

`aka` cannot produce this: `t1` and `driftDelay` are not an inflection class. `owe` cannot produce this: the `15` never moved.

kizu `fb355e0`: smokes (no crash). Fixture still exits 0.

v0.2 is: slot-first pairing, distinctive 1:1 only, stem-noise rejection, generic ident bound to a natal literal or docs/tests.

## Dogfood targets
- Synthetic ugly fixture (spaces, parens, nested git, `t1`/`T1`/`present_threshold`) — `./demo.sh`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — PresenceArbiter `e9b0f75`, rename `1fcdec6`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `fb355e0`

## Surprises
- `t1` is two characters. Every ancestor tokenizer required 3+ and dropped the natal name.
- `T1` in a markdown table is the same identity as `t1` by surface inflection, not by stemming `driftDelay`.
- A lint commit that *also* renamed the natal slots is a better query than the rename-only commit you wish existed. The change is the query; you do not need to know `SitboneCore.swift:107`.
- `case flowThreshold = "t1"` is an adapter (quoted-only), not unpaid docs. Classifying it as `alias` keeps CodingKeys from looking like forgotten kin.

## Failures
v0.1 (fixed in v0.2):
- Generic `threshold` recruited `SiteObserver.threshold = 0.7`.
- Leftover 1:1 pairing treated every vanished ident as erstwhile (`window`↔`focusedWindow`).
- Stem containment treated `updatedCounters` as `counters`.

Still open:
- `delta t1 → driftDelay, 15` sometimes lists a still-present literal as adopted when the ancestral line split.
- Same-magnitude floats in a different domain still collide if you query a 0.45 bump.
- `git log -L` per replacement can be slow on huge files.
- A rename that never occupied a `name: Type =` slot (pure call-site rewrite) will not 1:1-pair; that is intended, and it will miss a real erstwhile name that only lived in argument position.

## Suggested mutations
- Track a sibling forward with `git log -L` so a file rename without leftover tokens still resolves.
- Domain tags: cluster 0.4-threshold separately from 0.4-opacity without regex style lists.
- `--pr`: `gh pr diff | erst -`.
- Occupancy: show how long HEAD has held the erstwhile surface (`T1` since d3737ea).

## Kill / keep
**Keep.** `erst e9b0f75` producing leftover `threshold` *and* `0.4` without anyone naming `PresenceArbiter.swift:33`, and `erst 1fcdec6` producing leftover `T1`/`T2` from a lint SHA, is the "why doesn't this exist" moment. `aka` does not pair `t1`↔`driftDelay`. `owe` is silent when the number did not move. Worth mutating (rename-follow, domain tags) rather than killing.
