# HDD Ledger

Iteration: 2

## Preserve

- A cache can report FRESH while a newly requested output kind is absent
- Freshness identity may be keyed by inputs while requested outputs sit outside that identity
- FRESH plus a missing requested extra output is the observable

## Established

- Packet: first build without extra artifact, second build requests SBOM precursor, cache hit, file missing
- Turn 1 packet: first build without extra artifact, second build requests it, cache hit, file missing
- Owned cache_build.py prints first BUILT extra_exists False; second FRESH extra_exists False same key

## Rejected

- cargo-inspect is not present; its JSON is Dreamer-generated
- Specific fingerprint hashes and rustc 1.78.0 are unsupported precision
- CARGO_BUILD_SBOM / -Zsbom / sbom-precursor.json were not produced on this host
- Recommendations to change the cargo cache key are not specimen evidence
- cargo build logs in this turn are not host-executed

## Constraints

- No cache-introspection CLI that lists fingerprint components exists
- Observable evidence is build status text and whether named output files exist
- No cache-introspection CLI
- Observable evidence is FRESH/BUILT text and whether named output files exist
- Prefer the owned input-hash cache fixture over an invented cargo tree
- Ground on the owned Python cache fixture

## Open Questions

- Can the tool name the identity mismatch using only FRESH/BUILT and a missing path?

## Human Pressure

- There is no cache-introspection CLI that lists fingerprint components. Only build status text and whether named output files exist are observable. A tiny owned cache that keys only on input hash and ignores extra outputs is present. Use the same tool on that fixture.

## Harvest Candidates

- Ask which requested outputs are absent from the freshness identity that just said FRESH
- Report identity miss: FRESH while requested output absent

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: given two builds, say whether freshness identity omitted a requested output
Nearest existing operation: ls the output dir after a cache hit
Observable delta: names FRESH-but-missing as an identity miss not a successful hit
Reason: ls cannot say why the extra output was not part of the key
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
