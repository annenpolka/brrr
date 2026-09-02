# Fossil: staleid

Date: 2026-09-02
Origin: hdd-gocache / specimen-078
Destroyers: DESTROYER_staleid.md (KEEP), DESTROYER_staleid_2.md

**KILL** (Honor, second destroyer). THIN_WRAPPER of caller-labeled stale vs
live identity. `stale_binary` is `same_key` AND second `FRESH` AND
`cached_buildid != buildid` on records the caller already filled.
`key_includes_buildid` is whether two caller keys moved when two caller
buildids moved. Independent replica was byte-identical on 40/40 cases.
Second record against itself still prints `stale_binary yes`. Analog
`gocache_buildid.py` already prints `stale_binary True`. First KEEP is
not protection.

Not a first-selection KEEP lineage. Archive left under
`lineages/candidate-staleid/`. Do not mutate. Do not wrap `go tool buildid`
or a key function. Reimpl of this primitive is not a survivor.
