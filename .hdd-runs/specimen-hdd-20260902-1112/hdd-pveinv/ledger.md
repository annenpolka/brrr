# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B new LXC then leftover cache file because get_cache_key(path) is inventory file identity and refresh (cache=False) refetches in memory without writing _cache[cache_key]=results
- Case C cache dir deleted is fresh; Case A unchanged Proxmox is current

## Rejected

- Invented ansible-inspect key-provenance / simulate-refresh / cache-identity transcripts are not host-executed

## Constraints

- Do not send ansible proxmox inventory-cache theater back to R1. Distinct from 136 and 142.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover inventory after refresh_inventory
Nearest existing operation: grep get_cache_key(path) vs nested _cache[key][url] write
Observable delta: leftover_pveinv = jsonfile cache hit AND refresh omitted persist AND new LXC missing
Reason: Dreamer restated omitted persist from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
