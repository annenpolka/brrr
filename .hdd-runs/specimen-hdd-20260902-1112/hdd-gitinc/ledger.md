# HDD Ledger

Iteration: 1

## Preserve

- A config unset that treats the value as a regex can fail and leave includeIf in place while the workflow still concludes successfully

## Established

- Packet: checkout writes includeIf.gitdir; post-job unset errors invalid pattern; leftover remains

## Rejected

- Invented git config transcripts on this host are not evidence

## Constraints

- No git. Owned records: unset_exit, leftover key. Transfer onto silentadd

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- leftover includeIf key after failed unset vs exit 0

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a leftover config key after an unset that failed as a regex
Nearest existing operation: silentadd
Observable delta: exit 0 with leftover includeIf
Reason: adjacent to silentadd; do not mint git
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
