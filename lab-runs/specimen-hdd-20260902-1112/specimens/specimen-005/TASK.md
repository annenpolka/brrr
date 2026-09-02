# TASK

A crate is built once. A second build requests an extra artifact kind (SBOM precursor) for the same unit via `CARGO_BUILD_SBOM=true` and `-Zsbom`. Cargo reports the unit fresh. The extra artifact is missing from the target directory.

The developer wants to know what the cache considered “the same build” and which requested outputs were not part of that identity.
