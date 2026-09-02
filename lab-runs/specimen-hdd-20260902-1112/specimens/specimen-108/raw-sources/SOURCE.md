repository: npm/cli
issue: https://github.com/npm/cli/issues/9613
pr: https://github.com/npm/cli/pull/9632
failing_ref (squash parent): 696801574984ad19ffaa9a7200d7e752920a018d
fixed_ref (squash merge): 981e2498589c83859b3c9e8b92a2cc67562dc06b
merged_at: 2026-06-24T18:17:22Z
changed_files: workspaces/arborist/lib/arborist/reify.js, workspaces/arborist/test/arborist/reify.js
pr_title: fix(arborist): remove stale .bin shims after uninstall under linked
scout_note: not specimen-004/082/095 peer leftover. Distinct leftover: linked uninstall sweeps store+top-level links but skips .bin, leaving dangling shim identity. job-0339 git+ssh vs registry had no merged pair; packed this leftover-identity instead.
