# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B SYSTEMD_UNIT_PATH=/foo::/bar leftover cwd search path because get_paths_from_environ splits empty components and path_split_and_make_absolute turns them into .
- Case C empty string is empty search path; Case A unset is defaults; Case D trailing : appends defaults

## Rejected

- Invented path-behavior-analyzer simulate-env / leftover_cwd transcripts are not host-executed

## Constraints

- Do not send systemd empty-path-component theater back to R1. Distinct from 010/031/149.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover cwd after empty :: in search path
Nearest existing operation: grep path_split_and_make_absolute vs FIXME empty components
Observable delta: leftover_sdpath = empty :: split AND made absolute AND cwd . in search path
Reason: Dreamer restated leftover cwd from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
