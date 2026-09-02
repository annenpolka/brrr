# Harvest: hdd-k8s

- Core Affordance: For wait flags, report whether timeout 0 still visits the object or aborts on a creation-wait default.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read help text plus the error string
- Observable Delta: one query that names abort-before-visit vs one-shot check
- Surviving Abstractions: timeout-zero semantics; visit vs abort
- Removed Magic: live cluster, invented kubectl transcripts
- Reality Mapping: owned options fixture (timeout, wait-for-creation, for=delete)
- Research Boundary: does not talk to a kube API
- Smallest Useful Artifact: CLI over flag records that prints visited vs aborted
- Why Existing Tools Are or Are Not Enough: the error looks like a user mistake; it does not name the one-shot path
- Source Specimens: specimen-044
- Origin trial: hdd-k8s
