# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B package.py change with leftover concretizer cache keeps previous dag_hash because cache stores fully-finalized specs and omits _finalize_concretization on hit on failing_ref
- Case C cache off / spack clean -m is fresh; Case A unchanged package.py is current

## Rejected

- Invented spack --version / sed install() / mo2ogtq / xyzabcde transcripts are not host-executed

## Constraints

- Do not send spack concretizer-cache theater back to R1. Distinct from 136/140.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover spec hash after package.py change
Nearest existing operation: grep _conc_cache.store vs _finalize_concretization on cache hit
Observable delta: leftover_spackconc = cache hit AND package.py changed AND re-finalization omitted
Reason: Dreamer restated omitted re-finalization from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
