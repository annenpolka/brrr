# HDD Ledger

Iteration: 1

## Preserve

- Fallback cache restore can retain superseded workspace fingerprints beside live ones
- Workspace-member fingerprints from an older lockfile can sit beside live artifacts after a lockfile bump

## Established

- specimen-006 uv prune stale workspace cache
- Packet: CI Rust cache grows across lockfile updates; external deps should remain

## Rejected

- uv cache list JSON in this turn is Dreamer-generated
- Invented uv cache list/clean --exclude-lockfile-hash and uv lockfile-hash are not host evidence

## Constraints

- Transfer onto lockident/freshmiss family
- No uv. Owned records: current lockfile hash plus (id, member, lockfile_hash, size)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which fingerprints are superseded vs live
- Name live vs leftover fingerprints against the current lockfile hash without deleting the whole cache

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name which cache fingerprints still match the current lockfile versus leftover hashes
Nearest existing operation: ls plus grep of fingerprint dirs
Observable delta: one query names leftover vs live without a whole-cache wipe
Reason: adjacent to freshmiss; lockfile hash is the identity, leftover entries are the miss
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
