# DESTROYER pathnode

Date: 2026-09-02 13:30 JST

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathnode/pathnode`

sha256 `878b84db2a6e03b887893a523019faf6e78c8a30645a110fe54fc1a2490c86de` (6488 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-pathnode-pathnode/pathnode/pathnode` is byte-identical (HEAD `413939b45307a09a1c3644cc2a7ad1da60b052bc`). Tests 5/5 pass. `demo-1.log` / `demo-2.log` byte-identical.

Origin claim (`CANDIDATE.md`): same path can be two collection nodes; fixtures bound to the first miss on the second.

Happy path is real. Specimen-003 events: dir1 as n1 and n3, `same_node no`, `shared_fixture` bound to n1, lookup n3 missing. That is not enough. The implementation reprints caller-supplied `found|missing` bits and groups collect strings by path. A `found` lookup is never checked against `bound_to`. Two paths sharing one node id are invisible.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathnode/pathnode
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathnode/fixtures
```

No pytest. No merge onto `main`. This object is path-vs-node identity plus a fixture miss, not a Directory node implementation.

---

## What still works

Owned 003 events, unseen same-node twice, stdin, `/dev/stdin`, FIFO, process substitution, symlink, filename with a space.

```bash
python3 "$CLI" "$FIX/003-collect.rec"
```

```text
paths	dir1	dir2	dir1
nodes	n1	n2	n3
dup_path	dir1	nodes	n1	n3	same_node	no
miss	shared_fixture	lookup	n3	bound_to	n1	found	no
rc=0
```

Same path twice as the same node → `same_node yes`. Three collects of dir1 as n1/n2/n3 lists all three nodes, `same_node no`. Spaces in path (`my dir`) and `テスト` survive tab fields. Empty / newline-in-path / unknown field / incomplete lookup / missing collect: rc=1. UTF-8 BOM is `unknown field '\ufeffcollect'` rc=1. Invalid UTF-8 is caught. `YES`/`true` count as found; `FALSE`/`miss` count as missing; `maybe` is a parse error. CRLF works.

That is the whole useful delta. Attacks below break the bind-check claim around it, or show the primitive cannot tell a fixture miss from a caller label.

---

## Implementation

### 1. `found` is trusted; bind is not checked

`inspect` skips every lookup with `event.found`. Register rows fill `bound_to` only for lookups the caller already marked missing.

**Found lookup, never registered:**

```bash
printf 'collect\td\tn1\nlookup\tfx\tn1\tfound\n' | python3 "$CLI"
```

```text
dup_path	none
miss	none
rc=0
```

No fixture was bound to n1. The report is clean.

**Found lookup on the later node, registered only on the first** (the harvest shape, with the found bit flipped):

```bash
printf 'collect\td\tn1\ncollect\td\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tfound\n' | python3 "$CLI"
```

```text
dup_path	d	nodes	n1	n3	same_node	no
miss	none
rc=0
```

dir1 is two nodes. The fixture is bound to n1. Lookup is n3. The CLI prints `miss none` because the caller wrote `found`. Owned 003 works only because the record already says `lookup shared_fixture n3 missing`. The `lookup shared_fixture n1 found` row is ignored entirely.

**Missing lookup on the node that registered the fixture** (caller lie):

```bash
printf 'collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tmissing\n' | python3 "$CLI"
```

```text
miss	fx	lookup	n1	bound_to	n1	found	no
rc=0
```

`bound_to` is n1, lookup is n1, `found no`. The tool reprints the lie. CANDIDATE.md: “which fixture definition is bound to which node.” The CLI does not compute that against lookups. It formats the caller’s found bit.

### 2. Two paths sharing one node id are invisible

```bash
printf 'collect\ta\tn1\ncollect\tb\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tfound\n' | python3 "$CLI"
```

```text
paths	a	b
nodes	n1	n1
dup_path	none
miss	none
rc=0
```

`by_path` only reports paths with two collect events. Node identity across paths is not a row. The harvest was “same path, two nodes.” The inverse (same node, two paths) is how a Directory object would leak the other way. `nodes n1 n1` is visible if a human reads the dump; `dup_path none` is what a pipe greps.

### 3. Path identity is the collect string, not a path

`dir1` vs `./dir1`:

```bash
printf 'collect\tdir1\tn1\ncollect\t./dir1\tn3\nregister\tfx\tn1\nlookup\tfx\tn3\tmissing\n' | python3 "$CLI"
```

```text
paths	dir1	./dir1
nodes	n1	n3
dup_path	none
miss	fx	lookup	n3	bound_to	n1	found	no
```

The miss row fires (caller labeled missing). The identity row does not. `dir1` vs `dir1/`: `dup_path none`. Leading space (` dir1` vs `dir1`): `dup_path none`. `n1` vs `N1`: `same_node no` (string inequality). NUL in a path (`d\x00x` vs `d`): two paths, `dup_path none`.

Path equality is the wrong object for fixtures (CANDIDATE). This CLI’s path equality is also the wrong object for “the same directory.”

### 4. Empty tab fields shift columns; extra fields are dropped

`parts = [p for p in rest.split("\t") if p != ""]`. Empty node then extra:

```bash
printf 'collect\tdir1\t\tn99\n' | python3 "$CLI"
```

```text
paths	dir1
nodes	n99
rc=0
```

n99 is the node. The empty field vanished. Double empty (`dir1 <empty> <empty> n99`) is the same. Extra collect field (`collect dir1 n1 extra`) is ignored; node stays n1. Extra lookup field (`missing extra`) is ignored; still a miss.

Newline in a path is a parse error (line-oriented), not an escaped field:

```text
pathnode: .../nlpath.rec:1: collect needs path, node
rc=1
```

`collect dir<newline>1 n1` splits into a short collect plus `1 n1`.

### 5. Ghost binds and ghost lookups are formatted as misses

Register on a node that was never collected:

```bash
printf 'collect\td\tn1\nregister\tfx\tn99\nlookup\tfx\tn1\tmissing\n' | python3 "$CLI"
```

```text
miss	fx	lookup	n1	bound_to	n99	found	no
```

Lookup on a node that was never collected, never registered:

```text
miss	fx	lookup	n3	bound_to	none	found	no
```

No register at all, lookup missing: `bound_to none`. No lookup at all, fixture registered: `miss none`. The bind map is only consulted for caller-missing rows. Uncollected nodes are not an error.

Duplicate register of `fx` on n1 then n3, lookup n3 missing: `bound_to n1 n3`. The lookup node is in `bound_to` and still `found no`. Duplicate register of the same node is uniqued.

Two fixtures, crossed misses: `fx` miss on n3 bound_to n1, `other` miss on n1 bound_to n3. That part of the printer holds — once the caller has already labeled both missing.

### 6. `none` collides with the empty sentinel; TSV is not a predicate

Fixture named `none`, lookup missing, never registered:

```bash
printf 'collect\td\tn1\nlookup\tnone\tn1\tmissing\n' | python3 "$CLI"
```

```text
miss	none	lookup	n1	bound_to	none	found	no
rc=0
```

No misses (`miss none`) vs a miss of fixture `none` (`miss none lookup ...`). A pipe that greps `^miss	none$` keeps the empty case and drops the named miss, or the reverse.

Path named `none`, two nodes:

```text
dup_path	none	nodes	n1	n2	same_node	no
miss	none
```

`dup_path	none` is both “no duplicate path” and “duplicate path whose name is none.”

All misses and all dups are rc=0, including the harvest miss. `pytest` collection that cannot find a fixture is not rc=0 of a green session. This CLI is rc=0 while printing `found no`. Fine as a printer; hostile as a pipe predicate.

200_000-character path twice as n1 and n3: rc=0 in 0.03s, stdout 600065 bytes, `dup_path` present. 2000 collects of dir1 as n0..n1999: one `dup_path` row with 2000 node columns (31835 bytes). `count` is computed and not printed. No cap.

### 7. Parse edges (non-fatal except where noted)

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `No such file or directory` |
| directory as record | 1 | `Is a directory` |
| empty file / `/dev/null` | 1 | `missing collect` |
| invalid UTF-8 | 1 | `'utf-8' codec can't decode` |
| UTF-8 BOM | 1 | `unknown field '\ufeffcollect'` |
| `#collect` only | 1 | `missing collect` (comment dropped) |
| two positional args | 2 | argparse |
| JSON object | 1 | `expected key<TAB>value` |
| `-` as RECORD | 1 | `No such file or directory: '-'` |
| `/dev/stdin`, FIFO, proc subst, symlink | 0 | works |
| comments / blank lines | 0 | skipped |
| CRLF | 0 | `splitlines` |
| NUL in path | 0 | two paths, `dup_path none` |
| 200k path / 2000 nodes | 0 | no cap |

These do not save the found-bit or shared-node holes.

Owned events already contain the miss:

```text
collect	dir1	n1
collect	dir2	n2
collect	dir1	n3
register	shared_fixture	n1
lookup	shared_fixture	n1	found
lookup	shared_fixture	n3	missing
```

`demo.sh` already prints `pytest dir1 dir2 dir1 --collect-only` as the nearest operation, then feeds this record. The CLI will not parse collect-only output, and will not guess node ids. That is the advertised boundary. It means the `.rec` files are the answer’s ingredients, and the CLI is the join.

---

## Primitive

Reality-stripped operation: parse TSV of `collect PATH NODE`, `register FIXTURE NODE`, `lookup FIXTURE NODE found|missing`; group collect nodes by path string; `same_node` iff unique node ids == 1; for lookups with `found=False`, print `bound_to` from register events.

Nearest ordinary workflow: print CLI args plus `--collect-only`. Seeing `dir1` twice still leaves “two node ids, fixture bound to the first” as a hand comparison — but this CLI does not collect. `demo.sh` writes those facts into `.rec` files, including `missing` on n3. Observable capability lost if pathnode vanishes: the **named join** (`dup_path` + `same_node` + `miss`/`bound_to`) as one TSV. That join is real when the caller already labeled the lookup missing and already named both node ids. It is not a pytest Directory implementation, not `--keep-duplicates` on files (research boundary, honored).

That is why this is not KILL: the *question* (same path, two collection objects, fixture bound to the first, lookup on the second missing) is a debugging object `pytest --collect-only` will not emit as one row. The current embodiment is a specimen-003 event formatter that trusts `found` and only reports path→many-nodes.

The ceiling is already written down, and it is too small for the claim:

- miss = caller wrote `missing`/`no`/`false`, including lies and unbound-found silenced
- `found` lookup whose fixture was never registered on that node is `miss none`
- two paths, one node id → `dup_path none`
- `dir1` vs `./dir1` vs `dir1/` are different paths
- empty tab fields shift the node id
- `none` means both empty and the path/fixture `none`
- miss is always rc=0
- the owned fixture’s own collect log is not an input

Do not grow a pytest importer to escape this. Do not merge this join into a file-identity tool. Keep the path-vs-node row.

---

## Mutation (what must change)

Keep the object: for collection events, the same path can be two collection nodes, and a fixture bound to the first is a miss on the second.

Do not keep a printer that only replays specimen-003’s `missing` label.

1. **Derive found from register, or refuse the found bit.** A `found` lookup whose fixture was never registered on that node is a miss (or `unbound`), not `miss none`. A `missing` lookup whose fixture *is* bound to that node is a contradiction (`labeled-missing-but-bound`) or is not a miss. If the mutation still prints `miss none` for unbound-found, a later destroyer should KILL.

2. **Report nodes that name more than one path** (shared node id), not only paths that name more than one node. `collect a n1` + `collect b n1` is `dup_node` / `shared_node`, not `dup_path none`.

3. **Path identity is declared.** `./dir1` vs `dir1` vs `dir1/` is one name after normalize, or two names with an explicit `path-alias` row — not a silent non-dup plus a miss. Leading/trailing field space is strip or error.

4. **Empty tab fields are errors, not slides.** `collect dir1 <empty> n99` is rc≠0, not node=n99. Extra columns are an error or a documented ignored tail. Newline in a path stays a parse error; say so.

5. **`none` is not a list value.** Empty dups/misses is a distinct token (`-`, `.`, or a count column). A path or fixture named `none` must not render as the empty sentinel. Repeatable node ids stay one field, or get one row per node (2000-node `dup_path` is not a pipe).

6. **Ghost nodes are visible.** Register or lookup of a node that was never collected is rc≠0 or a `ghost` row, not a formatted miss with `bound_to n99`.

7. **rc=1 on miss** (or `--check` as the default predicate). rc=0 only for `dup_path none` and no derived miss. Cap huge path/node dumps.

8. **Ingest collect output or refuse.** Either parse `pytest --collect-only` / node-id traces so `demo.sh` is not a handwritten `.rec` that already contains `n3 missing`, or drop the implication that the CLI named the miss. Still do not import pytest. Still do not invent `--trace-config`.

If the mutation cannot do (1)+(2)+(7), the object is still “caller already labeled missing” plus “path collected twice”, and a later destroyer should KILL.

---

MUTATE
