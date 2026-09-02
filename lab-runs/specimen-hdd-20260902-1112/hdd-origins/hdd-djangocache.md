# Harvest: hdd-djangocache

- Core Affordance: For a response, name which Cache-Control tokens blocked store vs which were ignored, and whether the second GET was a cache hit.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read Cache-Control and compare two response bodies
- Observable Delta: one query that treats private-vs-no-store store policy as the object
- Surviving Abstractions: store-policy tokens; second-GET provenance
- Removed Magic: Django checkout
- Reality Mapping: owned token table (private / no-store / no-cache)
- Research Boundary: does not reimplement middleware
- Smallest Useful Artifact: CLI that labels store vs skip per token and hit vs miss
- Why Existing Tools Are or Are Not Enough: identical timestamps look like a slow clock
- Source Specimens: specimen-032
- Origin trial: hdd-djangocache
