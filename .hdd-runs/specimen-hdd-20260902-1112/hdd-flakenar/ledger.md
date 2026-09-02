# HDD Ledger

Iteration: 1

## Preserve

- A fetcher cache can map git rev fingerprint R2 to NAR H_nar1 after a poisoned lock, then fail when the lock later names H_nar2

## Established

- Packet: cache keys on rev fingerprint; substitution can serve H_nar1 store path while fingerprint is R2; later H_nar2 correction mismatches
- Fresh cache with consistent R2/H_nar2 evals rev2

## Rejected

- Invented nix eval / sqlite transcripts are not host-executed

## Constraints

- Owned labeled rev/narHash records. No nix daemon.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether the substitution cache keyed the input by lock rev or lock narHash, and which NAR that key mapped to after poison

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover cache NAR for a rev fingerprint vs lock narHash after correction
Nearest existing operation: diff flake.lock narHash vs sqlite cache value for that rev
Observable delta: leftover_stale_nar = cache_nar != lock_nar for same rev
Reason: grep of the rev hits both lock and cache; the leftover is H_nar1 still bound to R2
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
