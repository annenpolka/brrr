# Harvest: hdd-protobuf

- Core Affordance: For a nested Any-like payload, name which parser instance ran and whether outer ignore-unknown applied.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read two error strings and the outer flag
- Observable Delta: one query that treats inner-instance options as the object
- Surviving Abstractions: nested parser identity; option non-propagation
- Removed Magic: C++ greps, TypeInfo constructors, public patch
- Reality Mapping: owned nested-options fixture (outer ignore vs inner defaults)
- Research Boundary: does not rebuild protobuf
- Smallest Useful Artifact: CLI that prints outer vs inner option records for one nested object
- Why Existing Tools Are or Are Not Enough: the error looks like unknown fields are forbidden globally
- Source Specimens: specimen-041
- Origin trial: hdd-protobuf
