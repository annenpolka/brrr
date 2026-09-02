# HDD Ledger

Iteration: 1

## Preserve

- experimental.fsModuleCache can mint a hashed identity for a module that the run then treats as external

## Established

- Packet: getCachePath runs before shouldExternalize; resolver is not in hashString; saveCachedModule skipped when externalized so no disk write
- Other externalize paths never mint that identity

## Rejected

- Invented vitest run transcripts are not host-executed

## Constraints

- Owned labeled cache-key records. No vitest.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether a leftover cache key H_ext was minted for an externalized module (memory yes, disk no)

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover fsModuleCache key minted before shouldExternalize
Nearest existing operation: grep DEBUG vitest:cache:memory write vs fs empty
Observable delta: leftover_key = memory key present and disk write no when externalize yes
Reason: grep of the module id hits both logs; the leftover is H_ext without a file
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
