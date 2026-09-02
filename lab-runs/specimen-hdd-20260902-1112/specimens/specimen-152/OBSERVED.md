# OBSERVED

Public bazel-contrib/rules_distroless#237 (merged 2026-07-28). Squash `52a250a1135cd35440a3ff6616fc4f6ebd4819a0` (parent `42dd9a20c5c761e4131325a2cf594a753ffffa2d`). Local rules_distroless was not performed on this lab host.

PR body: the URL of the snapshot was not part of the cache key for facts. Upgrading the snapshot (everything else the same) yielded stale facts and stale packages. Repair bakes snapshot source URLs into the facts key and prunes facts from unused URLs.

On failing_ref, `_fetch_and_parse_sources` builds `pkg_fact_key` from dist/component/architecture only, then `glock.facts().get(pkg_fact_key)` on snapshot suites.

Not this packet: bazel#29298 `env_inherit` action cache local vs remote (SKIP unfixed). specimen-064/070 nix leftover. specimen-136 pants leftover vcs_version.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
