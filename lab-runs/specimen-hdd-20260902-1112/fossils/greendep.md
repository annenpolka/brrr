# Fossil: greendep

Date: 2026-09-02
Origin: hdd-rustcinc / specimen-075
Destroyers: DESTROYER_greendep.md (MUTATE applied), DESTROYER_greendep_2.md
(MUTATE applied), DESTROYER_greendep_3.md

**KILL** (Honor, third destroyer). After per-query / incomplete / cap / `-`
mutations, the object is still THIN_WRAPPER of
`set(changed[q]) - set(recorded[q])` (plus intersection) on a
caller-complete query/dep/changed table. Independent replica of leftover+rc
was byte-identical 51/51. Mutation could not recover edges from a dump.
Do not grow a rustc `-Zdump-dep-graph` importer. Do not send THIN_WRAPPER
back to R1. Do not merge into visitid.

Not a first-selection KEEP lineage. Archive left under
`lineages/candidate-greendep/`. Reimpl of this primitive is not a survivor.
