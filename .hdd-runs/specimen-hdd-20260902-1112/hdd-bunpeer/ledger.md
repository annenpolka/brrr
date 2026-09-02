# HDD Ledger

Iteration: 1

## Preserve

- A name can remain as a packages identity after remove while the never-installed lock only mentioned it in optionalPeers metadata

## Established

- Packet: never-install has no packages entry whose prefix is "no-deps": ["no-deps@; after add-then-remove the packages identity remains

## Rejected

- Invented bun add/remove transcripts are not host-executed

## Constraints

- Owned two lock excerpts. No bun.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether a name is a leftover packages identity or only mentioned in peer metadata

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover packages identity vs metadata-only mention after remove
Nearest existing operation: grep the lock for the name
Observable delta: packages yes vs mentioned-only
Reason: grep hits optionalPeers in both locks
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
