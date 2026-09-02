# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B leftover previous-env task output is reused because expand_env does not push env_file onto inputs and get_file_hashes skips gitignored paths
- Case C wipe cache is fresh; Case D hash env file even if gitignored

## Rejected

- Invented source-inspection transcripts are not host-executed
- Dreamer restated leftover omitted .env input from the seed

## Constraints

- Do not send moon .env-input theater back to R1. Distinct from 119/115/133.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover task cache after a .env change when the env file is omitted from hash
Nearest existing operation: grep expand_env inputs.push vs get_file_hashes is_file_ignored
Observable delta: leftover_cache = .env changed AND file not in hashed inputs
Reason: Dreamer restated leftover omitted .env input from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
