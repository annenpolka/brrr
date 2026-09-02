# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B leftover previous formatter output is reused because incremental_hash hashed the raw dprint.jsonc plugin map and omitted the plugin's resolved cache_key
- Case C clear-cache is fresh; Case D resolved config in hash misses after cacheKeyFiles change

## Rejected

- Invented dprint fmt / cache info transcripts are not host-executed
- Dreamer restated leftover config_hash unchanged after rustfmt.toml from the seed

## Constraints

- Do not send dprint cacheKeyFiles theater back to R1. Distinct from 132/133/114.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover incremental cache after a cacheKeyFiles change when resolved plugin cache_key is omitted
Nearest existing operation: grep format_config.plugin vs serialized_resolved_config in incremental_hash
Observable delta: leftover_cache = rustfmt.toml changed AND hash still raw plugin map
Reason: Dreamer restated leftover omitted resolved cache_key from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
