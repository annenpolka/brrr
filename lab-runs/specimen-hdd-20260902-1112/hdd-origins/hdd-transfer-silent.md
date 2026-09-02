# Harvest: hdd-transfer-silent

- Core Affordance: Given two otherwise-similar pair traces, name the one field that explains pass vs fail.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read both prints and diff by eye
- Observable Delta: one query that names the discriminating field
- Surviving Abstractions: paired-trace single axis
- Removed Magic: unseen-cli, poetry resolver
- Reality Mapping: owned pair_extras.py (specimen-017)
- Research Boundary: does not run a package solver
- Smallest Useful Artifact: CLI that diffs two pair records and emits the only differing key
- Why Existing Tools Are or Are Not Enough: diff shows many lines; the remainder is naming the axis
- Source Specimens: specimen-017 (paired from specimen-021)
- Origin trial: hdd-transfer-silent
