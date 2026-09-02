# DESTROYER requeue

Date: 2026-09-02 15:54 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0407
Worker: destroyer-requeue

Target (archive): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-requeue/requeue`

sha256 `fc1b43d91cdf07961f5c3c08b241df4dfc8fc83bbb7e09a3794dfdaf685f0d38` (4151 bytes, 126 lines). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-requeue-requeue/requeue/requeue` is **byte-identical** (`cmp` rc=0). Worktree HEAD `7db82537c8b77ff26e0d68174c6031e890f6aa1c` (`Add requeue CLI from hdd-s063 harvest (isolated; not for main).`), branch `specimen-hdd/candidate-requeue-requeue`. Parent `main` is `432f954`; `git ls-tree HEAD requeue` on `main` is empty. Archive is untracked (`?? lineages/candidate-requeue/`). Host Python 3.14.5. `pytest` / `xdist` specs are `None`. Source contains no `pytest`, `xdist`, `workqueue`, `send_runtest`, `loadgroup`, `loadscope`, `hang_risk`. unittest `python3 tests/test_requeue.py -v` 4/4 (`Ran 4 tests in 0.078s` `OK`). `demo.sh` ×2 live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0). No merge onto `main`. Archive was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-s063` / specimen-063): name completed work units put back after a worker crash, and assignments that have only completed units. Kind: USEFUL_COMPOSITION. Harvest embodiment recorded in `hdd-origins/hdd-s063.md` is `lineages/candidate-emptyunit/emptyunit`. Rejected: invented pytest `--debug` xdist traces. Constraint: no pytest.

Sibling emptyunit KEEP (`DESTROYER_emptyunit.md` FIFO hang_risk; `DESTROYER_emptyunit_3.md` assign-loop KEEP) is the first KEEP of this harvest. Job input is `requeue SECOND pass`. First KEEP is not protection.

This candidate is a **THIN_WRAPPER of caller-labeled requeue rows**. `already_done` is `requeued ∩ done=yes`. `unfinished` is `requeued ∩ done=no`. `empty_assign` is a worker whose assigned names are all `done=yes`. `inspect()` never reads a hang log, never parses a workqueue dump, never groups by dist, never builds `send_runtest_some` indexes. Host replica of that three-set filter (no import of the CLI) is **byte-identical** to CLI stdout on **29/29** parseable host records (`stdout_eq=True`, `rc_eq=True`), including both owned fixtures (79 / 63 bytes). awk of `$1=="unit"` / `$1=="requeued"` / `$1=="assigned"` matches `already_done` / `unfinished` / `empty_assign` on both owned fixtures. A python one-liner of requeued-name membership on `done==yes` already prints `test_1` from `063-crash.rec`. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-requeue/requeue
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-requeue/fixtures
S063=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-063
EU=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/emptyunit
EUFIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-emptyunit/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-requeue-requeue/requeue/requeue
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not merge with `emptyunit`. Do not grow a workqueue dump / `LoadScopeScheduling` parser to escape THIN_WRAPPER. Do not send pytest-xdist theater back to R1.

---

## What still works

Owned 063 crash record, unseen all-done empty assign, and any other TSV whose `unit NAME done yes|no` / `requeued NAME` / `assigned WORKER NAME` rows are already the harvest sentence.

```bash
python3 "$CLI" "$FIX/063-crash.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-alldone.rec"; echo rc=$?
```

```text
requeued	test_1	test_2
already_done	test_1
unfinished	test_2
empty_assign	none
rc=0

requeued	a	b
already_done	a	b
unfinished	none
empty_assign	gw2
rc=0
```

79 / 63 bytes. Stderr empty. `demo.sh` already names the nearest operation: “read the hang log”.

Stdin of the owned 063 record, symlink, filename with a space, process substitution `<(cat 063-crash.rec)`, `/dev/stdin`: same 79-byte harvest, rc=0. Unicode name `テスト` done yes + requeued + assigned: `already_done	テスト`, `empty_assign	gw1`, rc=0. 5000 all-done requeued units (~60kB stdout, 0.111s): `already_done` reprints every name, `empty_assign	gw1`, rc=0.

That is the whole useful surface. It is also what `awk` of the three caller-written fields already does. Attacks below break the “which completed unit was requeued as an empty send” claim, or show the primitive cannot grow.

---

## Implementation

Load-bearing body:

```python
already = [n for n in requeued if units.get(n) is True]
unfinished = [n for n in requeued if units.get(n) is False]
unknown = [n for n in requeued if n not in units]
by_worker: dict[str, list[str]] = {}
for worker, name in assigned:
    by_worker.setdefault(worker, []).append(name)
empty_assign = []
for worker, names in by_worker.items():
    open_names = [n for n in names if not units.get(n)]
    if names and not open_names:
        empty_assign.append(worker)
```

`inspect.__code__.co_names` is `('get', 'setdefault', 'append', 'items')`. `parse_record.co_names` is `('enumerate', 'splitlines', 'strip', 'startswith', 'ValueError', 'split', 'KNOWN', 'len', 'parse_done', 'append', 'unique')`. There is no dump, no dist, no index list, no hang. `order` is collected and never read. `format_report` reprints `requeued` and emits `unknown` only when the caller already typed a name with no `unit` row.

`demo.sh` already names the nearest operation: read the hang log.

---

## Attacks

### 1. THIN_WRAPPER: caller-labeled rows are the product

Host replica of the three-set filter (exec of `destroyers/_requeue_scratch/replica.py`, no package import) is byte-identical to CLI stdout+rc on **29/29** parseable host records, including both owned fixtures.

awk of the three fields, without importing the CLI:

```awk
BEGIN{FS="\t"}
$1=="unit" && $3=="done" { done[$2]=tolower($4) }
$1=="requeued" && !seen[$2]++ { rq[++nr]=$2 }
$1=="assigned" { w[$2]=w[$2] SUBSEP $3; if(!ws[$2]++) wo[++nw]=$2 }
```

`063-crash.rec` / `unseen-alldone.rec`: awk == CLI on `already_done` / `unfinished` / `empty_assign`. IDENTICAL.

One-liner of requeued ∩ done=yes on the owned crash record:

```bash
awk -F'\t' '$1=="unit" && $4=="yes"{d[$2]=1} $1=="requeued"{if(d[$2]) print $2}' "$FIX/063-crash.rec"
```

```text
test_1
```

That is `already_done`. The harvest records already *are* the input. The CLI reprints the stickers the caller wrote, intersects them, and exits 0.

Two rows, no `assigned`:

```bash
printf 'unit\ttest_1\tdone\tyes\nrequeued\ttest_1\n' | python3 "$CLI"
```

```text
requeued	test_1
already_done	test_1
unfinished	none
empty_assign	none
rc=0
```

No `requeued` rows, only `assigned` of all-done units:

```text
requeued	none
already_done	none
unfinished	none
empty_assign	gw2
rc=0
```

`empty_assign` does not require a `requeued` label. `already_done` does not require `assigned`. Each column is a separate membership test on rows the caller already classified.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`requeued` echo, `unknown`) to escape classification. Those rows are echo. They do not observe a crash. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First KEEP is not protection. Same shape as Honor-KILLed treeid (AND of two caller flags) and Honor-KILLed pairaxis (dict-diff of caller traces).

### 2. Spectator fields: `order` / unused units / mixed assigned never decide

`unit	b` then `unit	a`, both done, `requeued	a` then `b`: `already_done	a	b` follows requeued order, not unit order. `order` is unused.

Done unit not in `requeued`:

```text
unit	a	done	yes
unit	b	done	no
requeued	b
```

```text
already_done	none
unfinished	b
empty_assign	none
rc=0
```

`a` is completed work. It does not appear. The CLI only names units the caller already listed as `requeued`.

`requeued	b` (open) plus `assigned	gw1	a` (done): `unfinished	b`, `empty_assign	gw1`. The empty-assign worker is independent of the requeued name. The harvest join “completed unit requeued as empty send” is two stickers, not one observation.

Only `unit` rows, no `requeued`, no `assigned`: `requeued	none`, `already_done	none`, `empty_assign	none`, rc=0. A record of completed tests with no caller labels is a no-result, not a hang.

### 3. Contradiction: stickers, not a crash

`unit	open_test	done	yes` + `requeued	open_test`: `already_done	open_test`, rc=0. The name says open. The token says yes. The token wins.

Last-wins: `unit	a	done	no` then `done	yes` + `requeued	a` → `already_done	a`. Reverse → `unfinished	a`. Duplicate keys are a last assignment, not a pair of crash states.

`YES` / `True` / ` yes ` lowercased: `already_done	a`, rc=0. Token `1` is refused (`unit done must be yes|no, got '1'`, rc=1). `true`/`done`/`false`/`open` are aliases. The closed set is the product.

Duplicate `requeued	a`: unique-first, still `already_done	a`. Assigned unknown name `missing` next to done `a` on `gw1`: `empty_assign	none`, because `not units.get("missing")` is True (unknown counts as open). Ghost `requeued` with no unit: `unknown	ghost`, `already_done	none`, rc=0. Unknown is a reprint of a caller typo, not a missing collection index.

Two workers, `gw1` all-done, `gw2` open: `empty_assign	gw1` only. Worker order is first-seen in `assigned` rows (`z` then `a` → `empty_assign	z	a`).

### 4. Origin packet / emptyunit dump cannot enter

```bash
python3 "$CLI" "$S063/files/hang_log.txt"; echo rc=$?
python3 "$CLI" "$S063/files/remove_node_failing.py"; echo rc=$?
python3 "$CLI" "$EUFIX/063-hang.dump"; echo rc=$?
python3 "$CLI" "$EUFIX/063-hang.rec"; echo rc=$?
python3 "$EU" "$EUFIX/063-hang.dump"; echo eu_rc=$?
```

```text
requeue: …/hang_log.txt:1: expected key<TAB>value
rc=1
requeue: …/remove_node_failing.py:6: expected key<TAB>value
rc=1
requeue: …/063-hang.dump:1: expected key<TAB>value
rc=1
requeue: …/063-hang.rec:3: unknown field 'collection'
rc=1
```

emptyunit on the same dump: `hang_risk	yes`, `would_send	()`, `empty_send	yes` on `test_1`, rc=1. That is the harvest. This CLI cannot ingest it. The owned `063-crash.rec` is already the harvest sentence, typed as TSV. Dreamer pytest `--debug` traces were rejected; this is that inspect, reduced to caller-labeled rows.

### 5. Parse / IO / stdin

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `No such file or directory` |
| directory | 1 | `Is a directory` |
| empty / comments-only / `/dev/null` / argv-less empty stdin | 1 | `missing unit` |
| spaces instead of tabs | 1 | `expected key<TAB>value` |
| unknown field / `Unit` | 1 | `unknown field` |
| UTF-8 BOM | 1 | `unknown field '\ufeffunit'` |
| invalid UTF-8 | 1 | codec error |
| CRLF | 0 | `splitlines`, owned already_done |
| stdin no-args with owned record | 0 | same 79-byte harvest |
| argv `-` | 1 | dash is a filename, not stdin |
| `/dev/stdin` / process substitution / symlink / space in filename | 0 | owned harvest |
| 5000 all-done names | 0 | reprints names; empty_assign still the sticker |
| extra positional | 2 | argparse |
| `-h` | 0 | help |
| `requeued` only | 1 | `missing unit` |
| `unit done` without yes\|no | 1 | `unit NAME done yes\|no` |
| token `1` / `maybe` | 1 | `unit done must be yes\|no` |

Success and “named the hang” share rc=0. A pipe cannot tell “completed-only requeue” from “caller typed done yes.” Tests never hit aliases, last-wins, spectators, origin dumps, stdin, BOM, or empty_assign without `requeued`. Four tests: owned crash, owned CLI, unseen all-done, missing unit (rc=1 only).

### 6. rc never names the hang

Owned mixed 063: `already_done	test_1`, `empty_assign	none`, **rc=0**. Unseen all-done empty assign: `empty_assign	gw2`, **rc=0**. Harvest-true completed-only send is not an exit. emptyunit uses rc=1 on `hang_risk`. This CLI always exits 0 on a well-formed record, including the harvest case the demo prints.

---

## Primitive

Reality-stripped operation: parse a TSV of `unit NAME done TOKEN` plus optional `requeued NAME` and `assigned WORKER NAME`; `already_done` iff a requeued name’s token is in `{yes,true,done}`; `unfinished` iff in `{no,false,open}`; `empty_assign` iff a worker’s assigned names are all done (unknown names count as open); echo unique requeued names; rc=0 whenever the TSV parsed.

Nearest ordinary workflow: awk of the three caller-written fields, or reading the two owned records by eye. `demo.sh` already says read the hang log. Observable capability lost if requeue vanishes: **none**. The harvest records already are the input. The join is still a hand comparison after the TSV. A crash log is never read. A workqueue dump is never grouped.

That is why this is KILL, not MUTATE. The *question* (after a worker crash, did `_assign_work_unit` requeue a completed-only scope so the replacement is sent `send_runtest_some([])` and hangs) is a real debugging object. Sibling emptyunit asks it of a dump + dist + FIFO assign-loop. This embodiment does not. It asks three caller-labeled columns. Adding workqueue ingest / loadgroup regroup / hang_risk would be implementing emptyunit, which already KEEP, and would be a new harvest, not a patch of this 126-line filter. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First KEEP is not protection.

Hardcoded ceiling:

- `already_done` iff name ∈ unique(`requeued`) AND `units[name] is True`
- `empty_assign` iff assigned names nonempty AND none are open/`units.get` missing
- `order` / unused units / mixed assigned are spectators
- `YES`/`True`/` yes ` lowercased are done; `1` is not
- last-wins on duplicate `unit` rows; unique-first on `requeued`
- unknown assigned names block empty_assign (`not None` is open)
- origin hang log / `remove_node` excerpt / emptyunit dump refuse
- success and harvest-true share rc=0
- 5k-name dumps reprint the names and still intersect the stickers
- Dreamer pytest probe was rejected; this is that inspect, reduced to caller-labeled rows

Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection.

Do not grow a workqueue dump parser or LoadScopeScheduling to escape THIN_WRAPPER. Do not merge this filter onto `main`. Do not merge with `emptyunit`. No pytest. Do not send pytest-xdist theater back to R1.

---

KILL
