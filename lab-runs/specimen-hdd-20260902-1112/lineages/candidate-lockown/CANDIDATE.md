# candidate-lockown — lockown

origin:
  method: specimen-hdd
  trial: hdd-gradleid

classification: USEFUL_COMPOSITION

## Primitive

Name who owns a lock versus who is waiting on it.

## Why this might not exist

`threading.Lock.acquire(timeout=...)` returns False. `locked()` is a
boolean. A thread list does not label roles. jstack-style dumps leave a
hand join from waiter stack to lock id. Timeout does not name the owner.

## How to run

From the worktree product dir
(`$HOME/.grok/worktrees/annenpolka-brrr/candidate-lockown-lockown/lockown`):

```bash
./lockown
./demo.sh
python3 tests/test_lockown.py
```

## Reality assessment (pre-implementation)

Copied from harvest before code:

- Classification: USEFUL_COMPOSITION
- Nearest: threading.Lock.acquire timeout; locked(); thread list / jstack
- Delta: one query whose object is owner vs waiter
- Mapping: two named threads, one Lock; record owner on acquire, waiter
  while blocked; snapshot the pair
- Constraint: Python threading only; no Gradle
- Full copy: `REALITY.md`

## Empirical transcript

### First working commit (`50d136e`)

`python3 tests/test_lockown.py -v`: 8 tests, OK, 2.943s.
`./demo.sh` (`/usr/bin/time -p`, real 2.63s):

```
== nearest existing operation (threading.Lock.acquire timeout) ==
acquire_ok  false
locked  true
(timeout does not name the owner)

== lockown two threads one lock ==
lock  L
owner  holder
waiter  blocked
held  true
```

The pair is correct. After the snapshot the CLI joined the waiter until
`acquire(timeout=2)` returned False. That is the nearest operation: a
timeout that still does not name the owner, paid after the query already
had the pair.

### After dogfood

Owner releases immediately after the snapshot. Waiter is still a waiter at
query time. Demo does not wait out a timeout.

`python3 tests/test_lockown.py -v`: 10 tests, OK, 1.264s.
`./demo.sh` real 0.28s. `./demo.sh` twice (`demo-1.log`, `demo-2.log`)
identical:

```
== nearest existing operation (threading.Lock.acquire timeout) ==
acquire_ok  false
locked  true
(timeout does not name the owner)

== lockown two threads one lock ==
lock  L
owner  holder
waiter  blocked
held  true
```

CLI `lockown` (no args) finishes in under 1s
(`test_cli_does_not_wait_out_waiter_timeout`).

`fixtures/timeout_only.py` still has `acquire_ok` / `locked` and no `owner`
or `waiter` field.

## Dogfood targets

Done in the second commit:

- First demo spent ~2.6s waiting for the waiter to time out after the
  pair was already printed.
- CLI now releases the owner after snapshot so the waiter never has to
  time out for the process to exit.

## Surprises

- `threading.Lock` really has no owner. `locked()` after a failed timeout
  is `true` and still does not say `holder`.
- The first CLI was accidentally demonstrating the nearest operation
  (timeout) as its shutdown path.

## Failures

- Does not attach to another process or parse jstack.
- Stdlib `threading.Lock` has no owner; without the wrapper the pair is a
  hand join.
- One waiter field: extra waiters are recorded internally but only the
  first is printed.
- Not reentrant; this is `Lock`, not `RLock`.

## Suggested mutations

- Print every waiter, still one lock.
- Snapshot after timeout (waiter gone; timeout still unnamed).
- Named lock objects beyond the built-in two-thread scene.

## Kill / keep

Keep while the object is owner vs waiter on one lock. Kill if it becomes
a thread dump.
