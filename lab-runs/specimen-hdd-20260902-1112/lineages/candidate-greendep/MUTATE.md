# MUTATE greendep (applied 2026-09-02 14:40 JST)

From `destroyers/DESTROYER_greendep.md` after MUTATE (not KILL).

```yaml
origin:
  method: hdd
  trial: hdd-rustcinc
  specimens: [specimen-075]
  mutation: own-changed (not global); invalidation row; TSV query/dep pairs
  parent: candidate-greendep
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep
branch: specimen-hdd/candidate-greendep-greendep
parent_commit: b6d3317
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-greendep/
cli_sha256_before_archive: 307ba329ed834892e7054087789210155b50b37be822388589b4b564b091d21f
cli_bytes_before: 4053
cli_sha256_after: fa30c9a03ded1617713cf42fe3aa52193d0c10ef651b848e433b8c03cc90b857
cli_bytes_after: 6559
```

Not merged to `main`. rustc is not invoked. Not merged with visitid.

`python3 -m unittest discover -s tests -v` twice — 16/16 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

The object: a green query whose *own* changed dependency was never
recorded is named `false_green`, and rc≠0.

Owned 075: `typeck_of(S::poll)` / `typeck_of(poll)` green;
`type_of(Error)` unrecorded; `false_green` that query; rc=1.

## Change (DESTROYER_greendep §1, §3, §4)

1. **`changed` is not a global list.** Canonical form is
   `changed	QUERY	DEP`. Only that query is tested against that dep.
   An unrelated green is not `false_green`. `changed	D1	D2	D3`
   (old global list) is an error. Shorthand `changed	DEP` still binds
   to the unique green (owned 075-poll / 075-green). Two greens plus
   shorthand is an error, not “every green missed D”.

2. **Recorded ∩ own-changed is `invalidation`, not silence.** Green +
   recorded dep that also changed prints
   `invalidation	query	Q	dep	D`, `false_green	-`, rc=1.
   Do not call it `false_green`. When both happen (`type_of(Error)`
   recorded, `adt_def` not), both rows print. A red query that recorded
   the changed dep (`agree.rec`) stays rc=0.

3. **Pairs are TSV fields `query`, `dep`, never `->` glue.** One row
   per edge:
   `unrecorded_changed	query	typeck_of(S::poll)	dep	type_of(Error)`.
   Names containing `->` are opaque ids (`a->b` / `e->f`). A rustc-shaped
   `q -> d` dump is refused (`rustc-shaped q -> d dump is not an input`).
   Archive flatten and worktree `q->d` concatenation are gone.

## Not faked (leftover)

Cannot beat `set(changed[q]) - set(recorded[q])` without rustc. The
caller still names which query owns which changed identity. This cut
beats *global* `set(changed) - set(recorded[q])` that marked unrelated
greens. It does not recover edges from a dump. Documented, not hidden.

- No rustc ingest. `075-poll` vs `075-green` remain two spellings of
  the same join. `075-hang.rec` is still a leftover name (byte-identical
  to `075-green.rec`), not a hang.
- No visitid merge. Pointer-vs-value skip stays elsewhere.
- Incomplete / invalidation-rc / `-` NAME / color vocab: closed in the
  second cut below (DESTROYER_greendep_2).
- Empty tab fields still slide on leftover keys; duplicate `query`
  last-wins. No cap on 2000 greens / 200k-character names.
- Change is not propagated along recorded edges to other greens.
- Red is not auto-changed. A red-only record with no `changed` row is
  complete (no green to be false).

If a later mutation is still global `set(changed) - set(recorded[q])`
on caller-labeled greens, KILL as THIN_WRAPPER.

## Before (DESTROYER_greendep)

Unrelated green + global `changed	type_of(Error)`:

```
false_green	typeck_of(S::poll)	typeck_of(unrelated)
unrecorded_changed	typeck_of(S::poll)	type_of(Error)	typeck_of(unrelated)	type_of(Error)
rc=1
```

Green that recorded the changed dep (`unseen-recorded.rec`):

```
false_green	-
unrecorded_changed	-
rc=0
```

Worktree encoding: `unrecorded_changed	a->b->e->f`.

## After (this mutation)

Unrelated (`fixtures/unrelated.rec`, `changed	typeck_of(S::poll)	type_of(Error)`):

```
false_green	typeck_of(S::poll)
unrecorded_changed	query	typeck_of(S::poll)	dep	type_of(Error)
invalidation	-
rc=1
```

Recorded-changed green:

```
false_green	-
unrecorded_changed	-
invalidation	query	typeck_of(poll)	dep	type_of(Error)
rc=1
```

Owned 075-poll: `false_green	typeck_of(S::poll)`,
`unrecorded_changed	query	typeck_of(S::poll)	dep	type_of(Error)`,
`invalidation	-`, rc=1.

Arrow names: `unrecorded_changed	query	a->b	dep	e->f`.
Dump `typeck_of(S::poll) -> type_of(Error)`: refuse, rc=1.

---

# MUTATE greendep 2 (applied 2026-09-02 14:58 JST)

From `destroyers/DESTROYER_greendep_2.md` after MUTATE (not KILL).

```yaml
origin:
  method: hdd
  trial: hdd-rustcinc
  specimens: [specimen-075]
  mutation: incomplete rc=2; invalidation rc=0; `-` NAME refuse; color green|red
  parent: candidate-greendep
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep
branch: specimen-hdd/candidate-greendep-greendep
cli_sha256_before: fa30c9a03ded1617713cf42fe3aa52193d0c10ef651b848e433b8c03cc90b857
cli_sha256_after: 4eb8b1604e4d54fc21197b81996e898d089584f379bf488115705ebfde9ddf62
cli_bytes_after: 7802
```

Not merged to `main`. rustc is not invoked.

`python3 -m unittest discover -s tests -v` — 21/21 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical.

## Change (DESTROYER_greendep_2)

1. **Incomplete is rc=2.** Green queries and no `changed` pair → `incomplete	yes`, not agreement. `false_green	-`. Fixture `incomplete.rec`. Red-only without `changed` stays complete rc=0.

2. **Invalidation is labeled, rc=0.** Green + recorded ∩ own-changed prints `invalidation	query	Q	dep	D`, `false_green	-`, **rc=0**. Not treated as unrecorded miss. Both kinds still rc=1 because `false_green` is nonempty (`both.rec`).

3. **`-` is not a legal NAME.** Query/dep/changed `-` → stderr `not a legal NAME`, rc=1, empty stdout.

4. **Color is `green` or `red`.** `true` / `1` / `maybe` → `color … is not green or red`, rc=1.

Owned 075 false_green still rc=1. Unrelated green still not false_green.

## Not faked

Still `set(own-changed[q]) - set(recorded[q])` on a caller-complete table. No rustc. No visitid. Duplicate query last-wins. No cap. `075-hang.rec` leftover name. Red is not derived into `changed`.

---

# MUTATE greendep 2 (fix, applied 2026-09-02 15:05 JST)

From `destroyers/DESTROYER_greendep_2.md` after the 14:58 cut. That cut
landed incomplete + `-` NAME refuse, but set invalidation to rc=0
(already a KEEP from DESTROYER_greendep) and left dumps uncapped.

```yaml
origin:
  method: hdd
  trial: hdd-rustcinc
  specimens: [specimen-075]
  mutation: incomplete rc=2; invalidation rc=1; `-` NAME refuse; LIST_CAP/NAME_CAP
  parent: candidate-greendep
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep
branch: specimen-hdd/candidate-greendep-greendep
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-greendep/
cli_sha256_before: 4eb8b1604e4d54fc21197b81996e898d089584f379bf488115705ebfde9ddf62
cli_sha256_after: b7d0fe6855f57e18ae0fe8bba96e1d0765de41e7fd5aec6605dae7ae4fda8d60
cli_bytes_after: 8564
```

Not merged to `main`. rustc is not invoked. Not merged with visitid.

`python3 -m unittest discover -s tests -v` twice — 28/28 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

Per-query `false_green` (own unrecorded changed dep). `invalidation` is
recorded ∩ own-changed, a distinct row, **rc=1** (not the 14:58 rc=0,
not false_green). Owned 075 still rc=1. Unrelated green is not
false_green. Global `changed	D1	D2	D3` is still an error. TSV
`query`/`dep` fields, never `->` glue. rustc-shaped dump refused.

## Change (DESTROYER_greendep_2 leftovers 1, 3, 4 + restore KEEP)

1. **Incomplete record is not agreement.** Green and no `changed` pair
   (omitted or `changed<TAB>` = ∅) → `incomplete	yes`, rc=2,
   `false_green_n	0` / `false_green	-`. `changed<TAB>` is empty
   changed, not `expected key<TAB>value` via strip. Harvest colors
   without a changed pair are incomplete, not rc=0. Red-only without
   changed stays complete rc=0.

2. **Query named `-` is not the empty sentinel.** `-` as query/dep/changed
   is `not a legal NAME`, rc=1, empty stdout. Empty lists still print
   `-` plus uncapped counts (`false_green_n	0`). `grep '^false_green	-$'`
   matches empty, never a query named `-`.

3. **Cap huge dumps.** `LIST_CAP=32` on listed names/pairs;
   `NAME_CAP=256` on displayed names (`...` suffix). Counts stay
   uncapped (`false_green_n`, `unrecorded_changed_n`, `invalidation_n`,
   `green_n` when over cap). 2000 own-changed greens: 32 listed,
   `false_green_n	2000`, rc=1, stdout < 50k. 200k-character name:
   truncated in stdout, rc=1. 2000 greens + one `changed	g0	D`:
   only `g0` is `false_green` (not a global set-difference).

4. **Invalidation rc=1 restored.** `unseen-recorded.rec` prints
   `invalidation	query	typeck_of(poll)	dep	type_of(Error)`,
   `false_green	-`, rc=1. rc=0 only for a complete record with no
   unrecorded-changed green and no invalidation (`agree.rec`).

## Not faked (leftover)

(1)+(2)+(3) do not beat `set(changed[q]) - set(recorded[q])` and the
intersection on a caller-complete table. Still `comm` of two columns
the caller already bound per query. Documented, not hidden.

- No rustc ingest. No `-Zdump-dep-graph`. No visitid merge.
- Red is not auto-changed; `inspect` never walks `red`. A rec that is
  poll green / Error red / poll recorded Error **with** a changed pair
  on Error (not poll) stays rc=0. Incomplete only fires when there is
  **no** changed pair at all.
- Change is not propagated along `dep` edges. A green parent of a
  false_green/invalidated child stays green unless the caller also
  wrote `changed	parent	…`.
- Duplicate `query` last-wins. `075-hang.rec` is still a leftover name
  (byte-identical to `075-green.rec`), not a hang. `075-poll` vs
  `075-green` remain two spellings of the same join.

Do not revert to global `set(changed) - set(recorded[q])`. That is
already a KILL. Do not become visitid.

