# HDD Ledger

Iteration: 1

## Preserve

- A full System.getProperties snapshot can put an unread property into identity so a later unused change misses the cache

## Established

- Host analog: all_same False, used_same True, invalidate_unused True for idea.io.use.nio2 vs path
- Packet log: cannot be reused because system property idea.io.use.nio2 has changed

## Rejected

- cache-probe is not installed

## Constraints

- Owned two prop maps plus used-key list. No Gradle.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which unread properties entered identity and which of those changed

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name unused snapshot keys that changed identity while used keys did not
Nearest existing operation: lockident / print two hashes
Observable delta: invalidate_unused yes; unused idea.io.use.nio2
Reason: two hashes do not name the unread key
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
