# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B --flush-cache with leftover inventory plugin cache keeps previous parse because InventoryManager always parse_sources(cache=True) and _flush_cache only clears facts on failing_ref
- Case C delete jsonfile cache is fresh; Case A no-flush is current

## Rejected

- Invented ansible-playbook / cache_dir / host1 vs host2 transcripts are not host-executed

## Constraints

- Do not send ansible inventory-flush theater back to R1. Distinct from 136.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover inventory after --flush-cache
Nearest existing operation: grep parse_sources(cache=True) vs _flush_cache facts-only
Observable delta: leftover_ansflush = inventory cache hit AND --flush-cache AND inventory omitted from flush
Reason: Dreamer restated omitted inventory flush from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
