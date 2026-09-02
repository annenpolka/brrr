# MUTATE visitid (applied 2026-09-02)

From DESTROYER_visitid.md. Worktree
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-visitid-visitid`.

Keep: pointer identity can skip a distinct node that reuses an address;
value identity still visits it; name that skip.

1. **Value key is caller-chosen node identity**, not flake.lock input
   identity. Output `value_key	caller-node`. Optional `NAME ADDR INPUT`
   keeps a repeating input alias on a distinct node key. Same input name
   at two addresses is two nodes when the NAME keys differ.
2. **`never_fetched` lists pointer `address-reuse` skips** (distinct first
   occupant), not `value_visited − pointer_visited` names. Three-row
   `root@0x1000`, `home-manager@0x2000`, `home-manager@0x1000` prints
   `never_fetched	home-manager` / `never_fetched_n	1`, rc=1.
3. **Empty lists use `-`.** A node named `none` is not the empty sentinel.
4. **Empty / extra tab fields and padded names are errors.** `visit	0x1`
   is the node named visit (non-stealing). Third field is INPUT, not a
   dropped node.
5. **rc=1 on address-reuse / non-empty never_fetched.** rc=0 when that skip
   did not happen. Double `visitid:` prefix gone. Skip lists capped at 32
   entries; `never_fetched_n` is the full count.
6. **`--live` is CPython slot reuse** (`mode	cpython-slot`). Drop reports
   `allocator_reuse	ping-pong	unique_addrs	2	of	N`. An existing
   filesystem path is not a live NAME.
7. **Bare hex with an a-f digit (`7ffe1000`) is a pointer.** `1e2` is still
   `bad address`. Reuse rows print the first occupant's addr token; a
   different later spelling adds `later-token`.

Remaining: no insert-vs-worker time axis, so `pointer_done` still equals
`unique_addrs` on a sequential walk of a caller-complete list. Does not
encode 232/170/~150. `--live` ids remain process-unstable. same-value-only
is rc=0 (not the specimen skip).

Do not run nix. Do not merge onto main.

---

# MUTATE visitid (2) (applied 2026-09-02)

From DESTROYER_visitid_2.md. Archive
`lab-runs/specimen-hdd-20260902-1112/lineages/candidate-visitid/`.
Worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-visitid-visitid`.

sha256 `0b1b7c87ab9ea8f16c77cd6c1c0f7ab03ccd5b29cf634b3c4c9e6a5ea5019261`
(14936 bytes). `python3 tests/test_visitid.py` 35/35 twice. `demo-1.log` /
`demo-2.log` byte-identical. `--live --retain root nixpkgs home-manager`
from the repo root (cwd has `root/`) is rc=0, not a path error.

Keep: pointer identity can skip a distinct node that reuses an address;
value identity still visits it; `never_fetched` names that skip; rc=1
on reuse.

1. **Deleted `pointer_done` / `value_done`.** They were `len(unique_addrs)`
   and `len(unique_names)` on one sequential walk. No insert epoch, no
   worker epoch, no fetched column. A second time axis is adrid's
   primitive — not copied here. The owned table still cannot encode
   232/170/~150; those numbers are not printed.
2. **`--live` directory homonym is a NAME.** `Path(name).is_file()`
   refuses `--live FILE`. `root/` in cwd is not a file, so
   `--live root nixpkgs home-manager` works from the repo root. Ids stay
   process-local `0x…` (allocator-dependent; not a record).
3. **Cap unique names, not raw repeats.** `unique_in_order` then
   `LIST_CAP` on `never_fetched` / `pointer_skipped` / reuse-later keys.
   32× `dup` then `later0`…`later7` prints `never_fetched	dup	later0`…
   `later7` with `never_fetched_n	40`. `names` / `addrs` are unique keys
   (070 `addrs` is three tokens, not four). Counts stay uncapped.
4. **`-` as a NAME is an error** (empty-list token). `none` stays a name.
   UTF-8 BOM is an error, not a name prefix. Empty lists still print `-`.
5. **All-digit ADDR is hex.** `1000` and `0x1000` collapse (rc=1 reuse).
   `10` and `0x10` collapse. `1e2` / `1E2` / `0e10` stay `bad address`
   (scientific). `7ffe1000` still hex. Decimal table cells are gone:
   `1000` is not 0x3e8.

Leftover (not faked):

- No insert-vs-worker time axis. `unique_addrs` is the pointer set size
  after one walk. Concatenating adrid `insert`/`worker`/`fetched` rows is
  still `bad address`. Stop. Do not print 232/170/~150 as if they were
  measured here.
- `--live` ids change every process; a cwd *file* named `root` still
  blocks `--live root`.
- same-value-only is rc=0 (graph sharing, not the specimen skip). INPUT
  remains a display alias; `value_key	caller-node` is still the declared
  label; walk keys on NAME.
- The walks are still `set(addr)` and `set(name)` plus the named reuse
  join.

Do not run nix. Do not merge onto main. Do not become adrid.

---

# MUTATE visitid (3) (applied 2026-09-02)

From DESTROYER_visitid_2.md leftovers. Archive
`lab-runs/specimen-hdd-20260902-1112/lineages/candidate-visitid/`.
Worktree `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-visitid-visitid`.

sha256 `58e6d259f30df0e20b4280a4ba1a2e10811495399e6d96f88bd2533488beedc8`
(15056 bytes). `python3 tests/test_visitid.py` 41/41 twice. `demo-1.log` /
`demo-2.log` byte-identical. `--live --retain root nixpkgs home-manager`
from the repo root (cwd has `root/`) is rc=0, `pointer_key	slot`,
`addrs	slot0	slot1	slot2`, no `0x` join keys.

Keep: pointer identity can skip a distinct node that reuses an address;
value identity still visits it; `never_fetched` names that skip; rc=1
on reuse. same-value-only stays rc=0 (graph sharing).

1. **`pointer_done` / `value_done` stay deleted.** They were synonyms of
   `unique_addrs` / `unique_names` on one sequential walk. A second time
   axis is adrid's primitive — not copied. The owned table still cannot
   encode 232/170/~150; those numbers are not printed.
2. **`--live` does not emit process-local `0x…` as join keys.** Printed
   addrs are this-run `slot0`.. occupancy labels. `pointer_key	slot`.
   `Path(name).is_file()` still refuses `--live FILE`; a directory
   homonym (`root/` in cwd) is a NAME. Ids remain allocator-dependent;
   they are not records.
3. **This CLI does not accept flake input names.** A third field is
   `extra field` (NAME is the node key). No `inputs` column. Repeating
   NAME without a distinct node key is graph sharing (`same-value`,
   rc=0), not lock-node identity. Do not rc=1 on same-value.
4. **`value_key` is computed from the walk.** Output is `value_key	name`
   because `walk_value` keys on `event.name`. The old `caller-node` label
   is gone. `root/nixpkgs` and `nixpkgs` stay two keys (no lock-path
   rule).
5. **Cap unique names, not raw repeats** (held from cut 2). 32× `dup`
   then `later0`…`later7` prints `never_fetched	dup	later0`…`later7`
   with `never_fetched_n	40`.
6. **`-` as a NAME is an error.** `none` stays a name. BOM is an error.
   Empty lists still print `-`.
7. **All-digit ADDR is hex.** `1000` and `0x1000` collapse. `1e2` stays
   `bad address`.
8. **Did not become adrid.** No insert/worker/fetched column. Concatenating
   those rows is still `bad address`.

Leftover (not faked):

- No insert-vs-worker time axis. `unique_addrs` is the pointer set size
  after one walk. Stop. Do not print 232/170/~150 as if they were
  measured here. A later destroyer should KILL if a follow-up grows
  insert/worker/fetched and becomes adrid, or if `never_fetched` reverts
  to a name-set difference.
- `--live` slot labels are this-run occupancy, not a lock graph. A cwd
  *file* named `root` still blocks `--live root`.
- same-value-only is rc=0 (graph sharing). Feeding 170 repeating input
  names as NAME is silent graph sharing; the CLI says it will not accept
  flake input names and errors on a third field.
- The walks are still `set(addr)` and `set(name)` plus the named reuse
  join.

Do not run nix. Do not merge onto main. Do not become adrid.
