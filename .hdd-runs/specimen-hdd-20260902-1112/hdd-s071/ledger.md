# HDD Ledger

Iteration: 1

## Preserve

- A FRESH hit can keep an extra file that exists only as a 0-byte hashing stub
- A cache keyed only by inputs can write an empty extra stub on first miss, then report FRESH when a later request asks for that extra

## Established

- Host: first BUILT extra_exists True extra_bytes 0; second FRESH extra_requested True extra_bytes 0 same key 9280cc7e16e9 stub_leftover True
- Owned cache_build_stub.py: first BUILT extra_requested False extra_exists True extra_bytes 0 key 9280cc7e16e9; second FRESH extra_requested True extra_exists True extra_bytes 0; same_key True; stub_leftover True

## Rejected

- cachetool is not installed
- Invented cachetool inspect/build transcripts and hashes are not host evidence

## Constraints

- Transfer onto freshmiss; bytes NAME 0; no new binary
- No cachetool. Owned two events: extra_requested vs extra_bytes vs same key. extraedge is poetry extras, not this leftover stub

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- FRESH extra present with zero bytes is a stub leftover, not FRESH-complete
- whether the extra file was produced for this request or leftover from the identity write, and which requested outputs were outside that identity

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover extra stub on FRESH vs extra produced for this request
Nearest existing operation: extraedge / print cache key
Observable delta: leftover_stub yes; produced_for_request no; extra_outside_identity yes
Reason: adjacent to extra identity but leftover bytes vs declared extras
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
