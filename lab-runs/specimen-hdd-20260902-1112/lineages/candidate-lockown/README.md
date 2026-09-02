# lockown

Name who **owns** a `threading.Lock` versus who is **waiting** on it.

`Lock.acquire(timeout=...)` returning False, plus `locked()`, does not name
the owner. This command runs two threads on one lock and prints the pair.

origin:
  method: specimen-hdd
  trial: hdd-gradleid

## Primitive

One query whose object is owner vs waiter.

## Install / run

Python 3 stdlib only. From this directory:

```bash
./lockown
./demo.sh
python3 tests/test_lockown.py
```

Exit: `0` pair observed, `2` owner or waiter missing, `1` scene error.

## Output

Two spaces between field and value.

```
lock  L
owner  holder
waiter  blocked
held  true
```

`--contrast` is the nearest existing operation (timeout, owner unnamed).

The default scene snapshots while the waiter is blocked, then releases the
owner so the process does not wait out an acquire timeout.

## Boundary

Python `threading.Lock` only. Does not attach to another process, parse
jstack, or run Gradle. The stdlib lock has no owner field; labels are
recorded on acquire/wait and snapshotted while the waiter is blocked.
