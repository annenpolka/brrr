# hybrid-zerowhy — zerowhy

```yaml
origin:
  method: specimen-hdd
  kind: hybrid
  parents: [swallowecho, waitoneshot]
```

classification: USEFUL_COMPOSITION

## Primitive

Classify a lying zero / green as exactly one of `swallowed-nonzero`,
`abort-before-visit`, `observed-ok`, `unknown`.

## Why this might not exist

`swallowecho 'false || echo ok'` names a swallowed nonzero with step
status 0. `waitoneshot --timeout 0 --wait-for-creation true` names
abort-before-visit. Concatenating those reports still leaves a hand join:
which one *is* this green? Neither parent emits an exclusive class. A
wrapper that prints both is a mashup. The object is the XOR: one `why`,
or `unknown` when both claim the zero.

## Core operation

Take a small shell snippet and/or wait flags. Reimplement `decide_shell`
(`||` hid a nonzero and step is 0) and `decide_wait` (timeout 0 plus
creation-wait aborts before lookup). Collect claims, then keep exactly
one class. Two distinct claims become `unknown`.

## Observable delta

One query prints `why  swallowed-nonzero` (or abort / observed-ok /
unknown). `swallowecho` then `waitoneshot` does not.

## Reality mapping

Owned analogues (executed):

```
false || echo ok
  → swallowed-nonzero

timeout=0 wait_for_creation=true for=jsonpath object_exists=true
  → abort-before-visit

timeout=0 wait_for_creation=false for=jsonpath object_exists=true
  → observed-ok
```

Both swallow and abort in one invocation → `unknown` with
`claims  swallowed-nonzero abort-before-visit`.

## Research boundary

Does not run Bazel or kubectl. Does not shell out to parent binaries for
the answer (parents are oracles in tests). Unmodeled heads are a refusal.

## Removed

Concatenating parent stdout. Guessing status for `make` / `bazel`.

## Smallest artifact

Python 3 stdlib CLI `zerowhy` wrapping `classify()`.

## How to run

From this directory:

```
python3 tests/test_zerowhy.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `python3 tests/test_zerowhy.py -v`: 36 tests, OK.
`./demo.sh` twice (`demo-1.log`, `demo-2.log`) identical.

Nearest existing (parents concatenated, not the object):

```
step_status	0
swallow	yes
swallowed	false
...
timeout  0.0
visited  false
abort  wait-for-creation-requires-timeout
(two reports; no exclusive why)
```

```
== zerowhy 'false || echo ok' ==
why  swallowed-nonzero
claims  swallowed-nonzero
detail  || hid a nonzero; step status 0

== zerowhy --timeout 0 --wait-for-creation true ==
why  abort-before-visit
claims  abort-before-visit
detail  timeout 0 aborted before visiting the object

== zerowhy --timeout 0 --wait-for-creation false --object-exists true ==
why  observed-ok
claims  observed-ok
detail  oneshot visit

== zerowhy both swallow and abort (exclusive refuses) ==
why  unknown
claims  swallowed-nonzero abort-before-visit
detail  two reasons for the zero; exclusive class refuses
```

Parent oracles agree on the three demo rows and still differ in stdout:
`swallowecho` prints `swallow yes`; `waitoneshot` prints `visited false`;
`zerowhy` prints one `why`. Concatenation is not equal to this CLI.

## Dogfood targets

- `false || echo ok` / `true && echo ok`
- waitoneshot timeout-0 creation-wait abort
- waitoneshot timeout-0 oneshot visit
- join: snippet plus abort flags in one query

## Surprises

`false; echo ok` is step 0 without a `||` swallow, so it is `unknown`, not
`observed-ok`. `true && echo ok` is `observed-ok` because every executed
command was 0. Two `observed-ok` claims collapse to one class; a swallow
plus a visit is two classes and refuses.

## Failures

Unmodeled heads (`make test || true`) exit 2. Wait flags without
`--timeout` exit 2. Exit is 0 on `unknown`; the class is the object.
Does not treat pipe-last-status as this swallow.

## Suggested mutations

- `--status N` for unexecuted pipelines
- Exit 1 on `unknown`
- Parse a CI step that has both a wait invocation and a `|| echo`

## Kill / keep

Keep if the three demo rows stay exclusive and the join of swallow plus
abort is `unknown` rather than concatenated parent stdout.
