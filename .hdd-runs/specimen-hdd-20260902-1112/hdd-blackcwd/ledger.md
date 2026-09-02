# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B CWD change with leftover lru_cache keeps previous project root because find_project_root hashes (srcs, stdin_filename) and resolves Path.cwd() inside the cached function on failing_ref
- Case C new process is fresh; Case A same CWD is current

## Rejected

- Invented REPL /tmp/projectA /tmp/projectB find_project_root.cache_info transcripts are not host-executed

## Constraints

- Do not send black lru_cache CWD theater back to R1. Distinct from 114.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover project root after CWD change
Nearest existing operation: grep @lru_cache find_project_root vs Path.cwd inside cache
Observable delta: leftover_blackcwd = lru_cache hit AND CWD changed AND CWD omitted from key
Reason: Dreamer restated omitted CWD from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
