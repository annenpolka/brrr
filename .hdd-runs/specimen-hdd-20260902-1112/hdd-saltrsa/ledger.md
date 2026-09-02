# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B PEM rewritten leftover previous key object because get_rsa_key is @memoize on (path, passphrase) and omits mtime
- Case C new process is fresh; Case A same mtime is current

## Rejected

- Invented crypt-inspector gen-key / memoized-load / SHA3-256 transcripts are not host-executed

## Constraints

- Do not send salt get_rsa_key memoize theater back to R1. Distinct from 136 and 139.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover RSA key after file rotation
Nearest existing operation: grep @memoize get_rsa_key vs mtime omitted
Observable delta: leftover_saltrsa = memoize hit AND PEM rewritten AND mtime omitted from key
Reason: Dreamer restated omitted mtime from the seed; two greps already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
