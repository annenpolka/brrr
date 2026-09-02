# MUTATE leakorder

Date: 2026-09-02 15:20 JST. Job: `job-0333`. Worker: `mutate-leakorder`.

CLI sha256 before (class-attr cut, `MUTATION.md`): `0f70b0735fbf2d2a9ce909f1246f74d6ae9267e9651256c57db1b64dd674bca7` (4755 bytes). DESTROYER original: `6710f7f5e1a4c959c2491d35804ace5504759ec703638da66f1f00f51c13581a` (4127 bytes).

CLI sha256 after: `d711f95c4a8ff27e55b75fc93cae58ea4e1ee1ff4e837df68e594466afaa767d` (20896 bytes).

```yaml
origin:
  method: specimen-hdd
  trial: hdd-order
  mutation: isolate orders, class attrs, sufficient split
  parent: candidate-leakorder
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-leakorder-isolate
branch: specimen-hdd/candidate-leakorder-isolate
parent_commit: 432f954 Heartbeat no-op after 09:00 hard end.
commit: 3fc09c071650729ecd97cabf809e7b028f0d0053
cli_sha256: d711f95c4a8ff27e55b75fc93cae58ea4e1ee1ff4e837df68e594466afaa767d
```

Not merged to `main`. Not installed on PATH. Not merged into `ordleak`.

From DESTROYER_leakorder.md: keep the object (for named callables, report the binding whose value depended only on order, and the order that exposes a status split). Do not keep a same-process deepcopy of `vars(mod)` that only replays specimen-009 and prints `none` on specimen-060.

## What was kept

The FILE CLI (`leakorder FILE`, optional `--order`). Order rows still print leftover-after. specimen-009 still names `acc` and `test_a,test_b`. The class-attr cut's `Box.bucket` name is kept.

## What changed

1. **Class attributes (and the other FILE hiding places) are snapshotted, or the split is `unknown`.** `Box.bucket`, `holder.acc`, `bag.__defaults__[0]`, closure `acc`, `_acc`, sibling `helper.n` are named. `leaked_names none` next to `sufficient_exposing_order` ≠ `none` is illegal: that case is `unknown` (env/fs, not snapshotted).
2. **Orders are isolated.** One subprocess per order. FILE's directory and its parent are on `sys.path`. `from helper import bucket` is `[]` vs `['a']` into `test_b` via `test_a`; reverse PASSes. `helper.n` is `n=11` / `n=10`, never `n=21`.
3. **Leak is order-dependent start; leftover is labeled leftover.** Order lines no longer print `leaked=acc` on an all-PASS order. `leftover={'acc': ['a']}` stays. `leaked_names` is a start-of-victim diff that also has a writer in FILE. `nan` and `object()` identity are not leaks. Custom `__eq__` does not hide `box.n`.
4. **`sufficient_exposing_order` is a status split.** Unique fail-vs-pass order. Empty file / `MISSING` / always-fail-in-both → `none`. Both-fail `test_b` plus real `acc` mutation names `acc` and `sufficient_exposing_order none`.
5. **Names are discovered.** Default is source-order `test_*` (and `test_*` assignments) plus reverse, not hardcoded `test_a,test_b`. `unseen_bucket.py` names `bucket` / `test_write,test_empty` without `--order`. `Class.method` instantiates `Class()`. `async def` / generators are ERROR, not PASS.
6. **`BaseException` is a test ERROR.** `SystemExit(3)` is `test_a=ERROR SystemExit: 3`, not CLI rc=3. FAIL detail (`['a']`) is printed. `repr` is capped. Load errors are `leakorder:` lines. rc=1 when a leak is named or a split is unnamed; rc=0 only for the clean pair. Missing file / usage remain rc=2.
7. **One meaning vs `ordleak`.** `leaked_names` is now start-of-victim (same harvest question as `ordleak`). Leftover-after remains a labeled `leftover=` column, not a second `leaked` dialect. `_acc` is named here (`ordleak` prints `unknown`). This CLI must not remain a competing harvest under the same name; later jury picks one. Do not merge the binaries.
8. **Dogfood is specimen-060 and a helper-module pair**, not a copy of specimen-009. specimen-012 is still byte-identical to 009 and is not cited as unseen.

## Leftover honesty

| order line | meaning |
| --- | --- |
| `leftover={'acc': ['a']}` | within-order leftover-after (green `test_a` still mutates) |
| `leaked_names  acc` | start of a victim differed across isolated orders, and a FILE writer exists |
| `leaked_names  unknown` | status split, no snapshotted writer (env/fs) |
| `leaked_names  none` | only when there is no split to name |

`leaked=` was removed from order lines so an all-PASS order cannot claim `leaked=acc`. Import-time `time.time_ns()` is not a leak (not a writer). Filesystem writes still smear across children (not reset).

## Before (DESTROYER / class-attr cut)

```
python3 leakorder specimen-060/files/test_class_leak.py
# DESTROYER original: leaked_names none, leftover={}, sufficient test_a,test_b, rc=0
# class-attr cut: leaked=Box.bucket on the PASS order too; same process; sufficient = first non-PASS
```

Helper without isolation: reverse FAIL, leftover `['a','a']`, `n=21`.

Empty file: `sufficient_exposing_order test_a,test_b`.

## After (this mutation, `./demo.sh` ×2 identical)

`python3 tests/test_leakorder.py -v` twice — 24 OK (only the unittest duration line differs).

`./demo.sh` twice: byte-identical (`demo-1.log` / `demo-2.log`). Wrapper exit 0; CLI exit 1 on each named leak.

```
== leakorder specimen-009 (module global acc) ==
order test_a,test_b  test_a=PASS test_b=FAIL ['a']  leftover={'acc': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leftover={'acc': ['a']}
leaked_names  acc
sufficient_exposing_order  test_a,test_b
exit: 1

== leakorder class-attribute Box.bucket ==
order test_a,test_b  test_a=PASS test_b=FAIL ['a']  leftover={'Box.bucket': ['a']}
leaked_names  Box.bucket
sufficient_exposing_order  test_a,test_b
exit: 1

== leakorder helper-module bucket ==
order test_a,test_b  test_a=PASS test_b=FAIL ['a']  leftover={'bucket': ['a']}
order test_b,test_a  test_b=PASS test_a=PASS  leftover={'bucket': ['a']}
leaked_names  bucket
sufficient_exposing_order  test_a,test_b
exit: 1
```

## Remaining failures (not faked)

- Filesystem marker files still smear: children share FILE's directory as cwd. Env is isolated; a FILE-dir write is not.
- Three-test files default to the full list and its reverse, not every pair. `--order` still required for a subset pair.
- `from .helper import bucket` without a package still fails (absolute `import helper` is the dogfood).
- No timeout kill of a runaway *test* beyond the 20s worker bound; infinite loops become `leakorder: timeout running order`.
- Same harvest question as mutated `ordleak` (start-of-victim). Distinct surface: leftover column, `_` names, discovery, FILE-only argv. Do not keep both as competing PATH installs.

If a later mutation drops isolation or prints `leaked_names none` next to a real split, KILL as `run_orders.py` with extra print.
