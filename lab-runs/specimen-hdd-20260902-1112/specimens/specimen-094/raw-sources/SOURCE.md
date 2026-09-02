repository: vitest-dev/vitest
issue: none (PR body is the report)
pr: https://github.com/vitest-dev/vitest/pull/9077
related: https://github.com/vitest-dev/vitest/pull/9076
failing_ref (squash parent): 229b5b3b352b52b82aecf258bea7cb65670f2ae2
fixed_ref (squash merge commit): e1b2e086a40ce154ae11714fa71749ec21b1ac23
head_sha: d3ef427464c46c207bce418e1b0ad5d77ee913a7
merged_at: 2025-11-24T15:29:28Z
merged_by: sheremet-va
changed_files: packages/vitest/src/node/cache/fsModuleCache.ts, packages/vitest/src/node/environments/fetchModule.ts
pr_title: fix: externalize before caching
scout_note: not pytest 001-003. not #11029 leftover cacheConfig bytes in every module key. not #10869 leftover __vitestTmp after sweep. not #9422 leftover importers in cache payload. Distinct leftover: getCachePath still hashes file content into H_ext and saveMemoryCache for a module that later returns {externalize}; data:/client/network omit the key entirely.
