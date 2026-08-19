# mutation-38 — brood

## Primitive
Given a **commit or a diff** (never FILE:LINE), recover every **birth cohort** that change touches — natal keys still inflect (`t1`↔`driftDelay`) — but a natal literal is **domain-tagged** so `0.4`-threshold is not `0.4`-opacity.

## Why this might not exist
`erst` treats a natal number as a global token (with a STYLE_LINE denylist for `opacity`/`yaw`). Same-commit `alpha = 0.4` still joins a `threshold = 0.4` family because the bytes match. Reviewers have a SHA that bumped a cutoff. The leftover `0.4` in a color channel is not unpaid kin. A regex list of style words does not scale (`alpha`, `rgba`, `withAlphaComponent`, `wash`). The binder at birth *is* the domain.

## How to run
From this worktree:

```bash
./brood --selftest
./demo.sh
./brood HEAD
./brood -C /path/to/repo e9b0f75 --json --check
git diff | ./brood -
./brood --pr
./brood --tsv HEAD
```

## Empirical transcript

v0.1 is domain tags + `--pr` + `--tsv` + `git log -L` rename-follow. v0.2 is the improvement: quoted test names (`@Test("… threshold 0.4")`) no longer bind to `Test(`.

### Before (v0.1) — fixture

Birth commit introduces `t1 = 15`, `present_threshold = 0.4`, quiet `PORT = 8080`, **and** `ui/overlay.py` `alpha = 0.4` / `rgba(..., 0.4)` in the same commit. Mutation renames only `core.py`.

```
$ ./brood --no-color -C "$FIX" HEAD
owing  …  nee t1↔driftDelay  domain t1  keys t1@t1
owing  tests / docs / yaml leftover t1 and T1

owing  …  nee present_threshold↔presentThreshold
domain present_threshold
keys   present_threshold@present_threshold, 0.4@present_threshold
owing  deploy/timing.yaml:2: present_threshold: 0.4
owing  docs/how to set (t1).md:4: The present_threshold is 0.4.
owing  tests/test_core.py:5: assert present_threshold == 0.4
```

`ui/overlay.py` is absent. Intact `PORT=8080` is quiet. `FILE:LINE` exits 2. `--check` exits 1.

Same fixture through parent `erst`:

```
owing  docs/how to set (t1).md:6: The overlay wash uses alpha 0.4 (unrelated).
owing  ui/overlay.py:1: alpha = 0.4
owing  ui/overlay.py:2: wash = 0.4
```

That is the flip: erst accuses opacity-domain `0.4`; brood does not.

### Before (v0.1) — dogfood

sitbone `e9b0f75` (PresenceArbiter `threshold`/`0.4` → `presentThreshold`/`0.45`), invoked as a commit — nobody named `PresenceArbiter.swift:33`:

```
nee    threshold↔presentThreshold
domain threshold
keys   threshold@threshold, 0.4@threshold
paid   PresenceArbiter.swift:33: presentThreshold: Double = 0.45,
owing  PresenceArbiterTests.swift:177: // 3回目で0.4を下回る
owing  PresenceArbiterTests.swift:216: // … 0.214 < 0.4
echo   adr/0019 … 既存の `threshold: Double = 0.4`
echo   SPEC.md:145: `normalized > 0.4` → `.present`
```

SiteObserver.threshold=0.7 is gone. NotchOverlay `.opacity(0.4)` is gone.

Missed in v0.1: `CLAUDE.md` `@Test("… threshold 0.4")` — the number sat inside quotes, so the binder was parsed as `Test(`.

sitbone `1fcdec6` (lint SHA that also renamed `t1`→`driftDelay`, `t2`→`awayDelay`): leftover `T1`/`T2` in SPEC/README/CLAUDE. Local lint pairs (`counters`↔`updatedCounters`) stay quiet.

kizu `fb355e0`, tenaoshi `HEAD`, skills `HEAD`: smoke, no crash. tenaoshi `7505f56` still floods on `provider`↔`env` / leftover `mock` (inherited erst 1:1 pairing when a harness rewrite drops strings — not a domain-tag miss). skills `6b19433` (`update kinsoku`): `no unpaid kin at HEAD` (true negative).

### After (v0.2)

Quoted interiors are not outer-call binders. Idents inside strings count as domain neighbors. Same sitbone commit now also echoes:

```
echo   CLAUDE.md:329: @Test("… threshold 0.4")
echo   CLAUDE.md:332: @Test("… threshold 0.4")
```

Still no overlay/opacity/SiteObserver. Fixture still silent on `alpha = 0.4`.

v0.2 is: in-string domain, mention of the natal binder anywhere on the line, CLAUDE.md leftovers restored.

## Dogfood targets
- Synthetic ugly fixture (spaces, parens, nested git, same-commit `0.4@threshold` vs `0.4@alpha`) — `./demo.sh`
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — `e9b0f75`, `1fcdec6`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `fb355e0`
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — `HEAD`, `7505f56`
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — `HEAD`

## Surprises
- `erst` already denylists `opacity`/`yaw` via STYLE_LINE, yet still accuses `alpha = 0.4` and `wash = 0.4`. The missing primitive is the natal binder, not a longer denylist.
- Same-commit introduction of two `0.4`s is the hard case. Path-B rarity clustering by token alone merges them; brood clusters by `(token, domain)`.
- `@Test("… threshold 0.4")` looks like `Test(0.4)` to a call-binder walker. Quoted leftovers are how specs remember the old cutoff.
- Inflection is orthogonal to domain: `t1`↔`driftDelay` still works when the number (`15`) never moved.

## Failures
v0.1 (fixed in v0.2):
- Quoted test names bound `0.4` to `Test`, dropping CLAUDE.md leftovers.

Still open:
- Cutoff leftovers without binder or path affinity (`if x > 0.4` in an unrelated file) can still join a threshold brood.
- `self.presentThreshold = presentThreshold` is listed as paid on the ident cohort — noisy, not wrong.
- `git log -L` rename-follow is a fallback when same-path grep misses; huge files can time out (25s).
- `--pr` needs `gh`; the Unix form `gh pr diff | brood -` does not.

## Suggested mutations
- Occupancy: how long HEAD has held the erstwhile surface (`T1` since d3737ea).
- Domain from the enclosing function / type, not only the line, for `return 0.4`.
- Bake a tiny `0.4@threshold` vs `0.4@alpha` fixture into `--selftest` as a mini-repo (already in `demo.sh`).

## Kill / keep
**Keep.** The gold is real: `brood e9b0f75` leftover threshold `0.4` tests/docs without naming `PresenceArbiter.swift:33`; `brood 1fcdec6` leftover `T1`/`T2`; and a fixture where `erst` accuses `alpha = 0.4` while `brood` is silent. `aka` does not pair `t1`↔`driftDelay`. `also` wants FILE:LINE. `erst` cannot tell threshold from opacity without a denylist. Worth mutating (function-level domain, occupancy) rather than killing.
