# DESTROYER ordleak 4

Date: 2026-09-02 19:35–19:46 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0593 worker=destroyer-ordleak-4

Target (lineage archive, after copy-import-tree mutate-3; DESTROYER_ordleak_3 KEEP):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak`

Worktree (byte-identical, not edited):
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-ordleak-ordleak/ordleak/ordleak`

sha256 `4a4bc7d73f16688ad0330302bc4c0f0f3fcdbdbf8888ae75117ad5111faa3306` (28423 bytes). Matches `MUTATE.md` cut 3 (`cli_sha256: 4a4bc7d7…`, `cli_bytes: 28423`, 35/35). Worktree HEAD `bd892a4 MUTATE.md: record ordleak copy-tree HEAD e01b501.` Mutate commit `e01b501 MUTATE ordleak: copy importable tree; dual-FAIL smear is unseen.` Parent `main` is `432f954`; `git ls-tree -r HEAD` has **no** `ordleak`. Not merged onto `main`. Not merged with `leakorder` (`cmp` archive vs `lineages/candidate-leakorder/leakorder` rc=1; vs worktree `leakorder` / `leakorder.py` rc=1). No `copy.deepcopy` / `import copy`. Host Python 3.14.5.

`python3 tests/test_ordleak.py -v` → 35/35 OK twice (archive 4.347s / 4.372s). Host `./demo.sh` ×2 byte-identical to each other (`cmp` rc=0, 5641 bytes, sha256 `d743b4cb4bdfe0bcb9cce2336b0e6e26a5af6f96fd4365f3c30aee76a6d770c4`). Archived `demo-1.log` / `demo-2.log` byte-identical to each other (5305 bytes, sha256 `9ea40c5d9a9b986e17a65ab2912b41ab2fe27bb50dd038cbd3f2f53ae43165b1`); host vs archive differs only in the `file` path prefix (archive was recorded from the worktree copy). Wrapper exit 0.

First Selection KEEP (PATH kept ordleak, not leakorder). `DESTROYER_ordleak.md` MUTATE. `DESTROYER_ordleak_2.md` MUTATE. `DESTROYER_ordleak_3.md` KEEP. First KEEP/MUTATE is not protection. Mutate-3 claimed: copy importable tree so `from pkg.helper import bucket` / relative import load from the copy; dual-FAIL smear is leaked `<unseen>` rc=1 not `leaked none` rc=0; FILE-level slots named; worker stdio not test stdio.

Honor KILL if any of: (1) same-process helper smear (reverse order still dirty from order 1), (2) `leaked none` next to `exposing_order` ≠ `none`, (3) `time_ns` / `object()` / nan / dataclass type identity reported as leaks, (4) nested/relative helpers still `No module named` (mutate-3 claimed this closed), (5) dual-FAIL smear looks like a clean pair (`leaked none` rc=0), (6) THIN_WRAPPER of two greps. **Those conditions did not fire.** Remaining DESTROYER_2 leftovers (private-slots underscore skip, helper class attrs, nested `pkg.helper` walk, lazy import, bounded `*.py` copy) are documented ceilings, not a leftover-identity lie the copy-tree object can still cut without deepcopy. Start-of-victim join is still real. Decision: **KEEP**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak
S009=.../specimens/specimen-009/files/test_order.py
S012=.../specimens/specimen-012/files/test_order.py
S060=.../specimens/specimen-060/files/test_class_leak.py
PKG=.../lineages/candidate-ordleak/tests/fixtures/pkg/test_from_pkg.py
REL=.../lineages/candidate-ordleak/tests/fixtures/pkg/test_relative.py
PARENT=.../lineages/candidate-ordleak/tests/fixtures/parent_helper/sub/test_order.py
```

Host scratch: `destroyers/_ordleak4_scratch/` (`attack.py`, `attack.log`, `cases/`, `tests-1.log`, `tests-2.log`, `demo-host-1.log`, `demo-host-2.log`). Do not merge with `leakorder`. Do not merge onto `main`. Do not send THIN_WRAPPER back to R1. Do not start jury.

---

## What mutate-3 still does, host-executed this pass

Owned specimen-009 still names `acc` and `test_a test_b`, rc=1:

```text
exposing_order	test_a test_b
leaked	acc	into	test_b	[]	['a']	via	test_a
```

`from helper import bucket` — reverse order PASSes; start-of-victim is `[]` vs `['a']`. `import helper` names `helper.bucket` the same way. Unseen specimen-060 `class Box: bucket = []` names `Box.bucket` (not a 009 copy). specimen-012 remains byte-identical to 009 (`cmp` rc=0) and still names `acc`.

Package / relative / parent helpers load from the copy with cwd `/tmp` and no caller `PYTHONPATH`:

```text
# tests/fixtures/pkg/test_from_pkg.py  from pkg.helper import bucket
exposing_order	test_a test_b
leaked	bucket	into	test_b	[]	['a']	via	test_a
rc=1

# tests/fixtures/pkg/test_relative.py  from .helper import bucket
leaked	bucket	into	test_b	[]	['a']	via	test_a
rc=1

# tests/fixtures/parent_helper/sub/test_order.py  from helper import bucket
leaked	bucket	into	test_b	[]	['a']	via	test_a
rc=1
```

Scratch `nested_pkg` / `relative_import` / `helper_package` / `namespace_pkg` (no `__init__.py`) / `cwd_elsewhere` (cwd `/`) all name `bucket` the same way. Reverse PASS. No `No module named`.

Dual-FAIL hardcoded `/tmp` leftover is not a green pair:

```text
# MARKER = Path("/tmp/ordleak4-hard.marker")
order	test_a test_b
status	test_a	PASS
status	test_b	FAIL	a
order	test_b test_a
status	test_b	FAIL	a
status	test_a	PASS
exposing_order	none
leaked	<unseen>
rc=1
leftover exists=True
```

Same shape on the demo smear fixture and on a `$HOME` marker. Always-fail independent of order: `leaked <unseen>` rc=1, not `none` rc=0.

FILE-level slots named (`box` `Box(n=0)` vs `Box(n=1)` and `box.n` `0` vs `1`). Binary stdout `\xff\xfe` is ignored bytes, report present, rc=0. `time.time_ns()` / `object()` / `nan` / dataclass type identity / import-time `os.getpid()` are `leaked none` rc=0. A real `state.acc.append` still names `state`. A real `box["n"] = 1.0` from `nan` still names `box`. Hidden PASS leak still names `acc`. Two bindings both appear. `from helper import *` names `bucket`. `import helper as h` names `h.bucket`. `from pkg import helper` names `helper.bucket`. `thread.local().n` is named. `SimpleNamespace.n` is named. `deque` is named. Custom `__eq__` that always returns true still names `box` / `box.n` (structured encodings, not instance `__eq__`).

---

## Honor KILL probes (did not fire)

| # | condition | host | fire? |
| --- | --- | --- | --- |
| 1 | same-process helper smear (reverse still dirty from order 1) | unique_pids=`[13050, 13051]`; reverse `n=10` not leftover `n=11`; sys.modules reverse PASS; `__file__` marker reverse PASS + `helper.bucket` named; caller PYTHONPATH overwritten, reverse still `n=10` | **no** |
| 2 | `leaked none` next to `exposing_order` ≠ `none` | hunt across every host case transcript in `_ordleak4_scratch/cases/*.out`: **0** hits | **no** |
| 3 | `time_ns` / `object()` / nan / dataclass type identity reported as leaks | all `leaked none` rc=0; real `state.acc.append` still names `state` | **no** |
| 4 | nested/relative helpers still `No module named` | `from pkg.helper` / `from .helper` / parent helper / helper-as-package / namespace pkg / cwd `/` all name `bucket`; reverse PASS | **no** |
| 5 | dual-FAIL smear looks like a clean pair | `/tmp` leftover, `$HOME` leftover, always-fail `assert False`: `leaked <unseen>` rc=1 | **no** |
| 6 | THIN_WRAPPER of two greps | `run_orders.py` prints `acc_after ['a']` for a known name; `grep -nE 'FAIL\|PASS\|acc_after'` does not name `Box.bucket` or `into`/`via`; helper-source grep hits `bucket.append` without start-of-victim `[]` vs `['a']`. ordleak join names `acc` / `Box.bucket` / helper `bucket` / package `bucket` | **no** |

### 1. Same-process helper smear — gone

Each order writes `os.getpid()` to `/tmp/ordleak4-pids.txt`:

```text
a 13050
b 13050
b 13051
a 13051
unique_pids=[13050, 13051]
subprocess_isolation=YES
```

Classic helper counter (first destroyer smear was reverse still dirty `n=11`):

```text
status	test_b	FAIL	n=11    # order 1: test_a +=1 then test_b +=10
status	test_b	FAIL	n=10    # reverse, fresh helper, test_b first
exposing_order	none
leaked	helper.n	into	test_a	0	10	via	test_b
leaked	helper.n	into	test_b	0	1	via	test_a
```

`n=11` in order 1 is in-order accumulation, not smear. Reverse is `n=10`, not leftover `n=11`. Caller `PYTHONPATH` pointing at the original tree is overwritten by the worker; reverse still `n=10`. `sys.modules['ordleak4_smear']` does not survive into the other order (reverse `test_b` PASSes; split is `leaked <unseen>`). A helper that writes next to its own `__file__` is copy-isolated (reverse `test_b` PASSes; `helper.bucket` still named).

### 2. `leaked none` next to `exposing_order` ≠ `none` — no hits

Hunt across every host case transcript: every exposing split is a named binding or `<unseen>`. Zero `leaked none` beside a real exposing order. `_acc` / class attr / function attr / env / logging / contextvars / decimal / lru_cache / slots / warnings / unittest methods / private slots / helper class attrs / lazy import all obey that rule.

### 3. Import inequality — not a leak

`stamp = time.time_ns()`, `object()`, `nan`, dataclass type identity, import-time `pid = os.getpid()`: `leaked none` / rc=0.

### 4. Nested / relative helpers still `No module named` — no

`from pkg.helper import bucket`, `from .helper import bucket`, parent-level `from helper import bucket`, helper-as-package, namespace package without `__init__.py`: all load from the copy. Failures outside the advertised copy (`from ..helper`, `src/pkg` layout, helper two directories above FILE) print `ordleak: … outside the copied tree` or `relative import needs FILE loaded as a package member`, **not** a bare `No module named 'helper'` / `No module named 'pkg'`.

### 5. Dual-FAIL smear looks like a clean pair — no

`/tmp` leftover, `$HOME` leftover, always-fail `assert False`: `leaked <unseen>` rc=1. `leaked none` + rc=0 only when every status is PASS.

### 6. THIN_WRAPPER of two greps — no

```text
# run_orders.py
order ('test_a', 'test_b')
  test_a PASS
  test_b FAIL ['a']
  acc_after ['a']
order ('test_b', 'test_a')
  test_b PASS
  test_a PASS
  acc_after ['a']

# grep -nE 'FAIL|PASS|acc_after' of that output
2:  test_a PASS
3:  test_b FAIL ['a']
4:  acc_after ['a']
6:  test_b PASS
7:  test_a PASS
8:  acc_after ['a']
```

Two greps name neither `Box.bucket` nor start-of-victim `[]` vs `['a']` with `into`/`via`. Helper-source grep hits `from helper import bucket` / `bucket.append("a")` without saying which order wrote the start value. ordleak on the same pair:

```text
leaked	acc	into	test_b	[]	['a']	via	test_a          # S009
leaked	Box.bucket	into	test_b	[]	['a']	via	test_a   # S060
leaked	bucket	into	test_b	[]	['a']	via	test_a       # helper / pkg
```

That join is the object. `run_orders.py` already prints `acc_after` for a known name; it does not name `Box.bucket` or a package helper.

KILL would have been honor if any of those six still held. They do not. First KEEP is not protection; it also is not a reason to kill a cut that still copies the importable tree, refuses a green pair for unsandboxed smear, and still prints the start-of-victim join.

---

## Leftovers vs MUTATE.md “not this cut” (DESTROYER_2 ceilings)

These were re-hit. None is `leaked none` beside a status split. None is a leftover-identity **lie** the copy-tree object can still cut without deepcopy. They stay advertised ceilings.

### 1. Private-slots underscore skip (and instance `_` fields)

```text
# class Box: __slots__ = ("_n",); box._n += 1
exposing_order	test_a test_b
leaked	<unseen>
rc=1

# class Box: def __init__: self._n = 0   # __dict__, still is_field_name skip
exposing_order	test_a test_b
leaked	<unseen>
rc=1

# dataclass S(_n: int = 0); state._n += 1   # dataclasses.fields includes _n
leaked	state	into	test_b	S(_n=0)	S(_n=1)	via	test_a
rc=1

# helper._acc module global is named (is_data_name allows _)
leaked	helper._acc	into	test_b	[]	['a']	via	test_a
```

Legal under Honor-KILL (4) (`<unseen>` ≠ `none`). Module `_acc` and dataclass `_n` are named; instance `_` fields are refused. DESTROYER_2 leftover. Walking `_` instance fields would be object-model completeness, not a copy-tree lie.

### 2. Nested helper module walk / helper class attrs stay `<unseen>`

`from pkg.helper import bucket` and `from pkg import helper` then `helper.bucket` **are** named (FILE global / one-level helper walk). `import pkg.helper` then `pkg.helper.bucket` is `<unseen>` with reverse PASS (copy loaded; snapshot does not recurse into `pkg.helper`). Helper `class Box: bucket = []` via `helper.Box.bucket` is the same refuse. Lazy `from helper import bucket` *inside* the test body isolates (reverse PASS) but is `<unseen>` because the helper is not a FILE global at import. Honest refuse, not `none`. Recursing one more in-tree module would be snapshot completeness, not a required cut of the copy-tree object.

`import pkg` then `pkg.helper` without `pkg` exporting `helper` is AttributeError in both orders (`leaked <unseen>` rc=1) — Python, not a tool lie.

### 3. Hardcoded `/tmp` (and other shared disks) still smear

Isolation copies the importable tree. The leftover is `<unseen>` rc=1, not a tracer and not a green pair. Marker remains on disk after rc=1. Sandboxing `/tmp` would be a filesystem tracer / chroot — a different object.

### 4. Copy is bounded (honest, not a crash-shaped `No module named`)

| case | host |
| --- | --- |
| `from ..helper import bucket` | `relative import needs FILE loaded as a package member: attempted relative import beyond top-level package` |
| `src/pkg` + `tests/test_mod.py` | `imported module 'pkg' is outside the copied tree` |
| helper two directories above FILE | same outside-tree line |
| missing `import totally_not_a_module_ordleak4` | **same outside-tree line** (typo looks like a copy-boundary error) |
| helper reads sibling `payload.txt` | worker `OSError: No such file or directory` under the temp copy (only `*.py` is copied) |

### 5. `exposing_order` is still a status split

Always-fail `test_b` (`assert acc == []; assert False`):

```text
status	test_b	FAIL	['a']
status	test_b	FAIL
exposing_order	none
leaked	acc	into	test_b	[]	['a']	via	test_a
rc=1
```

The leaked row tells the truth; the exposing column does not name `test_a test_b`. First destroyer §9, not in the required (1)+(2)+(4) then copy-tree cut.

### 6. Snapshot holes that stay `<unseen>` on a real split

property/`__getattr__` stores, `warnings.filters`, logging handlers, decimal context, contextvars, env, sibling fs, `lru_cache.currsize`: reverse PASS (process/copy isolation), split is `<unseen>` not `none`. Enum mutation names CPython internals `Color._unhashable_values_` (a real write, not a false leak). Not a pytest runner: fixture-parameterized `test_a(ready)` is ERROR in both orders, `leaked <unseen>` rc=1.

### 7. Ceiling that is in-spec

Not leftover-after (that is leakorder; invoked with ordleak argv → rc=2 `unrecognized arguments: test_a test_b`, FILE-only). Env/fs are not named bindings. `Class.method` / `FILE::Class::method` instantiate-and-call. Unicode names, two bindings, hidden PASS leak, `SystemExit` ERROR row, tab/newline escaped in detail all hold.

---

## Primitive

Reality-stripped operation: spawn two `python3 ordleak --exec-order --report` workers on a temp copy of FILE's importable tree (package dirs + parent helpers), snapshot structured encodings before each 0-arg callable, diff start-of-victim only when a test in the other order wrote the binding, print the join. Dual-FAIL / unnamed split is `<unseen>` rc=1.

Nearest ordinary workflow is still `files/run_orders.py` plus looking at `acc`. Observable capability lost if ordleak vanishes: the **join** (binding name + values at start of victim + exposing order) as one TSV, now also on a sibling helper, a package helper, a relative helper, a parent helper, and on `box.n`, with real process isolation and a side-channel report fd. Two greps of `run_orders.py` do not emit that join.

That is why this is not KILL: the question survived, and the copy-import-tree / dual-FAIL-unseen / slots / report-fd cut is still host-true. It is not same-process deepcopy of `vars(mod)`. It is not import-inequality-as-leak. It is not `leaked none` beside a status split. Nested helpers load. Dual-FAIL smear is not a green pair. It is not two greps.

That is why this is not MUTATE: remaining holes are the advertised ceiling (shared disk, skipped caches, not a pytest runner, bounded py-tree copy, status-split exposing column, private instance `_` fields, nested `pkg.helper` snapshot walk) plus completeness of Python's object model (properties, lazy imports, non-`.py` data). DESTROYER_3 said if Honor KILL does not fire, do not mutate further to escape a KILL that does not apply. Honor KILL did not fire. Start-of-victim join is still real. Do not grow leakorder's leftover-after dialect. Do not send “snapshot `lru_cache.currsize` / chroot `/tmp` / walk `_` slots” back to R1 as novelty.

Do not merge with `leakorder`. Do not merge onto `main`.

Hardcoded ceiling:

- copy is `*.py` only, depth 6, 200 files, parent ≤60 entries; dot-dirs and symlinks skipped
- FILE is loaded as one synthetic package (`.helper` works; `..helper` does not)
- snapshot walks FILE globals + one level of in-tree helper modules; `import pkg.helper` then `pkg.helper.bucket` / helper class attrs stay `<unseen>`
- instance `_` fields skipped (`is_field_name`); module `_acc` and dataclass `_n` are named
- `lru_cache` wrappers skipped; `currsize` stays `<unseen>`
- env / fs / logging / contextvars / decimal / warnings are process-isolated but not named
- `exposing_order` is a status split
- not a pytest runner
- missing modules are labeled “outside the copied tree”
- `/tmp` and `$HOME` still smear; the join refuses them as `<unseen>` rc=1

---

KEEP
