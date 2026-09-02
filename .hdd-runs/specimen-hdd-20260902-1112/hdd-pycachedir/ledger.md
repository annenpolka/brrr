# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B interrupt after dir exists; Case C mkdir-then-set; both skip _ensure_supporting_files because _cachedir.exists() is true
- Case A first set on absent dir writes supporting files; Case D --cache-clear is a fresh identity

## Rejected

- Invented git clone pytest / Cache.set simulation transcripts are not host-executed

## Constraints

- Do not send pytest cache theater back to R1. Distinct from specimen-001-003.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover already-initialized .pytest_cache dir after supporting files were never written
Nearest existing operation: test -d .pytest_cache && test ! -f .pytest_cache/.gitignore
Observable delta: leftover_uninit = dir_exists AND NOT gitignore
Reason: Dreamer restated path.parent.is_dir / _cachedir.exists from the seed; two flags already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
