# reimpl-07 — brood

## Primitive

From a **commit or a diff** (never FILE:LINE), recover every **birth cohort** that change still owes at HEAD. Natal keys **inflect**: `t1` ↔ `driftDelay` because the same line used to say `t1`; `present_threshold` ↔ `presentThreshold` by snake/camel. Renamed siblings still count as unpaid kin.

Clean-room reimplementation of `erst` (mutation-19). The original Python file was never opened. CLI shape, JSON fields, fixture, and dogfood queries were recovered by running the binary and reading README / CANDIDATE / demo.

## Why this might not exist

`also` answers once you already know `FILE:LINE`. `owe` takes a change but matches natal keys as exact bytes, so `t1` → `driftDelay` looks like a no-op (the `15` never moved) and leftover `T1` docs stay invisible. `aka` catalogs inflection pacts in a tree and cannot pair `t1` with `driftDelay` because they share no stem. Reviewers have a SHA. The leftover mention may have been last-touched by a formatter, may no longer look like a clone, and may now be spelled `T1` or `present_threshold`.

Rebuilding from the outside tests whether the primitive is real or an accident of one implementation.

## How to run

From this worktree (Python 3, `git` on PATH, no other deps):

```bash
chmod +x ./brood ./demo.sh
./brood --selftest
./demo.sh                 # exits 0
./brood --no-color -C /path/to/sitbone e9b0f75
./brood --json --check HEAD
git diff | ./brood -
```

Exit codes: `0` ok, `1` `--check` found unpaid kin, `2` usage / not a repo / FILE:LINE.

## Empirical transcript

v0.1 is commit `3d7b9c4`. v0.2 is occupancy + generic-domain filtering driven by sitbone dogfood.

### Before (v0.1) — fixture

Birth: `t1 = 15` and `present_threshold = 0.4` introduced together with a weird markdown path, yaml, tests, and `src/foo bar/t1.py`. Mutation commit renames only `core.py`.

```
$ ./brood --no-color -C "$FIX" HEAD
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

owing  4 unpaid  ·  …
nee    present_threshold↔presentThreshold
keys   present_threshold, 0.4
delta  present_threshold, 0.4 → presentThreshold, 0.45
paid   core.py:2: presentThreshold = 0.45
owing  deploy/timing.yaml:2: present_threshold: 0.4
owing  docs/how to set (t1).md:4: The present_threshold is 0.4.
```

`FILE:LINE` exits 2. `--check` exits 1. Intact `PORT=8080` stays quiet. `T1` in the docs holds natal `t1`.

### Before (v0.1) — dogfood

sitbone `e9b0f75` (PresenceArbiter `threshold`/`0.4` → `presentThreshold`/`0.45`), invoked as a commit — no FILE:LINE:

```
nee    threshold↔presentThreshold
keys   threshold, 0.4
delta  threshold, 0.4 → presentThreshold, 0.45
paid   Sources/SitboneCore/PresenceArbiter.swift:33: presentThreshold: Double = 0.45,
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
owing  docs/adr/0019-presence-hysteresis.md:76: 既存の `threshold: Double = 0.4` …
owing  Sources/SitboneCore/SiteObserver.swift:45: private let threshold: Double = 0.7
```

The inversion works: leftover 0.4 tests *and* the erstwhile name `threshold` surface without anyone naming `PresenceArbiter.swift:33`. False owing: `SiteObserver.threshold = 0.7` is a different domain.

### After (v0.2)

Generic ident in code locates only when bound to a natal literal (or leftover in docs/tests). Slot-form `threshold: Double = 0.7` is dropped. Paid lines are adopted *slots*, not every mention. Each leftover carries occupancy: `since <sha>` from `git blame` of that surface at HEAD. `case flowThreshold = "t1"` is `alias` (quoted-only adapter).

Same PresenceArbiter commit. SiteObserver is gone. ADR leftover `threshold` and 0.4 tests remain. Occupancy shows the leftover 0.4 tests have been sitting since the birth commit `a95da43`; the ADR line that still writes `threshold: Double = 0.4` was last touched at `98a8009`.

```
$ ./brood --no-color -C sitbone e9b0f75
change commit  e9b0f75deabd  Implement dual-threshold hysteresis in PresenceArbiter

owing  6 unpaid  ·  a95da435efe6  Add PresenceArbiter …
nee    threshold↔presentThreshold
keys   threshold, 0.4
delta  threshold, 0.4 → presentThreshold, 0.45
paid   Sources/SitboneCore/PresenceArbiter.swift:33: presentThreshold: Double = 0.45,
owing  Tests/SitboneCoreTests/PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
       (holds 0.4) since a95da43
owing  docs/adr/0019-presence-hysteresis.md:76: 既存の `threshold: Double = 0.4` パラメータを削除し…
       (holds threshold) since 98a8009
echo   docs/adr/0019-presence-hysteresis.md:12: smoothedScore >= threshold ? .present : .absent
echo   CLAUDE.md:329: @Test("… threshold 0.4")
echo   SPEC.md:145: `normalized > 0.4` → `.present`。
```

Same lint commit. Only the natal renames remain (no `s↔score`, no `window↔focusedWindow`):

```
$ ./brood --no-color -C sitbone 1fcdec6
owing  …  nee t1↔driftDelay
owing  SPEC.md:110: - `T1` = 15秒（FLOW→DRIFT閾値）
       (holds T1) since a2512fe
owing  README.md:130: | FocusStateMachine | … T1=15s, T2=90s |
alias  Sources/SitboneCore/SessionProfile.swift:36: case flowThreshold = "t1"

owing  …  nee t2↔awayDelay
owing  SPEC.md:111: - `T2` = 90秒（DRIFT→AWAY閾値）
owing  Tests/…/FocusStateMachineEdgeCaseTests.swift:25: // > t2(90)
```

`aka` cannot produce this: `t1` and `driftDelay` are not an inflection class. `owe` cannot produce this: the `15` never moved.

kizu `fb355e0`: smokes (no crash). `./demo.sh` exits 0.

v0.2 is: generic ident bound to a natal literal or docs/tests, hunk-local slot pairing, distinctive `t1`/`t2` only (not 1-letter locals), leftover occupancy, quoted-only `alias`.

## Dogfood targets

- Synthetic ugly fixture (spaces, parens, nested git, `t1`/`T1`/`present_threshold`) — `./demo.sh`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — PresenceArbiter `e9b0f75`, rename `1fcdec6`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `fb355e0`

## Surprises

- `t1` is two characters. Tokenizers that require 3+ drop the natal name; 1-letter locals (`s`, `r`) that *are* two-or-fewer must *not* count as distinctive or `s↔score` explodes a lint commit.
- `T1` in a markdown table is the same identity as `t1` by surface case, not by stemming `driftDelay`.
- A lint commit that *also* renamed the natal slots is a better query than the rename-only commit you wish existed. The change is the query; you do not need to know `SitboneCore.swift:107`.
- `case flowThreshold = "t1"` is an adapter (quoted-only), not unpaid docs. Classifying it as `alias` keeps CodingKeys from looking like forgotten kin.
- Occupancy of leftover `T1` on SPEC.md blames `a2512fe` (docs rewrite), not the natal `d3737ea`. The surface has lived longer than the SHA that last touched the line would suggest only if you follow the identity, not the hunk.

## Failures

v0.1 (fixed in v0.2):

- Generic `threshold` recruited `SiteObserver.threshold = 0.7`.
- Whole-file slot pairing 1:1-paired 1-letter locals (`s↔score`, `r↔cornerRadius`).
- `presentThreshold` was treated as leftover `present_threshold` because snake↔camel surfaces overlapped.

Still open:

- Same-magnitude floats in a different domain still collide as echo (`GazeDetectorTests` `yaw: 0.4`).
- `git blame` per leftover can be slow on huge trees.
- Occupancy is last-touch of the leftover *line*, not first introduction of the natal identity (the mutation erst itself listed).
- A rename that never occupied a `name: Type =` / `let name:` slot (pure call-site rewrite) will not 1:1-pair; that is intended.

## Suggested mutations

- Follow a sibling forward with `git log -L` so occupancy is "T1 since d3737ea" even after a docs rewrite.
- Domain tags: cluster 0.4-threshold separately from 0.4-yaw without regex style lists.
- `--pr`: `gh pr diff | brood -`.
- Drop Path B intact numeric keys (`15`, `90`) from `--debug` noise.

## Kill / keep

**Keep.** `brood e9b0f75` producing leftover `threshold` *and* `0.4` without anyone naming `PresenceArbiter.swift:33`, and `brood 1fcdec6` producing leftover `T1`/`T2` from a lint SHA plus `alias` on `case flowThreshold = "t1"`, is the "why doesn't this exist" moment. `aka` does not pair `t1`↔`driftDelay`. `owe` is silent when the number did not move. Occupancy (`since a95da43`) is the mutation that erst suggested and the reimpl actually shipped. Worth mutating (identity-follow occupancy, domain tags) rather than killing.
