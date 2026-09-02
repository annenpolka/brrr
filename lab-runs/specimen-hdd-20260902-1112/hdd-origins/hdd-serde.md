# Harvest: hdd-serde

- Core Affordance: For one flatten unit-variant value, name which direction of the format boundary accepted it and which rejected it.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: run de and ser tests and read the panic
- Observable Delta: one query that treats ser/de disagreement as the object
- Surviving Abstractions: format-boundary asymmetry; unit variant as map key + null
- Removed Magic: serde-tokens, cargo, crate checkout
- Reality Mapping: packet snippet JSON {"Unit":null} plus the flatten ser error string
- Research Boundary: does not reimplement serde
- Smallest Useful Artifact: CLI that labels de vs ser for a flatten unit-variant case
- Why Existing Tools Are or Are Not Enough: sibling variants already round-trip; the remainder is the unit-variant boundary
- Source Specimens: specimen-050
- Origin trial: hdd-serde
