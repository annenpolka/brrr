# Reality assessment (pre-implementation)

Copied from harvest before code. origin.trial: hdd-gradleid.

classification: USEFUL_COMPOSITION

## Core operation

Name who owns a lock versus who is waiting on it.

## Nearest existing operation

`threading.Lock.acquire(timeout=...)` returning False, plus `Lock.locked()`,
plus listing threads. jstack-style dumps join a waiter stack to a lock id by
hand. A timeout does not name the owner.

## Observable delta

One query whose object is owner vs waiter. Timeout-plus-locked still leaves
the owner unnamed.

## Reality mapping

Python 3 `threading.Lock` only. Two named threads, one lock. The stdlib lock
does not record an owner, so the composition is: record owner on acquire,
record waiter while acquire is blocked, snapshot the pair while the waiter
still has not acquired.

## Research boundary

Does not run Gradle. Does not attach to another process. Does not parse
jstack. Does not use `RLock` owner internals as the public object. Does not
invent Java deadlock theater.

## Removed

Gradle configuration-cache hang, SharedObjectRegistry, DeadlockSimulation.java,
invented jstack transcripts.

## Smallest artifact

Python 3 stdlib CLI `lockown` that runs two threads on one lock and prints
owner vs waiter.

## Why existing tools are not enough

`acquire` timeout is `False`. `locked()` is a boolean. Thread lists do not
label the roles. The join (this waiter, that owner, same lock) is a hand
comparison.
