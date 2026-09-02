# Harvest: hdd-pipempty

- Core Affordance: For one key, show absent vs empty vs nonempty across config layers and which value won.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read two pip.conf files plus printenv
- Observable Delta: one query that distinguishes empty override from skipped empty
- Surviving Abstractions: layered empty clobber; empty ≠ unset
- Removed Magic: pip checkout, network install
- Reality Mapping: owned two-layer config fixture; adjacent to envlayers
- Research Boundary: does not implement pip
- Smallest Useful Artifact: CLI that prints layer presence/empty/value and winner
- Why Existing Tools Are or Are Not Enough: reading files does not show skip-empty vs clobber
- Source Specimens: specimen-031
- Origin trial: hdd-pipempty
