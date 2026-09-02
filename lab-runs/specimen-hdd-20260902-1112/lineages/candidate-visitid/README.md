# visitid

Show whether a visit set used pointer identity or value identity.
Address reuse skips a distinct node.

A walker can insert `&node` into a done-set. If `node` is a temporary,
that address can later name a different node. Printing `id(obj)`
still leaves skipped-because-pointer versus distinct-value as a hand join.

This command walks the same visit sequence twice:

- pointer: Python `set` of addresses (`id(obj)`)
- value: Python `set` of NAME (the node key)

and names pointer `address-reuse` skips whose first occupant was a
distinct key. NAME is that node key, not flake.lock input identity.
This CLI does not accept flake input names as a column. There is no nix.

## Usage

```
visitid RECORD
visitid < RECORD
visitid --live [--retain] NAME [NAME ...]
```

Event fields (tab- or space-separated):

| field | meaning |
| --- | --- |
| `visit NAME ADDR` | visit attempt; NAME is the value key; ADDR is hex |
| `NAME ADDR` | same, without the `visit` tag |

A third field is an error (flake input names are not a column).
`--live` constructs short-lived CPython `Node` objects and walks
`id(obj)` vs NAME. Printed addrs are this-run `slot0`.. labels, not
process-local `0x…` join keys. `--retain` keeps those objects alive so
ids stay unique. An existing regular file is not a live NAME; a
directory homonym (`root/` in cwd) is a NAME.

Empty or extra tab fields are errors. Padded names are errors. `-` as a
NAME is an error (it is the empty-list token). A UTF-8 BOM is an error.
ADDR is hex: `1000` and `0x1000` are the same pointer; `7ffe1000` is
hex; `1e2` is scientific and rejected. `root/nixpkgs` and `nixpkgs` are
two keys (no lock-path rule).

## Output

```
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
```

Exit 1 when `never_fetched_n` is non-zero (address-reuse of a distinct
first occupant). Exit 0 when that skip did not happen (`skip_kind` `-`
or `same-value` / `same-pointer` only). Empty lists use `-`; a node
named `none` is a name; a node named `-` is an error. `names` / `addrs`
are unique keys. Skip-name lists (`never_fetched`, `pointer_skipped`)
are unique-in-order then capped at 32; `never_fetched_n` is the full
skip count. There is no `pointer_done` / `value_done` (those were
synonyms of `unique_addrs` / `unique_names` on one sequential walk).
There is no `inputs` column.

| field | meaning |
| --- | --- |
| `pointer_key` / `value_key` | `id` (or live `slot`) vs walked NAME |
| `unique_names` / `unique_addrs` | distinct value keys vs distinct pointers |
| `skip_kind` | `address-reuse`, `same-pointer`, `same-value`, or `-` |
| `reuse` | first-seen address whose occupant is not the later key |
| `never_fetched` | pointer address-reuse skips (distinct first occupant) |
| `never_fetched_n` | count of those skips |

## Examples

Address reuse skips a distinct node (exit 1):

```
visitid fixtures/070-reuse.rec
# skip_kind  address-reuse
# never_fetched  home-manager
# rc=1
```

Same NAME, later copy reuses an earlier address — still named:

```
visitid fixtures/reuse-same-name.rec
# never_fetched  home-manager
# rc=1
```

Same NAME at different addrs with no pointer reuse is graph sharing
(exit 0), not flake-input identity:

```
visitid fixtures/unseen-same-value.rec
# skip_kind  same-value
# never_fetched  -
# rc=0
```

Live CPython slot reuse, dropped (printed slots may collide):

```
visitid --live root nixpkgs home-manager
# mode  cpython-slot
# pointer_key  slot
# addrs  slot0  slot1  slot0
# allocator_reuse  ping-pong  unique_addrs  2  of  3
```

Live objects retained (slots unique):

```
visitid --live --retain root nixpkgs home-manager
# addrs  slot0  slot1  slot2
```

## Boundary

Does not run nix, prefetch flakes, or parse a lock file. Addresses in
event files are owned table cells, not host `%p` logs. `--live` is
CPython allocation, not a lock graph; printed addrs are occupancy
labels, not records. A sequential walk of a caller-complete list has
no insert-vs-worker time axis and cannot encode 232 lock nodes / 170
unique inputs / ~150 fetching lines. That split belongs to `addrid`,
not here.
