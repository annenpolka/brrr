# HDD Ledger

Iteration: 2

## Preserve

- A cache load can wait on a shared object owned by another thread
- A waiter can block on a lock whose owner is another thread

## Established

- Packet: configuration-cache hang
- Packet: shared object wait

## Rejected

- jstack, SharedObjectRegistry traces, 92% hang are Dreamer-generated
- DeadlockSimulation.java is Dreamer-generated

## Constraints

- No Gradle
- Ground with threading.Lock owner/waiter labels

## Open Questions

- (none)

## Human Pressure

- No Gradle. Continue on two threads and one lock. Show owner vs waiter.

## Harvest Candidates

- Who owns the lock the waiter never acquired

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name lock owner vs waiter
Nearest existing operation: jstack
Observable delta: one query whose object is owner vs waiter
Reason: timeout does not name the owner
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
