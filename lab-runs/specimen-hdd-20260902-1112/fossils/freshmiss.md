# Fossil: freshmiss

Date: 2026-09-02
Origin: hdd-fingerprint / specimen-011 (022/024 queued, 071 stub leftover)
Destroyers: DESTROYER_freshmiss.md (MUTATE), DESTROYER_freshmiss_2.md

**KILL** (Honor, second destroyer). THIN_WRAPPER of two identity hashes
plus extra-stub vs produced. `same_identity` is string equality of two
caller `identity` fields. `FRESH-but-missing` is that equality AND exact
`FRESH` AND `requested - present`. `FRESH-but-stub` is extra present AND
`sizes.get(name, -1) == 0`. Independent replica was byte-identical on
63/63 cases. First MUTATE is not protection. Mutate-freshmiss-2 landed
only the stub integer; (1)+(3)+(7) and env/flag omitted did not.

Not a first-selection KEEP lineage. Archive left under
`lineages/candidate-freshmiss/`. Do not mutate. Do not grow a cargo
fingerprint / uv key / cache hasher. Do not merge onto stubextra.
Reimpl of this primitive is not a survivor.
