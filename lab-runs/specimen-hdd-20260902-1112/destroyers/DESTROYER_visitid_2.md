# DESTROYER visitid (2)

Date: 2026-09-02 14:14 JST

Target (POST-MUTATE never_fetched address-reuse): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-visitid/visitid`

sha256 `ab9785e6fa982241407f49bb29a3c59da0da3ff207ce22118b676ae1479c160e` (14240 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-visitid-visitid/visitid/visitid` is byte-identical (HEAD `945e8cf670acfd13813a5efc6c2cdf2c409b9010`, `Mutate visitid: never_fetched is address-reuse skip; rc=1.`). Tests 30/30 pass in archive and worktree. `demo-1.log` / `demo-2.log` byte-identical, include `value_key	caller-node` and `rc=1`. Direct exec and `python3 visitid` match.

First destroyer (`DESTROYER_visitid.md`) required: value key declared as caller-chosen node identity; `never_fetched` lists pointer `address-reuse` skips (not name-set difference); empty lists use a token other than `none`; extra/empty tabs are errors; rc=1 on address-reuse; `--live` labeled CPython slot reuse; bare hex with an a-f digit accepted. Those landed. This cut attacks what MUTATE.md left open: no insert-vs-worker time axis (`pointer_done` still equals `unique_addrs`); `--live` ids process-unstable; same-value-only rc=0; `value_key` caller-node vs lock-node; cap 32; node named `none` (sentinel moved); hex without `0x`; THIN_WRAPPER of `set(addr)` vs `set(name)`.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-visitid/visitid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-visitid/fixtures
```

No pytest. No merge onto `main`. Do not run nix. Sibling `addrid` already owns insert/worker/fetched; this object must not become that CLI.

---

## What the mutation still holds

Owned 070: `home-manager` reuses `root`'s `0x7ffe1000`, `skip_kind	address-reuse`, `never_fetched	home-manager`, rc=1. Same input name, later copy reuses a *different* node's address (`reuse-same-name.rec`): `never_fetched	home-manager`, rc=1 — the first destroyer's name-set-difference kill is closed. Node named `none` skipped: `never_fetched	none` / `never_fetched_n	1` / rc=1. Node named `none` visited: `never_fetched	-` / `never_fetched_n	0` / rc=0. Empty tab / extra field / padded name: rc=1, no TSV. `visit	0x1` is the node named visit. `7ffe1000` and `0x7ffe1000` collapse. `--live FILE` when FILE exists: rc=1, not a live NAME. `--live --retain`: `unique_addrs	3`, `allocator_reuse	-`, rc=0. Double `visitid:` prefix gone. FIFO, `/dev/stdin`, space-separated rows work.

```bash
python3 "$CLI" "$FIX/070-reuse.rec"; echo rc=$?
printf 'root\t0x1000\nhome-manager\t0x2000\nhome-manager\t0x1000\n' | python3 "$CLI"; echo rc=$?
```

```text
value_key	caller-node
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

That is the whole useful delta after mutation. Attacks below are the remaining ceiling, not a re-run of the closed holes.

---

## Implementation

### 1. No insert-vs-worker axis: `pointer_done` ≡ `unique_addrs`

`walk_pointer` inserts each new integer address once. `pointer_done` is `len(pointer_visited)`. `unique_addrs` is the same set. `value_done` is `len(unique_names)`. There is no insert epoch, no worker epoch, no fetched column.

50 random (name, addr) tables: `pointer_done == unique_addrs` and `value_done == unique_names` in 50/50. Owned 070: 3=3 and 4=4. Unseen unique: 3=3.

232 unique node keys, 170 unique addrs (later 62 reuse earlier addrs — the specimen's two published counts):

```text
unique_names	232
unique_addrs	170
pointer_done	170
value_done	232
skip_kind	address-reuse
never_fetched_n	62
never_fetched	<node170 … node201, 32 names, cap>
rc=1
```

Two numbers, not three. `~150` fetching activities cannot appear. `never_fetched_n` is `232-170=62`, a set-size difference on one sequential walk, not insert-then-worker.

Sibling `addrid` already splits the packet:

```text
insert	0xa	flake-utils
worker	0xa	naersk
fetched	flake-utils
→ reused	0xa	was	flake-utils	now	naersk
```

visitid will not parse that table (`bad address 'flake-utils'`). Concatenating insert rows then worker rows as one visit list still yields `pointer_done == unique_addrs`. A sequential walk of a caller-complete list cannot let the done-set shrink after a temporary dies.

`pointer_done` is a synonym. Naming it after the specimen's done-set does not create a time axis.

### 2. `--live` ids are process-unstable; path check is cwd-unstable

Eight `--live root nixpkgs home-manager` processes (cwd = candidate dir): skip pattern stable (`unique_addrs 2`, `never_fetched home-manager`, `allocator_reuse ping-pong unique_addrs 2 of 3`, rc=1). Address tuples: 8/8 distinct.

```text
addrs	0x1057eca30	0x1055d1de0	0x1057eca30
addrs	0x10a2d1cc0	0x10a2d14e0	0x10a2d1cc0
addrs	0x107d1edd0	0x107d1f4f0	0x107d1edd0
```

`--live --retain`: 3/3 processes `unique_addrs 3`, rc=0, and 3/3 distinct address tuples. Ids are not a record. A pipe that stores `--live` output cannot join to a later run.

Mutation 6 refuses an existing filesystem path as a live NAME. That check is `Path(name).exists()` against **cwd**:

```bash
cd lineages/candidate-visitid && python3 "$CLI" --live root nixpkgs home-manager
# rc=1, ping-pong, never_fetched home-manager

cd /Users/annenpolka/ghq/github.com/annenpolka/brrr && python3 "$CLI" --live root nixpkgs home-manager
# visitid: --live 'root': existing path is not a live NAME
```

The repo has a `root/` directory. The advertised three-name demo is cwd-dependent. `--live` is CPython slot reuse *and* a `stat` of whatever the caller spelled, including lock-node names that collide with directories.

232 live names drop: `unique_addrs 2`, `never_fetched_n 230`, list capped at 32, `allocator_reuse ping-pong unique_addrs 2 of 232`. Still two CPython slots, not a per-run missing set.

### 3. same-value-only is rc=0 (lock-input feed is silent)

`unseen-same-value.rec` and three `nixpkgs` at three addrs:

```text
skip_kind	same-value
never_fetched	-
never_fetched_n	0
rc=0
```

Documented. Combined with §4 it is the specimen-shaped feed. 232 visit attempts keyed by 170 repeating input names at 232 distinct addrs (graph sharing, no pointer reuse):

```text
unique_names	170
unique_addrs	232
pointer_done	232
value_done	170
skip_kind	same-value
never_fetched	-
rc=0
```

`value_skipped` is capped at 32 of 62. Exit 0. The extra 62 lock nodes are a value skip, not `never_fetched`. Specimen-070 is 232 lock nodes / 170 unique inputs / ~150 fetches / exit 0. Feeding that shape as NAME=input name is silent. Address-reuse rc=1 only fires if the caller already put *distinct* node keys in NAME, or a later same-name event reused a *different* first occupant's address.

same-pointer + same-value (`nixpkgs 0x1` twice): `skip_kind	same-pointer	same-value`, `never_fetched	-`, rc=0. Predicate is address-reuse only.

### 4. `value_key	caller-node` is a constant; INPUT does not walk

`format_report` always writes `value_key	caller-node`. `walk_value` keys on `event.name`. `Event.input` is printed as `inputs` when it differs from NAME and is not consulted by either walk.

Distinct node keys, repeating lock input alias, same address:

```bash
printf 'n1\t0x1\tnixpkgs\nn2\t0x1\tnixpkgs\n' | python3 "$CLI"
```

```text
value_key	caller-node
names	n1	n2
never_fetched	n2
inputs	nixpkgs	nixpkgs
rc=1
```

Same NAME, different INPUT aliases, different addrs:

```bash
printf 'nixpkgs\t0x1\tfrom-root\nnixpkgs\t0x2\tfrom-hm\n' | python3 "$CLI"
```

```text
unique_names	1
skip_kind	same-value
never_fetched	-
inputs	from-root	from-hm
rc=0
```

INPUT is a display alias. Lock-looking NAME `nixpkgs` still prints `value_key	caller-node`. `root/nixpkgs` vs `nixpkgs` are two keys (no lock-path rule). The mutation declared NAME is not flake.lock identity; it did not make a lock-node identity, and it did not refuse input-name keys. The label is the mutation.

### 5. Cap 32 drops distinct skipped names, keeps duplicates

`join_capped` slices the raw skip-name list. 32 first occupants, then 32 `dup` reuses, then 8 distinct `later0`…`later7` reuses:

```text
unique_names	41
unique_addrs	32
pointer_done	32
names_n	72
addrs_n	72
pointer_skipped_n	40
reuse_n	40
never_fetched_n	40
never_fetched	dup	dup	…	dup     # 32 fields, unique {dup}
rc=1
```

`later0`…`later7` are in the count and not in the list. The field whose job is to *name* skipped distinct nodes emits 32 copies of `dup` and omits the distinct later keys. `names` / `addrs` are the first 32 **events**, not unique keys: 33 unique addrs with `hidden 0xabc` as event 33 prints `unique_addrs	33` and an `addrs` row that stops at `0x1f` — `0xabc` and `hidden` are absent from the lists (`names_n	33`, `addrs_n	33`).

5000 events (4000 unique addrs + 1000 reuse): 0.035s, `never_fetched_n	1000`, `never_fetched` length 32, `pointer_done	4000` = `unique_addrs	4000`.

### 6. Node named `none` is fixed; node named `-` is the sentinel

Empty lists use `-`. A node named `none` is distinguishable (`never_fetched	none` vs `never_fetched	-`). A node named `-` is not.

Skip node `-` at `root`'s address:

```text
names	root	-
pointer_skipped	-
skip_kind	address-reuse
reuse	0x1	first	root	later	-
never_fetched_n	1
never_fetched	-
rc=1
```

No skip (`root` + `b`):

```text
pointer_skipped	-
skip_kind	-
reuse	-
never_fetched_n	0
never_fetched	-
rc=0
```

`grep '^never_fetched	-$'` and `grep '^pointer_skipped	-$'` match both. `never_fetched_n` and rc distinguish this pair. A consumer of the `never_fetched` cell does not. Visit node `-` with no skip: `pointer_skipped	-` is both “no pointer skip” and “the skipped name is `-`” — same cell as empty. The first destroyer's `none` collision moved one token.

UTF-8 BOM is now a name prefix, not an error: `names	\ufeffroot`, rc=0.

### 7. Hex without `0x` is only a pointer if an a-f digit is present

`7ffe1000` / `0x7ffe1000` / `7FFE1000` collapse (mutation 7). All-digit tokens are decimal. `%p` dumps that omit `0x` for addresses whose hex digits are 0-9 are a different pointer, or a miss:

```bash
printf 'root\t1000\nnixpkgs\t0x1000\n' | python3 "$CLI"; echo rc=$?
# unique_addrs 2, skip_kind -, rc=0

printf 'root\t1000\nnixpkgs\t0x3e8\n' | python3 "$CLI"; echo rc=$?
# unique_addrs 1, reuse 1000 later-token 0x3e8, rc=1

printf 'root\t10\nnixpkgs\t0x10\n' | python3 "$CLI"; echo rc=$?
# unique_addrs 2, rc=0
```

`ff` / `dead` / `cafe` / `1e` / `e2` / `e10` are hex. `1e2` / `1E2` / `1e0` / `10e2` / `0e10` are `bad address` (scientific). `-7ffe1000` is `bad address`. `010` and `10` collapse as decimal 10. `0x010` and `0x10` collapse as hex 16. The accept-or-say-so for `%p` without `0x` is “has a-f”; it is not “this token is hex.”

### 8. THIN_WRAPPER of `set(addr)` vs `set(name)`

`walk_pointer` is `if event.addr in done`. `walk_value` is `if event.name in done`. `never_fetched` is `[skip.name for skip in pointer_skipped if skip.kind == "address-reuse"]`. `inspect` is those two walks plus unique counts. REALITY.md already names the operation as two Python sets.

Replica of `never_fetched` on the owned fixtures (comment-skipping parse of `NAME ADDR`):

```python
done, occ, nf = set(), {}, []
for name, addr in events:
    if addr in done:
        if occ[addr] != name:
            nf.append(name)
    else:
        done.add(addr); occ[addr] = name
```

070 → `['home-manager']`. reuse-same-name → `['home-manager']`. Matches the CLI. awk of the same rule prints `home-manager` on both fixtures.

The TSV join (`skip_kind`, `reuse first/later`, `never_fetched`, rc=1) is formatting around that membership. After mutation it is an honest formatter of a caller-complete `(NAME, ADDR)` list. It is not a nix done-set, not insert-vs-worker, not lock-node identity.

---

## Primitive

Reality-stripped operation: sequential `set` of integer addresses and `set` of NAME strings on a caller-complete visit list; classify pointer skips as `address-reuse` vs `same-pointer`; print address-reuse names as `never_fetched`; exit 1 if that list is non-empty. `--live` is `id(Node(name))` with a cwd `exists()` gate.

Nearest ordinary workflow: the replica above, or print `id(obj)` / `%p` and compare. On unique-NAME owned 070 that pair is still “home-manager skipped because 0x7ffe1000 was root.” Mutation made `never_fetched` name that skip even when the later NAME already appeared. That is a real join **when the caller already listed every attempt with a node key in NAME**.

Observable capability lost if visitid vanishes: that named join as one TSV with rc=1. Not 232/170/~150. Not a stable `--live` id. Not flake.lock identity.

Ceiling after mutation, now measured:

- `pointer_done` ≡ `unique_addrs`, `value_done` ≡ `unique_names` — no third count, no insert/worker/fetched (addrid's split)
- `--live` ids change every process; `--live root` dies if cwd has `root/`
- same-value-only rc=0; NAME=input name on 232/170 is silent
- `value_key	caller-node` is a label; INPUT does not participate in identity
- cap 32 can list 32× `dup` and omit distinct later skips
- empty token `-` is a legal node name
- bare hex without a-f is decimal (`1000` ≠ `0x1000`)
- the walks are `set(addr)` and `set(name)`

First destroyer: KILL if mutation still defined `never_fetched` as a name-set difference, or could not do value-key declaration + address-reuse `never_fetched` + rc=1. Mutation did those three. This cut does not KILL for that reason.

KILL later if a follow-up grows insert/worker/fetched and becomes adrid, or if `never_fetched` reverts to a name-set difference. Do not merge visitid and adrid into a nix runner.

---

## Mutation (what must change)

Keep the object: for a visit sequence, pointer identity can skip a distinct node that reuses an address; value identity still visits it; name that skip; rc≠0.

Do not keep synonym counts, a cwd-`stat` live mode, or a cap that hides the names the object exists to print.

1. **Delete `pointer_done` / `value_done` or make them diverge.** A second time axis (insert occupancy vs later worker visit) is adrid's primitive — do not copy it here. If visitid stays one sequential walk, the fields are lies of naming. Stop implying 232/170/150; the owned table cannot encode ~150.

2. **`--live` ids are not records.** Do not emit process-local `0x…` as join keys, or refuse `--live` as dogfood. `Path(name).exists()` must not treat lock-node names as files because cwd has a homonym (`root/`). Ids remain allocator-dependent; that is not a later FIX of printing them.

3. **same-value-only rc=0 is the lock-input silent path.** Either refuse repeating NAME unless a distinct node key is present (third field as the value key, NAME as alias), or say the CLI will not accept flake input names. Do not rc=1 on same-value — that is graph sharing, not the specimen skip. Do not leave INPUT as a display-only column.

4. **`value_key` is computed or INPUT walks.** Hardcoding `caller-node` while walking `event.name` is a label. If NAME is the node key, drop `inputs` or key value identity on `(NAME)` only and error when INPUT would have changed the walk. `root/nixpkgs` vs `nixpkgs` needs a stated rule or stays two keys.

5. **Cap unique names, not raw repeats.** `unique_in_order` before `LIST_CAP` on `never_fetched` / `pointer_skipped`. `later0`…`later7` must appear when `never_fetched_n` is 40. `names` / `addrs` should be unique keys (or stop using those rows as identity). Counts stay uncapped.

6. **Empty token is not a legal NAME.** `-` as a node must error, or empty lists use a count-only row (`never_fetched_n	0` with no `never_fetched` cell). `none` stays a name. BOM is an error, not a name prefix.

7. **Bare hex: accept-or-say-so for all-digit tokens.** `1000` vs `0x1000` is the remaining `%p` hole. Either require `0x` always, or treat `[0-9a-fA-F]+` as hex and keep `1e2` rejected by a stated scientific rule.

8. **Do not thicken the wrapper into adrid.** The load-bearing delta is the named pointer-vs-value skip on a caller-complete list. A 12-line replica already computes `never_fetched`. Further novelty that is insert-vs-worker belongs in adrid, not here.

If a later mutation cannot do (1) without becoming adrid and cannot do (5)+(6) as FIX, the object is still two set walks on a list the caller already had, and a later destroyer should KILL.

---

MUTATE
