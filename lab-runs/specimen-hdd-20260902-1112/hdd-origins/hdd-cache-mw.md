# Harvest: hdd-cache-mw

- Core Affordance: Name the byte strings that formed a freshness identity and say whether the live lockfile is among them.
- Affordance Classification: USEFUL_COMPOSITION
- Nearest Existing Operation: print the fixture key twice and diff the lockfile by hand
- Observable Delta: one query that labels lockfile-in-identity vs lockfile-omitted
- Surviving Abstractions: identity membership; lockfile as an optional key input
- Removed Magic: cargo-inspect, real crate cache, invented tmp artifact paths
- Reality Mapping: owned cache_lock.py (specimen-016); compare src hash vs lock hashes
- Research Boundary: does not reconstruct cargo fingerprints
- Smallest Useful Artifact: CLI that reports which provided blobs hashed into the identity
- Why Existing Tools Are or Are Not Enough: sha256 of src and of lock are two commands; they do not join FRESH to omitted lock bytes
- Source Specimens: specimen-016 (derived from specimen-006)
- Origin trial: hdd-cache-mw
