# DESTROYER visitid 3

Date: 2026-09-02 15:37 JST (attacks) / 15:38 JST (record)
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0365 worker=destroyer-visitid-3
Target: `lineages/candidate-visitid/visitid` after mutate-3
(`MUTATE.md` third cut, 41 tests, sha256
`58e6d259f30df0e20b4280a4ba1a2e10811495399e6d96f88bd2533488beedc8`, 15056 bytes)

Worktree copy at
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-visitid-visitid/visitid/visitid`
is **byte-identical** (`cmp` rc=0). Worktree HEAD `3486a7d` records mutate
`3486a7d Mutate visitid: slot labels; value_key name; refuse flake-input column.`
Archive `HEAD.txt` is `3486a7d73a294e48ccfa5197a11b91bfe07f665c`. Parent remains
`main` `432f954`; `visitid` is not in that tree (0 product paths). nix is **not**
on PATH. No merge onto `main`. Do not merge with `addrid`. Host Python 3.14.5.

Prior destroyers: `DESTROYER_visitid.md` KEEP (value-key declaration +
address-reuse `never_fetched` + rc=1), `DESTROYER_visitid_2.md` MUTATE
(synonym done counts / unique cap / `-` NAME / cwd-homonym / hex 1000).
First KEEP/MUTATE is not protection. Honor KILL if still two set walks on a
caller-complete list / synonym counts / cwd-stat live.

Host `python3 tests/test_visitid.py` against that cut: 41/41 OK, 1.075s, rc=0
(archive and worktree). `demo-1.log` / `demo-2.log` byte-identical. Happy path
is real. That is not enough.

This candidate is still a **THIN_WRAPPER of two set walks** (`set(addr)` and
`set(name)`) plus first-occupant mismatch on a caller-complete `(NAME, ADDR)`
list. `inspect()` is `walk_pointer` + `walk_value` + unique counts.
`never_fetched` is `[skip.name for skip in pointer_skipped if skip.kind ==
"address-reuse"]`. An independent replica of parse+walks+cap+rc (does not
import visitid) is **byte-identical** to the CLI on 39/39 host cases
(`stdout_eq=True`, `rc_eq=True`). Occupancy membership without format MATCH
4/4 fixtures including rc. awk of the same rule names `home-manager` on both
owned reuse files. Mutate-3 could not add a time axis without becoming adrid,
and did not remove cwd-`stat` live. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-visitid/visitid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-visitid/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-visitid-visitid/visitid/visitid
```

No pytest. No nix. Do not grow insert/worker/fetched. Do not send THIN_WRAPPER
back to R1. Do not merge into adrid.

---

## What still works (mutate-3 claims, verified)

Owned 070: `home-manager` reuses `root`'s `0x7ffe1000`, `skip_kind	address-reuse`,
`never_fetched	home-manager`, `value_key	name`, no `pointer_done` / `value_done`
/ `inputs`, rc=1. Same NAME later reuses a *different* node's address
(`reuse-same-name.rec`): `never_fetched	home-manager`, rc=1. Unseen unique:
`never_fetched	-`, rc=0. Same-value-only: `skip_kind	same-value`, rc=0.
`--live --retain root nixpkgs home-manager` from a cwd that has `root/`
(directory): rc=0, `pointer_key	slot`, `addrs	slot0	slot1	slot2`, no `0x`.
`--live` drop: `unique_addrs	2`, `never_fetched	home-manager`,
`allocator_reuse	ping-pong	unique_addrs	2	of	3`, rc=1, slots not heap
ids. `-` as NAME is an error. Third field is `extra field`. `1000` and
`0x1000` collapse. `1e2` is `bad address`. Unique-then-cap: 32× `dup` then
`later0`…`later7` prints `never_fetched	dup	later0`…`later7` with
`never_fetched_n	40`. Concatenating adrid `insert`/`worker` three-column
rows is `extra field`. Worktree 070 stdout matches archive.

```bash
python3 "$CLI" "$FIX/070-reuse.rec"; echo rc=$?
printf 'root\t0x1000\nhome-manager\t0x2000\nhome-manager\t0x1000\n' | python3 "$CLI"; echo rc=$?
python3 "$CLI" "$FIX/unseen-same-value.rec"; echo rc=$?
```

```text
value_key	name
skip_kind	address-reuse
never_fetched	home-manager
rc=1
```

```text
unique_names	2
unique_addrs	2
skip_kind	address-reuse	same-value
never_fetched	home-manager
rc=1
```

```text
skip_kind	same-value
never_fetched	-
rc=0
```

That is the whole useful delta after mutate-3. It is also `awk` of occupancy
on two columns the caller already bound.

---

## Implementation

Load-bearing walks (archive, mutate-3):

```python
# walk_pointer
if event.addr in done:
    kind = "address-reuse" if first_name != event.name else "same-pointer"
    skipped.append(...)
    continue
done.add(event.addr)

# walk_value
if event.name in done:
    skipped.append(... kind="same-value")
    continue
done.add(event.name)

# never_fetched
return [skip.name for skip in pointer_skipped if skip.kind == "address-reuse"]
```

`format_report` always writes `value_key	name`. `--live` still does
`Path(name).is_file()` against **cwd**, then `id(Node(name))` relabeled
`slot0`...

### 1. THIN_WRAPPER of two set walks on a caller-complete list

Host replica (`destroyers/_visitid_scratch/attack.py`, does not import
visitid): parse `NAME ADDR`; pointer walk = `set(addr)` + first occupant;
value walk = `set(name)`; `never_fetched` = address-reuse names; unique-then
`LIST_CAP=32`; rc=1 iff that list is non-empty. Byte-identical stdout and rc
on every well-formed case and every parse-error case run:

```text
070-reuse / reuse-same-name / unseen-unique / unseen-same-value
stdin-070-shape / hex-collapse / ten-0x10 / space / none-skip / none-visit
visit-name / same-value-3 / lock-path / same-pointer / distinct-keys / 7ffe
zero / neg / cap-40 / cap-unique / 232-170
empty-tab / extra-field / padded / dash-name / bom / scientific / bad-addr
missing / crlf / comment-drop / unicode / fifo-shape / later-token
mixed-kinds / empty-stdin / only-spaces / visit-tag / addrid-rows
```

39/39. No mismatches.

Occupancy membership without format (no cap, no TSV printer) MATCH 4/4
fixtures including rc:

```text
MATCH 070-reuse.rec         nf=['home-manager'] rc=1
MATCH reuse-same-name.rec   nf=['home-manager'] rc=1
MATCH unseen-unique.rec     nf=[] rc=0
MATCH unseen-same-value.rec nf=[] rc=0
```

awk of the same occupancy rule on the fixture columns:

```text
# 070-reuse.rec        home-manager
# reuse-same-name.rec  home-manager
```

Same miss the CLI names. The TSV join (`skip_kind`, `reuse first/later`,
`never_fetched`, rc=1) is formatting around that membership.

Owned events already contain the miss:

```text
visit	root	0x7ffe1000
visit	nixpkgs	0x7ffe2000
visit	flake-utils	0x7ffe3000
visit	home-manager	0x7ffe1000
```

`demo.sh` prints `id(object())==id(object())`, then feeds this table. The CLI
will not parse an insert/worker split, and will not recover addresses from
nix. Mutate-3 leftover: “The walks are still `set(addr)` and `set(name)` plus
the named reuse join.” Host-executed: that leftover **is** the object.

A sequential walk of a caller-complete list cannot let the done-set shrink
after a temporary dies. `~150` fetching activities cannot appear.

### 2. Synonym counts: `pointer_done` deleted; `unique_addrs` ≡ `len(pointer_visited)`

Mutate-3 claimed `pointer_done` / `value_done` stay deleted. Host: those
strings are absent from source, from 070 stdout, and from `demo-1.log`.
Closed as printed fields.

They remain as the two set sizes after one walk. 50 random (name, addr)
tables: `unique_addrs == len(pointer_visited)` and
`unique_names == len(value_visited)` in 50/50. Owned 070: 3=3 and 4=4.
232 unique node keys, 170 unique addrs (later 62 reuse earlier addrs):

```text
unique_names	232
unique_addrs	170
pointer_visited_n	170
names_n	232
addrs_n	170
skip_kind	address-reuse
never_fetched_n	62
never_fetched	extra0 … extra31
rc=1
```

`never_fetched_n` is `232-170=62`, a set-size difference on one sequential
walk when every extra NAME is unique. Two numbers, not three. `~150` is not
printed (mutate-3 did not fake origin counts). Naming the pointer set size
`unique_addrs` instead of `pointer_done` does not create a time axis.

### 3. cwd-stat live is still live

Mutation 2/3: `Path(name).is_file()` refuses `--live FILE`; a directory
homonym is a NAME. Host:

```bash
# cwd has directory root/
python3 "$CLI" --live --retain root nixpkgs home-manager
# rc=0, addrs slot0 slot1 slot2

# cwd has regular file root
python3 "$CLI" --live --retain root nixpkgs home-manager
# visitid: --live 'root': existing file is not a live NAME
# rc=1, empty stdout
```

`--live visitid` from the candidate dir (the CLI is a file named `visitid`):
same file-homonym error. `--live README.md` from the repo root: same.
`--live FILE` when FILE exists: rc=1, not a live NAME.

The advertised three-name demo is cwd-dependent on whether the caller spelled
a path that `stat`s as a regular file. Directory `root/` at repo root is the
mutate-3 demo; a file named `root` is not. Ids remain allocator-dependent;
printed `slot0`/`slot1` are this-run occupancy labels, not records. A pipe
that stores `--live` output cannot join to a later run as heap identity.
Relabeling `hex(id)` to `slotN` does not remove the cwd `stat`.

232 live names drop: `unique_addrs	2`, `never_fetched_n	230`, list capped
at 32, `allocator_reuse	ping-pong	unique_addrs	2	of	232`. Still two
CPython slots, not a per-run missing set. 6/6 drop processes: `addrs	slot0
slot1`, rc=1, no `0x` in stdout.

### 4. same-value-only is still the lock-input silent path

232 visit attempts keyed by 170 repeating input names at 232 distinct addrs
(graph sharing, no pointer reuse):

```text
unique_names	170
unique_addrs	232
skip_kind	same-value
never_fetched	-
rc=0
```

`value_skipped` is capped. Exit 0. The extra 62 lock nodes are a value skip,
not `never_fetched`. Specimen-070 is 232 lock nodes / 170 unique inputs /
~150 fetches / exit 0. Feeding that shape as NAME=input name is silent.
Address-reuse rc=1 only fires if the caller already put *distinct* node keys
in NAME, or a later same-name event reused a *different* first occupant's
address.

Mutate-3 refuses a third field (`this CLI does not accept flake input names`)
instead of walking INPUT. That is a parse error, not lock-node identity.
`root/nixpkgs` vs `nixpkgs` stay two keys.

### 5. Cap still hides names the object exists to print

Mutate-3 unique-then-cap: 32× `dup` then `later0`…`later7` shows `dup` and
the eight laters (`never_fetched_n	40`, list length 9). Held.

40 distinct reuse names (`later0`…`later39` onto 8 first occupants):

```text
never_fetched_n	40
never_fetched	later0 … later31
rc=1
```

`later32`…`later39` are **not** in stdout. Count says 40. The field whose job
is to *name* skipped distinct nodes drops eight of them. 232/170 above: 62
skips, 32 listed, `extra32`…`extra61` hidden. Raising `LIST_CAP` would not
beat two set walks.

### 6. Did not become adrid (claimed — verified)

Three-column `insert 0xa flake-utils` / `worker 0xa naersk`: `extra field`,
rc=1, empty stdout. Two-column `insert 0xa` / `worker 0xa` parses as nodes
named `insert` and `worker`; `never_fetched	worker`, rc=1. That is occupancy
on a caller list, not insert-vs-worker. No `fetched` column. Stop. Do not
print 232/170/~150 as if they were measured here.

### 7. Printer claims that do not recover a primitive

Verified and closed as record fields:

- `-` as NAME: `empty-list token`, rc=1, empty stdout (`--live -` too)
- BOM: error, not a name prefix
- empty tab / extra field / padded name: rc=1, no TSV
- `none` is a name (`never_fetched	none` vs `never_fetched	-`)
- `value_key	name` (hardcoded string matching `walk_value`'s key)
- `--live` prints `slot0`.. not process-local `0x`
- all-digit ADDR is hex (`1000` ≡ `0x1000`; `10` ≡ `0x10`)
- `1e2` scientific `bad address`
- stdin, FIFO (writer after reader), missing file rc=1, `-` as RECORD is
  missing-file rc=1 (no stdin)

Those are a stricter printer of the occupancy join. They are not a time axis,
not a lock graph, not a live mode that does not `stat` cwd.

---

## Primitive

Reality-stripped operation: sequential `set` of integer addresses (with first
occupant) and `set` of NAME strings on a caller-complete visit list; classify
pointer skips as `address-reuse` vs `same-pointer`; print address-reuse names
as `never_fetched`; exit 1 if that list is non-empty. `--live` is
`id(Node(name))` relabeled `slotN` with a cwd `is_file()` gate.

Nearest ordinary workflow: the replica / awk above, or print `id(obj)` / `%p`
and compare. On unique-NAME owned 070 that pair is still “home-manager skipped
because 0x7ffe1000 was root.” Mutation made `never_fetched` name that skip
even when the later NAME already appeared. That is a real join **when the
caller already listed every attempt with a node key in NAME**.

Observable capability lost if visitid vanishes: **none** beyond a named
sticker. The caller already bound NAME and ADDR. awk of occupancy already
prints `home-manager`. The TSV labels (`skip_kind`, `reuse first/later`,
`never_fetched`, rc) are formatting around that membership.

That is why this is KILL, not MUTATE. The *question* (which later node was
skipped because a done-set still held a temporary's address) is a real
debugging object. This embodiment does not ask it of a nix graph or of
insert-then-worker. It asks `set(addr)` vs `set(name)` on a caller-complete
table. Adding insert/worker/fetched would be implementing adrid — forbidden.
Adding nix ingest / `%p` harvest would be a new harvest, not a patch of two
set walks. Constitution: a THIN_WRAPPER does not gain exotic features to
escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with
“make this more novel.” DESTROYER_visitid_2 already said: if a later mutation
cannot do a second time axis without becoming adrid, the object is still two
set walks on a list the caller already had, and a later destroyer should KILL.
Mutate-3 did synonym-field deletion, unique cap, `-` refuse, slot labels,
flake-input refuse as **record fields**. That is a stricter printer of the
answer key, not a recovered done-set.

Hardcoded ceiling:

- `walk_pointer` = `if addr in done` else insert; `walk_value` = `if name in done`
- `never_fetched` = pointer skips whose first occupant ≠ later NAME
- `unique_addrs` ≡ `len(pointer_visited)`; `unique_names` ≡ `len(value_visited)`
  on one sequential walk; no insert/worker/fetched; no 232/170/~150 as measured
- `--live` cwd `Path(name).is_file()`; directory homonym is a NAME; file
  homonym is not; printed addrs are this-run `slotN`, not records
- same-value-only rc=0; NAME=input name on 170/232 is silent graph sharing
- `value_key	name` is a label; a third field is an error
- LIST_CAP=32 hides skip names after 32 unique; counts uncapped
- empty lists print `-`; `-` is not a legal NAME; BOM is an error
- ADDR is hex (`1000` ≡ `0x1000`); `1e2` rejected; adrid three-column rows
  refused
- a leftover replica already computes `never_fetched` + rc

Do not grow an insert/worker split to escape THIN_WRAPPER. Do not merge this
join into adrid. Do not send it back to R1. Honor KILL. Dreamer ancestry is
not protection. First KEEP/MUTATE is not protection.

---

KILL
