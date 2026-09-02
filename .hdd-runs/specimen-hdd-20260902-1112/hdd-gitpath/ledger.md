# HDD Ledger

Iteration: 1

## Preserve

- Two Cargo.toml PathBufs can differ only by a surviving .. segment and still name the same checkout directory

## Established

- Packet: CARGO_HOME with .. makes visited HashSet see two lexical keys for one git PackageId; warning lists both spellings; build finishes
- Case A without .. has one PathBuf per id; case C is a true two-directory name clash

## Rejected

- Invented inspect-path / hashset-insert transcripts are not host-executed

## Constraints

- Owned two path spellings. No cargo.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether a git PackageId mapped to leftover lexical-dotdot PathBuf plus collapsed PathBuf, or a true two-directory clash

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover lexical .. PathBuf vs collapsed path for the same package id
Nearest existing operation: realpath / os.path.normpath the two warning lines
Observable delta: lexical_dup with same_after_collapse vs true two dirs
Reason: grep of the package name hits both warning lines; the leftover is .. still in one path
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
