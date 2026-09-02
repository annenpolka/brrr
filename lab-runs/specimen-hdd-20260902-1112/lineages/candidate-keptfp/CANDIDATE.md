# keptfp

origin.method: hdd
origin.trial: hdd-uvcache
specimens: [specimen-006]

classification: USEFUL_COMPOSITION

## Primitive

Given a current lockfile hash and cache fingerprint entries, name which
entries still match (live) versus leftover hashes. Does not delete.

## Why this might not exist

A cache restore is reported as success. Leftover workspace-member
fingerprints sit beside live artifacts after a lockfile bump. `ls` plus
`grep` of fingerprint dirs still leaves the join — this hash is current,
those hashes are leftover — as a hand comparison. Deleting the whole cache
removes external deps the packet wanted to keep.

## Core operation

Read `current` plus `entry` rows (id, member, lockfile_hash, size). Print
live rows whose hash equals current, leftover rows whose hash does not,
and leftover member names.

## Observable delta

One query names leftover vs live without a whole-cache wipe.

## Reality mapping

Owned record `fixtures/006-cache.rec`: current `f0e1d2c3b4`, three entries,
one live, two leftover. uv is not executed.

## Research boundary

Does not reconstruct uv/cargo caches. Does not delete files. Does not invent
entry names.

## Removed

`uv cache list/clean --type=workspace-member --exclude-lockfile-hash`,
`uv lockfile-hash`.

## Smallest artifact

Python 3 stdlib CLI `keptfp`.

## How to run

```
python3 tests/test_keptfp.py
./demo.sh
```
