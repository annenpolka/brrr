# HDD Ledger

Iteration: 1

## Preserve

- A pinned rev fetch can hash a different tree when a fallback ref is added

## Established

- Packet: two records share rev/lastModified/revCount; disagree on narHash and whether ref is present

## Rejected

- Invented nix eval fetchGit transcripts are not host evidence

## Constraints

- No nix. Owned two identity records. Transfer onto lockident/freshmiss

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which identity field (ref) changed the hash while rev stayed

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name an identity field present in one hash and omitted from the other while rev is equal
Nearest existing operation: lockident / freshmiss
Observable delta: ref=master vs no ref, same rev, different narHash
Reason: adjacent to lockident
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
