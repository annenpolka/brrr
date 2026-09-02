# Harvest: hdd-order

- Core Affordance: For two tests that share mutable module state, show which name leaked and which run order is sufficient to expose the failure.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: run the suite twice in opposite orders and print the leftover list
- Observable Delta: one query that reports leaked name plus exposing order instead of a two-run manual diff
- Surviving Abstractions: leak provenance; order as a first-class input
- Removed Magic: testflow-analyzer, JSON captures, inject-cleanup, hidden module-reload oracle
- Reality Mapping: execute the two ordered call sequences already in the owned fixture; print leak name, leftover value, pass/fail per order
- Research Boundary: does not infer pytest collection internals unless that runner is the fixture
- Smallest Useful Artifact: CLI that takes two ordered runs (or a tiny pair of callables) and prints leaked name + sufficient exposing order
- Why Existing Tools Are or Are Not Enough: pytest shows a single failure; it does not name the leak or the contrasting order as one object
- Source Specimens: specimen-009 (original), specimen-012 (unseen pair)
- Origin trial: hdd-order
