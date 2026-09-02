# keptfp

Name which cache fingerprints still match the current lockfile versus leftover hashes.

Workspace-member fingerprints from an older lockfile can sit beside live
artifacts after a lockfile bump. External dependency caches should remain.
`ls` of fingerprint dirs does not name leftover vs live.

This is a lockfile-hash plus entry-list fixture, not uv.

## Usage

```
keptfp RECORD
keptfp < RECORD
```

Record fields (tab-separated):

| field | meaning |
| --- | --- |
| `current HASH` | live lockfile hash |
| `entry ID MEMBER HASH [SIZE]` | one cache fingerprint |

## Output

```
current	f0e1d2c3b4
live	fm_8e9f0a1b	project_a	f0e1d2c3b4	131MB
leftover	fm_7a1b2c3d	project_a	a1b2c3d4e5	124MB
leftover	fm_5c6d7e8f	project_b	a1b2c3d4e5	118MB
live_n	1
leftover_n	2
leftover_members	project_a	project_b
```

## Example (specimen-006)

`keptfp fixtures/006-cache.rec` names one live fingerprint and two leftover
hashes without deleting anything.
