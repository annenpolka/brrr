# DESTROYER ordleak 2

Date: 2026-09-02 15:44 JST
RUN_ID: specimen-hdd-20260902-1112
JOB: job-0374 worker=destroyer-ordleak-2

Target (lineage archive, after isolate-subprocess mutate):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak`

Worktree (byte-identical):
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-ordleak-ordleak/ordleak/ordleak`

sha256 `ad60324a37b1063287b018563d019bba19eb4a3bb4a663326962551d6200887a` (21760 bytes). Matches `MUTATE.md` cut 2 (`cli_sha256: ad60324a…`, 26/26). Worktree HEAD `1f368b74262b67840a2e8ad1758d029f47822439` (`MUTATE.md: leftover honesty for ordleak isolation cut.`). Parent `main` is `432f954` and has no `ordleak`. Not merged onto `main`. Not merged with `leakorder` (`cmp` rc=1). Host Python 3.14.5.

`python3 tests/test_ordleak.py -v` → 26/26 OK. Archived `demo-1.log` / `demo-2.log` byte-identical. First Selection KEEP. First destroyer (`DESTROYER_ordleak.md`) → **MUTATE**.

Origin claim after mutate: for a named pair, one subprocess per order; name the binding whose **start-of-victim** value depended only on order, and the order that exposes a status split. Leak is a test-induced write, not import inequality. `leaked none` illegal next to `exposing_order` ≠ `none`.

Honor KILL if still same-process deepcopy / `leaked none` next to `exposing_order` / import inequality. Host-executed, not trusted. **Those conditions did not fire.** Decision: **MUTATE** (package-tree copy, dual-FAIL smear must not look clean, slots named), not KILL, not FIX.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-ordleak/ordleak
S009=.../specimens/specimen-009/files/test_order.py
S060=.../specimens/specimen-060/files/test_class_leak.py
HELPER=.../lineages/candidate-ordleak/tests/fixtures/helper/test_order.py
HELPER_IMPORT=.../lineages/candidate-ordleak/tests/fixtures/helper/test_import.py
```

Host scratch: `destroyers/_ordleak2_scratch/` (`attack.py`, `attack.log`, `cases/`).

---

## What still works (required cut, host-executed)

Owned specimen-009 still names `acc` and `test_a test_b`, rc=1:

```text
exposing_order	test_a test_b
leaked	acc	into	test_b	[]	['a']	via	test_a
```

`from helper import bucket` — reverse order PASSes; start-of-victim is `[]` vs `['a']`:

```text
order	test_a test_b
status	test_a	PASS
status	test_b	FAIL	['a']
order	test_b test_a
status	test_b	PASS
status	test_a	PASS
exposing_order	test_a test_b
leaked	bucket	into	test_b	[]	['a']	via	test_a
rc=1
```

`import helper` names `helper.bucket` the same way (`[]` vs `['a']` via `test_a`).

Unseen specimen-060 `class Box: bucket = []` names the class attribute (not a 009 copy):

```text
exposing_order	test_a test_b
leaked	Box.bucket	into	test_b	[]	['a']	via	test_a
rc=1
```

`time.time_ns()` at import is not a leak (`exposing_order none` / `leaked none` / rc=0). Env split is `leaked <unseen>`, not `none`. `_acc`, `Box.items`, `holder.acc`, mutable defaults, closures, `import helper as h` → `h.bucket`, `from helper import bucket as acc`, unittest `TestOrder.test_a`, `FILE::TestOrder::test_a`, unicode names, two bindings, hidden PASS leak, dataclass mutation, custom `__eq__` that always returns true (`Box(n=0)` vs `Box(n=1)` — MUTATE.md leftover was pessimistic), instance `box.bucket`, `SystemExit`/`GeneratorExit` as ERROR rows all hold.

Sibling `__file__` marker isolates (order 2 `test_b` PASSes, `leaked <unseen>` because fs is not a named binding). FILE's directory is on the worker path: `from helper import bucket` works with cwd `/tmp`.

No `copy.deepcopy` in the CLI. `run_order_isolated` is `python3 ordleak --exec-order` + `subprocess.run`.

---

## Honor KILL probes (did not fire)

### 1. Same-process deepcopy — gone

Each order writes `os.getpid()` to `/tmp/ordleak2-pids.txt`:

```text
a 5767
b 5767
b 5768
a 5768
unique_pids=[5767, 5768]
subprocess_isolation=YES
```

`--exec-order` snapshots of import-time `pid = os.getpid()`: `p1=5904` `p2=5905` `differ=True`.

Classic helper counter (first destroyer §1 smear was `n=1` then `n=11` with reverse still dirty):

```text
status	test_b	FAIL	n=11    # test_a +=1 then test_b +=10
status	test_b	FAIL	n=10    # reverse, fresh helper, test_b first
exposing_order	none
leaked	helper.n	into	test_a	0	10	via	test_b
leaked	helper.n	into	test_b	0	1	via	test_a
```

Reverse is `n=10`, not leftover `n=11`. Isolation holds. `exposing_order none` is the always-raise `test_b`, not smear.

`sys.modules['ordleak2_smear']` does not survive into the other order (reverse `test_b` PASSes; split is `leaked <unseen>`).

### 2. `leaked none` next to `exposing_order` ≠ `none` — no hits

Hunt across 40 host case transcripts: every exposing split is a named binding or `<unseen>`. Zero `leaked none` beside a real exposing order. `_acc` / class attr / function attr / env / logging / contextvars / decimal / lru_cache / slots all obey that rule.

### 3. Import inequality — not a leak

`stamp = time.time_ns()`, `object()`, `nan`, dataclass type identity across uuid loads: `leaked none` / rc=0. A real `box["n"] = 1.0` from `nan` still names `box`.

KILL would have been honor if any of those three still held. They do not. First KEEP is not protection; it also is not a reason to kill a cut that actually isolated.

---

## Leftovers vs MUTATE.md “not this cut”

### 1. Nested / relative / parent helpers still do not load

Sibling `*.py` copy only. No caller `PYTHONPATH`:

```text
# pkg/helper.py bucket=[]; from pkg.helper import bucket
ordleak: No module named 'pkg'    rc=1

# pkg/test_mod.py: from .helper import bucket
ordleak: attempted relative import with no known parent package    rc=1

# helper.py in parent of FILE
ordleak: No module named 'helper'    rc=1
```

With `PYTHONPATH` pointing at the original tree, the nested package **does** isolate in RAM (`leaked bucket [] ['a']`, reverse PASS) because orders are subprocesses — they import the original file twice in two processes. That is not a copy. A helper that writes next to the original `__file__` would smear. README: “Imported helpers … do not smear” / “fresh copy of sibling `.py` files”. Nested helpers are neither copied nor loadable.

### 2. Hardcoded `/tmp` smear still prints a clean pair

MUTATE.md: “A hardcoded path (`/tmp/ordleak.marker`) is still one disk. That split is `<unseen>`, not a tracer.”

Host:

```text
# MARKER = Path("/tmp/ordleak2-hard.marker")
order	test_a test_b
status	test_a	PASS
status	test_b	FAIL	a
order	test_b test_a
status	test_b	FAIL	a
status	test_a	PASS
exposing_order	none
leaked	none
rc=0
leftover exists=True
```

Statuses agree because order 1 left the file. No exposing split, so `leak_verdict` is `none`, exit 0. That is **not** `<unseen>`. It is the old “nothing leaked” lie for the one isolation hole the copy does not cover. Sibling-next-to-`__file__` is isolated; `/tmp` is not. `leaked none` next to `exposing_order none` is outside the Honor-KILL wording, and it is still unsupported certainty: tests failed, marker on disk, tool says clean.

### 3. `__slots__` instance state is `<unseen>`

```text
class Box:
    __slots__ = ("n",)
box = Box()          # test_a: box.n += 1; test_b: assert box.n == 0
exposing_order	test_a test_b
leaked	<unseen>
rc=1
```

Legal under (4) (`<unseen>` ≠ `none`). The binding lives on a FILE global. `encode()` walks `__dict__` / dataclass fields / repr; slots have no `__dict__` and default repr has no `n`. Same hole as first-destroyer class-attr, now refused instead of faked. `lru_cache` currsize is the same refuse (`leaked <unseen>` on a real `currsize=1` split).

### 4. `exposing_order` is still a status split, not an assertion-reason split

Always-fail `test_b` (`assert acc == []; assert False`):

```text
status	test_b	FAIL	['a']
status	test_b	FAIL
exposing_order	none
leaked	acc	into	test_b	[]	['a']	via	test_a
rc=1
```

The leaked row tells the truth; the exposing column does not name `test_a test_b`. First destroyer §9, not in the required (1)+(2)+(4) cut. rc=1 because the leak is named — better than parent rc=0.

### 5. Worker stdout is the JSON channel

`sys.stdout.buffer.write(b"\xff\xfe")` in `test_a`:

```text
ordleak: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
rc=1
stdout empty
```

No report. Text `print` is survived (`lines[-1]` JSON). Binary is not.

### 6. Ceiling that is in-spec

Env / sibling fs / logging / contextvars / decimal / `sys.modules` splits: `leaked <unseen>` when statuses split. Fixture parameters ERROR, not PASS. Not leftover-after (that is leakorder). specimen-012 is still byte-identical to 009; this pass dogfooded helper + 060 instead.

---

## Primitive

Reality-stripped operation: spawn two `python3 ordleak --exec-order` workers on a temp copy of FILE + sibling `*.py`, snapshot structured encodings before each 0-arg callable, diff start-of-victim only when a test in the other order wrote the binding, print the join.

Nearest ordinary workflow is still `files/run_orders.py` plus looking at `acc`. Observable capability lost if ordleak vanishes: the **join** (binding name + values at start of victim + exposing order) as one TSV, now also on a sibling helper and on `Box.bucket`, with real process isolation.

That is why this is not KILL: the question survived, and the isolate-subprocess cut is host-true. It is not same-process deepcopy of `vars(mod)`. It is not import-inequality-as-leak. It is not `leaked none` beside a status split.

That is why this is not FIX: nested packages failing to load, `/tmp` smear as rc=0 `leaked none`, and slots as unnamed FILE state are holes in the advertised isolation/join, not crashes of an otherwise complete object.

Do not grow leakorder's leftover-after dialect. Do not merge the two harvests.

---

## Mutation (what must change)

Keep the object: for a named pair, one isolated order per subprocess, report the binding whose start-of-victim value depended only on order, and the order that exposes a split.

Do not keep a sibling-only copy that cannot load a package helper, or a clean-pair printer for unsandboxed smear.

1. **Copy the importable tree, not only sibling `*.py`.** `from pkg.helper import bucket` and `from .helper import bucket` must load from the copy (FILE's directory / package parent on `sys.path`, package dirs copied) and name `bucket` `[]` vs `['a']` into `test_b` via `test_a` without the caller exporting `PYTHONPATH`. Reverse must PASS. A helper in FILE's parent is either copied or a one-line `ordleak:` that says it is outside the copy — not a bare `No module named 'helper'` that looks like a crash.

2. **Dual-FAIL smear is not a clean pair.** `leaked none` + rc=0 is legal only when every status is PASS. If any status is FAIL/ERROR and no snapshotted write is named, print `leaked <unseen>` and rc=1 — including the hardcoded `/tmp` leftover that makes both orders FAIL. MUTATE.md's leftover sentence (“that split is `<unseen>`”) is the spec; the CLI currently prints `none` / rc=0. Always-fail independent of order may keep `exposing_order none` but must not look like a green pair.

3. **FILE-level slots (and cache size) are identities or stay honestly unseen.** Encode `__slots__` so `box.n` is named `0` vs `1` via `test_a`, same as `__dict__` / dataclass. `lru_cache` `currsize` is either snapshotted or documented as refused; a status split there is already `<unseen>` — do not revert to `none`.

4. **Worker stdio is not the test stdio.** Capture order JSON on a side channel (fd / temp file). A test that writes `\xff` to stdout is an ERROR row or ignored bytes, not `utf-8 codec can't decode` with empty report. Bound that path.

5. **Do not become leakorder.** Start-of-victim across orders stays the join. Do not add leftover-after. Do not merge onto `main`.

If the mutation cannot do (1)+(2), nested helpers still do not load and unsandboxed smear still prints `leaked none` rc=0, and a later destroyer should KILL.

Do not merge with `leakorder`. Do not merge onto `main`.

---

MUTATE
