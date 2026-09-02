# HDD Ledger

Iteration: 2

## Preserve

- A fingerprint can ignore a newly requested lint/flag so the second build looks fresh
- Toggling -Zpublic-dependency on a reused target/ can keep the previous warning presence
- A fingerprint that omits flags can stay FRESH when a flag appears

## Established

- Packet: public-dependency fingerprint
- Packet: after check -Zpublic-dependency, plain check still warns and prints no [CHECKING]
- freshmiss already reports omitted extras

## Rejected

- cargo 1.97 nightly transcripts are Dreamer-generated
- Invented dep-lib-foo fingerprint bytes and cargo internals are not host evidence
- freshmiss create fp.bin is not the harvested CLI

## Constraints

- No cargo
- No cargo/nightly. Owned fingerprint-component fixture. Transfer onto freshmiss
- Transfer-test, no second fingerprint engine

## Open Questions

- (none)

## Human Pressure

- No cargo. Continue on an owned key that omits a flag. Show FRESH-but-flag-changed.

## Harvest Candidates

- Which flag was omitted from the freshness identity
- Which flag/config component was omitted from the fingerprint
- omitted flag from identity

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a flag omitted from freshness identity
Nearest existing operation: freshmiss
Observable delta: FRESH-but-flag-changed
Reason: same family as missing extra output
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
