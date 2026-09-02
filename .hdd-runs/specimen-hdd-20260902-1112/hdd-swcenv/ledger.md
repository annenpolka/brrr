# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B second in-process compile with different jsc.transform.optimizer.globals.envs keeps previous replacements because GlobalInliningPassEnvs::Map caches on self.vars and omits envs on failing_ref
- Case C new process is fresh; Case A same vars+envs is current

## Rejected

- Invented swc-diag cache-key analyze / cache simulate transcripts are not host-executed

## Constraints

- Do not send SWC envs-cache theater back to R1. Distinct from 090/156. In-flight before 22:45 freeze; no new Cambrian.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover optimizer env after envs map change
Nearest existing operation: grep cache_key from self.vars vs envs omitted
Observable delta: leftover_swcenv = DashMap hit AND vars identical AND envs omitted from key
Reason: Dreamer restated omitted envs from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
