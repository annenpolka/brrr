# MUTATION — ordleak isolation/exit

Ordinary mutation of `candidate-ordleak` after First Selection
KEEP + MUTATE isolation/exit.

```yaml
origin:
  method: specimen-hdd
  trial: hdd-order
  mutation: ordinary isolation/exit
  parent: candidate-ordleak
worktree: /Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-ordleak-ordleak
branch: specimen-hdd/candidate-ordleak-ordleak
parent_commit: fbdb7ef86ccee6db878d3cc8f3f1ed309e3f425c
commit: 885095826c38e95d6db9d0b9868e51dbb32b8fef
cli_sha256: d3cec45bc522aa61de3342b69aae50bc64b4fddf840225cdd1914a01a24fa4f8
```

Not merged to `main`. Not installed on PATH.

## What was kept

The object: for a named pair, run both orders, name the binding whose
*start* value depended only on order, and name the exposing order.
Hidden PASS leaks still name the binding. Independent pairs still print
`leaked none`.

## What changed

1. **Isolation of certainty for class-attribute / function-local leaks.**
   The parent snapshotted only non-callable, non-class module globals.
   `class Box: items = []` and `holder.acc = []` produced a real status
   split and `leaked none` — false "nothing leaked". The mutation
   snapshots class attributes, function attributes, mutable defaults, and
   closure cells on that file. A status split with no snapshotted binding
   (`_`-prefixed module global) is `leaked unknown`, not `leaked none`.
2. **Non-zero exit when a leak is found.** Parent exited 0 on specimen-009
   (`leaked acc`, `exposing_order test_a test_b`). CLI now exits 1 when
   `leak_verdict` is `named` or `unknown`. Exit 0 only for a clean pair.
   Usage remains 2. `demo.sh` prints `exit: N` and itself exits 0.

## Before (parent, executed at First Selection)

```
ordleak files/test_order.py test_a test_b
exposing_order	test_a test_b
leaked	acc	into	test_b	[]	['a']	via	test_a
rc=0
```

Class-attribute / function-local (Unix, Heretic, Skeptic, DESTROYER_ordleak):

| shape | exposing_order | leaked | rc |
| --- | --- | --- | --- |
| `class Box: items = []` | `test_a test_b` | `none` | 0 |
| `holder.acc = []` | `test_a test_b` | `none` | 0 |
| `_acc = []` | `test_a test_b` | `none` | 0 |

## After (this mutation, archive `./demo.sh` ×2 identical)

`python3 tests/test_ordleak.py -v` — 11 OK.

`./demo.sh` exit 0 (wrapper). CLI rows:

```
== ordleak test_a test_b (both orders) ==
exposing_order	test_a test_b
leaked	acc	into	test_b	[]	['a']	via	test_a
exit: 1

== class-attribute Box.items ==
exposing_order	test_a test_b
leaked	Box.items	into	test_b	[]	['a']	via	test_a
exit: 1

== function-local holder.acc ==
exposing_order	test_a test_b
leaked	holder.acc	into	test_b	[]	['a']	via	test_a
exit: 1

== unseen _acc (honest unknown) ==
exposing_order	test_a test_b
leaked	unknown
exit: 1
```

Also named in tests: `bag.__defaults__[0]`, closure cell `acc`.
Independent pair: `leaked none`, exit 0.

Transcripts: `demo-1.log`, `demo-2.log` (byte-identical).

## Remaining holes (not this cut)

- Orders still share this process: imported helper modules, `os.environ`,
  and filesystem writes can poison order 2. `via` can then lie.
- FILE's directory is still not on `sys.path`.
- Pytest `Class.method` is still not a module callable.
- Unique-module class identity can still false-leak instance `==`.
- Import-time `time.time_ns()` is still reported as a leak.

Unix also asked for a fresh process per order. That is a later mutation.
This cut only stops class/function-local leaks from being silent-wrong
and makes a found leak a pipe-failing exit.
