repository: pnpm/pnpm
pr: https://github.com/pnpm/pnpm/pull/10911
issue: https://github.com/pnpm/pnpm/issues/10911
related_issue_crlf_hash: https://github.com/pnpm/pnpm/issues/4961
related_pr_crlf_hash: https://github.com/pnpm/pnpm/pull/4969
related_issue_merger_drop: https://github.com/pnpm/pnpm/issues/8366
failing_ref (format-change commit, no read migrate): 223b9b2e993fcd8766fb0681fc03a349462f1916
failing_parent (old {path,hash} writer): 60d3a328bc047c211f75936d54003323ee7ee245
fixed_ref (migrate old format on read): fabf694a81b55f3a572c5a511d8f0651dcb495c8
head_sha: 0b305324f8c0f22c3a747e77ef0da13ba0b1ae28
merge_commit_sha: aeb06caae9585d14a51afdfd97e8494b31d72383
merged_at: 2026-03-08T18:26:48Z
merged_by: zkochan
milestone: v11.0
pr_title: refactor: simplify patchedDependencies lockfile format
changed_files: lockfile/fs/src/lockfileFormatConverters.ts, lockfile/settings-checker/src/calcPatchHashes.ts, lockfile/types/src/index.ts, patching/types/src/index.ts, patching/config/src/groupPatchedDependencies.ts, pkg-manager/core/test/install/patch.ts
scout_note: not specimen-068 (pacquet Unix node env-hop). not specimen-082/peerleft (bun leftover packages vs mention). not specimen-085 (derived yaml object vs string fixture, no git pins). not specimen-086 (cargo rustc fingerprint). Distinct leftover: path field still present in LockfileObject after 223b9b2 when reading a parent-format lockfile, vs hash-only string after fabf694.
