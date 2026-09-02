# DESTROYER greendep 3

Date: 2026-09-02 15:17 JST (attacks) / 15:19 JST (record)
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-greendep/greendep` after mutate-3
(`MUTATE.md` third cut, 28 tests, sha256
`b7d0fe6855f57e18ae0fe8bba96e1d0765de41e7fd5aec6605dae7ae4fda8d60`, 8564 bytes)

Worktree copy at
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep/greendep/greendep`
is **byte-identical** (`cmp` rc=0). Worktree HEAD `934bcda` records mutate
`0bd07b2`. Archive `HEAD.txt` is `0bd07b2`. Parent remains `main` `432f954`;
`greendep` is not in that tree. rustc is on PATH at `/opt/homebrew/bin/rustc`
and was **not** invoked. No merge onto `main`. Host Python 3.14.5.

Prior destroyers: `DESTROYER_greendep.md` MUTATE (per-query),
`DESTROYER_greendep_2.md` MUTATE (incomplete/cap/`-`). First KEEP/MUTATE is
not protection. Honor KILL.

Host `python3 -m unittest discover -s tests -v` against that cut: 28/28 OK,
0.745s, rc=0. Happy path is real. That is not enough.

This candidate is still a **THIN_WRAPPER of set-difference** on
caller-labeled `query` / `dep` / `changed` rows. `inspect()` is
`set(changed[q]) - set(recorded[q])` plus the intersection, plus
`incomplete = bool(green) and not rec["changed"]`. An independent replica
of leftover+cap+rc (does not import greendep) is **byte-identical** to the
CLI on 51/51 host cases (`stdout_eq=True`, `rc_eq=True`). Leftover
membership without format MATCH 9/9 fixtures including rc. awk of the same
rule names the same UNREC/INV pairs. Mutate-3 could not recover edges from
a dump: rustc-shaped `q -> d` is refused. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-greendep/greendep
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-greendep/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep/greendep/greendep
```

No pytest. No rustc. Do not grow a `-Zdump-dep-graph` importer. Do not send
THIN_WRAPPER back to R1. Do not merge into visitid. `075-hang.rec` is still
byte-identical to `075-green.rec` (sha256
`3b46357bd3f8b707f476cb24452b56ab5c28418fb31832f599a5e0bf44a88c09`); leftover
name, not a hang.

---

## What still works (mutate-3 claims, verified)

Owned 075-poll / 075-green: `false_green` the owner, unrecorded
`type_of(Error)`, rc=1. Unrelated green is not `false_green`. Invalidation
labeled, rc=1 (`unseen-recorded.rec`). Incomplete green without a changed
pair, rc=2. `-` is not a legal NAME (empty stdout, rc=1). Empty lists still
print `-` plus `false_green_n	0`. LIST_CAP=32 / NAME_CAP=256; counts
uncapped. Global `changed	D1	D2	D3` refused. Two greens + shorthand
refused. rustc-shaped dump refused. Worktree poll stdout matches archive.

```bash
python3 "$CLI" "$FIX/075-poll.rec"; echo rc=$?
python3 "$CLI" "$FIX/unrelated.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-recorded.rec"; echo rc=$?
python3 "$CLI" "$FIX/incomplete.rec"; echo rc=$?
printf 'query\t-\tgreen\nchanged\tq\tD\n' | python3 "$CLI" -; echo rc=$?
printf 'typeck_of(S::poll) -> type_of(Error)\n' | python3 "$CLI" -; echo rc=$?
```

```text
green	typeck_of(S::poll)
false_green	typeck_of(S::poll)
unrecorded_changed	query	typeck_of(S::poll)	dep	type_of(Error)
invalidation	-
incomplete	no
rc=1
```

```text
green	typeck_of(S::poll)	typeck_of(unrelated)
false_green	typeck_of(S::poll)
unrecorded_changed	query	typeck_of(S::poll)	dep	type_of(Error)
rc=1
```

```text
false_green_n	0
false_green	-
invalidation	query	typeck_of(poll)	dep	type_of(Error)
incomplete	no
rc=1
```

```text
incomplete	yes
false_green	-
rc=2
```

```text
greendep: <stdin>:1: query '-' is not a legal NAME
rc=1
```

```text
greendep: <stdin>:1: rustc-shaped q -> d dump is not an input; use query/dep/changed TSV
rc=1
```

Stdin `-`, `/dev/stdin`, symlink, filename with a space, FIFO (writer after
reader): owned 075-poll, rc=1. `agree.rec` (red, recorded the changed dep)
stays rc=0. Extra query column / empty tab field: parse errors, rc=1 (slides
closed). Color `true`/`maybe`: not green or red, rc=1. `GREEN` still green
(`.lower()`). Duplicate query last-wins (green then red → not false, rc=0;
red then green → false, rc=1).

That is the whole useful delta. It is also `comm` of two columns the caller
already bound per query.

---

## Implementation

`inspect()` in full (archive, mutate-3):

```python
for query in green:
    recs = set(rec["recorded"].get(query, []))
    missing: list[str] = []
    recorded_changed: list[str] = []
    for dep in own.get(query, []):
        if dep in recs:
            recorded_changed.append(dep)
        else:
            missing.append(dep)
    if missing:
        false_green.append(query)
        for dep in missing:
            unrecorded_changed.append((query, dep))
    for dep in recorded_changed:
        invalidation.append((query, dep))
incomplete = bool(green) and not rec["changed"]
```

False-green names are exactly:

```python
[q for q in green if set(own.get(q, [])) - set(recorded.get(q, []))]
```

Invalidation is the intersection. Incomplete is a global flag on the table
(`any green` and `changed` empty), not a recovered missing edge. `inspect`
never walks `red`. Change is not propagated along `dep` edges.

### 1. THIN_WRAPPER of set-difference on a caller-complete table

Host replica (`/tmp/greendep-d3/replica.py`, does not import greendep):
parse `query`/`dep`/`changed`; leftover = own-changed minus recorded;
invalidation = intersection; incomplete = greens present and `changed` empty;
LIST_CAP=32 / NAME_CAP=256 display; rc=2 / 1 / 0 as mutate-3. Byte-identical
stdout and rc on every well-formed case and every parse-error case run:

```text
075-poll / 075-green / 075-hang     stdout_eq=True rc_eq=True  greendep rc=1
agree                               stdout_eq=True rc_eq=True  rc=0
unrelated / arrows / unseen-const   stdout_eq=True rc_eq=True  rc=1
unseen-recorded                     stdout_eq=True rc_eq=True  rc=1
both / incomplete                   stdout_eq=True rc_eq=True  rc=1 / 2
rustc-dump / arrow-dep-notab        stdout_eq=True rc_eq=True  rc=1
40-unrecorded-deps                  stdout_eq=True rc_eq=True  rc=1
257-greens-one-changed              stdout_eq=True rc_eq=True  rc=1
257-own-changed-greens              stdout_eq=True rc_eq=True  rc=1
257-greens-40-deps                  stdout_eq=True rc_eq=True  rc=1
dash-query / dash-dep / dash-changed-query  stdout_eq=True rc=1
green-only / green+dep / changed-tab        stdout_eq=True rc=2
red-only / harvest-changed-on-red / agree-red  stdout_eq=True rc=0
mixed-green-incomplete-global       stdout_eq=True rc_eq=True  rc=1
unrelated-own-changed / no-propagate-parent stdout_eq=True rc=1
dup-query last-wins / extra-col / empty-tab / true-color
unicode / crlf / comment-drops-changed / empty-stdin / missing-file
```

51/51. No mismatches.

Leftover membership without format (no cap, no TSV printer) MATCH 9/9
fixtures including rc:

```text
MATCH 075-poll.rec         fg=[typeck_of(S::poll)] unrec=[(poll, Error)] rc=1
MATCH 075-green.rec        fg=[typeck_of(poll)]    unrec=[(poll, Error)] rc=1
MATCH unrelated.rec        fg=[typeck_of(S::poll)] unrec=[(poll, Error)] rc=1
MATCH unseen-recorded.rec  fg=[] inv=[(poll, Error)] rc=1
MATCH agree.rec            fg=[] inv=[] rc=0
MATCH both.rec             unrec=[(poll, adt_def)] inv=[(poll, Error)] rc=1
MATCH incomplete.rec       inc=True rc=2
MATCH unseen-const.rec     fg=[eval_const(N)] unrec=[(N, Inner)] rc=1
MATCH arrows.rec           fg=[a->b] unrec=[(a->b, e->f)] rc=1
```

awk of the same rule on the fixture columns:

```text
# 075-poll        UNREC typeck_of(S::poll) type_of(Error)
# 075-green       UNREC typeck_of(poll) type_of(Error)
# unrelated       UNREC typeck_of(S::poll) type_of(Error)
# unseen-recorded INV typeck_of(poll) type_of(Error)
# agree           (empty)
# both            INV …Error / UNREC …adt_def
# incomplete      (empty); CLI rc=2 from the global flag
# unseen-const    UNREC eval_const(N) type_of(Inner)
```

Same miss the CLI names. The TSV join (`false_green`, labeled
`unrecorded_changed` / `invalidation` pairs, `incomplete`, rc) is formatting
around that membership.

Owned events already contain the miss:

```text
query	typeck_of(S::poll)	green
dep	typeck_of(S::poll)	trait_def
dep	typeck_of(S::poll)	adt_def
changed	type_of(Error)
```

`demo.sh` prints two query names as the nearest operation, then feeds this
table. The CLI will not parse a dump, and will not guess that `typeck`
should have read `type_of(Error)`. Mutate-3 leftover: “still `comm` of two
columns the caller already bound per query.” Host-executed: that leftover
**is** the object.

A rustc-looking dump is not an input (mutate could not recover edges):

```bash
printf 'typeck_of(S::poll) -> type_of(Error)\n' | python3 "$CLI" -
# greendep: <stdin>:1: rustc-shaped q -> d dump is not an input
# rc=1, empty stdout

printf 'query\tq\tgreen\ndep\tq->d\nchanged\td\n' | python3 "$CLI" -
# greendep: <stdin>:2: dep needs query and dep name
# rc=1
```

### 2. Cap hiding: LIST_CAP hides names the object exists to print

Mutate-3 claimed LIST_CAP=32 / NAME_CAP=256; counts uncapped. Host:

**40 unrecorded deps** (`query q green` + `changed q d00` … `d39`):

```text
changed_n	40
false_green	q
unrecorded_changed_n	40
# 32 pair rows: d00 … d31
invalidation	-
incomplete	no
rc=1
```

`d32`…`d39` are **not** in stdout. Count says 40. The object exists to name
unrecorded edges; eight names are dropped. Replica matches the truncation.

**257 greens**, one `changed g0 D`: `green` lists 32 (`g0`…`g31`),
`green_n	257`, `false_green	g0`, `g256` absent from stdout. The owner
is shown; the cap hides unrelated greens.

**257 greens each with own-changed** (`changed g{i} D{i}`):
`false_green_n	257`, `false_green` lists 32 (`g0`…`g31`), `g32`/`g256`
absent. `unrecorded_changed_n	257`, 32 pair rows. Counts uncapped; **the
false_green names the object exists to print are hidden after 32.**

**257 greens + 40 unrecorded deps on g0**: `false_green	g0` (shown),
`unrecorded_changed_n	40`, 32 pair rows, `d32`…`d39` hidden, `g256`
hidden. Same hiding of the unrecorded-edge list.

NAME_CAP: two names that differ after byte 256 display as the same
`N`×256+`...` cell. Replica matches. Truncation is display-only; leftover
membership still distinguishes them. The list cap is the hole that hides
identities.

Raising LIST_CAP would not beat set-difference. It is not a FIX of this
wrapper.

### 3. `-` empty-list vs NAME collision (claimed closed — verified)

```bash
printf 'query\t-\tgreen\nchanged\tq\tD\n' | python3 "$CLI" -
# greendep: <stdin>:1: query '-' is not a legal NAME  rc=1  stdout empty

printf 'query\tq\tgreen\nchanged\tq\t-\n' | python3 "$CLI" -
# greendep: <stdin>:2: dep '-' is not a legal NAME  rc=1

printf 'query\tq\tgreen\nchanged\t-\tD\n' | python3 "$CLI" -
# greendep: <stdin>:2: query '-' is not a legal NAME  rc=1
```

`unseen-recorded.rec`: `false_green	-` with `false_green_n	0`.
`false_green\t-\n` is in stdout. `query	-	` is not. Empty lists still
print `-`. Collision closed as claimed. That does not recover edges.

### 4. Incomplete vs agreement vs false_green

| rec | incomplete | false_green | rc |
| --- | --- | --- | --- |
| `query a green` | yes | `-` | 2 |
| green + dep, no changed | yes | `-` | 2 |
| `changed<TAB>` = ∅ | yes | `-` | 2 |
| harvest colors, no changed pair | yes | `-` | 2 |
| red-only, no changed | **no** | `-` | **0** |
| green `a` + green `b` + `changed b D` | **no** | `b` | 1 |
| poll green / Error red / `changed Error field` | **no** | `-` | **0** |
| harvest colors + recorded Error + `changed` on the **red** query | **no** | `-` | **0** |
| green + unrecorded own-changed | no | `a` | 1 |
| green + recorded ∩ own-changed | no | `-` | 1 (invalidation) |
| red + recorded ∩ own-changed (`agree`) | no | `-` | 0 |

Incomplete is `bool(green) and not rec["changed"]` — a **global** flag.
One green with a changed pair makes every other green “complete.” A green
with no own-changed plus a red that carries the only `changed` pair is
clean agreement (rc=0). Mutate-3 leftover: “Incomplete only fires when
there is **no** changed pair at all.” Host-executed: harvest ingredients as
colors with the changed pair bound to Error (not poll) stay rc=0. The CLI
does not derive changed identities from red rows.

`#changed	a	D` is a comment; the change is dropped; green-only then
incomplete rc=2. That is the global flag, not an oracle.

### 5. Invalidation rc (claimed restored — verified)

1-part shorthand `changed	Y` with `dep	a	Y`, and 2-part
`changed	a	Y`:

```text
false_green	-
invalidation	query	a	dep	Y
incomplete	no
rc=1
```

`unseen-recorded.rec` same shape, rc=1. `both.rec`: unrecorded `adt_def` and
invalidation `type_of(Error)` both print, rc=1. `agree.rec` red stays rc=0.
Not treated as unrecorded miss. Restored as claimed. Intersection is still
`set(own-changed[q]) ∩ set(recorded[q])` on the caller table.

### 6. Unrelated green (claimed closed — verified)

`unrelated.rec`: `false_green	typeck_of(S::poll)` only.
`typeck_of(unrelated)` is on `green`, not on `false_green`. Two greens +
shorthand: `exactly one green`, rc=1, empty stdout. Global list: `not a
global list`, rc=1. Parent of a false_green child stays green unless the
caller also wrote `changed	parent	…`:

```bash
printf 'query\tparent\tgreen\nquery\tchild\tgreen\ndep\tparent\tchild\ndep\tchild\ttrait_def\nchanged\tchild\tError\n' | python3 "$CLI" -
```

```text
green	parent	child
false_green	child
unrecorded_changed	query	child	dep	Error
rc=1
```

Per-query set-difference is real. It still cannot tell “should have read”
from “caller wrote `changed	QUERY	DEP`.” No dep walk.

### 7. Owned 075 still holds

`075-poll.rec` rc=1, `false_green	typeck_of(S::poll)`,
`unrecorded_changed	query	typeck_of(S::poll)	dep	type_of(Error)`,
`invalidation	-`, `incomplete	no`. `075-green.rec` same join, other
spelling (`typeck_of(poll)`). Worktree byte-identical, same TSV. Tests
28/28. That is the harvest sentence as a handwritten table. It is not a
reason to KEEP a wrapper of `comm`.

### 8. Host replica of the set-diff matching leftover+rc

See §1. Replica match **51/51** stdout+rc. Leftover membership MATCH **9/9**
fixtures + rc. awk UNREC/INV matches pair rows on owned/unrelated/invalidation/both/const.
Worktree poll stdout_eq archive.

---

## Primitive

Reality-stripped operation: parse TSV of `query NAME COLOR`, `dep QUERY DEP`,
`changed QUERY DEP` (or shorthand DEP onto the unique green); for each
`COLOR==green`, `missing = [d for d in own[q] if d not in recorded[q]]`,
`invalidation = [d for d in own[q] if d in recorded[q]]`; incomplete iff
there is a green and `changed` is empty; print capped lists; exit 2 if
incomplete, 1 if false_green or invalidation, else 0.

Nearest ordinary workflow: the leftover membership / awk above, or print the
green name and the changed name. Seeing `typeck_of(poll)` green and
`type_of(Error)` changed still leaves “was that dep recorded?” as a hand
join — but this CLI does not recover edges. `demo.sh` writes those facts
into `.rec` files, including the missing `type_of(Error)` by omitting it
from `dep` rows.

Observable capability lost if greendep vanishes: **none** beyond a named
sticker. The caller already labeled green/red, already listed recorded
deps, already listed which query owns which changed identity. `comm` of
those two columns is the product. The TSV labels (`false_green`,
`unrecorded_changed query/dep`, `invalidation`, `incomplete`, rc) are
formatting around that membership.

That is why this is KILL, not MUTATE. The *question* (which green query
failed to record a changed identity after `-Znext-solver` typeck of
`fn poll` stayed green) is a real debugging object. This embodiment does
not ask it of a dump. It asks `set(changed[q]) - set(recorded[q])` on a
caller-complete table. Adding rustc ingest / `-Zdump-dep-graph` / a dep
walk would be implementing the harvest this artifact failed to embody — a
new harvest, not a patch of set-difference. Constitution: a THIN_WRAPPER
does not gain exotic features to escape classification. Worker rule: do
not send THIN_WRAPPER back to R1 with “make this more novel.” DESTROYER_greendep
already said: if a later mutation cannot recover edges and is still
set-difference on caller-labeled greens, KILL. Mutate-3 did (1)+(2)+(3) as
**record fields** (per-query `changed`, incomplete flag, invalidation row,
caps, `-` refuse). That is a stricter printer of the answer key, not a
recovered edge.

Hardcoded ceiling:

- `false_green` = green with `set(own-changed[q]) - set(recorded[q])` nonempty
- `invalidation` = recorded ∩ own-changed, rc=1, not false_green
- `incomplete` = any green and no changed pair at all (global); mixed greens
  and changed-on-red are agreement
- unrelated green is not false unless the caller bound `changed` to it
- no dump ingest; rustc-shaped `q -> d` refused
- no dep walk; parent of a false child stays green
- red is not auto-changed; `inspect` never walks `red`
- LIST_CAP=32 hides unrecorded-edge names and false_green names after 32;
  counts uncapped
- NAME_CAP=256 truncates display (`...`); empty lists print `-`; `-` is not
  a legal NAME
- color is `green`/`red` after `.lower()`; `true`/`1`/`maybe` error
- empty tab / extra columns error; duplicate query last-wins
- `075-poll` vs `075-green` remain two spellings of the same join;
  `075-hang.rec` leftover name
- a leftover replica already computes `false_green` + rc

Do not grow a rustc dump importer to escape THIN_WRAPPER. Do not merge this
join into visitid. Do not send it back to R1. Honor KILL. Dreamer ancestry
is not protection. First MUTATE is not protection.

---

KILL
