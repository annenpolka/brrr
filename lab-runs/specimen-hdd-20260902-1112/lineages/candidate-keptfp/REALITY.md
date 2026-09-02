# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Name which cache fingerprints still match the current lockfile versus leftover hashes.

## Nearest existing operation

`ls` plus `grep` of fingerprint directories.

## Observable delta

One query names leftover vs live without a whole-cache wipe. Listing dirs
still leaves “this hash is current, those hashes are leftover” as a hand join.

## Reality mapping

Owned record: current lockfile hash plus (id, member, lockfile_hash, size).
uv is not executed. No files are deleted.

## Research boundary

Does not reconstruct cargo/uv fingerprint directories. Does not claim disk
reclamation. Size is a recorded field, not measured.

## Removed

Invented `uv cache list/clean` CLIs.

## Smallest artifact

Python 3 stdlib CLI `keptfp`.
