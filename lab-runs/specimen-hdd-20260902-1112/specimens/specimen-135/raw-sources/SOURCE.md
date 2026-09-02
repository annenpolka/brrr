repository: dprint/dprint
issue: https://github.com/dprint/dprint/issues/1135
pr: https://github.com/dprint/dprint/pull/1138
failing_ref (parent of squash on main): 6fc0a066370e2c3a2a1030c56fbc229918a45cef
fixed_ref (include plugin's resolved config in incremental cache key): 0d9c1f2dc3b1ba9d916ba663eefc196f19ba1f9f
merged_at: 2026-05-31T16:32:42Z
pr_author: dsherret
merged_by: dsherret
changed_files: crates/dprint/src/resolution.rs, crates/dprint/src/plugins/implementations/mod.rs
pr_title: fix: include plugin's resolved config in incremental cache key
scout_note: not 132 eslint plugin-meta. not 133 stylelint empty CLI hash. Distinct leftover: host incremental hash omits plugin resolved cache_key so leftover cache after cacheKeyFiles change is treated as current. job-0581 unique vs 001-134.
