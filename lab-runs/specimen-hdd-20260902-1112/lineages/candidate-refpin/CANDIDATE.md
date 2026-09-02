# refpin

origin.method: hdd
origin.trial: hdd-s064
specimens: [specimen-064]

classification: USEFUL_COMPOSITION

## Primitive

Name whether a default ref attached to a fully pinned rev, and whether that
changed narHash identity while rev stayed.

## Why this might not exist

Two lock records share `rev`. Diffing them still leaves “the second grew
`ref=master` and that is the identity change” as a hand join. lockident
names blob-digest membership of a freshness key, not field-presence vs hash.

## Transfer attempt

Tried lockident: `--identity` is a 12-char digest of a blob, `--blob name=bytes`
membership. It cannot name `ref` present vs omitted while `rev` is equal and
`narHash` diverged. Transfer fails; this CLI is the harvest.

## Core operation

Compare two fetch records on the time axis FIRST=earlier, SECOND=later.
Ingest TSV maps, nix/flake lock JSON (`url`/`type` ignored), or a native
narHash mismatch log. Print one `verdict` for the join: default-ref attach
AND changed identity on the same rev. Presence of `ref` is not the token
`none`. lastModified/revCount are metadata, not identity.

## Observable delta

One query names attached default ref vs changed identity. Diff of the two
records names the field delta, not the verdict.

## Reality mapping

Owned pair from `narhash_mismatch.txt`. Native log ingest discovers
`master`. No nix.

## Removed

Invented nix eval / flake prefetch transcripts.

## Smallest artifact

Python 3 stdlib CLI `refpin`.
