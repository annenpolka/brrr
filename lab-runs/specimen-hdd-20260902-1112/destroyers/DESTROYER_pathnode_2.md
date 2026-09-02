# DESTROYER pathnode 2

Date: 2026-09-02 16:20 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0388 (worker destroyer-pathnode-2, CLAIMED 15:40; previous worker produced no DESTROYER_pathnode_2.md)

Target (archive; mutate-pathnode already landed unbound/shared stickers):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathnode/pathnode`

sha256 `4ed03807e59654f8ef43f4f746a07f2bb29f1bbd9d2d2b0abf15ab45734b38ce` (7462 bytes, 243 lines). Changed from first destroyer `878b84db…` (6488 bytes). Worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-pathnode-pathnode/pathnode/pathnode` is byte-identical (`cmp` rc=0). HEAD `4ba750f Mutate pathnode: unbound found is a miss; shared node ids.` on `specimen-hdd/candidate-pathnode-pathnode`. Parent `main` is `432f954`; `git show HEAD:pathnode` fatal (not in that tree). Host Python 3.14.5. unittest 7/7 archive and worktree (`Ran 7 tests in 0.110s` / `0.114s` `OK`). `./demo.sh` ×2 live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log`. No pytest import. No merge onto `main`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-pytest003` / specimen-003): same path can be two collection nodes; a fixture bound to the first misses on the second. Kind: USEFUL_COMPOSITION. `demo.sh` still prints `pytest dir1 dir2 dir1 --collect-only` as the nearest operation, then feeds a handwritten `.rec` that already contains `lookup shared_fixture n3 missing`.

First destroyer (`DESTROYER_pathnode.md`) **MUTATE**. Required (1) derive found from register / refuse the found bit (unbound-found is a miss, not `miss none`); (2) report a node id that names more than one path (`shared_node` / `dup_node`); (7) `rc=1` on miss or `--check` as the default predicate. If the mutation cannot do (1)+(2)+(7), a later destroyer should KILL. Also KILL if the object is still “caller already labeled missing” plus “path collected twice” (THIN_WRAPPER of found sticker). First MUTATE is not protection.

Mutate job-0152 (`MUTATION.md`, not MUTATE.md; commit `4ba750f`) claimed: (1) unbound-found is `unbound yes`, not `miss none`; (2) `shared_node` when one node id names more than one path; (3) tests unbound-found and two-paths-one-node. Host-executed those claims. (1) and (2) landed as extra TSV columns/rows. (7) did not. Tests grew 5→7 and pass. That is not protection once leftover (7) and the found-sticker wrapper still hold. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathnode/pathnode
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-pathnode/fixtures
```

Host-executed against the archive. Worktree was not edited. Do not grow a pytest importer / `--trace-config` / Directory node to escape THIN_WRAPPER. Do not send collection-event theater back to R1. Do not merge onto `main`.

Scratch: `destroyers/_pathnode2_scratch/` (attack.py, replica.py, attack.log, demo-host-1/2.log, tests-*.log). Independent replica does not import pathnode.

---

## Honor-KILL checklist (leftover from DESTROYER_pathnode.md)

| leftover | host | still? |
| --- | --- | --- |
| (1) found lookup never registered is `miss none` | `collect d n1` + `lookup fx n1 found` → `miss fx lookup n1 bound_to none found yes unbound yes` rc=0 | **no** (sticker landed) |
| (2) two paths, one node id is `dup_path none` / no shared_node | `collect a n1` + `collect b n1` + bound found → `shared_node n1 paths a b`, `dup_path none` rc=0 | **no** (sticker landed) |
| (7) miss still always rc=0, no `--check` | owned 003 miss rc=0; unbound-found rc=0; `pathnode --check RECORD` argparse rc=2 `unrecognized arguments: --check`; help has only `-h` / RECORD | **yes** |
| still “caller labeled missing” + “path collected twice” | drop the n3 lookup from owned 003 → `dup_path dir1 … same_node no` and `miss none` rc=0; awk of `lookup … missing` already names the harvest miss | **yes** |

Mutate claimed (1)+(2)+tests. Host-verified. (7) was the predicate. Without it the object is still a printer of caller TSV.

---

## What still works

Owned 003, unseen same-node twice, stdin, FIFO, symlink, filename with a space, UTF-8 path, CRLF, comments. unittest 7/7. Demo ×2.

```bash
python3 "$CLI" "$FIX/003-collect.rec"; echo rc=$?
```

```text
paths	dir1	dir2	dir1
nodes	n1	n2	n3
dup_path	dir1	nodes	n1	n3	same_node	no
shared_node	none
miss	shared_fixture	lookup	n3	bound_to	n1	found	no	unbound	yes
rc=0
```

The mutation added `shared_node none` and `unbound yes` on the harvest miss. `found no` is still the caller token from `lookup shared_fixture n3 missing`. rc is still 0.

Unseen `pkg/tests` twice as `a`: `same_node yes`, `shared_node none`, `miss none`, rc=0. Single bound found: `dup_path none` / `shared_node none` / `miss none`, rc=0.

That is the whole useful delta after mutation. It is also grouping collect strings plus `node not in bound[fixture]` plus a reprint of the found bit.

Nearest ordinary workflow, host-executed on the owned record:

```text
awk -F'\t' '$1=="collect"{print $2,$3}' 003-collect.rec
# dir1 n1 / dir2 n2 / dir1 n3
awk -F'\t' '$1=="register"{print $2,"on",$3}' 003-collect.rec
# shared_fixture on n1
awk -F'\t' '$1=="lookup" && $4 ~ /missing|no|false/{print $2,$3}' 003-collect.rec
# shared_fixture n3
```

`demo.sh` already writes those facts into the `.rec`, including `missing` on n3, then asks the CLI to join them.

---

## Implementation

Load-bearing body (`inspect`):

```python
# dups: paths with len(collect nodes) >= 2; same_node iff unique ids == 1
# shared: nodes with unique collect paths >= 2
bound[fixture] = unique register nodes
for lookup:
    unbound = event.node not in bound.get(fixture, [])
    if event.found and not unbound:
        continue
    misses.append(..., found=event.found, unbound=unbound)
```

`inspect.co_names` is `('setdefault', 'path', 'append', 'node', 'items', 'len', 'unique', 'fixture', 'list', 'get', 'found')`. `main` always `return 0` after a successful parse. No `--check`. No path normalize. Empty tab fields are dropped (`parts = [p for p in rest.split("\t") if p != ""]`). No pytest, no Directory, no collect-only parser.

`miss` is `not (found and bound)`: caller `missing` **or** node not in the register list. `found` is still the lookup token (`found|yes|true` vs `missing|miss|no|false`). `unbound` is set membership. `shared_node` is the inverse of `dup_path`.

Independent reconstruction that does not import pathnode is **byte-identical** on 41/41 well-formed host cases (`stdout_eq=True`, `rc_eq=True`) and raises on 9/9 parse errors matching CLI rc≠0 (empty, JSON, incomplete collect/lookup, `maybe`, unknown field, no tab, comment-only, register-only).

---

## 1. (7) leftover: miss is still rc=0; `--check` does not exist

Owned harvest miss: rc=0. Unbound-found miss: rc=0. Caller-lie missing-but-bound: rc=0. Ghost lookup: rc=0. Fixture named `none`: rc=0.

```bash
python3 "$CLI" --check "$FIX/003-collect.rec"; echo rc=$?
```

```text
usage: pathnode [-h] [RECORD]
pathnode: error: unrecognized arguments: --check
rc=2
```

`--help` has only `-h` and RECORD. A pipe cannot treat `found no` as a failed session. pytest collection that cannot find a fixture is not rc=0 of a green session. First destroyer: “rc=1 on miss (or `--check` as the default predicate). If the mutation cannot do (1)+(2)+(7) … KILL.”

---

## 2. Harvest miss still requires the caller lookup row

Same three collects and the n1 register, **without** `lookup shared_fixture n3 missing`:

```bash
printf 'collect\tdir1\tn1\ncollect\tdir2\tn2\ncollect\tdir1\tn3\nregister\tshared_fixture\tn1\nlookup\tshared_fixture\tn1\tfound\n' | python3 "$CLI"; echo rc=$?
```

```text
paths	dir1	dir2	dir1
nodes	n1	n2	n3
dup_path	dir1	nodes	n1	n3	same_node	no
shared_node	none
miss	none
rc=0
```

dir1 is still two nodes. The fixture is still bound only to n1. There is no miss, because nobody wrote a lookup on n3. The mutation did not derive “fixture bound to first, later node of the same path is a miss.” It still formats lookup events the caller already typed.

Flipping the owned found bit (`lookup fx n3 found` after register on n1) now prints `miss … found yes unbound yes` instead of `miss none`. That is leftover (1) closed as a sticker: the found token is kept (`found yes`) and `unbound yes` is appended. It is not a derived found.

---

## 3. THIN_WRAPPER of the found sticker plus register membership

**Found + bound** (skip): `miss none`.

**Found + unbound** (new sticker): `found yes unbound yes`.

**Missing + bound** (caller lie; first destroyer asked for contradiction or not-a-miss):

```bash
printf 'collect\td\tn1\nregister\tfx\tn1\nlookup\tfx\tn1\tmissing\n' | python3 "$CLI"; echo rc=$?
```

```text
miss	fx	lookup	n1	bound_to	n1	found	no	unbound	no
rc=0
```

`bound_to` is n1, lookup is n1, still a miss. The found bit is still trusted when it says missing.

**Missing + unbound**: miss with `unbound yes` (harvest shape).

`YES`/`true`/`Found` count as found and skip when bound. `FALSE`/`miss`/`MISSING` count as missing and still miss when bound. `maybe` is rc=1. The token is the predicate.

Two paths, one node, lookup found and bound: `shared_node n1 paths a b` and `miss none`. Inverse grouping, not a new object.

---

## 4. Path identity is still the collect string

`dir1` vs `./dir1`:

```text
paths	dir1	./dir1
dup_path	none
shared_node	none
miss	fx	lookup	n3	bound_to	n1	found	no	unbound	yes
rc=0
```

The miss row fires (caller labeled missing). The identity row does not. `dir1` vs `dir1/`: `dup_path none`. Leading space (` dir1` vs `dir1`): `dup_path none`. `n1` vs `N1`: `same_node no`. NUL in a path (`d\x00x` vs `d`): two paths, `dup_path none`. First destroyer mutation (3) did not land.

---

## 5. Empty tab fields still slide; extra fields still drop; ghosts still format

`collect dir1 <empty> n99`: `nodes n99` rc=0, not an error. Double empty: same. Extra collect field ignored; node stays n1. Extra lookup field ignored; still a miss.

Register on n99 never collected, lookup n1 missing: `bound_to n99 unbound yes` rc=0. Lookup n3 never collected never registered: `bound_to none` rc=0. Register without lookup: `miss none`. Duplicate register n1 then n3, lookup n3 missing: `bound_to n1 n3 unbound no found no` — the lookup node is in `bound_to` and still a miss.

Newline in a path is still a parse error (`collect needs path, node` rc=1). UTF-8 BOM is `unknown field '\ufeffcollect'` rc=1. `-` as RECORD is `No such file or directory: '-'` rc=1.

---

## 6. `none` still collides; TSV is still not a predicate

Fixture named `none`, lookup missing, never registered:

```text
miss	none	lookup	n1	bound_to	none	found	no	unbound	yes
rc=0
```

No misses (`miss none`) vs a miss of fixture `none` (`miss none lookup …`). Path named `none`, two nodes: `dup_path none nodes n1 n2 same_node no` plus `miss none`. `dup_path none` is both “no duplicate path” and “duplicate path whose name is none.” First destroyer mutation (5) did not land.

---

## Primitive

Reality-stripped operation: parse TSV of `collect PATH NODE`, `register FIXTURE NODE`, `lookup FIXTURE NODE found|missing`; group collect nodes by path string and collect paths by node string; skip lookups where `found` and `node in bound[fixture]`; print the rest with `unbound = node not in bound[fixture]`.

Nearest ordinary workflow: print CLI args plus `--collect-only`, then hand-compare. After mutate, also `node not in register-list` as a column. Observable capability lost if pathnode vanishes: the **named join** (`dup_path` + `same_node` + `shared_node` + `miss`/`bound_to`/`unbound`) as one TSV. That join is real when the caller already labeled the lookup and already named both node ids. It is not a pytest Directory implementation, not `--keep-duplicates` on files (research boundary, honored), not a predicate (`rc=0` on every well-formed miss).

That is why this is KILL, not MUTATE. The *question* (same path, two collection objects, fixture bound to the first, lookup on the second missing) is still a debugging object `pytest --collect-only` will not emit as one row. This embodiment asks it of a `.rec` the operator already filled, then reprints `found` and adds `unbound`/`shared_node` stickers. Adding a live collect parser / pytest import / `--trace-config` is the leftover the first destroyer forbade. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First MUTATE is not protection.

Hardcoded ceiling (still):

- miss = caller wrote `missing`/`no`/`false` **or** found lookup whose node is not in `bound[fixture]`
- `found` lookup that *is* bound is skipped (`miss none`)
- `missing` lookup that *is* bound is still a miss (`found no unbound no`)
- two paths, one node id → `shared_node` row; `dup_path none`
- `dir1` vs `./dir1` vs `dir1/` are different paths
- empty tab fields shift the node id
- `none` means both empty and the path/fixture `none`
- miss is always rc=0; no `--check`
- the owned fixture’s own collect log is not an input

Do not grow a pytest importer. Do not merge this join into a file-identity tool. Do not mutate again. Honor KILL. Dreamer ancestry is not protection.

Archive stays under `lineages/candidate-pathnode/`.

KILL
