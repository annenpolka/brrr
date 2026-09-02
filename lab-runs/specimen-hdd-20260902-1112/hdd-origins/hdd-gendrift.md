# Harvest: hdd-gendrift

- Core Affordance: Name the stale generated file and whether numeric identity rows collide with named opcode ids.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: read the CI diff and the generator comment
- Observable Delta: one query that treats identity-row vs named-id collision as the object
- Surviving Abstractions: generated-file drift; numeric vs named index
- Removed Magic: cpython-dev CLI
- Reality Mapping: packet diff on pycore_opcode_metadata.h
- Research Boundary: does not run make regen-all
- Smallest Useful Artifact: CLI that joins a regen diff with opcode id names
- Why Existing Tools Are or Are Not Enough: the CI job already shows a diff
- Source Specimens: specimen-054
- Origin trial: hdd-gendrift
