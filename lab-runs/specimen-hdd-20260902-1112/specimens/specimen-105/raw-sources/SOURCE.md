repository: denoland/deno_lockfile
pr: https://github.com/denoland/deno_lockfile/pull/62
consumer_pr: https://github.com/denoland/deno/pull/30998
failing_ref (squash parent): df96f06c70aaba8aa9152afc7726a78101694cdb
fixed_ref (squash merge): 3ef94bed3135eeae91515f8451a67de62094fe34
consumer_merge: e43662812db4f1c9c51aec875781d80593727313
merged_at: 2025-10-16T14:19:33Z
merged_by: dsherret
pr_author: dsherret
changed_files: src/graphs.rs, tests/specs/config_changes/remove_jsr_dep_with_npm_dep_shared_with_other_jsr_dep.txt
pr_title: fix: purged package reqs should be removed from the jsr deps when changing workspace config
scout_note: not npm leftover lock members (004/082/095). Distinct leftover: jsr.dependencies still names an npm: specifier after workspace purge removed it from specifiers.
