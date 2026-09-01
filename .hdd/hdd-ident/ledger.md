# HDD Ledger

Iteration: 1

## Preserve

- The CLI takes two entities and reports identical vs distinct with a stated discriminator.
- Hardlink vs distinct file and JSON key-order canonicalization were attempted locally.

## Established

- same A B; symlink treated as distinct type; JSON canonical match; schema mismatch error.

## Rejected

- https ETag, docker digest, postgres vs mongodb schema counts are unsupported.

## Constraints

- No network, docker, or database protocols.
- Identity kind must be explicit (inode, bytes, parsed-json). Do not silently pick a discriminator.
- Operate on real local files.

## Open Questions

- Is explicit identity-kind comparison a distinct verb from stat/cmp/jq, or only a flag bundle?

## Human Pressure

- (none)

## Harvest Candidates

- Ask whether two local names are the same under an explicit identity kind, and refuse if the kind is unspecified.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: compare two local names under an explicit identity kind and report the discriminator
Nearest existing operation: stat inodes, cmp/shasum, jq -S
Observable delta: one command that names the identity kind and refuses mixed kinds; not yet shown without network lore
Reason: worth one local-only turn; do not add more entity types
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no network and no container registry. Continue on real local files only.
- The identity kind must be an explicit flag. If omitted, list possible kinds and exit nonzero.
- Do not invent ETags, digests, or schemas.

## Pending

(none)
