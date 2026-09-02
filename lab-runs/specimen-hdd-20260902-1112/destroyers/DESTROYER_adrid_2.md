# DESTROYER adrid 2

Date: 2026-09-02 15:36 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0356
Worker: destroyer-addrid-2

Target (archive):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-addrid/addrid`

sha256 `79c1d7a6bc825cea8c3628b17fad787e4dd9fd72e75231da9ea97ae54f991eab` (4849 bytes).
Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-addrid-adrid/adrid/addrid` is byte-identical (`cmp` rc=0). HEAD `38e1f3de0a5c14a67520fcc6f1c428139aad6cd6` (`Add adrid CLI from hdd-nixptr harvest (isolated; not for main).`), branch `specimen-hdd/candidate-addrid-adrid`. Parent `main` is `432f954`; `git ls-tree HEAD addrid` empty. Host Python 3.14.5. unittest 4/4. `demo-1.log` / `demo-2.log` byte-identical. `command -v nix` empty; nix was not invoked. Not merged onto `main`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-nixptr` / specimen-070): name when a pointer address in a done-set no longer names the same lock node, and which inputs were therefore never fetched. Kind: USEFUL_COMPOSITION. Embodiment: insert/worker/fetched event table, not nix.

First destroyer (`DESTROYER_adrid.md`) **KEEP**: owned 0xa flake-utils now naersk, skipped naersk; empty stdin rc=1; unknown worker addr `kind unknown-addr`; skip-all reused none, skipped a. Tests 4/4. Demos identical. “Address equality is the object.” First KEEP is not protection.

This candidate is a **THIN_WRAPPER of `set(addr)` occupancy on a caller-complete insert bag versus later worker names, plus `set(name) - set(fetched)` leftover**. Independent replica of leftover+rc (does not import addrid) is **byte-identical** to CLI stdout+rc on 20/20 host cases. awk of the leftover names matches the `skipped` cell on owned/unseen/extra-unfetched/skip-all/reuse-fetched. Flattening insert-then-worker as one visit list yields the same reused triple on owned 070. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-addrid/addrid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-addrid/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-addrid-adrid/adrid/addrid
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not run nix. Do not merge with visitid. Do not grow a `std::set<const Node *>` walker or `nix flake prefetch-inputs --debug` parser to escape THIN_WRAPPER. Do not send pointer-set theater back to R1.

---

## What still works

Owned 070 and any other case where the caller already labeled insert(addr, name), later worker(addr, name), and fetched names.

```bash
python3 "$CLI" "$FIX/070-reuse.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-stable.rec"; echo rc=$?
```

```text
reused	0xa	was	flake-utils	now	naersk	kind	reused
skipped	naersk
fetched	flake-utils	nixpkgs
rc=0
```

```text
reused	none
skipped	none
fetched	a	b
rc=0
```

Empty stdin / fetched-only / `/dev/null`: `missing insert`, rc=1. Missing path: `No such file or directory`, rc=1. `-` is a missing path, not stdin. Unknown field `visit`: rc=1. `/dev/stdin`, FIFO, symlink, space in filename, process substitution, comments, CRLF: owned harvest. unittest 4/4.

That is the first KEEP. It is also first-occupancy of the insert column compared to the worker column, plus names not in the fetched column. Reuse does not change rc.

---

## Implementation

Load-bearing body of `inspect()`:

```python
first: dict[str, str] = {}
for event in inserts:
    if event.addr not in first:
        first[event.addr] = event.name
reused = []
for event in workers:
    was = first.get(event.addr)
    if was is None:
        reused.append({..., "kind": "unknown-addr"})
    elif was != event.name:
        reused.append({..., "kind": "reused"})
inserted_names = unique([e.name for e in inserts] + [w.name for w in workers])
skipped = [name for name in inserted_names if name not in set(fetched)]
```

`inspect.co_names` is `('addr', 'name', 'get', 'append', 'unique', 'set')`. `format_report.co_names` is `('append', 'join')`. `inserted` is computed and never printed. Addresses are opaque strings. There is no shrinking done-set, no integer pointer, no fetch log, no nix.

`main` returns 0 after a successful parse. `reused` nonempty is still rc=0.

---

## 1. THIN_WRAPPER of set(addr) occupancy vs set(name) leftover

Replica of leftover+rc (two bags + set difference; no import):

```python
first = {}
for addr, name in inserts:
    if addr not in first:
        first[addr] = name
reused = []
for addr, name in workers:
    was = first.get(addr)
    if was is None:
        reused.append((addr, "none", name, "unknown-addr"))
    elif was != name:
        reused.append((addr, was, name, "reused"))
names = unique([n for _, n in inserts] + [n for _, n in workers])
skipped = [n for n in names if n not in set(fetched)]
# format the three TSV rows; rc = 0
```

20/20 host cases: stdout byte-identical, rc identical (owned 070, unseen-stable, worker-before-insert, unknown-addr, duplicate insert, multi-worker, interleaved insert/worker, skip-all, reuse-but-fetched, extra-unfetched-no-reuse, fetched-extra, name `none`, same-worker, no-worker, `0xA` vs `0xa`, `1000` vs `0x1000`, comment, CRLF, space in name).

awk leftover (`insert`/`worker` name columns minus `fetched`) equals the CLI `skipped` cell on owned 070 (`naersk`), unseen-stable (`none`), extra-unfetched (`c`), skip-all (`a`), reuse-fetched (`none`).

awk occupancy of the insert bag then the worker bag names owned 070 `reused 0xa flake-utils naersk`.

Nearest ordinary workflow: the replica above, or `join` of two caller-typed columns plus `comm` of names vs fetched. `demo.sh` already prints “print fetch log plus pointer set” before invoking the CLI. The `.rec` files already contain the answer as labeled rows.

On a caller-complete visit list (insert rows, then worker rows, as `(NAME, ADDR)`):

```text
flake-utils	0xa
nixpkgs	0xb
flake-utils	0xa
naersk	0xa
```

Sequential `if addr in done` occupancy produces the same reused triple `(0xa, flake-utils, naersk)`. Sibling visitid on that flatten: `never_fetched	naersk`, rc=1. addrid: `skipped	naersk`, rc=0. The named skip is the same set-walk. The TSV is formatting. Do not merge the CLIs.

---

## 2. Insert vs worker is two labeled bags, not observed time

Claimed primitive: insert epoch occupancy, later worker visit. Stream order of the file is not that axis.

Worker row *before* the insert row, same addr, different name:

```bash
printf 'worker\t0xa\tnaersk\ninsert\t0xa\tflake-utils\nfetched\tflake-utils\n' | python3 "$CLI"; echo rc=$?
```

```text
reused	0xa	was	flake-utils	now	naersk	kind	reused
skipped	naersk
rc=0
```

All inserts occupy, then all workers compare. A later insert cannot update occupancy:

```bash
printf 'insert\t0xa\tA\nworker\t0xa\tB\ninsert\t0xa\tC\nfetched\tA\n' | python3 "$CLI"
```

```text
reused	0xa	was	A	now	B	kind	reused
skipped	C	B
```

`C` is leftover of the name set, not a new occupant. Duplicate insert first-wins; the second insert name is leftover only if unfetched.

Worker addr never inserted:

```text
reused	0xb	was	none	now	naersk	kind	unknown-addr
```

That is `addr not in set(insert addrs)`. Sequential flatten of insert+worker treats it as first occupancy (no reused row). `unknown-addr` is the unlabeled-epoch remainder of the two bags. It is not a shrinking done-set. The specimen’s done-set can later name a different node because a temporary died. This CLI never removes an address. The caller already split insert vs worker.

`0xA` vs `0xa`, and `1000` vs `0x1000`, are `unknown-addr`. Pointer identity is string equality of the token the caller typed.

---

## 3. leftover `skipped` is not “therefore never fetched”

Harvest: names skipped *because* the address no longer named the same lock node. Implementation: `set(insert names ∪ worker names) - set(fetched)`, independent of reuse.

| case | reused | skipped | rc |
| --- | --- | --- | --- |
| owned 070 | 0xa flake-utils→naersk | naersk | 0 |
| reuse but naersk fetched | 0xa flake-utils→naersk | none | 0 |
| extra name `c`, no reuse | none | c | 0 |
| skip-all `insert a`, `fetched b` | none | a | 0 |
| 170 insert + 62 worker reuse + 150 fetched | 62 | 82 (62 nodes + 20 unfetched inputs) | 0 |

Reuse with the new name fetched: harvest bit present, leftover empty. No reuse with an extra unfetched name: leftover present, harvest bit absent. `skipped` is leftover membership on a caller-complete name list. It is not causal.

170 insert + 62 worker reuse + 150 fetched: reused 62, skipped 82, **rc=0**. The specimen’s silent exit 0 is reproduced, not named. 4000 insert + 1000 worker reuse: 1000 reused rows, 1000 skipped names, 0.19s, rc=0. No cap. No third count. 232/170/~150 cannot appear; the owned table has no counts.

Sibling visitid flatten of extra-unfetched (`a 0x1`, `b 0x2`, `c 0x3`, then `a 0x1`, `b 0x2`): `never_fetched_n	0`, rc=0. addrid `skipped	c`. The leftover that is not address-reuse is the fetched-column set difference. That difference is `comm`.

---

## 4. `none` is the empty token and a legal name; `inserted` is a spectator

```bash
printf 'insert\t0x1\tnone\nfetched\ta\n' | python3 "$CLI"
# skipped	none     # name none was not fetched

printf 'insert\t0x1\ta\ninsert\t0x2\tb\nworker\t0x1\ta\nworker\t0x2\tb\nfetched\ta\nfetched\tb\n' | python3 "$CLI"
# skipped	none     # empty leftover
```

`grep '^skipped	none$'` matches both. `fetched	a` vs `fetched	a	b` distinguishes the pair; a consumer of the `skipped` cell does not. Name `none` visited and fetched prints `reused	none` / `skipped	none` / `fetched	none` — three empty-looking cells, rc=0.

`result["inserted"]` is never written. Extra tab on insert is kept as a longer name (`parts[1]`), not an error. UTF-8 BOM: `unknown field '\ufeffinsert'`, rc=1. Two file args: argparse rc=2.

---

## Primitive

Reality-stripped operation: partition a caller-complete TSV into insert/worker/fetched bags; occupy `dict[addr]=first insert name`; emit worker rows whose name differs or whose addr is missing; leftover = unique names not in fetched; exit 0 if the table parsed.

Nearest: the replica in §1, or awk of those two membership tests. Observable capability lost if addrid vanishes: **none**. The harvest question (did a done-set address later name a different lock node, and which inputs were therefore never fetched) is real. This embodiment asks it of labeled rows that already are those events.

Sibling visitid already walks `set(addr)` vs `set(name)` on a sequential visit list and names address-reuse as `never_fetched` with rc=1. addrid’s claimed time axis is the caller’s insert/worker labels on the same occupancy join, plus an independent fetched set-difference, at rc=0. Do not merge them. Do not grow either into a nix runner.

Ceiling, now measured:

- `reused` ↔ `first[insert.addr] != worker.name` (or `unknown-addr` if missing)
- `skipped` ↔ `set(names) - set(fetched)`, including names that were never reused
- rc=0 on reuse, on leftover, on skip-all; rc=1 is parse/IO
- insert vs worker is field bags, not file order, not a shrinking done-set
- addresses are opaque strings (`0xA` ≠ `0xa`, `1000` ≠ `0x1000`)
- empty token `none` is a legal NAME
- `inserted` is unused; no 232/170/150; no nix

Honor KILL. Dreamer ancestry is not protection. First-destroyer KEEP is not protection once leftover+rc is shown to be occupancy plus set difference on a caller-complete table. Constitution: a THIN_WRAPPER does not gain a live done-set walker to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.”

Do not merge onto `main`. Do not run nix. Do not merge with visitid. Archive stays under `lineages/candidate-addrid/`. Worktree stays under `~/.grok/worktrees/annenpolka-brrr/candidate-addrid-adrid/`.

KILL
