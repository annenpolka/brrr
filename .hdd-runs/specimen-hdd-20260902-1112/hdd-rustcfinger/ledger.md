# HDD Ledger

Iteration: 1

## Preserve

- Two rustc binaries can share path and clamped mtime and still print different Fedora host strings in rustc -vV

## Established

- Packet: rustc_fingerprint hashes resolved path + mtime only; Cache::load reuses .rustc_info.json on equal fingerprint and does not re-run -vV
- Owned split: same /usr/bin/rustc and 2024-10-17 mtime, vv fc42 vs fc40

## Rejected

- Invented Cache::load / cargo build transcripts are not host-executed

## Constraints

- Owned two rustc identity records. No cargo/rustc required for the identity question.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether two rustc identities collide on path+mtime fingerprint while verbose-version host strings differ

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name fingerprint collision vs -vV mismatch for two rustc identities
Nearest existing operation: diff two rustc -vV strings; compare path and mtime
Observable delta: hidden_by_fingerprint when path+mtime match and vv differs
Reason: path/mtime equality and vv mismatch are two observations; the join is cache reuse hiding the compiler
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
