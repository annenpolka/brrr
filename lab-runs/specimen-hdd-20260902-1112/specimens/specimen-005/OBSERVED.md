# OBSERVED

Public rust-lang/cargo#15695 / PR 17216.

1. Build without SBOM — succeeds, unit in cache.
2. Rebuild same unit with SBOM requested.
3. Cache hit. Expected SBOM precursor is not in top-level target output.

Regression test on the PR: build once without SBOM, enable it, assert precursor appears. On the failing revision it does not.
