# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B two tracked projects both locked dummy 1.0.0; upgrade only bar to 2.0.0; failing_ref keep-set uses use_locked_version=false for every config so foo's lock pin is omitted
- Case A single-project stale lock uninstall is intended; Case C prune already use_locked_version=true

## Rejected

- Invented mise upgrade / mise ls / mise exec dummy@1.0.0 transcripts are not host-executed

## Constraints

- Do not send mise upgrade theater back to R1. Distinct from specimen-006/022/023/102/078.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover sibling lock pin after upgrade cleanup ignored use_locked_version for every tracked config
Nearest existing operation: grep foo/mise.lock version vs mise ls --installed
Observable delta: leftover_pin = foo_lock is 1.0.0 AND 1.0.0 not installed AND bar upgraded
Reason: Dreamer restated the seed Case B tables; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
