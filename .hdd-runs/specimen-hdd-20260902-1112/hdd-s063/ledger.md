# HDD Ledger

Iteration: 1

## Preserve

- After a crashed worker is replaced, a work unit already completed can be put back on the queue and the replacement never finishes

## Established

- Packet: --dist=loadgroup hangs after faulthandler kills a worker; other dist modes finish

## Rejected

- Invented xdist DEBUG scheduler transcripts are not host evidence

## Constraints

- No pytest-xdist. Owned events: unit, completed, requeued, assigned

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which work units were requeued after the crash, which were already completed, and which the replacement never finished

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a completed work unit that was requeued to a replacement worker
Nearest existing operation: read the hang log
Observable delta: completed vs requeued vs unfinished
Reason: hang log still leaves that join as a hand comparison
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
