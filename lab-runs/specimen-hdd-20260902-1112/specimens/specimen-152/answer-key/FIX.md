KNOWN FIX (sealed): bazel-contrib/rules_distroless PR 237 squash 52a250a1135cd35440a3ff6616fc4f6ebd4819a0.

failing_ref is parent 42dd9a20c5c761e4131325a2cf594a753ffffa2d.

pkg_fact_key was dist/component/architecture/Packages with snapshot URL omitted. Upgrading the snapshot kept leftover previous facts and stale packages.

PR repair: index_fact_key appends sorted-deduplicated snapshot URLs; prune facts whose keys are not in this run's used_keys.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
