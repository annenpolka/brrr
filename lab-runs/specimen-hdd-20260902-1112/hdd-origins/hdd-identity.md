# Harvest: hdd-identity

- Core Affordance: For a name that exists in two files after a move, report which definition a given import actually bound.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: python import plus inspect.getfile / printing both results
- Observable Delta: one query that names the bound file and body for the imported name instead of grepping every parse
- Surviving Abstractions: split identity; stale import vs moved body
- Removed Magic: import tracer, bytecode signatures, memory addresses
- Reality Mapping: import both modules; print bound module, function id equality, and return values for the same input
- Research Boundary: does not reconstruct git-blame history; it answers the import that actually ran
- Smallest Useful Artifact: CLI that, given two modules and a name, prints which object the caller bound
- Why Existing Tools Are or Are Not Enough: grep/blame list candidates; they do not say which identity the failing test executed
- Source Specimens: specimen-013
- Origin trial: hdd-identity
