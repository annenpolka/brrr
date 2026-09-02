# Harvest: hdd-hypothesis → fossil keyorder

- Core Affordance: Label each displayed mapping as sorted-keys vs insertion-order when those views disagree.
- Affordance Classification: USEFUL_COMPOSITION at Red Pen; THIN_WRAPPER at destroyer.
- Source Specimens: specimen-034
- Origin trial: hdd-hypothesis
- Embodiment: `lineages/candidate-keyorder/keyorder`
- Rejected: Hypothesis checkout, pytest dump scraping, pretty-printer port
- Destroyer: DESTROYER_keyorder_2.md Honor-KILL (key-order diff on caller JSON / mapping literals; `tuple(keys)` vs `sorted` vs `--obj`). First MUTATE is not protection. Replica 29/29. Do not wrap `json.dumps(sort_keys=True)` / `jq keys`.
