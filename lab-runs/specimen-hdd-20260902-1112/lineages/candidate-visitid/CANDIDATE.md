# visitid

origin.method: hdd
origin.trial: hdd-nixptr
specimens: [specimen-070]

classification: USEFUL_COMPOSITION

## Primitive

Show whether a visit set used pointer identity or value identity.
Address reuse skips a distinct node.

## Why this might not exist

A done-set of pointers looks like graph-node identity. If the pointer is
the address of a temporary, a later distinct node can reuse it and be
skipped. `id(object())==id(object())` can be true. Printing those ids
still leaves skipped-because-pointer versus distinct-value as a hand join.

## Core operation

Read visit events `(NAME, ADDR)`. NAME is the node key, not flake.lock
input identity; a third field is an error. Walk `set(addr)` (pointer /
`id(obj)`) and `set(NAME)` (value). Print visited/skipped for each,
unique counts, reuse first/later keys, and pointer address-reuse skips
whose first occupant was distinct (`never_fetched`). ADDR is hex.
`value_key` is `name` (the walked key). There is no insert-vs-worker
axis and no `pointer_done` synonym. `--live` prints `slot0`.. labels,
not process-local `0x` join keys.

## Observable delta

One query names skipped-because-pointer vs distinct-value. Printing ids
does not.

## Reality mapping

Owned events `fixtures/070-reuse.rec`:

```
root 0x7ffe1000, nixpkgs 0x7ffe2000, flake-utils 0x7ffe3000,
home-manager 0x7ffe1000
→ pointer skips home-manager (address-reuse; first occupant root)
→ value visits home-manager
→ never_fetched home-manager
→ rc=1
```

nix is not executed. `--live` is CPython `Node` slot reuse.

## Research boundary

Does not run nix. Does not invent `--debug` address logs. Does not parse
`flake.lock`. `--live` ids are allocator-dependent occupancy labels;
event files are not. Does not copy adrid's insert/worker/fetched split.

## Removed

Invented nix prefetch-inputs runs and `%p` logs.

## Smallest artifact

Python 3 stdlib CLI `visitid`.

## Pre-implementation Reality assessment

Copied from harvest before code. Full copy: `REALITY.md`.

- Classification: USEFUL_COMPOSITION
- Nearest existing operation: print object ids
- Observable delta: skipped-because-pointer vs distinct-value
- Constraint: owned addr/name table; not nix
- Established on the fixture: the 070-reuse row above

## How to run

From this directory:

```
python3 tests/test_visitid.py
./demo.sh
visitid --live root nixpkgs home-manager
visitid --live --retain root nixpkgs home-manager
```

## Empirical transcript

Host-executed 2026-09-02. Mutate (3) after DESTROYER_visitid_2 leftovers.

`python3 tests/test_visitid.py`: 41 OK (twice).

`./demo.sh` twice (`demo-1.log` and `demo-2.log` match):

```
== nearest existing operation (print object ids) ==
id(object())==id(object()) True
(equal ids after the first object dies still do not name skipped-because-pointer vs distinct-value)

== fixture counts .../specimen-070/files/observed_counts.txt ==
lock nodes: 232
unique inputs: 170
fetching activities: ~150
missing set: different each run
exit: 0
(origin counts; visitid walks a caller-complete (node, addr) list and does not encode 232/170/150)

== specimen-070 prefetch_failing.cc done-set (origin excerpt, not executed) ==
8:    if (!state_.lock()->done.insert(&node).second)

== visitid specimen-070 owned addr/name events (address reuse skips distinct node) ==
mode	events
pointer_key	id
value_key	name
names	root	nixpkgs	flake-utils	home-manager
addrs	0x7ffe1000	0x7ffe2000	0x7ffe3000
unique_names	4
unique_addrs	3
pointer_visited	root	nixpkgs	flake-utils
pointer_skipped	home-manager
value_visited	root	nixpkgs	flake-utils	home-manager
value_skipped	-
skip_kind	address-reuse
reuse	0x7ffe1000	first	root	later	home-manager
never_fetched_n	1
never_fetched	home-manager
rc=1

== visitid unseen unique addrs ==
skip_kind	-
never_fetched_n	0
never_fetched	-
rc=0

== visitid unseen same-name different-addr (value skip) ==
skip_kind	same-value
never_fetched	-
rc=0

== visitid same input name, later node reuses earlier addr ==
names	root	home-manager
unique_names	2
unique_addrs	2
pointer_skipped	home-manager
value_skipped	home-manager
skip_kind	address-reuse	same-value
reuse	0x1000	first	root	later	home-manager
never_fetched_n	1
never_fetched	home-manager
rc=1
```

`id(object())==id(object()) True` still looks like one object. `visitid`
names `skip_kind address-reuse` and `never_fetched home-manager`, exit 1.

Host-executed `--live` (CPython slot reuse; labels are this-run slots):

```
visitid --live root nixpkgs home-manager
mode	cpython-slot
retain	false
allocator	cpython
pointer_key	slot
value_key	name
unique_addrs	2
addrs	slot0	slot1
skip_kind	address-reuse
never_fetched	home-manager
allocator_reuse	ping-pong	unique_addrs	2	of	3
rc=1
```

`--live --retain`: unique_addrs 3, addrs slot0 slot1 slot2, skip_kind `-`,
allocator_reuse `-`, rc=0. From repo root (cwd has `root/`) the same
retain command is rc=0, not a path error.

## Dogfood targets

- specimen-070 `070-reuse.rec` (owned, executed as addr/name events).
- `reuse-same-name.rec` (same NAME, later address-reuse still named).
- prefetch_failing.cc `done.insert(&node)` excerpt (origin only; no nix).
- Destroyer extra: `--live` drop vs retain on CPython objects.

## Surprises

CPython `--live` without retain did not reuse one id for every name.
root and home-manager shared a slot; nixpkgs got another. unique_addrs 2
of 3 names, pointer skipped only home-manager. That is two-slot CPython
ping-pong, not a lock-graph missing set.

`id(object())==id(object())` was True both demo runs on this host.

Same name at two addresses with no pointer reuse is a value skip, not
never_fetched. Same name that reuses a *different* node's address is
never_fetched (the later event), even when the name was already visited.

## Failures

Does not run nix, prefetch, or parse flake.lock. Negative/zero addresses
are accepted as table cells. `--live` slot labels are not stable across
processes as records (they are occupancy, not heap `0x`). Event `ADDR`
is hex: `1000` and `0x1000` are the same pointer; reuse prints the
first-seen token and `later-token` when the later spelling differs.
Names are case-sensitive. `-` as a NAME is an error. A sequential walk
has no `pointer_done`; it does not encode 232/170/~150. same-value-only
stays rc=0. `--live` directory homonyms are names; file homonyms are not.
A third field is an error (flake input names are not a column).

## Suggested mutations

- JSON output
- Parse a lock-file node list plus a separate addr column from nix (still
  do not run nix)
- Insert-vs-worker remains adrid's object, not a visitid follow-up

## Kill / keep

Keep: pointer identity can skip a distinct node that reuses an address.
Value identity still visits it. Name that skip. `never_fetched` is the
address-reuse skip list, not a unique-name set difference.
Mutated after DESTROYER_visitid_2 leftovers. Leftover: no time axis (do
not fake 232/170); `--live` slots are occupancy not records;
same-value-only rc=0; walks are still `set(addr)` vs `set(name)`.
