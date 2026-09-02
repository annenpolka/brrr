# waitoneshot

origin.method: specimen-hdd
origin.trial: hdd-k8s
specimens: [specimen-044, specimen-056]

classification: USEFUL_COMPOSITION

## Primitive

For wait flags, report whether timeout 0 still visits the object or aborts
on a creation-wait default.

## Why this might not exist

Timeout 0 is documented as check once. A creation-wait default can refuse
before lookup. The error string looks like a bad flag. Help text plus that
error still leave abort-before-visit versus one-shot check as a hand join.

## Core operation

Take timeout, wait-for-creation, for-condition, and whether the object
exists. Print visited, oneshot, abort, and reason.

## Observable delta

One query names abort-before-visit versus a one-shot check. Reading help
text plus `--wait-for-creation requires a timeout value greater than 0`
does not.

## Reality mapping

Owned flag records (no cluster). specimen-056:

```
timeout=0 wait_for_creation=true for=jsonpath object_exists=true → abort, visited false
timeout=0 wait_for_creation=false for=jsonpath object_exists=true → oneshot visit
timeout=0 wait_for_creation=true for=delete object_exists=true → oneshot visit
```

specimen-044 is the kubectl wait timeout-0 origin of that table. kubectl is
not executed here.

## Research boundary

Does not talk to a kube API. Does not evaluate jsonpath. Does not wait.

## Removed

live cluster, invented kubectl transcripts.

## Smallest artifact

Python 3 stdlib CLI `waitoneshot` wrapping `decide()`.

## Pre-implementation Reality assessment

- Classification: USEFUL_COMPOSITION
- Nearest existing operation: read help text plus the error string
- Observable delta: one query that names abort-before-visit vs one-shot check
- Constraint: observable evidence is flag records, not a cluster
- Established on the fixture: the three specimen-056 rows above

## How to run

From this directory:

```
python3 tests/test_waitoneshot.py
./demo.sh
```

## Empirical transcript

Host-executed 2026-09-02. `./demo.sh` (twice; `demo-1.log` and `demo-2.log` match):

```
== fixture .../specimen-056/files/flags.txt ==
timeout=0 wait_for_creation=true for=jsonpath exists=true

== nearest existing operation (help text plus error string) ==
timeout help: Zero means check once and don't wait
wait-for-creation default: true; ignored in --for=delete
error: --wait-for-creation requires a timeout value greater than 0
(the error does not name abort-before-visit vs one-shot check)

== specimen-044 wait.go abort (origin excerpt, not executed) ==
34:if o.WaitForCreation && o.Timeout == 0 {
35-return fmt.Errorf("--wait-for-creation requires a timeout value greater than 0")
36-}

== waitoneshot timeout 0 wait-for-creation true (abort before visit) ==
timeout  0.0
wait_for_creation  true
for  jsonpath
object_exists  true
visited  false
oneshot  false
abort  wait-for-creation-requires-timeout
reason  creation-wait default aborts before lookup when timeout is 0

== waitoneshot timeout 0 wait-for-creation false (oneshot visit) ==
timeout  0.0
wait_for_creation  false
for  jsonpath
object_exists  true
visited  true
oneshot  true
abort  none
reason  one-shot check

== waitoneshot timeout 0 for=delete (oneshot) ==
timeout  0.0
wait_for_creation  true
for  delete
object_exists  true
visited  true
oneshot  true
abort  none
reason  one-shot check
```

Help text plus the error still look like a user mistake. `waitoneshot`
names `visited false` and `abort wait-for-creation-requires-timeout`.

Tests: 15 OK (`python3 tests/test_waitoneshot.py`).

## Dogfood targets

- specimen-056 `flags.txt` (owned, executed as flag records).
- specimen-044 wait.go excerpt (origin only; no cluster).
- Destroyer extra: timeout 5 + wait-for-creation true + missing object is
  wait-path, visited false, not oneshot.

## Surprises

`for=delete` is oneshot even when wait-for-creation is true: the harvest
and the flag help (`ignored in --for=delete`). The wait.go excerpt still
tests `WaitForCreation && Timeout == 0` before `isForDelete`. This tool
follows the harvest table, not a live binary.

A missing object with timeout 0 and wait-for-creation true still aborts
before lookup. Existence is not consulted on that path.

## Failures

Does not wait, watch, or talk to a kube API. Does not evaluate jsonpath
on an object body. Negative timeout is not the kubectl "wait a week"
path; only `timeout == 0` is oneshot. `for` is case-sensitive (`delete`,
not `Delete`). Exit is 0 even on abort; the abort field is the object.

## Suggested mutations

- Parse specimen-056 `flags.txt` as `--file` input
- Exit 1 on abort
- Case-fold `--for` the way kubectl does
- Name the excerpt's abort-before-isForDelete as a separate row

## Kill / keep

Keep: timeout 0 + wait-for-creation true aborts before visit. Timeout 0 +
wait-for-creation false is a oneshot visit. `for=delete` is oneshot.
Destroyer KEEP 2026-09-02.
