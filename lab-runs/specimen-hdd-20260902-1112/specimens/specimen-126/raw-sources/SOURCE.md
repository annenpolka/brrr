repository: npm/cli
issue: https://github.com/npm/cli/issues/9659
pr: https://github.com/npm/cli/pull/9671
failing_ref (squash parent): ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
fixed_ref (squash merge): 968e42fbd62eb3a6f446466359c9431f41d76b2b
merged_at: 2026-06-26T13:30:43Z
pr_author: manzoorwanijk
merged_by: owlstronaut
changed_files: workspaces/arborist/lib/arborist/build-ideal-tree.js, workspaces/arborist/lib/arborist/load-actual.js, workspaces/arborist/test/arborist/build-ideal-tree.js, workspaces/arborist/test/arborist/load-actual.js
pr_title: fix(arborist): apply overrides across a file:/workspace link boundary
scout_note: not specimen-004/033 optional-peer leftover. not specimen-095 subsequent-install OverrideSet leftover. Distinct leftover: nested root override omitted across file: Link so leftover original transitive identity stays in the lock. job-0530 was coord-skipped as already 095; this axis is leftover original across Link, not leftover OverrideSet after subsequent install.
