# MUTATE emptyunit (applied 2026-09-02)

From `destroyers/DESTROYER_emptyunit_2.md` after MUTATE (not KILL).

```yaml
origin:
  method: specimen-hdd
  trial: hdd-s063
  mutation: hang_risk is replacement burst (FIFO first + _reschedule if pending <= 2)
  parent: candidate-emptyunit
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-emptyunit-emptyunit
branch: specimen-hdd/candidate-emptyunit-emptyunit
parent_commit: a5d91b9684f6600c2ce1006841890b97c6d3c310
commit: b61e26943bfabfceda0cc371e13ed5053e475417
cli_sha256: 40bd25683ab0173036ed722c756adcb6b78db41bf3bb1637d2b174c8491c9ddb
```

Not merged to `main`. pytest-xdist is not imported. Not merged with `requeue`.

`python3 tests/test_emptyunit.py -v` — 27 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

The object: a completed-only work unit put back after a crash is assigned
as `send_runtest_some([])`, and that is the hang, even when another scope
still has pending tests.

This is the same object as the last cut (would the replacement be sent
`()`), not a new scheduler. Completions are not simulated.

## Change (DESTROYER_emptyunit_2 §1)

`hang_risk` is any empty send in the replacement burst:

1. FIFO first unit (same as last cut).
2. If that unit’s pending ≤ 2, xdist `_reschedule` assigns the next FIFO
   unit too. Live-first + completed-only second is hang, rc=1.
3. Empty send hangs the worker; nothing after that unit is received.

Owned 063 stays hang: first assign is already `()`. First pending=3 then
completed-only is not hang at this snapshot (watermark holds the second
unit). `first_assigned` / `would_send` still name the first assign.
`assigned` / `reschedule` / `hang_unit` name the burst.

## Not faked

`empty_send` is still `completed_only`. After index-error, `send ()` iff
the unit has no incomplete items. Two names, one bit. hang_risk is now
“is that bit set on a unit the replacement actually receives?”, not a
thicker meaning of `empty_send`. Do not pretend they were split.

Dist still validates caller keys; it does not regroup collection.
Ingest is still the `{collection, workqueue}` envelope. Caps still refuse.
Those holes were not this cut.

## Before (DESTROYER_emptyunit_2)

Live-first (`unseen-live-first.rec` / JSON same shape):

```
first_assigned	live.py::u
would_send	(1)
hang_risk	no
empty_send	yes    # done.py::t, second unit
rc:0
```

That second `send ()` is a hang under `-n1 --dist=loadgroup` because
assigned pending 1 ≤ 2. False negative.

## After (this mutation)

Live-first:

```
first_assigned	live.py::u
would_send	(1)
assigned	live.py::u	done.py::t
reschedule	yes
hang_unit	done.py::t
hang_risk	yes
rc:1
```

Owned dump (`fixtures/063-hang.dump`): still

```
first_assigned	testing/test_timeout.py::test_1
would_send	()
assigned	testing/test_timeout.py::test_1
reschedule	no
hang_unit	testing/test_timeout.py::test_1
hang_risk	yes
rc:1
```

Pending=2 then completed-only: `reschedule yes`, `hang_risk yes`, rc=1.
Pending=3 then completed-only: `reschedule no`, `hang_unit -`,
`hang_risk no`, rc=0. Two live units: `reschedule yes`, `hang_risk no`.

## Remaining holes (not this cut)

- **THIN_WRAPPER: `empty_send` == `completed_only`.** Not faked. The join
  is hang_risk over the burst, not a new empty-list check.
- **Completions are not simulated.** After pending=3 drops to 2,
  `_reschedule` would assign the completed-only unit. That is a later
  snapshot. This CLI is the replacement-start burst (first + at most one
  reschedule).
- **Dist is still a key sticker.** Same tests under loadgroup vs
  loadscope do not regroup; `scope mismatch` is still the only effect.
- **Ingest is still the envelope**, not `print(workqueue)` /
  `OrderedDict` repr. `str(None)`/`True`/`0` still become nodeids.
  `workqueue {}` still shadows `assigned`.
- **Caps** 512/256 still refuse a legal 257-unit loadgroup dump.
- Sentinel `-` still collides with a nodeid named `-`.
- Not a LoadScopeScheduling implementation. Do not merge with `requeue`.

---

# MUTATE emptyunit (3) (applied 2026-09-02)

From `destroyers/DESTROYER_emptyunit_2.md` remaining holes after cut (1)
(replacement burst). Keep the object: name a completed-only work unit a
replacement would be sent as `send_runtest_some([])`.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-s063
  mutation: dist regroups; ingest print(workqueue); 257 units legal
  parent: candidate-emptyunit
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-emptyunit-emptyunit
branch: specimen-hdd/candidate-emptyunit-emptyunit
archive: lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/
parent_commit: 8b231321c12f7a8925670639ffa232ea1c1d87e3
commit: 4168ca2f59bca2ca3e58874f79351cef8d2fd6d6
cli_sha256: 9e224d35637d45ea2f324e439f784c25c003d47c5b12cce6550e221078758627
cli_bytes: 24307
```

Not merged to `main`. pytest-xdist is not imported. Not merged with `requeue`.

`python3 tests/test_emptyunit.py -v` twice — 39/39 OK.

`./demo.sh` ×2, `demo-1.log` / `demo-2.log` byte-identical. Wrapper exit 0.

## What was kept

Assign loop from cut (1): hang_risk is any empty send in the replacement
burst (FIFO first + `_reschedule` if assigned pending ≤ 2). Live-first +
completed-only second is hang, rc=1. Owned 063 stays hang. Completions
are not simulated.

## Change (DESTROYER_emptyunit_2 §2–4)

1. **Dist grouping is a scheduler.** Caller scope keys are ignored.
   Units are derived from nodeids + dist: loadgroup is the full nodeid,
   or `@` after `]`; loadscope is `rsplit("::", 1)`. Same tests under
   the two dists change hang_risk without the caller regrouping.
   `scope mismatch` is gone.

2. **Ingest what xdist prints.** `print(workqueue)` / `OrderedDict([...])`
   and a nested dict ingest. A collection list may be supplied or inferred
   from inner nodeids. JSON/`dict` envelopes stay. `workqueue {}` does not
   shadow filled `assigned`. Non-string collection/nodeid values
   (`null`/`true`/`0`) are refused, not `str()`-coerced. Nodeid `-` is
   refused (empty sentinel). `none` stays an identity; `dist none` stays
   an error.

3. **Caps.** 257 loadgroup units is a legal dump (first-done hangs;
   all-open does not). No 256-unit refuse. Collection has a safety cap
   of 8192, labeled as such, not as pytest collection.

## Before (DESTROYER_emptyunit_2 leftover)

Same two tests, flip dist on the same keys:

```
# dist=loadscope on 063-hang.json
emptyunit: <stdin>: scope mismatch 'testing/test_timeout.py::test_1' != 'testing/test_timeout.py' (loadscope)
rc:1
```

`OrderedDict([...])` → `expected key<TAB>value`. 257 units →
`workqueue exceeds cap (256)`. Nodeid `-` collided with empty lists.

## After (this mutation)

Same tests, no caller regroup:

```
dist loadgroup → hang_risk yes / would_send () / scopes_n 2 / rc=1
dist loadscope → hang_risk no  / would_send (1) / scopes_n 1 / first_assigned mod.py / rc=0
```

Owned 063 with dist forced to loadscope: one module unit, `send (1)`,
hang_risk no. `print(workqueue)` OrderedDict of the owned dump: hang,
rc=1. Handwritten both-done rec: regrouped to two completed loadgroup
units, pending 0, not the hang, rc=0.

## Remaining holes (not faked)

- After index-error, `empty_send` (`send == ()`) still coincides with
  `completed_only` on every reported unit. Two names, one bit.
- Completions are not simulated. Pending=3 then completed-only is still
  not hang at this snapshot (watermark holds the second unit).
- Collection safety cap 8192 still refuses a huge table. Not a 256-unit
  ceiling; still not unlimited pytest collection.
- JSONL two objects (unless list then dict), trailing commas, and
  `/* comments */` still fail. Duplicate JSON keys last-wins.
- A nodeid containing TAB still splits a TSV collection row.
- Dist is a closed enum (`loadgroup|loadscope`). `load` / `each` /
  `loadfile` are errors, not `--dist=load` semantics.
- Not a LoadScopeScheduling implementation. Do not merge with `requeue`.
