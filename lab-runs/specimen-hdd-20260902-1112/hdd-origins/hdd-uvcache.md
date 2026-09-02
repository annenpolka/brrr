# Harvest: hdd-uvcache → fossil keptfp

- Core Affordance: Name which cache fingerprints still match the current lockfile versus leftover hashes, without deleting the whole cache.
- Affordance Classification: USEFUL_COMPOSITION at Red Pen; THIN_WRAPPER at destroyer.
- Source Specimens: specimen-006
- Origin trial: hdd-uvcache
- Embodiment: `lineages/candidate-keptfp/keptfp`
- Transfer: adjacent to freshmiss/lockident (identity miss, leftover hashes) — do not merge
- Rejected: invented `uv cache list/clean --type=workspace-member`
- Destroyer: DESTROYER_keptfp_2.md Honor-KILL (caller fingerprint membership `lockfile_hash == current`). First MUTATE is not protection. Mutation never queued.
