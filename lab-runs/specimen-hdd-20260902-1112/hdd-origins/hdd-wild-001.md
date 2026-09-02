# Harvest: hdd-wild-001

- Core Affordance: Compare pytest and direct-call results for one function and name the disagreement.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: run pytest and python -c and diff by eye
- Observable Delta: one query that treats the two-runtime disagreement as the object
- Surviving Abstractions: dual-runtime delta
- Removed Magic: dv, test_mode, hidden inspectors
- Reality Mapping: packet pytest vs python -c already captured
- Research Boundary: does not invent module flags
- Smallest Useful Artifact: CLI that runs or accepts two results and names the mismatch
- Why Existing Tools Are or Are Not Enough: each command looks locally consistent
- Source Specimens: wild-001
- Origin trial: hdd-wild-001
