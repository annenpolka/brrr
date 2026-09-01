# HDD Ledger

Iteration: 2

## Preserve

- The CLI takes two entities and reports identical vs distinct with a stated discriminator.
- Hardlink vs distinct file and JSON key-order canonicalization were attempted locally.
- Omitted kind exits nonzero and lists --inode --bytes --json.
- Kinds are mutually exclusive.
- --bytes follows symlinks; --inode does not treat symlink as the file.
- Empty files: identical under --bytes, distinct under --inode.

## Established

- same A B; symlink treated as distinct type; JSON canonical match; schema mismatch error.
- same --inode, --bytes, --json on local files; JSON key-order independent; invalid JSON errors.

## Rejected

- https ETag, docker digest, postgres vs mongodb schema counts are unsupported.
- Printed sha256 prefixes were not computed in this environment as shown.

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
- Compare two local paths under exactly one explicit identity kind.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: compare two local names under exactly one explicit identity kind (inode, bytes, or canonical JSON)
Nearest existing operation: stat, cmp, jq -S
Observable delta: refuses mixed or omitted identity kind; one verb for three discriminators with named output
Reason: not a new identity theory; the exclusive-kind contract is harvestable; further dreaming would add directory lore
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
