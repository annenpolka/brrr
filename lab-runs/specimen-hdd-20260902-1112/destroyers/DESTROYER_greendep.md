# DESTROYER greendep

Date: 2026-09-02 14:26 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested archive): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-greendep/greendep`

sha256 `307ba329ed834892e7054087789210155b50b37be822388589b4b564b091d21f` (4053 bytes). Direct `./greendep` and `python3 greendep` match.

Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep/greendep/greendep` is **not** byte-identical (sha256 `4f7abbb1842e793668e99697d7dc74be963388fc280beba8df2c0250524e22e6`, 4001 bytes, HEAD `b6d3317 align greendep fixtures to query/dep/changed table`). Archive `HEAD.txt` still says `8eda724`. The only code delta: archive `format_report` flattens `unrecorded_changed` into alternating TSV fields `(q, d, q, d, …)`; worktree still emits one field per pair as `q->d`. Worktree `test_owned` fails (`'type_of(Error)' not found in ['typeck_of(S::poll)->type_of(Error)']`). This record attacks the **archive** CLI. Arrow names are re-run on the worktree only to show the encoding the flatten was meant to escape.

Archive tests: `python3 -m unittest discover -s tests -v` → 4/4 OK, 0.104s, rc=0. `demo.sh` twice: `demo-1.log` / `demo-2.log` byte-identical, and a third host run matches `demo-1.log`. Parent tree remains `main`. No merge onto `main`. rustc is on PATH at `/opt/homebrew/bin/rustc` and was **not** invoked.

Origin claim (`CANDIDATE.md` / harvest `hdd-rustcinc` / specimen-075): name a green query whose changed dependency was never recorded. rc=1 on `false_green`. Kind: USEFUL_COMPOSITION. Owned analog: `typeck_of(S::poll)` / `typeck_of(poll)` green; `type_of(Error)` changed and unrecorded. Rejected: invented rustc `-Zdump-dep-graph` transcripts.

Happy path is real. That is not enough. `inspect()` is `set(changed) - set(recorded[q])` for every caller-labeled green. A host replica of parse+inspect+format is byte-identical to the CLI on every owned fixture and every attack rec below (`wrapper == cli: True`). Decision: **MUTATE**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-greendep/greendep
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-greendep/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-greendep-greendep/greendep/greendep
```

No pytest. No rustc. Do not merge this join into visitid. `075-hang.rec` is byte-identical to `075-green.rec` (197 bytes); leftover name, not a hang.

---

## What still works

Owned 075-poll (tests) and 075-green (demo), unseen `eval_const(N)` / `type_of(Inner)`, recorded-the-changed-dep, stdin, `/dev/stdin`, process substitution, FIFO (writer after reader), symlink, filename with a space, CRLF, Unicode names, comments/blanks.

```bash
python3 "$CLI" "$FIX/075-poll.rec"; echo rc=$?
python3 "$CLI" "$FIX/075-green.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-recorded.rec"; echo rc=$?
python3 "$CLI" "$FIX/agree.rec"; echo rc=$?
```

```text
green	typeck_of(S::poll)
red	-
changed	type_of(Error)
false_green	typeck_of(S::poll)
unrecorded_changed	typeck_of(S::poll)	type_of(Error)
rc=1
```

```text
green	typeck_of(poll)
red	type_of(Error)
changed	type_of(Error)
false_green	typeck_of(poll)
unrecorded_changed	typeck_of(poll)	type_of(Error)
rc=1
```

```text
green	typeck_of(poll)
red	type_of(Error)
changed	type_of(Error)
false_green	-
unrecorded_changed	-
rc=0
```

```text
green	-
red	typeck_of(S::poll)
changed	type_of(Error)
false_green	-
unrecorded_changed	-
rc=0
```

`075-poll` names `typeck_of(S::poll)` and has no red query row. `075-green` names `typeck_of(poll)` and lists `type_of(Error)` as red. Both fire the same join. Tests use poll; `demo.sh` uses green. Missing file / directory / `/dev/null` / empty stdin / invalid UTF-8 / binary / JSON / BOM / unknown field / short `query`/`dep`: `greendep: …` rc=1. Two positional args: argparse rc=2. 2000 greens: 0.027s, `false_green` lists all 2000. 200k-character name: 0.027s, stdout 600058 bytes. No cap.

That is the whole useful delta. Attacks below break the claim that `false_green` names *the* query whose result depended on an unrecorded change, or show the primitive is set-difference on a table that already contains the answer.

---

## Implementation

`inspect()` in full:

```python
green = [q for q, c in rec["queries"].items() if c == "green"]
red = [q for q, c in rec["queries"].items() if c != "green"]
unrecorded_changed: list[tuple[str, str]] = []
false_green: list[str] = []
for q in green:
    recs = set(rec["recorded"].get(q, []))
    missing = [d for d in rec["changed"] if d not in recs]
    if missing:
        false_green.append(q)
        for d in missing:
            unrecorded_changed.append((q, d))
```

`parse_truth()` accepts `green`/`true`/`yes`/`1`/`recorded`/`changed` and is never called. Color is `parts[1].lower() == "green"`. Everything else is `red`, including `true` and `maybe`.

### 1. Recorded dep that also changed is not false green

Harvest primitive: unrecorded changed dep. Invalidation primitive: recorded changed dep, query still green. This CLI implements only the first.

Green query that **did** record `type_of(Error)`, which is also `changed`:

```bash
printf 'query\ttypeck_of(S::poll)\tgreen\ndep\ttypeck_of(S::poll)\ttype_of(Error)\nchanged\ttype_of(Error)\n' | python3 "$CLI" -
echo rc=$?
```

```text
green	typeck_of(S::poll)
red	-
changed	type_of(Error)
false_green	-
unrecorded_changed	-
rc=0
```

Same shape as `unseen-recorded.rec` (plus a red `type_of(Error)` query row): rc=0. In a real dep graph a recorded dep that went red must redden the parent. The CLI cannot name that. It is “not this bug”, printed as agreement.

Recorded `type_of(Error)` **and** unrecorded `adt_def`:

```text
changed	type_of(Error)	adt_def
false_green	typeck_of(S::poll)
unrecorded_changed	typeck_of(S::poll)	adt_def
rc=1
```

The recorded-changed identity is dropped from the pair list. Only the unrecorded remainder is the object. Red query that recorded the changed dep (`agree.rec`) is also rc=0 — correct for *this* primitive, and indistinguishable from the green-recorded-changed hole except for the `green`/`red` rows.

### 2. Green with no changed list is agreement; red is not changed

```bash
printf 'query\ttypeck_of(S::poll)\tgreen\ndep\ttypeck_of(S::poll)\ttrait_def\n' | python3 "$CLI" -
printf 'query\ttypeck_of(S::poll)\tgreen\n' | python3 "$CLI" -
printf 'query\ttypeck_of(poll)\tgreen\nquery\ttype_of(Error)\tred\ndep\ttypeck_of(poll)\ttrait_def\n' | python3 "$CLI" -
```

All three:

```text
false_green	-
unrecorded_changed	-
changed	-
rc=0
```

The third rec has the harvest ingredients as **colors** (`poll` green, `Error` red) and no `changed` row. Nothing fires. `changed` is not derived from red queries. A forgotten `changed` line is a clean session.

`changed` with a trailing tab and no name (`changed\t` / `changed` alone): `expected key<TAB>value` rc=1. There is no legal empty changed list except omitting the field, which is the silent path above.

### 3. Multiple greens: every green must record every changed identity

```bash
printf 'query\ttypeck_of(S::poll)\tgreen\nquery\ttypeck_of(unrelated)\tgreen\ndep\ttypeck_of(S::poll)\ttrait_def\nchanged\ttype_of(Error)\n' | python3 "$CLI" -
echo rc=$?
```

```text
green	typeck_of(S::poll)	typeck_of(unrelated)
red	-
changed	type_of(Error)
false_green	typeck_of(S::poll)	typeck_of(unrelated)
unrecorded_changed	typeck_of(S::poll)	type_of(Error)	typeck_of(unrelated)	type_of(Error)
rc=1
```

`typeck_of(unrelated)` never claimed to depend on `Error`. It is `false_green` because it did not list a global changed identity as a dep. There is no expected-dep / “should-have-read” oracle. `changed` is treated as a dep that **every** green must have recorded.

Two greens, two changed names, no deps: `false_green	a	b` and `unrecorded_changed	a	X	a	Y	b	X	b	Y` (eight fields, four pairs). `a` recorded `X` but not `Y`; `b` recorded nothing: `unrecorded_changed	a	Y	b	X	b	Y`. The pair list is a flattened even/odd stream. `cut -f2` returns the first query name, not an edge.

When the second green **did** record `type_of(Error)`, only poll is `false_green`. The per-query set difference is real. It still cannot tell “unrelated” from “false green”.

2000 greens and one `changed	D`: all 2000 are `false_green`. Owned 075 works because the rec contains one green.

### 4. Node names with arrows; flatten vs glue

Worktree (not the attack target; the encoding the archive just left):

```bash
python3 "$WT" "$FIX/075-poll.rec"
# unrecorded_changed	typeck_of(S::poll)->type_of(Error)

printf 'query\ta->b\tgreen\ndep\ta->b\tc->d\nchanged\te->f\n' | python3 "$WT" -
# unrecorded_changed	a->b->e->f
```

`q->d` concatenated onto a name that already contains `->` is not round-trippable. A query whose name *is* the edge string `typeck_of(S::poll)->type_of(Error)` prints `…->type_of(Error)->trait_def`.

Archive flatten on the same arrow names:

```text
green	a->b
changed	e->f
false_green	a->b
unrecorded_changed	a->b	e->f
rc=1
```

Opaque names survive as fields. The pair is still not marked as an edge. `unrecorded_changed	a->b	e->f` is the same shape as two names. A query named `typeck_of(S::poll)->type_of(Error)` is one identity, not an edge:

```text
green	typeck_of(S::poll)->type_of(Error)
unrecorded_changed	typeck_of(S::poll)->type_of(Error)	trait_def
```

A rustc-looking dump is not an input:

```bash
printf 'typeck_of(S::poll) -> type_of(Error)\n' | python3 "$CLI" -
# greendep: <stdin>:1: expected key<TAB>value
# rc=1

printf 'query\tq\tgreen\ndep\tq->d\nchanged\td\n' | python3 "$CLI" -
# greendep: <stdin>:2: dep needs query and dep name
```

`demo.sh` already says “two dumps still leave the unrecorded edge as a hand join”, then feeds a handwritten `.rec`. The CLI will not parse an arrow dump. The flatten closed worktree glue and did not create an edge type.

### 5. THIN_WRAPPER of set difference

Host replica of parse+inspect+format is byte-identical to the CLI (`wrapper == cli: True`, rc match) on `075-poll.rec`, `075-green.rec`, `agree.rec`, `unseen-recorded.rec`, `unseen-const.rec`, and on the unrelated / recorded-changed / no-changed / arrows / multi-green recs.

False-green names are exactly:

```python
[q for q in green if set(changed) - set(recorded.get(q, []))]
```

On the unrelated-green rec that list is `['typeck_of(S::poll)', 'typeck_of(unrelated)']`, same as `false_green`.

Nearest ordinary workflow on owned 075-poll (no CLI): recorded `{adt_def, trait_def}`, changed `{type_of(Error)}`, difference `{type_of(Error)}`. awk of the same rule:

```text
# 075-poll
typeck_of(S::poll)	type_of(Error)
# 075-green
typeck_of(poll)	type_of(Error)
# unseen-recorded
(empty)
# agree (no green)
(empty)
```

Same miss the CLI names. The TSV join (`false_green`, flattened `unrecorded_changed`, rc=1) is formatting around that membership. With one green, `comm` of the two lists is the product. With several greens, it is that `comm` per query against a **global** changed set — still not “whose result depended”.

REALITY.md already names nearest as “print two dep lists / visitid”. Two dumps still leave the unrecorded edge as a hand join; this CLI is that join **when the caller already labeled green/red, already listed recorded deps, and already listed changed identities**. `demo.sh` writes those facts into `.rec` files.

### 6. Stdin works; `-` is stdin, not a file

`-`, default argv (no record), `/dev/stdin`, process substitution, FIFO: owned 075-poll, rc=1, same TSV. Empty stdin / `/dev/null`: `no query rows` rc=1.

```bash
python3 "$CLI" - < "$FIX/075-poll.rec"   # rc=1, TSV
: | python3 "$CLI" -                     # greendep: <stdin>: no query rows
```

A file named `-` in cwd is **not** read when argv is `-` (stdin empty → `no query rows`). An explicit path to that file works. `-` is the stdin token, documented by argparse default.

Stdin is not the hole. The hole is that the pipe still has to carry a handwritten three-table rec.

### 7. Sentinel `-`; dead `parse_truth`; empty tabs slide; last-wins

Empty lists print `-`. Query named `-`, missing `D`:

```text
green	-
red	-
changed	D
false_green	-
unrecorded_changed	-	D
rc=1
```

Query named `-`, recorded `D`:

```text
green	-
false_green	-
unrecorded_changed	-
rc=0
```

`grep '^false_green	-$'` matches both, and also “only a red query, no green” (`green	-` / `false_green	-` / rc=0). `false_green_n` does not exist. rc distinguishes the miss of `-` from empty; a consumer of the cell does not.

`parse_truth` is defined and never called. Host colors against `changed	D`:

| color | green row | treated as | rc |
| --- | --- | --- | --- |
| `green` / `GREEN` / `Green` | `q` | green | 1 |
| `green ` (end of line) | `q` | green (`raw.strip`) | 1 |
| ` green ` (internal field) | `-` | red | 0 |
| `true` / `yes` / `1` / `recorded` / `changed` | `-` | red | 0 |
| `red` / `false` / `maybe` | `-` | red | 0 |

`true` is a parse_truth-green that inspect prints as red. Extra query field (`query	q	green	ignored`) is dropped; still green. Empty tab between name and color (`query	q		green`) slides; still green. Leading/trailing space in the **name** is kept (` q` and `q ` are identities). Duplicate `query` last-wins (green then red → not false; red then green → false). Duplicate `changed	D	D` with no recorded dep: `unrecorded_changed	q	D	q	D` (pair repeated). Duplicate recorded dep uniqued by `set`.

UTF-8 BOM: `unknown field '\ufeffquery'` rc=1. JSON object: `expected key<TAB>value`. `#comment` and blank lines skipped (`#changed	D` drops the change, then silent agreement if nothing else changed).

### 8. Parse edges (non-fatal except where noted)

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `No such file or directory` |
| directory as record | 1 | `Is a directory` |
| empty file / `/dev/null` / empty stdin | 1 | `no query rows` |
| invalid UTF-8 / binary | 1 | `'utf-8' codec can't decode` |
| UTF-8 BOM | 1 | `unknown field '\ufeffquery'` |
| two positional args | 2 | argparse |
| JSON / rustc `q -> d` dump | 1 | `expected key<TAB>value` |
| `-` as RECORD | 1 if stdin empty; 1+TSV if piped | stdin, not a file named `-` |
| `/dev/stdin`, FIFO, proc subst, symlink | 1 | owned miss, works |
| comments / blank lines / CRLF | 0 or 1 | skipped; color of remaining rows |
| 2000 greens / 200k name | 1 | no cap |
| query named `-` | 1 or 0 | collides with empty sentinel |

These do not save the set-difference, unrelated-green, or recorded-changed holes.

Owned events already contain the miss:

```text
query	typeck_of(S::poll)	green
dep	typeck_of(S::poll)	trait_def
dep	typeck_of(S::poll)	adt_def
changed	type_of(Error)
```

`demo.sh` prints two query names as the nearest operation, then feeds this table (green fixture) and the recorded-dep negative. The CLI will not parse a dump, and will not guess that `typeck` should have read `type_of(Error)`. That is the advertised boundary. It means the `.rec` files are the answer’s ingredients, and the CLI is the join.

---

## Primitive

Reality-stripped operation: parse TSV of `query NAME COLOR`, `dep QUERY DEP`, `changed ID…`; for each `COLOR==green`, `missing = [d for d in changed if d not in set(recorded[q])]`; if missing, name that query `false_green` and emit `(q,d)` pairs; exit 1 iff that list is non-empty.

Nearest ordinary workflow: the awk/`comm` above, or print the green name and the changed name. Seeing `typeck_of(poll)` green and `type_of(Error)` changed still leaves “was that dep recorded?” as a hand join — but this CLI does not recover edges. `demo.sh` writes those facts into `.rec` files, including the missing `type_of(Error)` by omitting it from `dep` rows. Observable capability lost if greendep vanishes: the **named join** (`false_green` + `unrecorded_changed` + rc=1) as one TSV. That join is real when the caller already labeled the query green and already listed changed identities that were not deps. It is not a rustc incremental graph, not visitid, not two dumps.

That is why this is not KILL: the *question* (which green query failed to record a changed identity) is a debugging object `comm` of two unlabeled lists will not emit as one rc=1 row with the edge named. The current embodiment is a specimen-075 record formatter that marks every green whose recorded set does not cover a global `changed` list.

The ceiling is already written down, and it is too small for the claim:

- `false_green` = green with `set(changed) - set(recorded[q])` nonempty, including unrelated greens and a green listed in `changed` with no self-dep (`unrecorded_changed	q	q`)
- recorded-changed green is rc=0 (invalidation miss is invisible)
- omitted `changed` / green-only rec is rc=0; red query is not auto-changed
- `unrecorded_changed` is flattened pairs (archive) or `q->d` glue (worktree); names containing `->` are opaque identities, not edges
- `-` means both empty and the query/dep named `-`
- `parse_truth` is dead; only exact `green` (after whole-line strip + `.lower()`) is green; `true`/`1` are red
- empty tab fields slide; extra columns dropped; duplicate query last-wins
- the owned fixture’s own rustc sessions are not an input; `075-poll` vs `075-green` are two spellings of the same join
- a 12-line replica already computes `false_green`

Do not grow a rustc dump importer to escape this. Do not merge this join into visitid. Keep the false-green row.

---

## Mutation (what must change)

Keep the object: for a query/dep/color table, a green query whose changed dependency was never recorded is named, and rc≠0.

Do not keep a global set-difference that only replays specimen-075’s one green.

1. **Unrelated greens are not false.** `changed` is per-query (`changed	QUERY	DEP`) or an expected-read table is required. A second green that did not list `type_of(Error)` is not `false_green` unless something says it should have. If the mutation still marks every green that misses a global changed set, a later destroyer should KILL as THIN_WRAPPER.

2. **Incomplete record is an error, not agreement.** No `changed` row (or `changed` empty) with a green query is rc≠0 (`incomplete`, not `false_green -`). A `red` query is not silently ignored: either derive changed identities from red rows, or require `changed` and refuse red-without-changed. `changed<TAB>` is changed=∅, not `expected key<TAB>value`.

3. **Recorded-changed green is a different verdict.** Green + dep in `changed` ∩ recorded is `recorded_changed_green` / `invalidation_miss` (or a labeled `not-this-primitive`), never `false_green -` rc=0 with no other row. Do not rc=1 on that case as if it were unrecorded. Do not hide it behind the unrecorded remainder when both happen (`type_of(Error)` recorded, `adt_def` not: print both kinds).

4. **`unrecorded_changed` is pairs, not a name stream and not `->` glue.** One row per edge (`unrecorded_changed	q	d` repeated, or `q -> d` as a *documented* encoding that forbids `->` in names). Archive flatten and worktree `a->b->e->f` are both wrong. Query/dep names containing `->` are legal opaque ids or a refuse — not silent glue. A rustc `q -> d` dump stays a refuse unless ingest is a separate, tested parser; do not add rustc.

5. **Empty token is not a legal NAME.** `-` as query/dep/changed must error, or empty lists use a count-only row (`false_green_n	0` with no `false_green` cell). Delete `parse_truth` or use it: color vocabulary is declared; `true`/`1`/` green ` are errors, not red. Empty tab fields and extra columns are errors, not slides. Duplicate `query` is an error or a counted last-win event.

6. **Cap huge dumps; keep rc=1 on `false_green`.** 2000-green / 200k-name stdout is not a pipe. rc=1 on false green already holds; keep it. rc=0 only for a complete record with no unrecorded-changed green.

7. **Ingest a two-table log or refuse.** Either parse a caller-complete “green queries” list plus “changed identities” plus “recorded edges” that is not already the answer (and still not rustc), or drop the implication that the CLI named the unrecorded edge. `075-poll` vs `075-green` must be one identity or two documented spellings. Delete `075-hang.rec` or make it a hang.

8. **Do not thicken the wrapper into visitid or a rustc runner.** The load-bearing delta is the named unrecorded edge on a caller-complete table. A 12-line replica already computes `false_green`. Further novelty that is pointer-vs-value skip belongs in visitid; further novelty that is next-solver `read_index` belongs in the sealed packet, not here.

If a later mutation cannot do (1)+(2)+(3) and is still `set(changed) - set(recorded[q])` on caller-labeled greens, the object is still `comm` plus extra print, and a later destroyer should KILL.

---

MUTATE
