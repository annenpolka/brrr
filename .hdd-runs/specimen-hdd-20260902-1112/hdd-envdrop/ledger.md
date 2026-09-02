# HDD Ledger

Iteration: 1

## Preserve

- A POSIX shim can drop env names that are not valid identifiers while the real binary keeps them

## Established

- Packet: TEST-VAR missing through node shim, present through managed binary

## Rejected

- Invented pnpm runtime set / docker transcripts are not host evidence

## Constraints

- No pnpm. Owned two env maps: before hop vs after. Transfer envlayers

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which process exec'd Node, and which environment names survived that hop

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name env keys dropped because they are not POSIX identifiers
Nearest existing operation: envlayers
Observable delta: TEST-VAR present vs MISSING
Reason: adjacent to envlayers; do not mint pnpm
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
