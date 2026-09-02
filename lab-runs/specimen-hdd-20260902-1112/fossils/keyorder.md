# Fossil: keyorder

Date: 2026-09-02
Origin: hdd-hypothesis / specimen-034
Destroyers: DESTROYER_keyorder.md (MUTATE), DESTROYER_keyorder_2.md

**KILL** (Honor, second destroyer). THIN_WRAPPER of key-order diff on
caller JSON / mapping literals: `tuple(keys)` vs `tuple(sorted(keys))`
vs `tuple(--obj)` after `ast.literal_eval`. Independent replica of
inspect TSV was byte-identical 29/29. `json.loads` +
`list(d)==sorted(d)` vs `list(d)==list(obj)` matches CLI labels 4/4.
`jq keys` vs `keys_unsorted` already names the JSON split. First MUTATE
is not protection. Mutation leftover (1)+(2)+(3) never landed; sha256
unchanged. No `MUTATE.md`.

Not a first-selection KEEP. Archive left under
`lineages/candidate-keyorder/`. Do not mutate. Do not grow a pytest dump
parser or a pretty-printer port. Do not send key-order theater back to R1.
