# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B two JSR packages share npm:dep; dropping one JSR root purges the npm specifier from specifiers while remaining jsr.dependencies still names it
- Public error: Invalid jsr dependency 'npm:preact@^10.22.1' for '@preact-icons/common@1.1.0'

## Rejected

- Invented deno cache --lock-write / jq / deno upgrade transcripts are not host-executed
- Dreamer claimed the repair keeps npm in both specifiers and jsr.dependencies; that is not a host observation of failing_ref

## Constraints

- Do not send deno lockfile theater back to R1. Distinct from specimen-004/082/095.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover npm: specifier inside jsr.dependencies after specifiers no longer has it
Nearest existing operation: jq jsr[].dependencies vs specifiers keys in deno.lock
Observable delta: leftover_npm = jsr_dep is npm: AND specifier missing
Reason: Dreamer restated the seed Case B tables and the public deserialize error; two JSON greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
